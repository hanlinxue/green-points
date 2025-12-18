#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查提现记录状态
"""
from apps import create_app
from apps.merchants.models import WithdrawalRecord
from exts import db

app = create_app()

with app.app_context():
    # 查询所有提现记录
    records = WithdrawalRecord.query.all()

    print("=" * 60)
    print("所有提现记录:")
    print("=" * 60)

    for record in records:
        print(f"\nID: {record.id}")
        print(f"提现单号: {record.withdrawal_no}")
        print(f"商户名: {record.merchant_username}")
        print(f"积分数量: {record.points_amount}")
        print(f"现金金额: {record.cash_amount}")
        print(f"状态码: {record.status}")
        print(f"状态文字: {'待审核' if record.status == 0 else ('已通过' if record.status == 1 else '已拒绝')}")
        print(f"审核管理员: {record.audit_admin}")
        print(f"审核时间: {record.audit_time}")
        print(f"拒绝原因: {record.reject_reason}")
        print(f"创建时间: {record.create_time}")
        print("-" * 40)

    # 特别查看状态为 0 的记录
    pending_records = WithdrawalRecord.query.filter_by(status=0).all()
    print(f"\n\n待审核提现申请数量: {len(pending_records)}")

    if pending_records:
        print("\n待审核记录详情:")
        for record in pending_records:
            print(f"- 提现单号: {record.withdrawal_no}, 商户: {record.merchant_username}, 积分: {record.points_amount}")