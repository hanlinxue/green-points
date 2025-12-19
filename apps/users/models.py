# ORM 类--->表
# 类对象--->表中的一条记录
from datetime import datetime, timedelta

from exts import db


class User(db.Model):
    __tablename__ = 'tb_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    nickname = db.Column(db.String(30), default="manbo")
    password = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(30))
    isdelete = db.Column(db.Boolean, default=False)
    iscancel = db.Column(db.Boolean, default=False)
    rdatetime = db.Column(db.DateTime, default=datetime.now)
    now_points = db.Column(db.Integer, default=0)  # 当前积分
    all_points = db.Column(db.Integer, default=0)  # 累积获得积分
    use_points = db.Column(db.Integer, default=0)  # 累积使用积分


# 收货地址
class Address(db.Model):
    __tablename__ = 'tb_address'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), db.ForeignKey('tb_user.username'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.String(200), nullable=False)
    is_default = db.Column(db.Boolean, default=0)
    create_time = db.Column(db.DateTime, default=datetime.now)


# 积分流水
class PointsFlow(db.Model):
    __tablename__ = 'tb_pointsflow'
    # 基础流水字段（所有积分变动都需要）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    change_type = db.Column(db.String(20), nullable=False)  # 变动类型："获得"/"扣除"
    reason = db.Column(db.String(50), nullable=False)  # 变动原因："出行"/"兑换商品"/"积分过期"/"补发"
    points = db.Column(db.Integer, nullable=False)  # （+为增，-为减）
    balance = db.Column(db.Integer, nullable=False)  # 变动后积分余额
    create_time = db.Column(db.DateTime, default=datetime.now)  # 变动时间

    # 兑换场景专属字段（可选，非兑换场景为null）
    goods_id = db.Column(db.Integer, nullable=True)  # 兑换的商品ID（关联商品表）
    goods_name = db.Column(db.String(50), nullable=True)  # 兑换的商品名称
    exchange_status = db.Column(db.String(20), nullable=True, default=None)  # 兑换状态："已兑换"/"已发货"/"已完成"


# 用户记录出行表
class UserTrip(db.Model):
    __tablename__ = "tb_usertrip"
    # 核心字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="出行记录ID")
    username = db.Column(db.String(50), db.ForeignKey("tb_user.username"), nullable=False, comment="关联用户名（外键）")
    period = db.Column(db.String(50), nullable=False, comment="出行周期（如：2025-11-01 - 2025-11-07）")
    mode = db.Column(db.String(30), nullable=False, comment="出行方式（walk/bike/public_transit/car）")
    distance = db.Column(db.Float, nullable=False, comment="出行里程（公里）")
    note = db.Column(db.Text, nullable=True, comment="出行备注（可选）")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="记录创建时间")

    status = db.Column(db.String(20), default="pending", nullable=False, comment="审核状态：pending-审核中，approved-通过，rejected-驳回")
    audit_time = db.Column(db.DateTime, nullable=True, comment="审核完成时间")
    audit_admin = db.Column(db.String(50), nullable=True, comment="审核管理员用户名")
    reject_reason = db.Column(db.String(200), nullable=True, comment="驳回原因（可选）")


# 短信验证码
class SmsCode(db.Model):
    __tablename__ = 'tb_sms_code'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(11), nullable=False, comment="手机号")
    code = db.Column(db.String(6), nullable=False, comment="验证码")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    expire_time = db.Column(db.DateTime, nullable=False, comment="过期时间")
    is_used = db.Column(db.Boolean, default=False, comment="是否已使用：True-已使用，False-未使用")

    # 设置联合索引（手机号 + 是否使用），提高查询效率
    __table_args__ = (
        db.Index('idx_phone_used', 'phone', 'is_used'),
    )