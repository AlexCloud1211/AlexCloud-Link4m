from flask import Flask, request, jsonify, render_template
import os
import json
import time
import threading

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
        
        print(f"\n📦 ĐƠN HÀNG MỚI!")
        print(f"👤 User: {user_id}")
        print(f"📦 Sản phẩm: {json.dumps(items, indent=2)}")
        print(f"💰 Tổng: {total} VND")
        print("="*50)
        
        # Lưu vào file
        with open('orders.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] User {user_id}: {json.dumps(items)} | Total: {total}\n")
        
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
# TELEGRAM BOT
# ============================================

def run_bot():
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
        
        app = Application.builder().token(BOT_TOKEN).build()
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            keyboard = [
                [InlineKeyboardButton("🛒 Vào Shop", web_app=WebAppInfo(url=WEBAPP_URL))],
                [InlineKeyboardButton("📦 Đơn hàng", callback_data='orders')],
                [InlineKeyboardButton("📞 Liên hệ", callback_data='contact')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🛍️ <b>ZENMODS SHOP</b>\n\n"
                "🔹 Hack FreeFire Root/Non-Root\n"
                "🔹 Mod iOS\n"
                "🔹 Tool Auto Headshot\n"
                "🔹 Skin Hack\n\n"
                "👇 <b>Bấm nút bên dưới để mua hàng!</b>",
                reply_markup=reply_markup,
                parse_mode='html'
            )
        
        async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            if query.data == 'orders':
                await query.edit_message_text("📦 <b>ĐƠN HÀNG</b>\n\nChưa có đơn hàng nào!", parse_mode='html')
            elif query.data == 'contact':
                await query.edit_message_text(
                    "📞 <b>LIÊN HỆ</b>\n\n"
                    "Admin: @ZenVnStore\n"
                    "Group: https://t.me/ZenStoreVn",
                    parse_mode='html'
                )
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        print("🤖 Bot đang chạy...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"❌ Lỗi bot: {e}")

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Đang chạy Flask trên port {port}...")
    flask_app.run(host='0.0.0.0', port=port, debug=False)
