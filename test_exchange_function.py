#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试兑换功能
"""

import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:5000"

def test_exchange():
    """
    测试兑换功能
    """
    # 1. 登录用户
    print("1. 登录用户...")
    login_data = {
        "username": "user1",  # 替换为实际的用户名
        "password": "123456"  # 替换为实际的密码
    }

    session = requests.Session()

    # 先获取CSRF token（如果需要）
    login_response = session.post(f"{BASE_URL}/user/login", json=login_data)
    print(f"登录响应状态: {login_response.status_code}")

    if login_response.status_code != 200:
        print("登录失败，请检查用户名和密码")
        return

    # 2. 获取商品列表
    print("\n2. 获取商品列表...")
    products_response = session.get(f"{BASE_URL}/user/products")

    if products_response.status_code == 200:
        products = products_response.json()
        print(f"获取到 {len(products)} 个商品")

        # 显示前3个商品
        for i, product in enumerate(products[:3]):
            print(f"\n商品 {i+1}:")
            print(f"  ID: {product['id']}")
            print(f"  名称: {product['goods_name']}")
            print(f"  积分: {product['need_points']}")
            print(f"  库存: {product['stock']}")

        if not products:
            print("没有可用的商品")
            return

        # 选择第一个商品进行测试
        test_product = products[0]
        print(f"\n选择测试商品: {test_product['goods_name']} (ID: {test_product['id']})")

        # 3. 获取用户积分
        print("\n3. 获取用户积分...")
        points_response = session.get(f"{BASE_URL}/user/user_profile/user_points")

        if points_response.status_code == 200:
            points_data = points_response.json()
            print(f"用户当前积分: {points_data['points']}")

            # 4. 测试兑换（如果积分足够）
            if points_data['points'] >= test_product['need_points']:
                print(f"\n4. 开始兑换测试...")
                exchange_data = {
                    "goods_id": test_product['id'],
                    "quantity": 1
                }

                exchange_response = session.post(
                    f"{BASE_URL}/user/exchange",
                    json=exchange_data,
                    headers={"Content-Type": "application/json"}
                )

                print(f"兑换响应状态: {exchange_response.status_code}")
                print(f"兑换响应内容: {exchange_response.text}")

                if exchange_response.status_code == 200:
                    result = exchange_response.json()
                    if result.get('success'):
                        print("\n✅ 兑换成功！")
                        print(f"订单号: {result.get('order_no')}")
                        print(f"使用积分: {result.get('points_used')}")
                        print(f"剩余积分: {result.get('remaining_points')}")
                    else:
                        print(f"\n❌ 兑换失败: {result.get('error')}")
                else:
                    print("\n❌ 请求失败")
            else:
                print(f"\n⚠️ 积分不足，无法兑换（需要: {test_product['need_points']}，拥有: {points_data['points']}）")
        else:
            print(f"\n❌ 获取积分失败: {points_response.status_code}")
    else:
        print(f"\n❌ 获取商品列表失败: {products_response.status_code}")

if __name__ == "__main__":
    print("=" * 50)
    print("测试兑换功能")
    print("=" * 50)
    print("\n注意：请确保Flask应用正在运行在 http://127.0.0.1:5000")
    print("请修改脚本中的用户名和密码\n")

    test_exchange()