from flask import Flask, request, jsonify, render_template_string, session
import os
import json
import time
import threading
import logging
import hashlib

# ===== TẮT LOG =====
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

# ============================================
# CẤU HÌNH
# ============================================

BOT_TOKEN = '8856256732:AAHbU087YImuUwheV4qhkh_uvZH0DOq6dnw'
ADMIN_ID = 8336469751  # Bot sẽ gửi thông báo về đây
WEBAPP_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://alexcloud-link4m.onrender.com')
ADMIN_PASS = '121113'
SECRET_KEY = 'zenmods_secret_key_2026'

# ============================================
# FLASK APP
# ============================================

flask_app = Flask(__name__)
flask_app.secret_key = SECRET_KEY

# ============================================
# FILE LƯU SẢN PHẨM
# ============================================

PRODUCTS_FILE = 'products.json'

def load_products():
    """Tải danh sách sản phẩm từ file"""
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except:
        return []

def save_products(products):
    """Lưu danh sách sản phẩm vào file"""
    try:
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ============================================
# MẪU SẢN PHẨM MẶC ĐỊNH
# ============================================

DEFAULT_PRODUCTS = [
    {"id": 1, "name": "Hack FF Root", "price": 50000, "stock": 10, "desc": "Full tính năng cho FF", "image": "🔥"},
    {"id": 2, "name": "Hack FF Non-Root", "price": 70000, "stock": 15, "desc": "Không cần root vẫn xài", "image": "⚡"},
    {"id": 3, "name": "Mod iOS", "price": 60000, "stock": 8, "desc": "Mod cho iPhone/iPad", "image": "📱"},
    {"id": 4, "name": "Auto Headshot", "price": 30000, "stock": 20, "desc": "Auto headshot 100%", "image": "🎯"},
    {"id": 5, "name": "Skin Hack", "price": 20000, "stock": 25, "desc": "Mở skin giới hạn", "image": "👑"},
]

# ============================================
# HTML TEMPLATE
# ============================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>⚡ ZENMODS Shop</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg-primary: #07070f;
            --bg-secondary: #0f0f23;
            --bg-card: rgba(26, 26, 62, 0.7);
            --text-primary: #ffffff;
            --text-secondary: rgba(255,255,255,0.6);
            --accent: #ff6b35;
            --accent2: #f7c948;
            --gradient-main: linear-gradient(135deg, #ff6b35, #f7c948);
            --radius: 20px;
            --radius-sm: 14px;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 16px 16px 140px;
            background-image: radial-gradient(ellipse at 20% 0%, rgba(255,107,53,0.08) 0%, transparent 60%);
        }
        .header { text-align: center; padding: 28px 0 20px; position: relative; }
        .header::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 40%; height: 2px; background: var(--gradient-main); border-radius: 2px; opacity: 0.5; }
        .header .logo { font-size: 60px; display: block; animation: floatVip 3.5s ease-in-out infinite; }
        @keyframes floatVip { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
        .header h1 { font-size: 34px; font-weight: 900; background: var(--gradient-main); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 4px; }
        .header .sub { color: var(--text-secondary); font-size: 13px; margin-top: 4px; }
        .header .sub span { color: var(--accent2); font-weight: 600; }
        .badge-row { display: flex; justify-content: center; gap: 8px; margin: 16px 0 22px; flex-wrap: wrap; }
        .badge { background: rgba(255,255,255,0.04); padding: 6px 18px; border-radius: 30px; font-size: 11px; font-weight: 600; color: var(--text-secondary); border: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; gap: 6px; }
        .badge .dot { width: 7px; height: 7px; border-radius: 50%; background: #00e676; animation: pulseDot 1.5s ease-in-out infinite; }
        @keyframes pulseDot { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        .badge.gold { border-color: rgba(247,201,72,0.25); color: var(--accent2); }
        .badge.premium { background: var(--gradient-main); color: #fff; border: none; }
        
        .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 4px; }
        @media (min-width: 500px) { .product-grid { grid-template-columns: repeat(3, 1fr); } }
        @media (min-width: 768px) { .product-grid { grid-template-columns: repeat(4, 1fr); } }
        
        .product-card {
            background: var(--bg-card);
            border-radius: var(--radius);
            padding: 20px 14px 16px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.04);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        .product-card:hover { transform: translateY(-8px); border-color: rgba(255,107,53,0.25); box-shadow: 0 0 40px rgba(255,107,53,0.15); }
        .product-card .icon-wrap { font-size: 44px; display: block; margin-bottom: 4px; }
        .product-card .name { font-weight: 700; font-size: 14px; margin: 4px 0 2px; }
        .product-card .desc { font-size: 11px; color: var(--text-secondary); margin: 4px 0 8px; min-height: 28px; }
        .product-card .price { font-size: 20px; font-weight: 800; background: var(--gradient-main); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 6px 0 10px; }
        .product-card .price span { font-size: 11px; font-weight: 400; color: var(--text-secondary); -webkit-text-fill-color: var(--text-secondary); }
        .product-card .stock { font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; }
        .product-card .stock .num { color: var(--accent2); font-weight: 700; }
        
        .btn-add { background: var(--gradient-main); border: none; color: #fff; padding: 11px 0; border-radius: 30px; cursor: pointer; font-weight: 700; font-size: 13px; width: 100%; transition: all 0.3s; box-shadow: 0 4px 20px rgba(255,107,53,0.25); }
        .btn-add:hover { transform: scale(1.04); }
        .btn-add:active { transform: scale(0.92); }
        .btn-add:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
        
        .cart {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(15, 15, 35, 0.95);
            padding: 16px 20px 20px;
            border-top: 1px solid rgba(255,107,53,0.12);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            z-index: 100;
            backdrop-filter: blur(30px);
            box-shadow: 0 -8px 60px rgba(0,0,0,0.6);
            border-radius: 28px 28px 0 0;
        }
        .cart-info { display: flex; gap: 14px; align-items: center; font-size: 14px; }
        .cart-info .count { background: var(--gradient-main); color: #fff; padding: 1px 14px; border-radius: 30px; font-size: 13px; font-weight: 700; min-width: 28px; text-align: center; }
        .cart-info .total { font-weight: 800; font-size: 18px; background: var(--gradient-main); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .btn-checkout { background: var(--gradient-main); border: none; color: #fff; padding: 13px 34px; border-radius: 30px; font-weight: 700; cursor: pointer; transition: all 0.3s; font-size: 14px; box-shadow: 0 4px 30px rgba(255,107,53,0.3); }
        .btn-checkout:hover { transform: scale(1.05); }
        .btn-checkout:active { transform: scale(0.94); }
        .btn-checkout:disabled { background: rgba(255,255,255,0.06); box-shadow: none; cursor: not-allowed; opacity: 0.4; }
        
        .toast {
            position: fixed;
            top: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(-40px);
            background: rgba(15, 15, 35, 0.95);
            color: var(--text-primary);
            padding: 16px 32px;
            border-radius: var(--radius-sm);
            display: none;
            z-index: 999;
            font-weight: 600;
            font-size: 14px;
            box-shadow: 0 8px 60px rgba(0,0,0,0.6);
            border: 1px solid rgba(255,107,53,0.12);
            animation: slideDownVip 0.5s ease forwards;
            text-align: center;
            max-width: 90%;
            backdrop-filter: blur(30px);
        }
        @keyframes slideDownVip { from { transform: translateX(-50%) translateY(-40px); opacity: 0; } to { transform: translateX(-50%) translateY(0); opacity: 1; } }
        
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.75);
            backdrop-filter: blur(16px);
            z-index: 200;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .modal-overlay.active { display: flex; }
        .modal-bank {
            background: var(--bg-secondary);
            border-radius: var(--radius);
            padding: 32px 26px 26px;
            max-width: 420px;
            width: 100%;
            border: 1px solid rgba(255,107,53,0.08);
            box-shadow: 0 24px 100px rgba(0,0,0,0.6);
            animation: scaleUpVip 0.4s ease;
            max-height: 95vh;
            overflow-y: auto;
            position: relative;
        }
        @keyframes scaleUpVip { from { transform: scale(0.85) translateY(20px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
        .modal-bank .close-btn { position: absolute; top: 16px; right: 20px; background: none; border: none; color: var(--text-secondary); font-size: 24px; cursor: pointer; }
        .modal-bank .close-btn:hover { color: var(--text-primary); }
        .modal-bank .bank-title { text-align: center; font-size: 22px; font-weight: 800; margin-bottom: 4px; background: var(--gradient-main); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .modal-bank .bank-sub { text-align: center; color: var(--text-secondary); font-size: 13px; margin-bottom: 18px; }
        .modal-bank .qr-container { background: #fff; border-radius: var(--radius-sm); padding: 12px; text-align: center; margin-bottom: 16px; }
        .modal-bank .qr-container img { max-width: 100%; max-height: 180px; border-radius: 8px; }
        .modal-bank .bank-info { background: rgba(255,255,255,0.04); border-radius: var(--radius-sm); padding: 14px 16px; margin-bottom: 14px; }
        .modal-bank .bank-info .row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.04); }
        .modal-bank .bank-info .row:last-child { border-bottom: none; }
        .modal-bank .bank-info .label { color: var(--text-secondary); font-weight: 400; }
        .modal-bank .bank-info .value { font-weight: 700; }
        .modal-bank .bank-info .value.highlight { color: var(--accent2); }
        .modal-bank .amount-input { width: 100%; padding: 14px 18px; border-radius: var(--radius-sm); border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.04); color: var(--text-primary); font-size: 16px; font-weight: 600; outline: none; transition: all 0.3s; margin-bottom: 12px; }
        .modal-bank .amount-input:focus { border-color: var(--accent); box-shadow: 0 0 0 4px rgba(255,107,53,0.1); }
        .modal-bank .amount-input::placeholder { color: var(--text-secondary); font-weight: 400; }
        .modal-bank .copy-btn { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); color: var(--text-primary); padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 12px; font-weight: 600; transition: all 0.3s; }
        .modal-bank .copy-btn:hover { background: rgba(255,107,53,0.12); border-color: rgba(255,107,53,0.2); }
        .modal-bank .btn-confirm { width: 100%; padding: 15px; border: none; border-radius: 30px; background: var(--gradient-main); color: #fff; font-weight: 700; font-size: 16px; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 30px rgba(255,107,53,0.25); }
        .modal-bank .btn-confirm:hover { transform: scale(1.02); }
        .modal-bank .btn-confirm:active { transform: scale(0.96); }
        .modal-bank .btn-confirm:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .modal-bank .note { text-align: center; font-size: 12px; color: var(--text-secondary); margin-top: 12px; }
        .modal-bank .note span { color: var(--accent2); font-weight: 600; }
        
        .empty-state { text-align: center; padding: 60px 20px; color: var(--text-secondary); grid-column: 1/-1; }
        .empty-state .icon { font-size: 52px; display: block; margin-bottom: 12px; }
        .empty-state h3 { font-size: 18px; color: var(--text-primary); margin-bottom: 4px; }
        
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 4px; }
        
        .shimmer { background: var(--bg-card); border-radius: var(--radius); padding: 20px 14px 16px; text-align: center; animation: shimmerVip 1.5s ease-in-out infinite; }
        .shimmer .icon-s { width: 44px; height: 44px; background: rgba(255,255,255,0.04); border-radius: 50%; margin: 0 auto 8px; }
        .shimmer .name-s { height: 14px; background: rgba(255,255,255,0.04); border-radius: 8px; margin: 4px auto; width: 70%; }
        .shimmer .desc-s { height: 10px; background: rgba(255,255,255,0.04); border-radius: 8px; margin: 4px auto; width: 50%; }
        .shimmer .price-s { height: 16px; background: rgba(255,255,255,0.04); border-radius: 8px; margin: 6px auto; width: 40%; }
        .shimmer .btn-s { height: 38px; background: rgba(255,255,255,0.04); border-radius: 30px; margin-top: 8px; }
        @keyframes shimmerVip { 0% { opacity: 0.4; } 50% { opacity: 0.8; } 100% { opacity: 0.4; } }
        
        /* ===== ADMIN FOOTER ===== */
        .admin-footer {
            text-align: center;
            padding: 20px 0 10px;
            margin-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.04);
            position: relative;
            cursor: pointer;
            transition: all 0.3s;
        }
        .admin-footer:hover { opacity: 0.7; }
        .admin-footer .admin-text {
            font-size: 12px;
            color: rgba(255,255,255,0.15);
            letter-spacing: 2px;
            font-weight: 300;
            user-select: none;
        }
        .admin-footer .admin-text span { color: rgba(255,107,53,0.15); }
        
        .admin-panel {
            display: none;
            background: var(--bg-secondary);
            border-radius: var(--radius);
            padding: 24px;
            margin-top: 16px;
            border: 1px solid rgba(255,107,53,0.08);
        }
        .admin-panel.active { display: block; animation: scaleUpVip 0.4s ease; }
        .admin-panel h3 { font-size: 18px; margin-bottom: 16px; background: var(--gradient-main); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .admin-panel input, .admin-panel textarea, .admin-panel select {
            width: 100%;
            padding: 12px 16px;
            border-radius: var(--radius-sm);
            border: 1px solid rgba(255,255,255,0.06);
            background: rgba(255,255,255,0.04);
            color: var(--text-primary);
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
            margin-bottom: 10px;
            font-family: 'Inter', sans-serif;
        }
        .admin-panel input:focus, .admin-panel textarea:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 4px rgba(255,107,53,0.1);
        }
        .admin-panel textarea { min-height: 60px; resize: vertical; }
        .admin-panel .btn-admin {
            background: var(--gradient-main);
            border: none;
            color: #fff;
            padding: 12px 24px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 700;
            font-size: 14px;
            transition: all 0.3s;
            width: 100%;
        }
        .admin-panel .btn-admin:hover { transform: scale(1.02); }
        .admin-panel .btn-admin.danger { background: linear-gradient(135deg, #ff3366, #ff6b35); }
        .admin-panel .product-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 14px;
            background: rgba(255,255,255,0.03);
            border-radius: var(--radius-sm);
            margin-bottom: 8px;
            border: 1px solid rgba(255,255,255,0.04);
        }
        .admin-panel .product-item .info { flex: 1; }
        .admin-panel .product-item .info .pname { font-weight: 600; font-size: 14px; }
        .admin-panel .product-item .info .pdetail { font-size: 12px; color: var(--text-secondary); }
        .admin-panel .product-item .btn-del {
            background: none;
            border: none;
            color: #ff3366;
            font-size: 18px;
            cursor: pointer;
            padding: 4px 12px;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .admin-panel .product-item .btn-del:hover { background: rgba(255,51,102,0.1); }
        .admin-pass-input {
            display: flex;
            gap: 10px;
            margin-bottom: 16px;
        }
        .admin-pass-input input { flex: 1; margin-bottom: 0; }
        .admin-pass-input .btn-unlock {
            background: var(--gradient-main);
            border: none;
            color: #fff;
            padding: 12px 24px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 700;
            white-space: nowrap;
        }
        .admin-pass-input .btn-unlock:hover { transform: scale(1.02); }
    </style>
</head>
<body>
    <!-- ===== TOAST ===== -->
    <div class="toast" id="toast"><span id="toastMsg">✅ Đã thêm vào giỏ hàng!</span></div>

    <!-- ===== MODAL BANK ===== -->
    <div class="modal-overlay" id="bankModal">
        <div class="modal-bank">
            <button class="close-btn" onclick="closeBankModal()">✕</button>
            <div class="bank-title">💎 THANH TOÁN</div>
            <div class="bank-sub">Chuyển khoản ngân hàng</div>
            <div class="qr-container">
                <img src="https://cdn.phototourl.com/free/2026-07-18-6bc7cc20-67ab-4aec-8575-c8c11cc017f5.jpg" alt="QR Bank">
            </div>
            <div class="bank-info">
                <div class="row"><span class="label">🏦 Ngân hàng</span><span class="value highlight">Vietcombank</span></div>
                <div class="row"><span class="label">👤 Chủ tài khoản</span><span class="value">NGO THANH LONG</span></div>
                <div class="row"><span class="label">🔢 Số tài khoản</span><span class="value" id="bankNumber">0911000015181</span></div>
                <div class="row"><span class="label">💰 Tổng đơn hàng</span><span class="value highlight" id="orderTotal">0 VND</span></div>
            </div>
            <div style="display:flex; gap:8px; margin-bottom:12px;">
                <button class="copy-btn" onclick="copyBankNumber()" style="flex:1;">📋 Copy STK</button>
                <button class="copy-btn" onclick="copyBankContent()" style="flex:1;">📋 Copy ND</button>
            </div>
            <input class="amount-input" id="amountPaid" type="number" placeholder="💵 Nhập số tiền bạn đã chuyển..." min="0" step="1000">
            <button class="btn-confirm" id="btnConfirmPayment" onclick="confirmPayment()">✅ Tôi đã chuyển khoản</button>
            <div class="note">📌 Vui lòng nhập <span>chính xác số tiền</span> đã chuyển để admin duyệt</div>
        </div>
    </div>

    <!-- ===== HEADER ===== -->
    <header class="header">
        <span class="logo">⚡</span>
        <h1>ZENMODS SHOP</h1>
        <div class="sub">🔹 <span>Hack</span> · Mod · Tool 🔹</div>
        <div class="badge-row">
            <span class="badge"><span class="dot"></span> Online</span>
            <span class="badge gold">🏆 Uy tín #1</span>
            <span class="badge premium">⚡ VIP</span>
            <span class="badge">💬 24/7</span>
        </div>
    </header>

    <!-- ===== PRODUCTS ===== -->
    <div class="product-grid" id="productGrid">
        <div class="shimmer"><div class="icon-s"></div><div class="name-s"></div><div class="desc-s"></div><div class="price-s"></div><div class="btn-s"></div></div>
        <div class="shimmer"><div class="icon-s"></div><div class="name-s"></div><div class="desc-s"></div><div class="price-s"></div><div class="btn-s"></div></div>
        <div class="shimmer"><div class="icon-s"></div><div class="name-s"></div><div class="desc-s"></div><div class="price-s"></div><div class="btn-s"></div></div>
        <div class="shimmer"><div class="icon-s"></div><div class="name-s"></div><div class="desc-s"></div><div class="price-s"></div><div class="btn-s"></div></div>
    </div>

    <!-- ===== ADMIN FOOTER ===== -->
    <div class="admin-footer" id="adminFooter">
        <div class="admin-text">© 2026 <span>ZENMODS2009</span></div>
        <div class="admin-panel" id="adminPanel">
            <div class="admin-pass-input">
                <input type="password" id="adminPassInput" placeholder="Nhập mật khẩu admin..." />
                <button class="btn-unlock" onclick="unlockAdmin()">🔓 Mở</button>
            </div>
            <div id="adminContent" style="display:none;">
                <h3>📦 QUẢN LÝ SẢN PHẨM</h3>
                <input type="text" id="prodName" placeholder="Tên sản phẩm" />
                <input type="number" id="prodPrice" placeholder="Giá (VND)" />
                <input type="number" id="prodStock" placeholder="Số lượng tồn kho" />
                <input type="text" id="prodImage" placeholder="Icon/Emoji hoặc URL ảnh" />
                <textarea id="prodDesc" placeholder="Mô tả sản phẩm..."></textarea>
                <button class="btn-admin" onclick="addProduct()">➕ Thêm sản phẩm</button>
                <hr style="border-color:rgba(255,255,255,0.06); margin: 16px 0;" />
                <div id="adminProductList"></div>
            </div>
        </div>
    </div>

    <!-- ===== CART ===== -->
    <div class="cart">
        <div class="cart-info">
            <span>🛒</span>
            <span class="count" id="cartCount">0</span>
            <span class="total" id="cartTotal">0 ₫</span>
        </div>
        <button class="btn-checkout" id="btnCheckout" disabled>💳 Thanh toán</button>
    </div>

    <script>
        // ============================================
        // STATE
        // ============================================
        
        let products = [];
        let cart = [];

        // ============================================
        // DOM REFS
        // ============================================
        
        const productGrid = document.getElementById('productGrid');
        const cartCount = document.getElementById('cartCount');
        const cartTotal = document.getElementById('cartTotal');
        const btnCheckout = document.getElementById('btnCheckout');
        const toast = document.getElementById('toast');
        const toastMsg = document.getElementById('toastMsg');
        const bankModal = document.getElementById('bankModal');
        const orderTotal = document.getElementById('orderTotal');
        const amountPaid = document.getElementById('amountPaid');
        const btnConfirm = document.getElementById('btnConfirmPayment');

        // ============================================
        // TELEGRAM WEB APP
        // ============================================
        
        const tg = window.Telegram?.WebApp;
        const userId = tg?.initDataUnsafe?.user?.id || 7463456773;
        const userName = tg?.initDataUnsafe?.user?.first_name || 'Người dùng';
        
        if (tg) {
            tg.ready();
            tg.expand();
            tg.setHeaderColor('#07070f');
            tg.setBackgroundColor('#07070f');
        }

        // ============================================
        // ADMIN
        // ============================================
        
        function toggleAdmin() {
            const panel = document.getElementById('adminPanel');
            panel.classList.toggle('active');
            if (panel.classList.contains('active')) {
                document.getElementById('adminPassInput').focus();
            }
        }
        
        document.getElementById('adminFooter').addEventListener('click', function(e) {
            if (!e.target.closest('.admin-panel') && !e.target.closest('.admin-text')) {
                toggleAdmin();
            }
        });
        
        function unlockAdmin() {
            const pass = document.getElementById('adminPassInput').value;
            if (pass === '121113') {
                document.getElementById('adminContent').style.display = 'block';
                document.getElementById('adminPassInput').parentElement.style.display = 'none';
                loadAdminProducts();
                showToast('✅ Đã mở Admin Panel!');
                if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
            } else {
                showToast('❌ Sai mật khẩu!');
                if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('error');
            }
        }
        
        async function loadAdminProducts() {
            try {
                const res = await fetch('/api/products');
                const data = await res.json();
                renderAdminProducts(data);
            } catch (e) {
                console.error(e);
            }
        }
        
        function renderAdminProducts(prods) {
            const container = document.getElementById('adminProductList');
            if (!prods || prods.length === 0) {
                container.innerHTML = '<p style="color:var(--text-secondary);text-align:center;">Chưa có sản phẩm</p>';
                return;
            }
            container.innerHTML = prods.map(p => `
                <div class="product-item">
                    <div class="info">
                        <div class="pname">${p.icon || '📦'} ${p.name}</div>
                        <div class="pdetail">${p.price.toLocaleString()}đ | Tồn: ${p.stock} | ${p.desc || ''}</div>
                    </div>
                    <button class="btn-del" onclick="deleteProduct(${p.id})">✕</button>
                </div>
            `).join('');
        }
        
        async function addProduct() {
            const name = document.getElementById('prodName').value.trim();
            const price = parseInt(document.getElementById('prodPrice').value);
            const stock = parseInt(document.getElementById('prodStock').value) || 0;
            const image = document.getElementById('prodImage').value.trim() || '📦';
            const desc = document.getElementById('prodDesc').value.trim();
            
            if (!name || !price) {
                showToast('❌ Vui lòng nhập tên và giá!');
                return;
            }
            
            const data = { name, price, stock, image, desc };
            
            try {
                const res = await fetch('/api/admin/products', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                if (result.status === 'success') {
                    showToast('✅ Đã thêm sản phẩm!');
                    document.getElementById('prodName').value = '';
                    document.getElementById('prodPrice').value = '';
                    document.getElementById('prodStock').value = '';
                    document.getElementById('prodImage').value = '';
                    document.getElementById('prodDesc').value = '';
                    loadAdminProducts();
                    loadProducts();
                } else {
                    showToast('❌ ' + result.message);
                }
            } catch (e) {
                showToast('❌ Lỗi kết nối!');
            }
        }
        
        async function deleteProduct(id) {
            if (!confirm('Xóa sản phẩm này?')) return;
            try {
                const res = await fetch(`/api/admin/products/${id}`, { method: 'DELETE' });
                const result = await res.json();
                if (result.status === 'success') {
                    showToast('✅ Đã xóa sản phẩm!');
                    loadAdminProducts();
                    loadProducts();
                }
            } catch (e) {
                showToast('❌ Lỗi!');
            }
        }
        
        // ============================================
        // LOAD PRODUCTS
        // ============================================
        
        async function loadProducts() {
            try {
                const res = await fetch('/api/products');
                if (!res.ok) throw new Error('Network error');
                products = await res.json();
                renderProducts();
            } catch (e) {
                productGrid.innerHTML = `<div class="empty-state"><span class="icon">🔌</span><h3>Không thể kết nối</h3><button onclick="loadProducts()" style="margin-top:16px;background:var(--gradient-main);border:none;color:#fff;padding:10px 30px;border-radius:30px;font-weight:700;cursor:pointer;">🔄 Thử lại</button></div>`;
                console.error(e);
            }
        }

        function renderProducts() {
            if (!products || products.length === 0) {
                productGrid.innerHTML = `<div class="empty-state"><span class="icon">📭</span><h3>Chưa có sản phẩm</h3></div>`;
                return;
            }
            
            productGrid.innerHTML = products.map((p) => `
                <div class="product-card">
                    <span class="icon-wrap">${p.image || '📦'}</span>
                    <div class="name">${p.name}</div>
                    <div class="desc">${p.desc || ''}</div>
                    <div class="price">${p.price.toLocaleString()} <span>₫</span></div>
                    <div class="stock">📦 Tồn: <span class="num">${p.stock || 0}</span></div>
                    <button class="btn-add" data-id="${p.id}" ${(p.stock || 0) <= 0 ? 'disabled' : ''}>
                        ${(p.stock || 0) > 0 ? '➕ Thêm' : '📭 Hết hàng'}
                    </button>
                </div>
            `).join('');
            
            document.querySelectorAll('.btn-add').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = parseInt(btn.dataset.id);
                    addToCart(id);
                    if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
                });
            });
        }

        // ============================================
        // CART
        // ============================================
        
        function addToCart(productId) {
            const product = products.find(p => p.id === productId);
            if (!product) return;
            if (product.stock <= 0) { showToast('❌ Sản phẩm đã hết hàng!'); return; }

            const existing = cart.find(item => item.id === productId);
            if (existing) {
                if (existing.qty >= product.stock) {
                    showToast('❌ Không đủ số lượng tồn kho!');
                    return;
                }
                existing.qty += 1;
            } else {
                cart.push({ ...product, qty: 1 });
            }
            
            updateCart();
            showToast(`✅ Đã thêm ${product.name}`);
        }

        function updateCart() {
            const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
            const totalPrice = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
            cartCount.textContent = totalItems;
            cartTotal.textContent = totalPrice.toLocaleString() + ' ₫';
            btnCheckout.disabled = totalItems === 0;
        }

        let toastTimer = null;

        function showToast(msg) {
            toastMsg.textContent = msg;
            toast.style.display = 'block';
            toast.style.animation = 'none';
            setTimeout(() => toast.style.animation = 'slideDownVip 0.5s ease forwards', 10);
            clearTimeout(toastTimer);
            toastTimer = setTimeout(() => { toast.style.display = 'none'; }, 2500);
        }

        // ============================================
        // BANK MODAL
        // ============================================
        
        function openBankModal() {
            const totalPrice = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
            orderTotal.textContent = totalPrice.toLocaleString() + ' VND';
            amountPaid.value = '';
            amountPaid.placeholder = `💵 Nhập số tiền đã chuyển (${totalPrice.toLocaleString()} VND)`;
            btnConfirm.disabled = false;
            btnConfirm.textContent = '✅ Tôi đã chuyển khoản';
            bankModal.classList.add('active');
            setTimeout(() => amountPaid.focus(), 300);
            if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
        }
        
        function closeBankModal() { bankModal.classList.remove('active'); }
        
        function copyBankNumber() {
            const number = document.getElementById('bankNumber').textContent;
            navigator.clipboard.writeText(number).then(() => { showToast('📋 Đã copy STK!'); });
        }
        
        function copyBankContent() {
            const content = `ZENMODS ${userId}`;
            navigator.clipboard.writeText(content).then(() => { showToast('📋 Đã copy ND!'); });
        }
        
        // ============================================
        // CONFIRM PAYMENT - GỬI VỀ BOT ADMIN
        // ============================================
        
        async function confirmPayment() {
            const amount = parseInt(amountPaid.value);
            const totalPrice = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
            
            if (!amount || amount <= 0) {
                showToast('❌ Vui lòng nhập số tiền đã chuyển!');
                amountPaid.focus();
                return;
            }
            
            btnConfirm.disabled = true;
            btnConfirm.textContent = '⏳ Đang gửi...';
            
            const orderData = {
                user_id: userId,
                user_name: userName,
                items: cart.map(item => ({ id: item.id, name: item.name, price: item.price, qty: item.qty })),
                total: totalPrice,
                amount_paid: amount,
                status: 'pending'
            };
            
            try {
                const res = await fetch('/api/order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(orderData)
                });
                const result = await res.json();
                
                if (result.status === 'success') {
                    showToast('✅ Đơn hàng đã gửi! Chờ admin duyệt.');
                    if (tg) tg.sendData(JSON.stringify({ type: 'order_sent', order_id: result.order_id }));
                    cart = [];
                    updateCart();
                    closeBankModal();
                } else {
                    showToast('❌ Lỗi gửi đơn! Thử lại.');
                    btnConfirm.disabled = false;
                    btnConfirm.textContent = '✅ Tôi đã chuyển khoản';
                }
            } catch (e) {
                showToast('❌ Lỗi kết nối!');
                console.error(e);
                btnConfirm.disabled = false;
                btnConfirm.textContent = '✅ Tôi đã chuyển khoản';
            }
        }

        btnCheckout.addEventListener('click', () => {
            if (cart.length === 0) return;
            openBankModal();
        });

        document.getElementById('bankModal').addEventListener('click', function(e) {
            if (e.target === this) closeBankModal();
        });

        // ============================================
        // START
        // ============================================
        
        loadProducts();
    </script>
</body>
</html>
"""

# ============================================
# FLASK ROUTES
# ============================================

@flask_app.route('/')
def index():
    try:
        return render_template_string(HTML_TEMPLATE)
    except Exception as e:
        return f"Lỗi: {e}", 500

@flask_app.route('/api/products')
def get_products():
    try:
        products = load_products()
        if not products:
            # Nếu chưa có file, tạo mặc định
            save_products(DEFAULT_PRODUCTS)
            products = DEFAULT_PRODUCTS
        return jsonify(products)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/admin/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Không có dữ liệu"}), 400
        
        products = load_products()
        new_id = max([p.get('id', 0) for p in products] + [0]) + 1
        
        new_product = {
            "id": new_id,
            "name": data.get('name', 'Sản phẩm mới'),
            "price": int(data.get('price', 0)),
            "stock": int(data.get('stock', 0)),
            "desc": data.get('desc', ''),
            "image": data.get('image', '📦')
        }
        
        products.append(new_product)
        save_products(products)
        
        return jsonify({"status": "success", "message": "Đã thêm sản phẩm", "product": new_product})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        products = load_products()
        products = [p for p in products if p.get('id') != product_id]
        save_products(products)
        return jsonify({"status": "success", "message": "Đã xóa sản phẩm"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Không có dữ liệu"}), 400
        
        user_id = data.get('user_id', 'Unknown')
        user_name = data.get('user_name', 'Người dùng')
        items = data.get('items', [])
        total = data.get('total', 0)
        amount_paid = data.get('amount_paid', 0)
        
        # Tạo nội dung đơn hàng
        items_str = '\n'.join([f"   • {item['name']} x{item['qty']} = {(item['price'] * item['qty']):,}đ" for item in items])
        
        order_message = f"""
🛍️ <b>ĐƠN HÀNG MỚI!</b>

━━━━━━━━━━━━━━━━━━
👤 <b>Khách hàng:</b> {user_name}
🆔 <b>User ID:</b> <code>{user_id}</code>

📦 <b>Chi tiết:</b>
{items_str}

💰 <b>Tổng đơn:</b> {total:,.0f} VND
💵 <b>Đã chuyển:</b> {amount_paid:,.0f} VND
📌 <b>Trạng thái:</b> ⏳ Chờ xử lý
━━━━━━━━━━━━━━━━━━
"""
        
        # Lưu log
        with open('orders.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] User {user_id} ({user_name}): Total: {total} | Paid: {amount_paid}\n")
        
        # Gửi tin nhắn cho Admin qua Bot
        try:
            from telegram import Bot
            bot = Bot(token=BOT_TOKEN)
            bot.send_message(chat_id=ADMIN_ID, text=order_message, parse_mode='HTML')
            print(f"✅ Đã gửi đơn hàng của {user_name} cho Admin")
        except Exception as e:
            print(f"❌ Lỗi gửi tin nhắn: {e}")
        
        return jsonify({
            "status": "success",
            "message": "Đơn hàng đã được gửi!",
            "order_id": int(time.time())
        })
        
    except Exception as e:
        print(f"❌ Lỗi tạo đơn hàng: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/ping')
def ping():
    return "Pong! Bot is alive!", 200

# ============================================
# TELEGRAM BOT
# ============================================

def run_telegram_bot():
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
        
        print("🤖 Đang khởi động Telegram Bot...")
        
        app = Application.builder().token(BOT_TOKEN).build()
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            keyboard = [
                [InlineKeyboardButton("🛒 Vào Shop", web_app=WebAppInfo(url=WEBAPP_URL))],
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
            if query.data == 'contact':
                await query.edit_message_text(
                    "📞 <b>LIÊN HỆ</b>\n\n"
                    "Admin: @ZenVnStore\n"
                    "Group: https://t.me/ZenStoreVn",
                    parse_mode='html'
                )
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        print("🤖 Bot đã sẵn sàng!")
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Lỗi bot: {e}")

# ============================================
# KHỞI CHẠY
# ============================================

if __name__ == '__main__':
    print("="*50)
    print("🚀 ZENMODS BOT ĐANG KHỞI ĐỘNG...")
    print("="*50)
    
    # Chạy bot trong thread riêng
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    print("✅ Bot thread đã khởi động")
    
    time.sleep(2)
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Đang chạy Flask trên port {port}...")
    print(f"🌐 Web App URL: {WEBAPP_URL}")
    print(f"📱 Admin Bot ID: {ADMIN_ID}")
    print("="*50)
    
    flask_app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
