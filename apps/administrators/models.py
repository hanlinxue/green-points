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