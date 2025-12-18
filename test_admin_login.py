import requests
import json

# 测试管理员登录
session = requests.Session()

# 管理员登录
login_url = "http://localhost:5000/user/login"
login_data = {
    "id": "admin",
    "password": "admin123"
}

response = session.post(login_url, json=login_data)
print(f"Login status: {response.status_code}")
print(f"Login response: {response.text}")

# 检查session
print(f"\nSession cookies: {session.cookies.get_dict()}")

# 尝试访问管理员主页
admin_page = session.get("http://localhost:5000/admin/admin_index")
print(f"\nAdmin page status: {admin_page.status_code}")

# 测试API
api_url = "http://localhost:5000/admin/api/admin/withdrawals/pending"
api_response = session.get(api_url)
print(f"\nAPI status: {api_response.status_code}")
print(f"API response: {api_response.text[:1000]}")