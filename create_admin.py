#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建管理员账号
"""

from apps import create_app
from apps.administrators.models import Administrator
from exts import db

def create_admin():
    app = create_app()

    with app.app_context():
        # 检查是否已有管理员
        admin = Administrator.query.filter_by(adminname='Aadmin').first()

        if admin:
            print(f"管理员 '{admin.adminname}' 已存在")
        else:
            # 创建新管理员（注意：管理员登录需要用户名以'A'开头）
            admin = Administrator(
                adminname='Aadmin',
                password='123456',  # 使用明文密码，与登录验证逻辑保持一致
                phone='13800138000',
                email='admin@example.com'
            )

            db.session.add(admin)
            db.session.commit()

            print("管理员账号创建成功！")
            print("用户名: Aadmin")
            print("密码: 123456")

if __name__ == '__main__':
    create_admin()