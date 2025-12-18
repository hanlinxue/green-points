import requests
import json

# 测试API端点
url = "http://localhost:5000/admin/api/admin/withdrawals/pending"

try:
    # 首先需要登录获取session
    session = requests.Session()

    # 登录管理员账号
    login_data = {
        "id": "admin",
        "password": "admin123"
    }

    # 先访问登录页面
    login_page = session.get("http://localhost:5000/")
    print(f"Login page status: {login_page.status_code}")

    # 提交登录表单
    login_response = session.post("http://localhost:5000/user/login",
                                json=login_data,
                                headers={"Content-Type": "application/json"})
    print(f"Login response: {login_response.status_code}")
    print(f"Login response body: {login_response.text[:200]}")

    # 访问提现申请API
    response = session.get(url)
    print(f"\nAPI Status: {response.status_code}")
    print(f"API Response: {response.text[:500]}")

    if response.status_code == 500:
        print("\nServer error occurred!")

except Exception as e:
    print(f"Error: {str(e)}")