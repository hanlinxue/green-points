import re

from flask import Blueprint, request, render_template, jsonify

from apps.administrators.models import Administrator
from apps.merchants.models import Merchant
from apps.users.models import User
from exts import db

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/')
def index():
    return render_template('login/index.html')


# register.html
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        account_id = data.get('id')
        account_id = data.get('id')
        account_email = data.get('email')
        account_phone = data.get('phone')
        account_password = data.get('password')

        if not re.match(r'^\d{11}$', account_phone):
            return jsonify({"message": "手机号格式错误，请输入11位数字"}), 400
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, account_email):
            return jsonify({"message": "邮箱格式错误，请输入有效的邮箱地址"}), 400

        password_pattern = r'^(?=.*[A-Za-z])(?=.*\d).{11,}$'
        if not re.match(password_pattern, account_password):
            return jsonify({
                "message": "密码强度不够！密码必须由数字和字母组成，且长度不少于11位。"
            }), 400

        first_char = account_id[0]
        # 用户注册
        if first_char == 'U':
            phone_exists = User.query.filter_by(phone=account_phone).first()
            if phone_exists:
                return jsonify({"message": "该手机号已存在，请更换手机号"}), 400
            user = User()
            user.username = account_id
            user.password = account_password
            user.phone = account_phone
            user.email = account_email
            db.session.add(user)
        # 商户注册
        elif first_char == 'M':
            # 手机号只检查 Merchant 表是否唯一
            phone_exists = Merchant.query.filter_by(phone=account_phone).first()
            if phone_exists:
                return jsonify({"message": "该手机号已存在，请更换手机号"}), 400
            merchant = Merchant()
            merchant.username = account_id
            merchant.password = account_password
            merchant.phone = account_phone
            merchant.email = account_email
            db.session.add(merchant)
        # 提交
        db.session.commit()
        return jsonify({
            "message": "注册成功,即将返回登录页面!",
        }), 200
    return render_template('login/register.html')


# 登录
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        account_role = data.get('id')
        password = data.get('password')
        first_char = account_role[0]
        # 用户
        if first_char == 'U':
            user = User.query.filter_by(username=account_role).first()
            if not user:
                return jsonify({"message": "用户不存在"}), 400

            if user.password != password:
                return jsonify({"message": "密码错误"}), 400
            return jsonify({
                "message": "登录成功！",
                "role": "user"
            }), 200
        # 商户
        elif first_char == 'M':
            merchant = Merchant.query.filter_by(username=account_role).first()
            if not merchant:
                return jsonify({"message": "商家不存在"}), 400

            if merchant.password != password:
                return jsonify({"message": "密码错误"}), 400

            return jsonify({
                "message": "登录成功！",
                "role": "merchant"
            }), 200
        # 系统管理员
        elif first_char == 'A':
            admin = Administrator.query.filter_by(adminname=account_role).first()
            if not admin:
                return jsonify({"message": "管理员不存在"}), 400

            if admin.password != password:
                return jsonify({"message": "密码错误"}), 400

            return jsonify({
                "message": "登录成功！",
                "role": "admin"
            }), 200
    return render_template('login/index.html')


@user_bp.route('/forgot')
def forgot():
    return render_template('login/forgot.html')


@user_bp.route('/reset')
def reset():
    return render_template('login/reset.html')


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
    if request.method == 'POST':
        return render_template('users/user_trip.html')
    return render_template('users/user_trip.html')


# 退出登录
@user_bp.route('/user_out', methods=['GET', 'POST'])
def user_out():
    return render_template('login/index.html')
