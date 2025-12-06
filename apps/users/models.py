# ORM 类--->表
# 类对象--->表中的一条记录
from datetime import datetime

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
    points = db.Column(db.Integer, default=0)
    # 增加一个字段
    # articles = db.relationship('Article', backref='tb_user')
