# 更新商品图片路径
from apps import create_app
from exts import db
from apps.merchants.models import Goods

def update_goods_images():
    """更新商品的图片URL"""
    app = create_app()

    with app.app_context():
        # 查询所有商品
        goods_list = Goods.query.all()

        # 更新图片URL（去掉扩展名，使用不同的文件名）
        updates = {
            "环保竹纤维水杯": "/static/img/goods/bamboo_cup.png",
            "有机棉环保购物袋": "/static/img/goods/cotton_bag.png",
            "太阳能充电宝": "/static/img/goods/solar_powerbank.png",
            "可降解餐具套装": "/static/img/goods/biodegradable_cutlery.png",
            "环保文具礼盒": "/static/img/goods/stationery_set.png",
            "竹制牙刷套装": "/static/img/goods/bamboo_toothbrush.png",
            "植物基洗衣液": "/static/img/goods/plant_detergent.png",
            "环保种子卡片": "/static/img/goods/seed_card.png",
            "不锈钢吸管套装": "/static/img/goods/steel_straws.png",
            "微纤维清洁布": "/static/img/goods/microfiber_cloth.png"
        }

        updated_count = 0

        for goods in goods_list:
            if goods.goods_name in updates:
                goods.img_url = updates[goods.goods_name]
                updated_count += 1
                print(f"✓ 更新 {goods.goods_name} 的图片URL")

        # 提交更改
        if updated_count > 0:
            db.session.commit()
            print(f"\n成功更新 {updated_count} 个商品的图片URL")

            # 显示更新后的商品列表
            print("\n更新后的商品列表：")
            for idx, goods in enumerate(Goods.query.all(), 1):
                print(f"{idx}. {goods.goods_name}")
                print(f"   图片: {goods.img_url}")
                print(f"   积分: {goods.need_points} | 库存: {goods.stock} | 状态: {goods.status}\n")
        else:
            print("\n没有需要更新的商品")

if __name__ == '__main__':
    update_goods_images()