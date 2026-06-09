import requests
import os
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

# Cấu hình Token
LINK4M_API_TOKEN = "6a27be48f348053ba11f3502"
keys_db = {}

@app.route('/')
def home():
    return "Server OK"

@app.route('/create-link')
def create_link():
    chars = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
    nums = "".join(random.choices("0123456789", k=3))
    new_key = f"AlexCloud-{chars}-{nums}"
    keys_db[new_key] = "pending"
    
    # URL phải khớp với tên miền trên Render của bạn
    destination_url = f"https://alexcloud-link4m-1.onrender.com/verify?key={new_key}"
    api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API_TOKEN}&url={destination_url}"
    
    try:
        response = requests.get(api_url).json()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify')
def verify():
    key = request.args.get('key')
    if key in keys_db:
        keys_db[key] = "active"
        return "<h1>Key Da Kich Hoat</h1>"
    return "Key khong hop le"

if __name__ == '__main__':
    app.run()
