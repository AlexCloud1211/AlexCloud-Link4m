from flask import Flask, request, jsonify, render_template
import os
import json
import time
import threading
import asyncio
import logging

# ===== TẮT LOG NHIỀU =====
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

# ============================================
# CẤU HÌNH
# ============================================

BOT_TOKEN = '8856256732:AAHbU087YImuUwheV4qhkh_uvZH0DOq6dnw'
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
    try:
        data = request.json
        user_id = data.get('user_id', 'Unknown')
        items = data.get('items', [])
        total = data.get('total', 0)
        status = data.get('status', 'pending')
        
        print(f"\n📦 ĐƠN HÀNG MỚI!")
        print(f"👤 User: {user_id}")
        print(f"📦 Sản phẩm: {json.dumps(items, indent=2)}")
        print(f"💰 Tổng: {total} VND")
        print(f"📌 Trạng thái: {status}")
        print("="*50)
        
        with open('orders.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] User {user_id}: {json.dumps(items)} | Total: {total} | Status: {status}\n")
        
        return jsonify({
            "status": "success",
            "message": "Đơn hàng đã được ghi nhận!",
            "order_id": int(time.time())
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/ping')
def ping():
    return "Pong! Bot is alive!", 200

# ============================================
# TELEGRAM BOT - CHẠY RIÊNG BIỆT
# ============================================

def run_telegram_bot():
    """Chạy Telegram Bot trong thread riêng với asyncio mới"""
    try:
        # Import bên trong để tránh xung đột
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
        
        print("🤖 Đang khởi động Telegram Bot...")
        
        # Tạo ứng dụng
        app = Application.builder().token(BOT_TOKEN).build()
        
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
        
        async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "🛒 <b>MỞ SHOP...</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🛒 Vào Shop", web_app=WebAppInfo(url=WEBAPP_URL))
                ]]),
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
        
        # Thêm handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("shop", shop))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        print("🤖 Bot đã sẵn sàng, đang lắng nghe...")
        
        # Chạy polling (blocking)
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Lỗi bot: {e}")
        import traceback
        traceback.print_exc()

# ============================================
# KHỞI CHẠY
# ============================================

if __name__ == '__main__':
    # ===== CHẠY BOT TRONG THREAD RIÊNG =====
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=False)
    bot_thread.start()
    print("✅ Bot thread đã khởi động")
    
    # ===== CHẠY FLASK =====
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Đang chạy Flask trên port {port}...")
    print(f"🌐 Web App URL: {WEBAPP_URL}")
    
    # Chạy Flask (blocking) nhưng bot chạy song song
    flask_app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
