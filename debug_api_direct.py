#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接调试API - 不需要服务器运行
"""

from apps import create_app
from apps.administrators.models import PointsExchangeRate
from exts import db

def debug_direct():
    """直接调试模型和数据库"""
    app = create_app()

    with app.app_context():
        print("=== 直接调试API ===")

        # 1. 尝试创建表
        print("\n1. 尝试创建表...")
        try:
            PointsExchangeRate.__table__.create(db.engine, checkfirst=True)
            print("✓ 表创建成功")
        except Exception as e:
            print(f"✗ 表创建失败: {e}")
            import traceback
            traceback.print_exc()
            return

        # 2. 尝试查询数据
        print("\n2. 尝试查询数据...")
        try:
            rates = PointsExchangeRate.query.all()
            print(f"✓ 查询成功，找到 {len(rates)} 条记录")

            if len(rates) == 0:
                print("没有数据，尝试插入...")
                # 插入测试数据
                test_rate = PointsExchangeRate(
                    currency_code='CNY',
                    currency_name='人民币',
                    exchange_rate=0.01,
                    symbol='¥',
                    is_active=True
                )
                db.session.add(test_rate)
                db.session.commit()
                print("✓ 插入测试数据成功")

                # 再次查询
                rates = PointsExchangeRate.query.all()
                print(f"✓ 插入后查询成功，找到 {len(rates)} 条记录")

            # 3. 测试数据格式化
            print("\n3. 测试数据格式化...")
            rate_list = []
            for rate in rates:
                try:
                    # 确保能正确处理decimal类型
                    exchange_rate = float(rate.exchange_rate) if rate.exchange_rate is not None else 0

                    rate_dict = {
                        "id": rate.id,
                        "currency_code": rate.currency_code,
                        "currency_name": rate.currency_name,
                        "exchange_rate": exchange_rate,
                        "symbol": rate.symbol,
                        "is_active": rate.is_active
                    }
                    rate_list.append(rate_dict)

                    print(f"  成功格式化: {rate_dict}")
                except Exception as e:
                    print(f"  格式化失败: {e}")
                    import traceback
                    traceback.print_exc()

            # 4. 测试JSON序列化
            print("\n4. 测试JSON序列化...")
            try:
                import json
                json_str = json.dumps({
                    "success": True,
                    "message": "获取积分兑换汇率成功",
                    "data": rate_list
                }, ensure_ascii=False, indent=2)
                print("✓ JSON序列化成功")
                # print(json_str)
            except Exception as e:
                print(f"✗ JSON序列化失败: {e}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            print(f"✗ 查询失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_direct()