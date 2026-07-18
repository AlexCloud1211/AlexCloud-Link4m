from flask import Flask, request, jsonify, render_template
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import json
import time
import threading

# ============================================
# CẤU HÌNH
# ============================================

BOT_TOKEN = '8856256732:AAHbU087YImuUwheV4qhkh_uvZH0DOq6dnw'
YOUR_USER_ID = 7463456773
WEBAPP_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://your-app.onrender.com')

# ============================================
# FLASK APP
# ============================================

flask_app = Flask(__name__)

# ============================================
# DỮ LIỆU SẢN PHẨM
# ============================================

PRODUCTS = [
    {"id": 1, "name": "Hack FreeFire Root", "price": 50000, "desc": "Hack full tính năng cho FF"},
    {"id": 2, "name": "Hack FreeFire Non-Root", "price": 70000, "desc": "Không cần root vẫn xài"},
    {"id": 3, "name": "Mod iOS", "price": 60000, "desc": "Mod cho iPhone/iPad"},
    {"id": 4, "name": "Tool Auto Headshot", "price": 30000, "desc": "Auto headshot 100%"},
    {"id": 5, "name": "Skin Hack", "price": 20000, "desc": "Mở skin giới hạn"},
]

# ============================================
# FLASK ROUTES
# ============================================

@flask_app.route('/')
def index():
    """Trang chủ Web App"""
    return render_template('index.html')

@flask_app.route('/api/products')
def get_products():
    """API lấy danh sách sản phẩm"""
    return jsonify(PRODUCTS)

@flask_app.route('/api/order', methods=['POST'])
def create_order():
    """API tạo đơn hàng"""
    data = request.json
    user_id = data.get('user_id')
    items = data.get('items', [])
    total = data.get('total', 0)
    
    # In ra console
    print(f"\n📦 ĐƠN HÀNG MỚI!")
    print(f"👤 User: {user_id}")
    print(f"📦 Sản phẩm: {json.dumps(items, indent=2)}")
    print(f"💰 Tổng: {total} VND")
    print("="*50)
    
    # Lưu vào file log
    with open('orders.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{time.ctime()}] User {user_id}: {json.dumps(items)} | Total: {total}\n")
    
    return jsonify({
        "status": "success",
        "message": "Đơn hàng đã được ghi nhận!",
        "order_id": int(time.time())
    })

@flask_app.route('/ping')
def ping():
    """Endpoint để ping giữ bot không ngủ"""
    return "Pong! Bot is alive!", 200

# ============================================
# TELEGRAM BOT HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start"""
    keyboard = [
        [InlineKeyboardButton("🛒 Vào Shop", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("📦 Đơn hàng", callback_data='orders')],
        [InlineKeyboardButton("📞 Liên hệ", callback_data='contact')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛍️ <b>CHÀO MỪNG ĐẾN ZENMODS SHOP!</b>\n\n"
        "Chuyên cung cấp:\n"
        "🔹 Hack FreeFire Root/Non-Root\n"
        "🔹 Mod iOS\n"
        "🔹 Tool Auto Headshot\n"
        "🔹 Skin Hack\n\n"
        "👇 <b>Bấm nút Vào Shop để mua hàng!</b>",
        reply_markup=reply_markup,
        parse_mode='html'
    )

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /shop"""
    await update.message.reply_text(
        "🛒 <b>MỞ SHOP...</b>\n"
        "Bấm nút bên dưới để vào cửa hàng:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🛒 Vào Shop", web_app=WebAppInfo(url=WEBAPP_URL))
        ]]),
        parse_mode='html'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý nút bấm"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'orders':
        await query.edit_message_text(
            "📦 <b>ĐƠN HÀNG CỦA BẠN</b>\n\n"
            "Hiện chưa có đơn hàng nào.\n"
            "Hãy vào Shop để mua sắm! 🛒",
            parse_mode='html'
        )
    elif query.data == 'contact':
        await query.edit_message_text(
            "📞 <b>LIÊN HỆ</b>\n\n"
            "Admin: @ZenVnStore\n"
            "Group: https://t.me/ZenStoreVn\n\n"
            "💬 Hỗ trợ 24/7!",
            parse_mode='html'
        )

# ============================================
# KHỞI CHẠY FLASK
# ============================================

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

# ============================================
# KHỞI CHẠY BOT
# ============================================

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🤖 Bot đang chạy...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    # Chạy Flask trong thread riêng
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print(f"🌐 Web App URL: {WEBAPP_URL}")
    print("⏳ Đang khởi động...")
    
    # Đợi Flask khởi động
    import time as t
    t.sleep(3)
    
    # Chạy Bot
    run_bot()
