#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加测试积分流水记录"""

from apps import create_app
from apps.users.models import User, PointsFlow
from apps.merchants.models import Merchant
from exts import db
from datetime import datetime

def add_test_points_flow():
    """添加各种类型的测试积分流水记录"""
    app = create_app()
    with app.app_context():
        current_time = datetime.now()
        print(f"当前时间: {current_time}")

        # 查找用户
        user = User.query.first()
        if not user:
            print("没有找到用户！")
            return
        print(f"找到用户: {user.username}, 当前积分: {user.now_points}")

        # 查找商户
        merchant = Merchant.query.first()
        if merchant:
            print(f"找到商户: {merchant.username}, 当前积分: {merchant.now_points}")

        # 1. 添加出行记录审核通过的积分记录
        print("\n1. 添加出行记录...")
        trip_flow = PointsFlow.query.filter_by(
            username=user.username,
            change_type='trip_approved'
        ).first()

        if not trip_flow:
            # 用户通过地铁出行
            points = 20
            user.now_points += points
            user.all_points += points

            flow = PointsFlow(
                username=user.username,
                points=points,
                change_type='trip_approved',
                reason='出行-地铁（审核通过）',
                balance=user.now_points,
                create_time=current_time
            )
            db.session.add(flow)
            print(f"  - 添加地铁出行记录: +{points}积分")

            # 用户通过公交出行
            points = 10
            user.now_points += points
            user.all_points += points

            flow = PointsFlow(
                username=user.username,
                points=points,
                change_type='trip_approved',
                reason='出行-公交（审核通过）',
                balance=user.now_points,
                create_time=current_time
            )
            db.session.add(flow)
            print(f"  - 添加公交出行记录: +{points}积分")

        # 2. 添加用户兑换商品的记录
        print("\n2. 添加兑换记录...")
        # 先删除已有的兑换记录（需要重新添加）
        PointsFlow.query.filter_by(
            username=user.username,
            change_type='exchange'
        ).delete()

        # 添加兑换记录
        # 先给用户一些积分用于兑换
        user.now_points += 200
        user.all_points += 200

        # 兑换商品消耗积分
            points = -50
            user.now_points += points
            user.use_points += 50  # use_points是正数

            flow = PointsFlow(
                username=user.username,
                points=points,
                change_type='exchange',
                reason='兑换-环保购物袋',
                balance=user.now_points,
                goods_name='环保购物袋',
                goods_id=1,  # 添加商品ID
                create_time=current_time
            )
            db.session.add(flow)
            print(f"  - 添加兑换记录: {points}积分（环保购物袋）")

            # 兑换另一个商品
            points = -30
            user.now_points += points
            user.use_points += 30

            flow = PointsFlow(
                username=user.username,
                points=points,
                change_type='exchange',
                reason='兑换-可降解垃圾袋',
                balance=user.now_points,
                goods_name='可降解垃圾袋',
                goods_id=2,  # 添加商品ID
                create_time=current_time
            )
            db.session.add(flow)
            print(f"  - 添加兑换记录: {points}积分（可降解垃圾袋）")
        }

        # 3. 添加商户提现记录
        print("\n3. 添加商户提现记录...")
        if merchant:
            withdrawal_flow = PointsFlow.query.filter_by(
                username=merchant.username,
                change_type='withdrawal'
            ).first()

            if not withdrawal_flow:
                # 先给商户一些积分
                merchant.now_points += 500
                merchant.all_points += 500

                # 商户申请提现
                points = -200
                merchant.now_points += points
                merchant.use_points += 200

                flow = PointsFlow(
                    username=merchant.username,
                    points=points,
                    change_type='withdrawal',
                    reason='商户提现-申请（单号：WD20241221001）',
                    balance=merchant.now_points,
                    create_time=current_time
                )
                db.session.add(flow)
                print(f"  - 添加商户提现记录: {points}积分")

                # 另一个商户提现
                points = -150
                merchant.now_points += points
                merchant.use_points += 150

                flow = PointsFlow(
                    username=merchant.username,
                    points=points,
                    change_type='withdrawal',
                    reason='商户提现-申请（单号：WD20241221002）',
                    balance=merchant.now_points,
                    create_time=current_time
                )
                db.session.add(flow)
                print(f"  - 添加商户提现记录: {points}积分")

        # 提交所有更改
        db.session.commit()
        print("\n所有积分流水记录添加成功！")

        print(f"\n最终状态:")
        print(f"用户 {user.username} 积分: {user.now_points} (累计:{user.all_points}, 已用:{user.use_points})")
        if merchant:
            print(f"商户 {merchant.username} 积分: {merchant.now_points} (累计:{merchant.all_points}, 已用:{merchant.use_points})")

        # 显示所有积分记录
        print("\n积分流水记录总数:", PointsFlow.query.count())

        # 显示最新的10条记录
        print("\n最新的10条积分记录:")
        latest_flows = PointsFlow.query.order_by(PointsFlow.create_time.desc()).limit(10).all()
        for flow in latest_flows:
            print(f"  - {flow.create_time} | {flow.username} | {flow.reason} | {flow.points}积分")

if __name__ == '__main__':
    add_test_points_flow()