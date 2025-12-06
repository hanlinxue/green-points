import re

from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for

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
            # 登录成功 → 写 session
            session["nickname"] = user.nickname
            session["username"] = user.username
            session["password"] = user.password
            session["phone"] = user.phone
            session["email"] = user.email

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
    username = session.get("username")
    if not username:
        return redirect(url_for("user.login"))
    return render_template('users/products.html')


# 个人中心
@user_bp.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    return render_template('users/user_profile.html')


# 个人资料展示
@user_bp.route('/user_info', methods=['GET', 'POST'])
def user_info():
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录"}), 401

    user = User.query.filter_by(username=username).first()
    print(user)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify({
        "nickname": user.nickname or "",
        "username": user.username or "",
        "password": user.password or "",
        "phone": user.phone or "",
        "email": user.email or ""
    })


# 更新个人资料
@user_bp.route('/user_profile/user_update', methods=['POST'])
def update_user_profile():
    # 1. 验证用户是否登录（session中是否有username）
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    # 2. 验证请求格式（必须是JSON）
    if not request.is_json:
        return jsonify({"error": "请求格式错误，请提交JSON数据！"}), 400

    # 3. 解析前端提交的参数
    data = request.get_json()
    nickname = data.get("nickname", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not nickname:
        return jsonify({"error": "昵称不能为空！"}), 400

    if not re.match(r'^\d{11}$', phone):
        return jsonify({"error": "请输入正确的11位手机号！"}), 400

    if phone and User.query.filter_by(phone=phone).filter(User.username != username).first():
        return jsonify({"error": "该手机号已被其他账号绑定！"}), 400

    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({"error": "请输入正确的邮箱格式！"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "用户不存在！"}), 404

    # 6. 更新用户信息（按需更新，避免覆盖未修改的字段）
    try:
        user.nickname = nickname
        if phone:
            user.phone = phone
        if email:
            user.email = email
        if password and password != "******":
            user.password = password

        db.session.commit()
        return jsonify({"message": "资料更新成功！"}), 200

    except Exception as e:
        # 异常回滚，避免数据库锁死
        db.session.rollback()
        print(f"更新资料失败：{str(e)}")
        return jsonify({"error": "服务器内部错误，更新失败！"}), 500


# 用户收货地址
@user_bp.route('/user_address', methods=['GET', 'POST'])
def user_address():
    return render_template('users/address.html')


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
