#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查待审核提现记录
"""
from apps import create_app
from apps.merchants.models import WithdrawalRecord

app = create_app()

with app.app_context():
    print("=" * 60)
    print("检查所有提现记录:")
    print("=" * 60)

    # 查询所有提现记录
    all_records = WithdrawalRecord.query.all()
    print(f"\n总提现记录数: {len(all_records)}")

    for record in all_records:
        print(f"\nID: {record.id}")
        print(f"提现单号: {record.withdrawal_no}")
        print(f"商户: {record.merchant_username}")
        print(f"积分数量: {record.points_amount}")
        print(f"现金金额: {record.cash_amount}")
        print(f"状态: {record.status} ({'待审核' if record.status == 0 else ('已通过' if record.status == 1 else '已拒绝')})")
        print(f"创建时间: {record.create_time}")

    # 特别查询状态为 0 的记录
    print("\n" + "=" * 60)
    print("查询状态为 0（待审核）的记录:")
    print("=" * 60)

    pending_records = WithdrawalRecord.query.filter_by(status=0).all()
    print(f"\n待审核记录数: {len(pending_records)}")

    if pending_records:
        for record in pending_records:
            print(f"\n- ID: {record.id}")
            print(f"  提现单号: {record.withdrawal_no}")
            print(f"  商户: {record.merchant_username}")
            print(f"  积分数量: {record.points_amount}")
            print(f"  现金金额: {record.cash_amount}")
    else:
        print("\n没有找到待审核的提现记录！")
        print("所有记录的状态都不是 0")