#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据库连接和表
"""

from apps import create_app
from apps.administrators.models import PointsExchangeRate
from exts import db

def test_db():
    app = create_app()

    with app.app_context():
        print("1. Checking if table exists...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        if 'tb_points_exchange_rate' in tables:
            print("Table exists!")

            print("\n2. Trying to create table (if not exists)...")
            PointsExchangeRate.__table__.create(db.engine, checkfirst=True)

            print("\n3. Querying data...")
            try:
                rates = PointsExchangeRate.query.all()
                print(f"Found {len(rates)} records")

                if len(rates) == 0:
                    print("No records found, inserting default data...")
                    default_rates = [
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
                        )
                    ]

                    for rate in default_rates:
                        db.session.add(rate)
                    db.session.commit()
                    print("Default data inserted!")
                else:
                    for rate in rates:
                        print(f"Rate: {rate.currency_code} = {rate.exchange_rate}")
            except Exception as e:
                print(f"Error querying data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Table does not exist!")

if __name__ == '__main__':
    test_db()