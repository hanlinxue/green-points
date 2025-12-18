#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试积分兑换汇率功能
"""

from apps import create_app
from apps.administrators.models import PointsExchangeRate
from exts import db
import json

def debug_exchange_rates():
    """调试积分兑换汇率功能"""
    app = create_app()

    with app.app_context():
        print("=" * 50)
        print("调试积分兑换汇率功能")
        print("=" * 50)

        # 1. 检查表是否存在
        print("\n1. 检查数据库表是否存在...")
        try:
            import sqlalchemy
            inspector = sqlalchemy.inspect(db.engine)
            tables = inspector.get_table_names()
            if 'tb_points_exchange_rate' in tables:
                print("✓ 积分兑换汇率表存在")

                # 2. 检查表结构
                columns = inspector.get_columns('tb_points_exchange_rate')
                print("\n2. 表结构：")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")

                # 3. 尝试查询数据
                print("\n3. 尝试查询数据...")
                try:
                    rates = PointsExchangeRate.query.all()
                    print(f"✓ 查询成功，找到 {len(rates)} 条记录")

                    for rate in rates:
                        print(f"\n  记录 {rate.id}:")
                        print(f"    货币代码: {rate.currency_code}")
                        print(f"    货币名称: {rate.currency_name}")
                        print(f"    汇率: {rate.exchange_rate} (类型: {type(rate.exchange_rate)})")
                        print(f"    符号: {rate.symbol}")
                        print(f"    状态: {'启用' if rate.is_active else '禁用'}")

                except Exception as e:
                    print(f"✗ 查询数据失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print("✗ 积分兑换汇率表不存在")
                print("\n需要先创建表，请执行以下SQL:")
                print("CREATE TABLE tb_points_exchange_rate (...)")

        except Exception as e:
            print(f"✗ 检查表失败: {str(e)}")
            import traceback
            traceback.print_exc()

        # 4. 测试序列化
        print("\n4. 测试JSON序列化...")
        try:
            rates = PointsExchangeRate.query.all()
            rate_list = []
            for rate in rates:
                exchange_rate = float(rate.exchange_rate) if rate.exchange_rate is not None else 0
                rate_list.append({
                    "id": rate.id,
                    "currency_code": rate.currency_code,
                    "currency_name": rate.currency_name,
                    "exchange_rate": exchange_rate,
                    "symbol": rate.symbol,
                    "is_active": rate.is_active
                })

            json_str = json.dumps(rate_list, ensure_ascii=False, indent=2)
            print("✓ JSON序列化成功:")
            print(json_str)

        except Exception as e:
            print(f"✗ JSON序列化失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_exchange_rates()