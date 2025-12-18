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
    now_points = db.Column(db.Integer, default=0)  # 当前积分
    all_points = db.Column(db.Integer, default=0)  # 累积获得积分
    use_points = db.Column(db.Integer, default=0)  # 累积兑换积分

class GoodsStatusEnum(Enum):
    ON_SHELF = "on_shelf"  # 上架（可兑换）
    OFF_SHELF = "off_shelf"  # 下架（不可兑换）
    SOLD_OUT = "sold_out"  # 售罄（临时不可兑换）


# 商品表（tb_goods）
class Goods(db.Model):
    __tablename__ = "tb_goods"
    # 核心主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="商品ID（主键）")
    merchant_username = db.Column(db.String(30), db.ForeignKey("tb_merchant.username"), nullable=False, comment="商户ID")
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
    user_username = db.Column(db.String(30), db.ForeignKey("tb_user.username"), nullable=False, comment="用户ID")
    goods_id = db.Column(db.Integer, db.ForeignKey("tb_goods.id"), nullable=False, comment="商品ID")
    merchant_username = db.Column(db.String(30), db.ForeignKey("tb_merchant.username"), nullable=False, comment="商户ID")
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


# 提现记录表
class WithdrawalRecord(db.Model):
    __tablename__ = "tb_withdrawal_record"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="提现记录ID")
    withdrawal_no = db.Column(db.String(32), unique=True, nullable=False, comment="提现单号")
    merchant_username = db.Column(db.String(30), db.ForeignKey("tb_merchant.username"), nullable=False, comment="商户ID")
    points_amount = db.Column(db.Integer, nullable=False, comment="提现积分数量")
    cash_amount = db.Column(db.Numeric(10, 2), nullable=False, comment="提现金额（人民币）")
    exchange_rate = db.Column(db.Numeric(10, 2), nullable=False, comment="提现时使用的汇率")
    status = db.Column(db.SmallInteger, nullable=False, default=0, comment="提现状态：0-待审核 1-审核通过 2-审核拒绝 3-提现完成 4-提现失败")
    bank_account = db.Column(db.String(50), nullable=True, comment="银行账号")
    bank_name = db.Column(db.String(100), nullable=True, comment="银行名称")
    account_holder = db.Column(db.String(50), nullable=True, comment="账户持有人")
    remark = db.Column(db.String(200), default=None, comment="备注")
    admin_remark = db.Column(db.String(200), default=None, comment="管理员备注")
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="申请时间")
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    approve_time = db.Column(db.DateTime, default=None, comment="审核时间")
    complete_time = db.Column(db.DateTime, default=None, comment="完成时间")
