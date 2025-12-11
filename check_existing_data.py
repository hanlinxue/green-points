# 检查数据库中的现有数据
from apps import create_app
from exts import db
from apps.merchants.models import Goods, Merchant

def check_data():
    """检查数据库中的商户和商品数据"""
    app = create_app()

    with app.app_context():
        # 查询所有商户
        merchants = Merchant.query.all()
        print(f"\n数据库中的商户 ({len(merchants)} 个):")
        for m in merchants:
            print(f"- 用户名: {m.username}, 电话: {m.phone}, 邮箱: {m.email}")

        # 查询所有商品
        goods = Goods.query.all()
        print(f"\n数据库中的商品 ({len(goods)} 个):")
        for g in goods:
            print(f"- {g.goods_name}, 商户: {g.merchant_username}, 积分: {g.need_points}")

if __name__ == '__main__':
    check_data()