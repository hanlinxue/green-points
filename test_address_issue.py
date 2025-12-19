#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试地址相关问题"""

from apps import create_app
from apps.users.models import User, Address, PointsFlow
from apps.merchants.models import Merchant, Order
from exts import db

app = create_app()

with app.app_context():
    print("=== 检查地址和订单数据 ===\n")

    # 检查地址数据
    addresses = Address.query.all()
    print(f"地址总数: {len(addresses)}")
    if addresses:
        print("\n最近添加的几个地址:")
        for addr in addresses[:5]:
            print(f"  用户: {addr.username}, 姓名: {addr.name}, 电话: {addr.phone}")
            print(f"  地址: {addr.region} {addr.detail}\n")

    # 检查订单数据
    orders = Order.query.filter_by(is_delete=0).order_by(Order.create_time.desc()).limit(10).all()
    print(f"\n订单总数: {Order.query.filter_by(is_delete=0).count()}")
    print("\n最近10个订单的地址ID:")
    for order in orders:
        print(f"  订单ID: {order.id}, 用户: {order.user_username}")
        print(f"  商品ID: {order.goods_id}, 积分: {order.point_amount}")
        print(f"  地址ID: {order.address_id}")
        print(f"  订单状态: {order.order_status}\n")

    # 检查是否有未关联地址的订单
    orders_no_address = Order.query.filter_by(is_delete=0, address_id=None).all()
    print(f"\n未关联地址的订单数: {len(orders_no_address)}")
    if orders_no_address:
        print("这些订单没有关联地址ID:")
        for order in orders_no_address:
            print(f"  订单ID: {order.id}, 订单号: {order.order_no}")