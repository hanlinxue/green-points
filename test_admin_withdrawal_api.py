#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理员提现申请 API
"""
import requests
import json

# 测试获取待审核提现申请
def test_get_pending_withdrawals():
    url = "http://127.0.0.1:5000/admin/api/admin/withdrawals/pending"

    # 先登录管理员账户
    session = requests.Session()

    # 首先访问登录页面
    login_data = {
        "username": "admin",  # 假设管理员用户名是 admin
        "password": "admin123"  # 假设密码
    }

    print("=" * 60)
    print("测试提现申请 API")
    print("=" * 60)

    # 直接尝试访问 API（可能需要先登录）
    try:
        response = session.get(url)
        print(f"\n1. 获取待审核提现申请:")
        print(f"   URL: {url}")
        print(f"   状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   响应成功: {data.get('success', False)}")
            if data.get('success'):
                items = data.get('data', {}).get('items', [])
                print(f"   待审核提现数量: {len(items)}")
                for item in items:
                    print(f"   - 提现单号: {item.get('withdrawal_no')}")
                    print(f"     商户名: {item.get('merchantName')}")
                    print(f"     积分数量: {item.get('points')}")
                    print(f"     现金金额: {item.get('amount')}")
                    print(f"     创建时间: {item.get('createTime')}")
                    print()
            else:
                print(f"   错误信息: {data.get('message', '未知错误')}")
        else:
            print(f"   请求失败")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    error_data = response.json()
                    print(f"   错误信息: {error_data}")
                except:
                    pass
            print(f"   响应内容: {response.text[:500]}")

    except Exception as e:
        print(f"\n请求异常: {e}")

    # 测试完整的提现申请列表 API
    print("\n" + "=" * 60)
    print("测试完整的提现申请 API")
    print("=" * 60)

    full_url = "http://127.0.0.1:5000/admin/api/withdrawals/pending"
    try:
        response = session.get(full_url)
        print(f"\n2. 获取所有提现申请:")
        print(f"   URL: {full_url}")
        print(f"   状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   响应成功: {data.get('success', False)}")
            if data.get('success'):
                items = data.get('data', {}).get('items', [])
                print(f"   待审核提现数量: {len(items)}")
                for item in items:
                    status = "待审核" if item.get('status') == 0 else ("已通过" if item.get('status') == 1 else "已拒绝")
                    print(f"   - ID: {item.get('id')}")
                    print(f"     提现单号: {item.get('withdrawal_no')}")
                    print(f"     商户名: {item.get('merchantName')}")
                    print(f"     积分数量: {item.get('points')}")
                    print(f"     现金金额: {item.get('amount')}")
                    print(f"     状态: {status}")
                    print(f"     创建时间: {item.get('createTime')}")
                    print()
            else:
                print(f"   错误信息: {data.get('message', '未知错误')}")
        else:
            print(f"   请求失败")
            print(f"   响应内容: {response.text[:500]}")

    except Exception as e:
        print(f"\n请求异常: {e}")

if __name__ == "__main__":
    test_get_pending_withdrawals()