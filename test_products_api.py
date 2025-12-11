# 测试商品API
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps import create_app
from apps.merchants.models import Goods

def test_products_api():
    app = create_app()

    with app.app_context():
        # 查询所有商品
        all_goods = Goods.query.all()
        print(f"\n数据库中总共有 {len(all_goods)} 个商品")

        # 查询上架商品
        on_shelf_goods = Goods.query.filter_by(status='on_shelf').all()
        print(f"其中上架商品有 {len(on_shelf_goods)} 个")

        print("\n商品列表：")
        for idx, goods in enumerate(on_shelf_goods, 1):
            print(f"\n{idx}. {goods.goods_name}")
            print(f"   分类: {goods.category}")
            print(f"   积分: {goods.need_points}")
            print(f"   库存: {goods.stock}")
            print(f"   描述: {goods.description[:50]}...")

if __name__ == "__main__":
    test_products_api()