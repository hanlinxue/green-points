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
    __tablename__ = "tb_goods"
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


# 订单表
class Order(db.Model):
    __tablename__ = "tb_order"  # 指定表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="订单主键ID")
    order_no = db.Column(db.String(32), unique=True, nullable=False, comment="订单编号")
    user_id = db.Column(db.Integer, db.ForeignKey("tb_user.id"), nullable=False, comment="用户ID")
    goods_id = db.Column(db.Integer, db.ForeignKey("tb_goods.id"), nullable=False, comment="商品ID")
    merchant_id = db.Column(db.Integer, db.ForeignKey("tb_merchant.id"), nullable=False, comment="商户ID")
    address_id = db.Column(db.Integer, db.ForeignKey("tb_address.id"), default=None, comment="收货地址ID")
    point_amount = db.Column(db.Float(10, 2), nullable=False, default=0.00, comment="消耗积分数量")
    order_status = db.Column(db.SmallInteger, nullable=False, default=0, comment="订单状态：0-创建中 1-已扣积分 2-商户已接单 3-已发货 4-完成 5-取消 6-售后中")
    logistics_no = db.Column(db.String(64), default=None, comment="物流单号")
    logistics_company = db.Column(db.String(32), default=None, comment="物流公司名称")
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,comment="更新时间")
    pay_time = db.Column(db.DateTime, default=None, comment="积分扣除成功时间")
    ship_time = db.Column(db.DateTime, default=None, comment="商户发货时间")
    finish_time = db.Column(db.DateTime, default=None, comment="订单完成时间")
    cancel_time = db.Column(db.DateTime, default=None, comment="订单取消时间")
    cancel_reason = db.Column(db.String(100), default=None, comment="取消原因")
    remark = db.Column(db.String(200), default=None, comment="订单备注")
    is_delete = db.Column(db.SmallInteger, nullable=False, default=0, comment="软删除标识")
