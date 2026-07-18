from flask import Flask, request, jsonify, render_template_string
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
ADMIN_ID = 7463456773
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
# HTML TEMPLATE (NHÚNG TRỰC TIẾP TRONG PYTHON)
# ============================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>🛒 ZENMODS Shop</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg-primary: #0a0a1a;
            --bg-secondary: #12122a;
            --bg-card: #1a1a3e;
            --text-primary: #ffffff;
            --text-secondary: #a0a0c0;
            --accent: #ff6b35;
            --accent2: #f7c948;
            --gradient: linear-gradient(135deg, #ff6b35, #f7c948);
            --radius: 20px;
            --radius-sm: 14px;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 16px 16px 120px;
            background-image: radial-gradient(ellipse at 20% 0%, rgba(255,107,53,0.10) 0%, transparent 60%);
        }
        .header { text-align: center; padding: 24px 0 20px; position: relative; }
        .header .logo { font-size: 52px; display: block; margin-bottom: 4px; animation: float 3s ease-in-out infinite; }
        @keyframes float { 0%, 100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-8px) scale(1.02); } }
        .header h1 { font-size: 30px; font-weight: 900; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .header .sub { color: var(--text-secondary); font-size: 13px; margin-top: 4px; }
        .header .sub span { color: var(--accent2); font-weight: 600; }
        .badge-row { display: flex; justify-content: center; gap: 8px; margin: 14px 0 20px; flex-wrap: wrap; }
        .badge { background: rgba(255,255,255,0.05); padding: 6px 16px; border-radius: 30px; font-size: 11px; font-weight: 600; color: var(--text-secondary); border: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; gap: 6px; }
        .badge .dot { width: 7px; height: 7px; border-radius: 50%; background: #00e676; animation: pulse-dot 1.5s ease-in-out infinite; }
        @keyframes pulse-dot { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.3; transform: scale(0.7); } }
        .badge.gold { border-color: rgba(247,201,72,0.3); color: var(--accent2); }
        .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 4px; }
        @media (min-width: 500px) { .product-grid { grid-template-columns: repeat(3, 1fr); } }
        @media (min-width: 768px) { .product-grid { grid-template-columns: repeat(4, 1fr); } }
        .product-card { background: var(--bg-card); border-radius: var(--radius); padding: 20px 14px 16px; text-align: center; border: 1px solid rgba(255,255,255,0.04); transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; }
        .product-card:hover { transform: translateY(-6px); border-color: rgba(255,107,53,0.25); box-shadow: 0 16px 48px rgba(255,107,53,0.08); }
        .product-card .icon-wrap { font-size: 40px; display: block; margin-bottom: 4px; position: relative; z-index: 1; }
        .product-card .name { font-weight: 700; font-size: 14px; line-height: 1.3; margin: 4px 0 2px; position: relative; z-index: 1; }
        .product-card .desc { font-size: 11px; color: var(--text-secondary); margin: 4px 0 8px; min-height: 28px; line-height: 1.4; position: relative; z-index: 1; }
        .product-card .price { font-size: 18px; font-weight: 800; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 6px 0 10px; position: relative; z-index: 1; }
        .product-card .price span { font-size: 11px; font-weight: 400; color: var(--text-secondary); -webkit-text-fill-color: var(--text-secondary); }
        .btn-add { background: var(--gradient); border: none; color: #fff; padding: 10px 0; border-radius: 30px; cursor: pointer; font-weight: 700; font-size: 13px; width: 100%; transition: all 0.3s ease; position: relative; z-index: 1; box-shadow: 0 4px 20px rgba(255,107,53,0.25); }
        .btn-add:hover { transform: scale(1.03); }
        .btn-add:active { transform: scale(0.94); }
        .cart { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(18, 18, 42, 0.95); padding: 14px 20px 18px; border-top: 1px solid rgba(255,107,53,0.15); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; z-index: 100; backdrop-filter: blur(24px); box-shadow: 0 -8px 48px rgba(0,0,0,0.6); border-radius: 24px 24px 0 0; }
        .cart-info { display: flex; gap: 14px; align-items: center; font-size: 14px; }
        .cart-info .count { background: var(--gradient); color: #fff; padding: 1px 14px; border-radius: 30px; font-size: 13px; font-weight: 700; min-width: 28px; text-align: center; }
        .cart-info .total { font-weight: 800; font-size: 17px; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .btn-checkout { background: var(--gradient); border: none; color: #fff; padding: 12px 30px; border-radius: 30px; font-weight: 700; cursor: pointer; transition: all 0.3s ease; font-size: 14px; box-shadow: 0 4px 24px rgba(255,107,53,0.3); }
        .btn-checkout:hover { transform: scale(1.04); }
        .btn-checkout:active { transform: scale(0.94); }
        .btn-checkout:disabled { background: #2a2a5a; box-shadow: none; cursor: not-allowed; opacity: 0.5; }
        .toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%) translateY(-30px); background: rgba(18, 18, 42, 0.95); color: var(--text-primary); padding: 14px 28px; border-radius: var(--radius-sm); display: none; z-index: 999; font-weight: 600; font-size: 14px; box-shadow: 0 8px 48px rgba(0,0,0,0.6); border: 1px solid rgba(255,107,53,0.15); animation: slideDown 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards; text-align: center; max-width: 90%; backdrop-filter: blur(20px); }
        @keyframes slideDown { from { transform: translateX(-50%) translateY(-30px); opacity: 0; } to { transform: translateX(-50%) translateY(0); opacity: 1; } }
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(12px); z-index: 200; display: none; align-items: center; justify-content: center; padding: 20px; animation: fadeIn 0.3s ease; }
        .modal-overlay.active { display: flex; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .modal-bank { background: var(--bg-secondary); border-radius: var(--radius); padding: 28px 24px 24px; max-width: 420px; width: 100%; border: 1px solid rgba(255,107,53,0.12); box-shadow: 0 24px 80px rgba(0,0,0,0.6); animation: scaleUp 0.35s cubic-bezier(0.4, 0, 0.2, 1); max-height: 95vh; overflow-y: auto; }
        @keyframes scaleUp { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
        .modal-bank .close-btn { float: right; background: none; border: none; color: var(--text-secondary); font-size: 24px; cursor: pointer; }
        .modal-bank .close-btn:hover { color: var(--text-primary); }
        .modal-bank .bank-title { text-align: center; font-size: 20px; font-weight: 800; margin-bottom: 4px; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .modal-bank .bank-sub { text-align: center; color: var(--text-secondary); font-size: 13px; margin-bottom: 16px; }
        .modal-bank .qr-container { background: #fff; border-radius: var(--radius-sm); padding: 12px; text-align: center; margin-bottom: 14px; }
        .modal-bank .qr-container img { max-width: 100%; max-height: 180px; border-radius: 8px; }
        .modal-bank .bank-info { background: rgba(255,255,255,0.04); border-radius: var(--radius-sm); padding: 14px; margin-bottom: 14px; }
        .modal-bank .bank-info .row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.04); }
        .modal-bank .bank-info .row:last-child { border-bottom: none; }
        .modal-bank .bank-info .label { color: var(--text-secondary); font-weight: 400; }
        .modal-bank .bank-info .value { font-weight: 700; }
        .modal-bank .bank-info .value.highlight { color: var(--accent2); }
        .modal-bank .amount-input { width: 100%; padding: 14px 16px; border-radius: var(--radius-sm); border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04); color: var(--text-primary); font-size: 16px; font-weight: 600; outline: none; transition: border-color 0.3s; margin-bottom: 12px; }
        .modal-bank .amount-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(255,107,53,0.15); }
        .modal-bank .amount-input::placeholder { color: var(--text-secondary); font-weight: 400; }
        .modal-bank .copy-btn { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); color: var(--text-primary); padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 12px; font-weight: 600; transition: all 0.2s; }
        .modal-bank .copy-btn:hover { background: rgba(255,107,53,0.15); border-color: rgba(255,107,53,0.3); }
        .modal-bank .btn-confirm { width: 100%; padding: 14px; border: none; border-radius: 30px; background: var(--gradient); color: #fff; font-weight: 700; font-size: 16px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 24px rgba(255,107,53,0.25); }
        .modal-bank .btn-confirm:hover { transform: scale(1.02); }
        .modal-bank .btn-confirm:active { transform: scale(0.96); }
        .modal-bank .btn-confirm:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .modal-bank .note { text-align: center; font-size: 12px; color: var(--text-secondary); margin-top: 12px; }
        .modal-bank .note span { color: var(--accent2); font-weight: 600; }
        .empty-state { text-align: center; padding: 60px 20px; color: var(--text-secondary); grid-column: 1/-1; }
        .empty-state .icon { font-size: 52px; display: block; margin-bottom: 12px; }
        .empty-state h3 { font-size: 18px; color: var(--text-primary); margin-bottom: 4px; }
        .empty-state p { font-size: 13px; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 4px; }
        .shimmer { background: var(--bg-card); border-radius: var(--radius); padding: 20px 14px 16px; text-align: center; animation: shimmer 1.5s ease-in-out infinite; }
        .shimmer .icon-s { width: 40px; height: 40px; background: #2a2a5a; border-radius: 50%; margin: 0 auto 8px; }
        .shimmer .name-s { height: 14px; background: #2a2a5a; border-radius: 8px; margin: 4px auto; width: 70%; }
        .shimmer .desc-s { height: 10px; background: #2a2a5a; border-radius: 8px; margin: 4px auto; width: 50%; }
        .shimmer .price-s { height: 16px; background: #2a2a5a; border-radius: 8px; margin: 6px auto; width: 40%; }
        .shimmer .btn-s { height: 38px; background: #2a2a5a; border-radius: 30px; margin-top: 8px; }
        @keyframes shimmer { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    </style>
</head>
<body>
    <div class="toast" id="toast"><span id="toastMsg">✅ Đã thêm vào giỏ hàng!</span></div>
    <div class="modal-overlay" id="bankModal">
        <div class="modal-bank">
            <button class="close-btn" onclick="closeBankModal()">✕</button>
            <div class="bank-title">💳 THANH TOÁN</div>
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
    <header class="header">
        <span class="logo">⚡</span>
        <h1>ZENMODS SHOP</h1>
        <div class="sub">🔹 <span>Hack</span> · Mod · Tool 🔹</div>
        <div class="badge-row">
            <span class="badge"><span class="dot"></span> Online</span>
            <span class="badge gold">🏆 Uy tín #1</span>
            <span class="badge">⚡ 24/7 Support</span>
        </div>
    </header>
    <div class="product-grid" id="productGrid">
        <div class="shimmer"><div class="icon-s"></div><div class="name-s"></div><div class="desc-s"></div><div class="price-s"></div><div class="btn-s"></div></div>
        <div class="shimmer"><div class="icon-s"></div><div class="name-s"></div><div class="desc-s"></div><div class="price-s"></div><div class="btn-s"></div></div>
        <div class="shimmer"><div class="icon-s"></div><div class="name-s"></div><div class="desc-s"></div><div class="price-s"></div><div class="btn-s"></div></div>
        <div class="shimmer"><div class="icon-s"></div><div class="name-s"></div><div class="desc-s"></div><div class="price-s"></div><div class="btn-s"></div></div>
    </div>
    <div class="cart">
        <div class="cart-info">
            <span style="font-size:20px;">🛒</span>
            <span class="count" id="cartCount">0</span>
            <span class="total" id="cartTotal">0 ₫</span>
        </div>
        <button class="btn-checkout" id="btnCheckout" disabled>💳 Thanh toán</button>
    </div>
    <script>
        let products = [], cart = [];
        const productGrid = document.getElementById('productGrid'), cartCount = document.getElementById('cartCount'), cartTotal = document.getElementById('cartTotal');
        const btnCheckout = document.getElementById('btnCheckout'), toast = document.getElementById('toast'), toastMsg = document.getElementById('toastMsg');
        const bankModal = document.getElementById('bankModal'), orderTotal = document.getElementById('orderTotal');
        const amountPaid = document.getElementById('amountPaid'), btnConfirm = document.getElementById('btnConfirmPayment');
        const tg = window.Telegram?.WebApp;
        const userId = tg?.initDataUnsafe?.user?.id || 7463456773;
        const userName = tg?.initDataUnsafe?.user?.first_name || 'Người dùng';
        if (tg) { tg.ready(); tg.expand(); tg.setHeaderColor('#0a0a1a'); tg.setBackgroundColor('#0a0a1a'); }
        async function loadProducts() {
            try {
                const res = await fetch('/api/products');
                if (!res.ok) throw new Error('Network error');
                products = await res.json();
                renderProducts();
            } catch (e) {
                productGrid.innerHTML = `<div class="empty-state"><span class="icon">🔌</span><h3>Không thể kết nối</h3><p>Vui lòng thử lại sau</p><button onclick="loadProducts()" style="margin-top:16px;background:var(--gradient);border:none;color:#fff;padding:10px 30px;border-radius:30px;font-weight:700;cursor:pointer;">🔄 Thử lại</button></div>`;
                console.error(e);
            }
        }
        function renderProducts() {
            if (!products || products.length === 0) { productGrid.innerHTML = `<div class="empty-state"><span class="icon">📭</span><h3>Chưa có sản phẩm</h3><p>Quay lại sau nhé!</p></div>`; return; }
            const icons = ['🔫', '💀', '📱', '🎯', '👑', '🛡️', '⚔️', '🔥'];
            productGrid.innerHTML = products.map((p, i) => `<div class="product-card"><span class="icon-wrap">${icons[i % icons.length]}</span><div class="name">${p.name}</div><div class="desc">${p.desc || ''}</div><div class="price">${p.price.toLocaleString()} <span>₫</span></div><button class="btn-add" data-id="${p.id}">➕ Thêm</button></div>`).join('');
            document.querySelectorAll('.btn-add').forEach(btn => { btn.addEventListener('click', () => { const id = parseInt(btn.dataset.id); addToCart(id); if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light'); }); });
        }
        function addToCart(productId) {
            const product = products.find(p => p.id === productId);
            if (!product) return;
            const existing = cart.find(item => item.id === productId);
            if (existing) existing.qty += 1; else cart.push({ ...product, qty: 1 });
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
            setTimeout(() => toast.style.animation = 'slideDown 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards', 10);
            clearTimeout(toastTimer);
            toastTimer = setTimeout(() => { toast.style.display = 'none'; }, 2500);
        }
        function openBankModal() {
            const totalPrice = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
            orderTotal.textContent = totalPrice.toLocaleString() + ' VND';
            amountPaid.value = '';
            amountPaid.placeholder = `💵 Nhập số tiền bạn đã chuyển (${totalPrice.toLocaleString()} VND)`;
            btnConfirm.disabled = false;
            btnConfirm.textContent = '✅ Tôi đã chuyển khoản';
            bankModal.classList.add('active');
            setTimeout(() => amountPaid.focus(), 300);
            if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
        }
        function closeBankModal() { bankModal.classList.remove('active'); }
        function copyBankNumber() { const number = document.getElementById('bankNumber').textContent; navigator.clipboard.writeText(number).then(() => { showToast('📋 Đã copy số tài khoản!'); }); }
        function copyBankContent() { const content = `ZENMODS ${userId}`; navigator.clipboard.writeText(content).then(() => { showToast('📋 Đã copy nội dung chuyển khoản!'); }); }
        async function confirmPayment() {
            const amount = parseInt(amountPaid.value);
            const totalPrice = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
            if (!amount || amount <= 0) { showToast('❌ Vui lòng nhập số tiền đã chuyển!'); amountPaid.focus(); return; }
            btnConfirm.disabled = true;
            btnConfirm.textContent = '⏳ Đang gửi...';
            const orderData = { user_id: userId, user_name: userName, items: cart.map(item => ({ id: item.id, name: item.name, price: item.price, qty: item.qty })), total: totalPrice, amount_paid: amount, status: 'pending' };
            try {
                const res = await fetch('/api/order', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(orderData) });
                const result = await res.json();
                if (result.status === 'success') {
                    showToast('✅ Đơn hàng đã gửi! Vui lòng chờ admin duyệt.');
                    if (tg) tg.sendData(JSON.stringify({ type: 'order_sent', order_id: result.order_id, total: totalPrice, amount_paid: amount }));
                    cart = []; updateCart(); closeBankModal();
                } else { showToast('❌ Lỗi gửi đơn hàng! Thử lại.'); btnConfirm.disabled = false; btnConfirm.textContent = '✅ Tôi đã chuyển khoản'; }
            } catch (e) { showToast('❌ Lỗi kết nối! Thử lại.'); console.error(e); btnConfirm.disabled = false; btnConfirm.textContent = '✅ Tôi đã chuyển khoản'; }
        }
        btnCheckout.addEventListener('click', () => { if (cart.length === 0) return; openBankModal(); });
        document.getElementById('bankModal').addEventListener('click', function(e) { if (e.target === this) closeBankModal(); });
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
    return jsonify(PRODUCTS)

@flask_app.route('/api/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        user_id = data.get('user_id', 'Unknown')
        user_name = data.get('user_name', 'Người dùng')
        items = data.get('items', [])
        total = data.get('total', 0)
        amount_paid = data.get('amount_paid', 0)
        status = data.get('status', 'pending')
        
        # Tạo nội dung đơn hàng
        items_str = '\n'.join([f"   • {item['name']} x{item['qty']} = {(item['price'] * item['qty']):,}đ" for item in items])
        
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
"""
        
        # Lưu vào file log
        with open('orders.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] User {user_id} ({user_name}): {json.dumps(items)} | Total: {total} | Paid: {amount_paid} | Status: {status}\n")
        
        # Gửi tin nhắn cho Admin qua Bot
        try:
            from telegram import Bot
            bot = Bot(token=BOT_TOKEN)
            bot.send_message(chat_id=ADMIN_ID, text=order_message, parse_mode='HTML')
            print(f"✅ Đã gửi đơn hàng của {user_name} cho Admin")
        except Exception as e:
            print(f"❌ Lỗi gửi tin nhắn cho Admin: {e}")
        
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
            elif query.data.startswith('duyet_'):
                user_id = query.data.replace('duyet_', '')
                await query.edit_message_text(f"✅ Đã duyệt đơn hàng của User {user_id}", parse_mode='html')
                await context.bot.send_message(chat_id=int(user_id), text="✅ Đơn hàng của bạn đã được <b>DUYỆT</b>!", parse_mode='html')
            elif query.data.startswith('huy_'):
                user_id = query.data.replace('huy_', '')
                await query.edit_message_text(f"❌ Đã hủy đơn hàng của User {user_id}", parse_mode='html')
                await context.bot.send_message(chat_id=int(user_id), text="❌ Đơn hàng của bạn đã bị <b>HỦY</b>!", parse_mode='html')
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        print("🤖 Bot đã sẵn sàng!")
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Lỗi bot: {e}")
        import traceback
        traceback.print_exc()

# ============================================
# KHỞI CHẠY
# ============================================

if __name__ == '__main__':
    # Chạy bot trong thread riêng
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    print("✅ Bot thread đã khởi động")
    
    # Chạy Flask
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Đang chạy Flask trên port {port}...")
    print(f"🌐 Web App URL: {WEBAPP_URL}")
    
    flask_app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
