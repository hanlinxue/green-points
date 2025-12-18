#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建管理员账号
"""

from apps import create_app
from apps.administrators.models import Administrator
from exts import db
from werkzeug.security import generate_password_hash

def create_admin():
    app = create_app()

    with app.app_context():
        # 检查是否已有管理员
        admin = Administrator.query.filter_by(adminname='admin').first()

        if admin:
            print(f"管理员 '{admin.adminname}' 已存在")
        else:
            # 创建新管理员
            admin = Administrator(
                adminname='admin',
                password=generate_password_hash('123456'),
                phone='13800138000',
                email='admin@example.com'
            )

            db.session.add(admin)
            db.session.commit()

            print("管理员账号创建成功！")
            print("用户名: admin")
            print("密码: 123456")

if __name__ == '__main__':
    create_admin()