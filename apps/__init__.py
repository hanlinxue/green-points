# apps/__init__.py - 统一的app创建入口
import os
from flask import Flask
from exts import init_exts  # 你的数据库/扩展初始化函数
from settings import Config  # 你的配置文件

# 导入蓝图（确保路径正确）
from apps.users.view import user_bp
from apps.merchants.view import merchant_bp
from apps.administrators.view import admin_bp


def create_app(config=Config):
    """创建Flask应用（完整初始化，支持独立调用）"""
    # 1. 初始化app
    app = Flask(
        __name__,
        template_folder='../templates',  # 确保模板路径正确
        static_folder='../static'  # 确保静态文件路径正确
    )
    # 2. 加载配置
    app.config.from_object(config)
    app.config['SECRET_KEY'] = os.urandom(24)  # 会话密钥

    # 3. 初始化扩展（数据库、Redis等）
    init_exts(app)  # 关键！消费者必须执行这一步，否则db无效

    # 4. 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(merchant_bp, url_prefix='/merchant')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
