from datetime import datetime

from exts import db


class Administrator(db.Model):
    __tablename__ = 'tb_administrator'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    adminname = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(30))
    rdatetime = db.Column(db.DateTime, default=datetime.now)


class PointRule(db.Model):
    __tablename__ = "tb_point_rule"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="规则ID")
    # 基础字段（出行方式）
    trip_mode = db.Column(db.String(30), nullable=False, unique=True, comment="出行方式（walk/bike/public_transit/car）")
    # 碳减排核心字段
    carbon_reduction_coeff = db.Column(db.Float, nullable=False, default=0.0, comment="碳减排系数（kg CO₂/公里）")
    point_exchange_coeff = db.Column(db.Float, nullable=False, default=0.0, comment="积分兑换系数（积分/kg CO₂）")
    # 备注&时间
    remark = db.Column(db.String(100), nullable=True, comment="规则备注（如：步行每公里减排0.09kg CO₂，1kg兑换10积分）")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class PointsExchangeRate(db.Model):
    __tablename__ = 'tb_points_exchange_rate'
    # 基础字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    currency_code = db.Column(db.String(10), nullable=False, unique=True, comment="货币代码（如：CNY、USD、EUR）")
    currency_name = db.Column(db.String(50), nullable=False, comment="货币名称（如：人民币、美元、欧元）")
    exchange_rate = db.Column(db.Numeric(10, 4), nullable=False, comment="兑换汇率（1积分=X货币）")
    symbol = db.Column(db.String(10), nullable=False, comment="货币符号（如：¥、$、€）")
    is_active = db.Column(db.Boolean, default=True, comment="是否启用")
    # 时间字段
    rdatetime = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    udatetime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
