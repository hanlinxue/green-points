# 插入商品数据的脚本（使用现有商户）
from datetime import datetime
from apps import create_app
from exts import db
from apps.merchants.models import Goods, Merchant

# 商品数据列表
goods_records = [
    {
        "merchant_username": "M1764328599217",
        "goods_name": "环保竹纤维水杯",
        "description": "采用天然竹纤维制成，不含BPA，容量500ml，便携设计，适合办公和户外使用",
        "category": "日用品",
        "need_points": 150.0,
        "stock": 100,
        "stock_warning": 20,
        "img_url": "/static/img/goods/bamboo_cup.png",
        "status": "on_shelf"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "有机棉环保购物袋",
        "description": "100%有机棉材质，可重复使用，承重能力强，尺寸40x35cm，多种颜色可选",
        "category": "日用品",
        "need_points": 80.0,
        "stock": 200,
        "stock_warning": 30,
        "img_url": "/static/img/goods/cotton_bag.png",
        "status": "on_shelf"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "太阳能充电宝",
        "description": "10000mAh容量，支持太阳能和USB充电，双USB输出，适合户外应急使用",
        "category": "数码",
        "need_points": 450.0,
        "stock": 50,
        "stock_warning": 10,
        "img_url": "/static/img/goods/solar_powerbank.png",
        "status": "on_shelf"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "可降解餐具套装",
        "description": "包含筷子、勺子、叉子各1支，采用玉米淀粉材料制成，100%可生物降解",
        "category": "日用品",
        "need_points": 60.0,
        "stock": 150,
        "stock_warning": 25,
        "img_url": "/static/img/goods/biodegradable_cutlery.png",
        "status": "on_shelf"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "环保文具礼盒",
        "description": "包含再生纸笔记本、环保铅笔、植物墨水笔，适合学生和办公人群",
        "category": "文创",
        "need_points": 120.0,
        "stock": 80,
        "stock_warning": 15,
        "img_url": "/static/img/goods/stationery_set.png",
        "status": "on_shelf"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "竹制牙刷套装",
        "description": "4支装，竹制手柄，软毛刷头，环保包装，可替换刷头设计",
        "category": "日用品",
        "need_points": 100.0,
        "stock": 0,
        "stock_warning": 20,
        "img_url": "/static/img/goods/bamboo_toothbrush.png",
        "status": "sold_out"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "植物基洗衣液",
        "description": "2L装，采用天然植物提取成分，无磷无荧光剂，温和不伤手",
        "category": "日用品",
        "need_points": 90.0,
        "stock": 60,
        "stock_warning": 15,
        "img_url": "/static/img/goods/plant_detergent.png",
        "status": "on_shelf"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "环保种子卡片",
        "description": "可种植的贺卡，内含花籽，使用后可埋入土中发芽，独特环保礼品",
        "category": "文创",
        "need_points": 50.0,
        "stock": 300,
        "stock_warning": 50,
        "img_url": "/static/img/goods/seed_card.png",
        "status": "on_shelf"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "不锈钢吸管套装",
        "description": "包含8mm和10mm吸管各2根，配备清洁刷和收纳袋，食品级304不锈钢",
        "category": "日用品",
        "need_points": 110.0,
        "stock": 120,
        "stock_warning": 20,
        "img_url": "/static/img/goods/steel_straws.png",
        "status": "on_shelf"
    },
    {
        "merchant_username": "M1764328599217",
        "goods_name": "微纤维清洁布",
        "description": "3片装，超细纤维材质，可水洗重复使用，无需化学清洁剂",
        "category": "日用品",
        "need_points": 40.0,
        "stock": 5,
        "stock_warning": 10,
        "img_url": "/static/img/goods/microfiber_cloth.png",
        "status": "off_shelf"
    }
]

def insert_goods():
    """插入商品数据到数据库"""
    app = create_app()

    with app.app_context():
        # 先查询是否已有商品
        existing_goods = Goods.query.all()
        if existing_goods:
            print(f"数据库中已有 {len(existing_goods)} 条商品记录。")
            choice = input("是否清空现有商品并插入新数据？(y/n): ")
            if choice.lower() == 'y':
                # 清空现有数据
                Goods.query.delete()
                db.session.commit()
                print("已清空现有商品数据")
            else:
                print("操作取消")
                return

        # 插入新数据
        count = 0
        for record in goods_records:
            goods = Goods(
                merchant_username=record['merchant_username'],
                goods_name=record['goods_name'],
                description=record['description'],
                category=record['category'],
                need_points=record['need_points'],
                stock=record['stock'],
                stock_warning=record['stock_warning'],
                img_url=record['img_url'],
                status=record['status'],
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(goods)
            count += 1

        # 提交事务
        db.session.commit()
        print(f"\n成功插入 {count} 条商品记录！")

        # 显示插入的数据
        print("\n插入的商品列表：")
        for idx, goods in enumerate(Goods.query.all(), 1):
            print(f"{idx}. {goods.goods_name} - 商户:{goods.merchant_username} - {goods.need_points}积分 - 库存:{goods.stock} - 状态:{goods.status}")

if __name__ == '__main__':
    insert_goods()