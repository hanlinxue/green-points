#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试订单管理功能
"""

import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:5000"

def test_merchant_order_management():
    """
    测试商户订单管理
    """
    print("=" * 50)
    print("测试商户订单管理")
    print("=" * 50)

    # 1. 登录商户
    print("\n1. 登录商户...")
    login_data = {
        "username": "merchant1",  # 替换为实际的商户账号
        "password": "123456"
    }

    session = requests.Session()
    login_response = session.post(f"{BASE_URL}/user/login", json=login_data)
    print(f"登录响应状态: {login_response.status_code}")

    if login_response.status_code != 200:
        print("商户登录失败，请检查用户名和密码")
        return

    # 2. 获取商户订单列表
    print("\n2. 获取商户订单列表...")
    orders_response = session.get(f"{BASE_URL}/merchant/merchant_orders")

    if orders_response.status_code == 200:
        orders = orders_response.json()
        print(f"获取到 {len(orders)} 个订单")

        if len(orders) > 0:
            # 显示前3个订单
            for i, order in enumerate(orders[:3]):
                print(f"\n订单 {i+1}:")
                print(f"  订单号: {order['order_no']}")
                print(f"  商品: {order['goods_name']}")
                print(f"  用户: {order['user_nickname']}")
                print(f"  状态: {order['order_status_text']}")
                print(f"  积分: {order['point_amount']}")

                # 如果有可以操作的订单
                if order['order_status'] == 1:  # 已扣积分
                    print(f"\n3. 测试接单（订单ID: {order['id']}）...")
                    accept_response = session.post(
                        f"{BASE_URL}/merchant/merchant_orders/{order['id']}/accept",
                        headers={"Content-Type": "application/json"}
                    )
                    print(f"接单响应: {accept_response.status_code}")
                    if accept_response.status_code == 200:
                        result = accept_response.json()
                        print(f"接单结果: {result.get('message', '操作成功')}")
                    else:
                        print("接单失败")
    else:
        print(f"获取订单列表失败: {orders_response.status_code}")

def test_user_order_viewing():
    """
    测试用户订单查看
    """
    print("\n" + "=" * 50)
    print("测试用户订单查看")
    print("=" * 50)

    # 1. 登录用户
    print("\n1. 登录用户...")
    login_data = {
        "username": "user1",  # 替换为实际的用户账号
        "password": "123456"
    }

    session = requests.Session()
    login_response = session.post(f"{BASE_URL}/user/login", json=login_data)
    print(f"登录响应状态: {login_response.status_code}")

    if login_response.status_code != 200:
        print("用户登录失败，请检查用户名和密码")
        return

    # 2. 获取用户订单列表
    print("\n2. 获取用户订单列表...")
    orders_response = session.get(f"{BASE_URL}/user/user_orders")

    if orders_response.status_code == 200:
        orders = orders_response.json()
        print(f"获取到 {len(orders)} 个订单")

        if len(orders) > 0:
            # 显示订单信息
            for i, order in enumerate(orders):
                print(f"\n订单 {i+1}:")
                print(f"  订单号: {order['order_no']}")
                print(f"  商品: {order['goods_name']}")
                print(f"  商户: {order['merchant_name']}")
                print(f"  状态: {order['order_status_text']}")
                print(f"  积分: {order['point_amount']}")

                # 测试获取订单详情
                print(f"\n3. 获取订单详情（订单ID: {order['id']}）...")
                detail_response = session.get(f"{BASE_URL}/user/user_orders/{order['id']}")

                if detail_response.status_code == 200:
                    order_detail = detail_response.json()
                    print(f"订单详情获取成功")
                    print(f"  订单号: {order_detail['order_no']}")
                    print(f"  创建时间: {order_detail['create_time']}")
                    if order_detail.get('address_info'):
                        print(f"  收货地址: {order_detail['address_info']['region']} {order_detail['address_info']['detail']}")
                else:
                    print("获取订单详情失败")

                # 如果有已发货的订单，测试确认收货
                if order['order_status'] == 3:  # 已发货
                    print(f"\n4. 测试确认收货（订单ID: {order['id']}）...")
                    confirm_response = session.post(
                        f"{BASE_URL}/user/user_orders/{order['id']}/confirm",
                        headers={"Content-Type": "application/json"}
                    )
                    print(f"确认收货响应: {confirm_response.status_code}")
                    if confirm_response.status_code == 200:
                        result = confirm_response.json()
                        print(f"确认收货结果: {result.get('message', '操作成功')}")
                    else:
                        print("确认收货失败")
    else:
        print(f"获取订单列表失败: {orders_response.status_code}")

def test_full_order_flow():
    """
    测试完整的订单流程（需要用户和商户配合）
    """
    print("\n" + "=" * 50)
    print("测试完整订单流程")
    print("=" * 50)
    print("\n注意：此测试需要先创建一些测试订单")
    print("请先在商品页面进行兑换操作创建订单")

    # 这里可以添加更复杂的测试逻辑
    # 比如创建订单、商户接单、发货、用户确认收货等完整流程

if __name__ == "__main__":
    print("订单管理功能测试")
    print("请确保Flask应用正在运行在 http://127.0.0.1:5000")
    print("请修改脚本中的用户名和密码以匹配实际账户\n")

    # 测试商户订单管理
    test_merchant_order_management()

    # 测试用户订单查看
    test_user_order_viewing()

    # 测试完整流程
    test_full_order_flow()

    print("\n测试完成！")