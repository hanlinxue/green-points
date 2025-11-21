from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()  # ORM
migrate = Migrate()  # 数据迁移
bootstrap = Bootstrap()


def init_exts(app):
    db.init_app(app=app)  # 将db对象与app进行关联
    migrate.init_app(app=app, db=db)
