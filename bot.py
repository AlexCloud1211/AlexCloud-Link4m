from flask import Flask, request, jsonify, render_template
import os
import json
import time
import threading
import logging

# ===== TẮT LOG =====
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

# ============================================
# CẤU HÌNH
# ============================================

BOT_TOKEN = '8856256732:AAHbU087YImuUwheV4qhkh_uvZH0DOq6dnw'
ADMIN_ID = 7463456773  # ID Telegram của bạn (Admin)
WEBAPP_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://alexcloud-link4m.onrender.com')

# ============================================
# FLASK APP
# ============================================

flask_app = Flask(__name__)

# ============================================
# DỮ LIỆU SẢN PHẨM
# ============================================

PRODUCTS = [
    {"id": 1, "name": "Hack FF Root", "price": 50000, "desc": "Full tính năng cho FF"},
    {"id": 2, "name": "Hack FF Non-Root", "price": 70000, "desc": "Không cần root vẫn xài"},
    {"id": 3, "name": "Mod iOS", "price": 60000, "desc": "Mod cho iPhone/iPad"},
    {"id": 4, "name": "Auto Headshot", "price": 30000, "desc": "Auto headshot 100%"},
    {"id": 5, "name": "Skin Hack", "price": 20000, "desc": "Mở skin giới hạn"},
    {"id": 6, "name": "ESP Wallhack", "price": 45000, "desc": "Nhìn xuyên tường"},
]

# ============================================
# FLASK ROUTES
# ============================================

@flask_app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Lỗi: {e}", 500

@flask_app.route('/api/products')
def get_products():
    return jsonify(PRODUCTS)

@flask_app.route('/api/order', methods=['POST'])
def create_order():
    """Nhận đơn hàng và gửi qua bot cho Admin duyệt"""
    try:
        data = request.json
        user_id = data.get('user_id', 'Unknown')
        user_name = data.get('user_name', 'Người dùng')
        items = data.get('items', [])
        total = data.get('total', 0)
        amount_paid = data.get('amount_paid', 0)
        status = data.get('status', 'pending')
        
        # Tạo nội dung đơn hàng
        items_str = '\n'.join([f"   • {item['name']} x{item['qty']} = {(item['price'] * item['qty']).to_locale_string()}đ" for item in items])
        
        order_message = f"""
🛍️ <b>ĐƠN HÀNG MỚI CẦN DUYỆT!</b>

━━━━━━━━━━━━━━━━━━
👤 <b>Khách hàng:</b> {user_name}
🆔 <b>User ID:</b> <code>{user_id}</code>

📦 <b>Chi tiết đơn hàng:</b>
{items_str}

💰 <b>Tổng đơn:</b> {total:,.0f} VND
💵 <b>Đã chuyển:</b> {amount_paid:,.0f} VND

📌 <b>Trạng thái:</b> ⏳ Chờ duyệt
━━━━━━━━━━━━━━━━━━

✅ <b>Hành động:</b>
/duyet_{user_id} - Duyệt đơn hàng
/huy_{user_id} - Hủy đơn hàng
        """
        
        # Lưu vào file log
        with open('orders.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] User {user_id} ({user_name}): {json.dumps(items)} | Total: {total} | Paid: {amount_paid} | Status: {status}\n")
        
        # Gửi tin nhắn cho Admin qua Bot (sẽ được xử lý trong thread)
        order_data = {
            'user_id': user_id,
            'user_name': user_name,
            'items': items,
            'total': total,
            'amount_paid': amount_paid,
            'message': order_message
        }
        
        # Lưu vào queue để bot gửi (vì flask không thể gọi bot trực tiếp)
        global pending_orders
        pending_orders.append(order_data)
        
        return jsonify({
            "status": "success",
            "message": "Đơn hàng đã được gửi đến Admin!",
            "order_id": int(time.time())
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/ping')
def ping():
    return "Pong! Bot is alive!", 200

# ============================================
# BOT XỬ LÝ ĐƠN HÀNG - GỬI CHO ADMIN
# ============================================

pending_orders = []
bot_instance = None

def send_order_to_admin(order_data):
    """Gửi đơn hàng cho Admin qua Bot"""
    global bot_instance
    
    if bot_instance is None:
        print("❌ Bot chưa sẵn sàng để gửi tin nhắn")
        return False
    
    try:
        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)
        
        # Gửi tin nhắn cho Admin
        bot.send_message(
            chat_id=ADMIN_ID,
            text=order_data['message'],
            parse_mode='HTML'
        )
        
        # Gửi nút duyệt/hủy
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Duyệt", callback_data=f"duyet_{order_data['user_id']}"),
                InlineKeyboardButton("❌ Hủy", callback_data=f"huy_{order_data['user_id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bot.send_message(
            chat_id=ADMIN_ID,
            text="📌 Chọn hành động:",
            reply_markup=reply_markup
        )
        
        print(f"✅ Đã gửi đơn hàng của {order_data['user_name']} cho Admin")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi gửi tin nhắn cho Admin: {e}")
        return False

def process_pending_orders():
    """Xử lý đơn hàng đang chờ gửi"""
    import time
    while True:
        if pending_orders:
            order = pending_orders.pop(0)
            send_order_to_admin(order)
        time.sleep(2)

# ============================================
# TELEGRAM BOT - CHẠY RIÊNG BIỆT
# ============================================

def run_telegram_bot():
    """Chạy Telegram Bot trong thread riêng"""
    global bot_instance
    
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Bot
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
        
        print("🤖 Đang khởi động Telegram Bot...")
        
        # Tạo ứng dụng
        app = Application.builder().token(BOT_TOKEN).build()
        bot_instance = Bot(token=BOT_TOKEN)
        
        # ===== HANDLERS =====
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            keyboard = [
                [InlineKeyboardButton("🛒 Vào Shop", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton("📦 Đơn hàng", callback_data='orders')],
                [InlineKeyboardButton("📞 Liên hệ", callback_data='contact')],
            ]
            await update.message.reply_text(
                "🛍️ <b>ZENMODS SHOP</b>\n\n"
                "🔹 Hack FreeFire Root/Non-Root\n"
                "🔹 Mod iOS\n"
                "🔹 Tool Auto Headshot\n\n"
                "👇 <b>Bấm nút bên dưới để mua hàng!</b>",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='html'
            )
        
        async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            if query.data == 'orders':
                await query.edit_message_text(
                    "📦 <b>ĐƠN HÀNG</b>\n\nChưa có đơn hàng nào!",
                    parse_mode='html'
                )
            elif query.data == 'contact':
                await query.edit_message_text(
                    "📞 <b>LIÊN HỆ</b>\n\n"
                    "Admin: @ZenVnStore\n"
                    "Group: https://t.me/ZenStoreVn",
                    parse_mode='html'
                )
            elif query.data.startswith('duyet_'):
                user_id = query.data.replace('duyet_', '')
                await query.edit_message_text(
                    f"✅ <b>ĐÃ DUYỆT</b>\n"
                    f"Đơn hàng của User ID: <code>{user_id}</code>\n"
                    f"Đã được xác nhận!",
                    parse_mode='html'
                )
                # Gửi thông báo cho user (nếu có)
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text="✅ Đơn hàng của bạn đã được <b>DUYỆT</b>!\nCảm ơn bạn đã mua hàng!",
                    parse_mode='html'
                )
            elif query.data.startswith('huy_'):
                user_id = query.data.replace('huy_', '')
                await query.edit_message_text(
                    f"❌ <b>ĐÃ HỦY</b>\n"
                    f"Đơn hàng của User ID: <code>{user_id}</code>\n"
                    f"Đã bị hủy!",
                    parse_mode='html'
                )
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text="❌ Đơn hàng của bạn đã bị <b>HỦY</b>!\nVui lòng liên hệ Admin để biết thêm chi tiết.",
                    parse_mode='html'
                )
        
        # Thêm handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        print("🤖 Bot đã sẵn sàng!")
        
        # Chạy polling
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Lỗi bot: {e}")
        import traceback
        traceback.print_exc()

# ============================================
# KHỞI CHẠY
# ============================================

if __name__ == '__main__':
    # ===== CHẠY BOT TRONG THREAD =====
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    print("✅ Bot thread đã khởi động")
    
    # ===== CHẠY THREAD XỬ LÝ ĐƠN HÀNG =====
    order_thread = threading.Thread(target=process_pending_orders, daemon=True)
    order_thread.start()
    print("✅ Order processor đã khởi động")
    
    # ===== CHẠY FLASK =====
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Đang chạy Flask trên port {port}...")
    print(f"🌐 Web App URL: {WEBAPP_URL}")
    
    flask_app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
