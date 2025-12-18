#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试管理员API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_admin_login():
    """测试管理员登录"""
    print("测试管理员登录...")
    login_data = {
        "adminname": "admin",
        "password": "123456"
    }

    session = requests.Session()

    try:
        response = session.post(f"{BASE_URL}/admin/login", data=login_data)
        print(f"登录响应状态: {response.status_code}")

        if response.status_code == 302:
            print("登录成功（重定向）")
            return session
        else:
            print(f"登录响应内容: {response.text}")
            return None
    except Exception as e:
        print(f"登录失败: {str(e)}")
        return None

def test_exchange_rates_show(session):
    """测试获取兑换汇率接口"""
    print("\n测试获取兑换汇率接口...")

    try:
        response = session.get(f"{BASE_URL}/admin/exchange_rates_show")
        print(f"请求状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")

        if response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            print(f"JSON数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

        return response.status_code == 200

    except Exception as e:
        print(f"请求失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # 先登录
    session = test_admin_login()

    if session:
        # 测试接口
        success = test_exchange_rates_show(session)
        if success:
            print("\n✓ 接口测试成功！")
        else:
            print("\n✗ 接口测试失败！")

if __name__ == '__main__':
    main()