#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建表并插入数据
"""

from apps import create_app
from apps.administrators.models import PointsExchangeRate
from exts import db

def create_and_insert():
    """创建表并插入数据"""
    app = create_app()

    with app.app_context():
        print("Creating table and inserting data...")

        # 创建表（如果不存在）
        PointsExchangeRate.__table__.create(db.engine, checkfirst=True)

        # 检查是否有数据
        count = PointsExchangeRate.query.count()
        print(f"Current record count: {count}")

        if count == 0:
            # 插入默认数据
            rates = [
                PointsExchangeRate(
                    currency_code='CNY',
                    currency_name='人民币',
                    exchange_rate=0.01,
                    symbol='¥',
                    is_active=True
                ),
                PointsExchangeRate(
                    currency_code='USD',
                    currency_name='美元',
                    exchange_rate=0.0014,
                    symbol='$',
                    is_active=True
                ),
                PointsExchangeRate(
                    currency_code='EUR',
                    currency_name='欧元',
                    exchange_rate=0.0013,
                    symbol='€',
                    is_active=True
                )
            ]

            for rate in rates:
                db.session.add(rate)
            db.session.commit()

            print("Inserted 3 default records")
        else:
            print("Records already exist")

        # 测试查询
        rates = PointsExchangeRate.query.all()
        print(f"\nAll records:")
        for rate in rates:
            print(f"  {rate.currency_code}: 1 point = {rate.exchange_rate} {rate.currency_name}")

        print("\nSuccess!")

if __name__ == '__main__':
    create_and_insert()