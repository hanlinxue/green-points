#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""更新兑换记录，添加goods_id"""

from apps import create_app
from apps.users.models import User, PointsFlow
from exts import db
from datetime import datetime

def update_exchange_records():
    """更新兑换记录，添加goods_id"""
    app = create_app()
    with app.app_context():
        current_time = datetime.now()
        print(f"当前时间: {current_time}")

        # 查找用户
        user = User.query.first()
        if not user:
            print("没有找到用户！")
            return
        print(f"找到用户: {user.username}")

        # 查找已有的兑换记录
        exchange_records = PointsFlow.query.filter_by(
            username=user.username,
            change_type='exchange'
        ).all()

        print(f"\n找到 {len(exchange_records)} 条兑换记录，正在更新...")

        for record in exchange_records:
            # 根据商品名称设置goods_id
            if "环保购物袋" in record.reason:
                record.goods_id = 1
                print(f"  - 更新记录 {record.id}: 环保购物袋 -> goods_id=1")
            elif "可降解垃圾袋" in record.reason:
                record.goods_id = 2
                print(f"  - 更新记录 {record.id}: 可降解垃圾袋 -> goods_id=2")

        db.session.commit()
        print("\n兑换记录更新成功！")

        # 显示更新后的兑换记录
        updated_records = PointsFlow.query.filter_by(
            username=user.username,
            change_type='exchange'
        ).all()

        print("\n更新后的兑换记录:")
        for record in updated_records:
            print(f"  - {record.create_time} | {record.reason} | {record.points}积分 | goods_id={record.goods_id}")

if __name__ == '__main__':
    update_exchange_records()