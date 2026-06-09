import requests
import uuid
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# CẤU HÌNH TOKEN CỦA BẠN
LINK4M_API_TOKEN = "6a27be48f348053ba11f3502"

# Lưu Key dưới dạng { "KEY_ABC": "active" }
# LƯU Ý: Với server Render Free, dữ liệu này sẽ mất khi server khởi động lại.
# Để lưu bền vững, sau này bạn cần dùng cơ sở dữ liệu (Database).
keys_db = {} 

@app.route('/')
def home():
    return "AlexCloud Server đang hoạt động!"

# 1. API Tạo Link Vượt (Để App gọi vào)
@app.route('/create-link')
def create_link():
    # Tạo một mã Key ngẫu nhiên 8 ký tự cho lần này
    new_key = str(uuid.uuid4())[:8].upper() 
    keys_db[new_key] = "pending" # Đánh dấu là chưa xác thực
    
    # URL đích mà người dùng sẽ bị điều hướng tới sau khi vượt xong
    # Phải dùng link thật của bạn trên Render để server nhận được Key
    destination_url = f"https://alexcloud-ukf8.onrender.com/verify?key={new_key}"
    
    # API gọi sang Link4m để rút gọn link
    api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API_TOKEN}&url={destination_url}"
    
    try:
        response = requests.get(api_url).json()
        if response.get("status") == "success":
            return jsonify({"shortenedUrl": response["shortenedUrl"], "key": new_key})
        else:
            return jsonify({"error": "Lỗi API Link4m"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Trang nhận Key từ Link4m (Link4m chuyển hướng về đây)
@app.route('/verify')
def verify():
    key = request.args.get('key')
    if key in keys_db:
        keys_db[key] = "active" # Xác nhận Key đã được vượt qua thành công
        return f"<h1>Key của bạn là: {key}</h1><p>Hãy copy key này và dán vào App!</p>"
    return "Key không tồn tại hoặc đã hết hạn!"

# 3. API Xác thực Key (Để App kiểm tra xem Key đó đã được vượt chưa)
@app.route('/check-key', methods=['POST'])
def check_key():
    data = request.json
    key = data.get('key')
    
    # Kiểm tra Key có tồn tại và đã được kích hoạt (active) chưa
    if key in keys_db and keys_db[key] == "active":
        return jsonify({"status": "success", "message": "Key hợp lệ!"})
    return jsonify({"status": "error", "message": "Key chưa vượt link hoặc không tồn tại"}), 401

if __name__ == '__main__':
    # Render yêu cầu dùng PORT từ biến môi trường, máy tính dùng 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)