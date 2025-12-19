#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试地址匹配问题"""

from apps import create_app
from apps.users.models import User, Address
from apps.merchants.models import Merchant
from exts import db

app = create_app()

with app.app_context():
    print("=== 检查地址存储格式 ===\n")

    # 获取所有用户
    users = User.query.all()
    print(f"用户总数: {len(users)}\n")

    for user in users:
        print(f"\n用户: {user.username}")
        if hasattr(user, 'nickname') and user.nickname:
            print(f"昵称: {user.nickname}")

        # 获取该用户的所有地址
        addresses = Address.query.filter_by(username=user.username).all()
        print(f"地址数量: {len(addresses)}")

        for addr in addresses:
            print(f"\n地址ID: {addr.id}")
            print(f"姓名: '{addr.name}'")
            print(f"电话: '{addr.phone}'")
            print(f"地区: '{addr.region}'")
            print(f"详细地址: '{addr.detail}'")
            print(f"是否默认: {addr.is_default}")

            # 生成完整的地址字符串（用于兑换时的格式）
            full_address = f"{addr.name} / {addr.phone} / {addr.region} {addr.detail}"
            print(f"完整地址格式: '{full_address}'")

        print("-" * 50)