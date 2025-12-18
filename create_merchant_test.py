from apps.merchants.models import Merchant
from apps.administrators.models import PointsExchangeRate
from exts import db
from datetime import datetime
from apps import create_app

# 创建测试商户
def create_test_merchant():
    # 检查商户是否已存在
    merchant = Merchant.query.filter_by(username='Mtest_merchant').first()
    if not merchant:
        # 创建新商户
        merchant = Merchant(
            username='Mtest_merchant',  # 商户账号以M开头
            password='123456',  # 实际应用中需要加密
            phone='13900139000',
            email='merchant@test.com',
            now_points=1000,  # 给商户1000积分用于测试
            all_points=1000,
            use_points=0
        )
        db.session.add(merchant)
        db.session.commit()
        print(f"商户创建成功：{merchant.username}，积分：{merchant.now_points}")
    else:
        print(f"商户已存在：{merchant.username}，积分：{merchant.now_points}")

    # 检查兑换汇率是否存在
    exchange_rate = PointsExchangeRate.query.filter_by(currency_code='CNY', is_active=True).first()
    if not exchange_rate:
        # 创建人民币兑换汇率（1积分=0.01元）
        exchange_rate = PointsExchangeRate(
            currency_code='CNY',
            currency_name='人民币',
            exchange_rate=0.01,  # 1积分 = 0.01元
            symbol='¥',
            is_active=True
        )
        db.session.add(exchange_rate)
        db.session.commit()
        print(f"汇率创建成功：1积分={exchange_rate.exchange_rate}元")
    else:
        print(f"汇率已存在：1积分={exchange_rate.exchange_rate}元")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        create_test_merchant()