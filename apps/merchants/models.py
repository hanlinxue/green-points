from datetime import datetime
from enum import Enum

from exts import db


class Merchant(db.Model):
    __tablename__ = 'tb_merchant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(30))
    isdelete = db.Column(db.Boolean, default=False)
    iscancel = db.Column(db.Boolean, default=False)
    rdatetime = db.Column(db.DateTime, default=datetime.now)


class GoodsStatusEnum(Enum):
    ON_SHELF = "on_shelf"  # 上架（可兑换）
    OFF_SHELF = "off_shelf"  # 下架（不可兑换）
    SOLD_OUT = "sold_out"  # 售罄（临时不可兑换）


# 商品表（tb_goods）
class Goods(db.Model):
    __tablename__ = "tb_goods"  # 表名，和你的UserTrip表命名风格一致
    # 核心主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="商品ID（主键）")
    # 商品基础信息
    goods_name = db.Column(db.String(100), nullable=False, comment="商品名称（如：环保水杯、帆布包）")
    description = db.Column(db.Text, nullable=True, comment="商品详细描述（可选）")
    category = db.Column(db.String(50), nullable=True, default="通用", comment="商品分类（如：日用品、文创、数码）")
    # 积分兑换相关（核心业务字段）
    need_points = db.Column(db.Float, nullable=False, comment="兑换该商品所需积分（如：100、250.5）")
    # 库存管理
    stock = db.Column(db.Integer, nullable=False, default=0, comment="商品库存数量（≥0）")
    stock_warning = db.Column(db.Integer, nullable=True, default=10, comment="库存预警值（低于该值提醒补货）")
    # 展示相关
    img_url = db.Column(db.String(255), nullable=True,comment="商品图片URL（存储静态文件路径，如：/static/img/goods/1.jpg）")
    # 状态控制
    status = db.Column(db.String(20), default=GoodsStatusEnum.ON_SHELF.value,comment="商品状态：on_shelf/off_shelf/sold_out")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="（上架时间）")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="商品信息更新时间")
