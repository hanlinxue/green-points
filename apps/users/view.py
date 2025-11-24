import re

from flask import Blueprint, request, render_template, jsonify

from apps.users.models import User
from exts import db

user_bp = Blueprint('user', __name__)


@user_bp.route('/')
def index():
    return render_template('login/index.html')


# register.html
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('id')
        user_email = data.get('email')
        user_phone = data.get('phone')
        user_password = data.get('password')

        if not re.match(r'^\d{11}$', user_phone):
            return jsonify({"message": "手机号格式错误，请输入11位数字"}), 400
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, user_email):
            return jsonify({"message": "邮箱格式错误，请输入有效的邮箱地址"}), 400

        password_pattern = r'^(?=.*[A-Za-z])(?=.*\d).{11,}$'
        if not re.match(password_pattern, user_password):
            return jsonify({
                "message": "密码强度不够！密码必须由数字和字母组成，且长度不少于11位。"
            }), 400

        user = User()
        user.username = user_id
        user.password = user_password
        user.phone = user_phone
        user.email = user_email
        # 插入
        db.session.add(user)
        # 提交
        db.session.commit()
        return jsonify({
            "message": "注册成功,即将返回登录页面!",
            "user_id": user_id
        }), 200
    return render_template('login/register.html')


# index.html
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('id')
        print(username)
        password = data.get('password')
        print(password)
        user_list = User.query.filter_by(username=username)  # 返回多条记录
        for u in user_list:
            # u表示的是用户对象，里面存的是用户名
            if u.password == password:
                return jsonify({
                    "message": "注册成功,即将进入系统!",
                }), 200
            else:
                return jsonify({"message": "用户名或者密码有错误！"}), 400
    return render_template('login/index.html')


@user_bp.route('/forgot')
def forgot():
    return render_template('login/forgot.html')


# products.html
@user_bp.route('/user_index', methods=['GET', 'POST'])
def user_index():
    return render_template('users/products.html')


# 个人中心
@user_bp.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if request.method == 'POST':
        return render_template('users/user_profile.html')
    return render_template('users/user_profile.html')


# 提交出行
@user_bp.route('/user_trip', methods=['GET', 'POST'])
def user_trip():
    return render_template('users/user_trip.html')


# 退出登录
@user_bp.route('/user_out', methods=['GET', 'POST'])
def user_out():
    return render_template('login/index.html')
