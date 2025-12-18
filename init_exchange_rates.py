#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化积分兑换汇率数据
"""

from apps import create_app
from apps.administrators.models import PointsExchangeRate
from exts import db

def init_exchange_rates():
    """初始化默认的积分兑换汇率"""
    app = create_app()

    with app.app_context():
        # 先创建表（如果不存在）
        try:
            PointsExchangeRate.__table__.create(db.engine, checkfirst=True)
            print("确保积分兑换汇率表存在")
        except Exception as e:
            print(f"创建表失败（可能已存在）：{e}")

        # 检查是否已有汇率数据
        try:
            existing_rates = PointsExchangeRate.query.all()
            if existing_rates:
                print(f"已存在 {len(existing_rates)} 条汇率数据，跳过初始化")
                return
        except Exception as e:
            print(f"查询汇率数据失败：{e}")
            # 继续尝试插入数据

        # 默认汇率数据
        default_rates = [
            {
                'currency_code': 'CNY',
                'currency_name': '人民币',
                'symbol': '¥',
                'exchange_rate': 0.01,  # 1积分 = 0.01元
                'is_active': True
            },
            {
                'currency_code': 'USD',
                'currency_name': '美元',
                'symbol': '$',
                'exchange_rate': 0.0014,  # 1积分 ≈ 0.0014美元（约1:7汇率）
                'is_active': True
            },
            {
                'currency_code': 'EUR',
                'currency_name': '欧元',
                'symbol': '€',
                'exchange_rate': 0.0013,  # 1积分 ≈ 0.0013欧元
                'is_active': True
            }
        ]

        try:
            # 添加默认汇率
            for rate_data in default_rates:
                rate = PointsExchangeRate(**rate_data)
                db.session.add(rate)

            db.session.commit()
            print(f"成功初始化 {len(default_rates)} 条默认汇率数据")

            # 查询并显示
            rates = PointsExchangeRate.query.all()
            for rate in rates:
                print(f"  {rate.symbol}1积分 = {rate.exchange_rate}{rate.currency_name}")

        except Exception as e:
            db.session.rollback()
            print(f"初始化汇率数据失败：{str(e)}")

if __name__ == '__main__':
    init_exchange_rates()