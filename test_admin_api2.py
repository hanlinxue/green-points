import requests
import json

# 测试管理员登录（使用A开头的账号）
session = requests.Session()

# 管理员登录 - 使用正确的管理员账号格式
login_url = "http://localhost:5000/user/login"
login_data = {
    "id": "Aadmin",
    "password": "admin123"
}

response = session.post(login_url, json=login_data)
print(f"Login status: {response.status_code}")

# 检查返回的JSON
try:
    result = response.json()
    if isinstance(result, dict):
        print(f"Login response JSON: {result}")
    else:
        print(f"Login response is not JSON: {result[:500]}")
except:
    print(f"Login response text: {response.text[:500]}")

# 测试API
api_url = "http://localhost:5000/admin/api/admin/withdrawals/pending"
api_response = session.get(api_url)
print(f"\nAPI status: {api_response.status_code}")
print(f"API response: {api_response.text[:1000]}")