from datetime import datetime

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
