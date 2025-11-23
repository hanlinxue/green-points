from flask import Flask

import settings
from apps.users.view import user_bp
from exts import init_exts


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    # 预处理
    app.config.from_object(settings.Config)
    # 蓝图
    app.register_blueprint(user_bp)
    # 数据库连接
    init_exts(app)
    return app
