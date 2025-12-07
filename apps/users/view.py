import re

from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for

from apps.administrators.models import *
from apps.merchants.models import *
from apps.users.models import *
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
    username = session.get("username")
    if not username:
        return redirect(url_for("user.login"))
    return render_template('users/address.html')


# 显示已有收货地址
@user_bp.route('/user_profile/user_address', methods=['GET'])
def get_address_list():
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        address_list = Address.query.filter_by(username=username).order_by(Address.id.desc()).all()

        # 3. 格式化数据（匹配前端需要的字段）
        result = []
        for addr in address_list:
            result.append({
                "id": addr.id,
                "name": addr.name,
                "phone": addr.phone,
                "region": addr.region,
                "detail": addr.detail,
                "is_default": addr.is_default
            })

        # 4. 返回格式化后的地址列表
        return jsonify(result), 200

    except Exception as e:
        # 捕获数据库异常，返回错误信息
        print(f"查询地址列表失败：{str(e)}")
        return jsonify({"error": "获取地址列表失败，请稍后重试！"}), 500


# 编辑地址
@user_bp.route('/user_profile/user_address/get/<int:id>', methods=['GET', 'POST'])
def get_address(id):
    # 1. 登录验证：校验用户是否已登录（session中是否有username）
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        address = Address.query.filter_by(id=id, username=username).first()

        # 3. 校验地址是否存在
        if not address:
            return jsonify({"error": "该地址不存在或无访问权限！"}), 404

        # 4. 格式化返回数据（完全匹配前端需要的字段）
        result = {
            "id": address.id,
            "name": address.name,
            "phone": address.phone,
            "region": address.region,
            "detail": address.detail,
            "is_default": address.is_default
        }

        # 5. 返回数据（前端可直接用addr.name/addr.phone等填充表单）
        return jsonify(result), 200

    except Exception as e:
        # 捕获异常（如数据库连接失败、ID格式错误等）
        print(f"查询地址详情失败：{str(e)}")
        return jsonify({"error": "查询地址详情失败，请稍后重试！"}), 500


# 删除地址
@user_bp.route('/user_profile/user_address/delete/<int:id>', methods=['GET', 'POST'])
def delete_address(id):
    # 1. 登录验证
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    # 2. 校验地址是否存在且属于当前用户
    address = Address.query.filter_by(id=id, username=username).first()
    if not address:
        return jsonify({"error": "该地址不存在或无删除权限！"}), 404

    # 3. 删除地址
    try:
        db.session.delete(address)
        db.session.commit()
        return jsonify({"message": "地址删除成功！"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"删除地址失败：{str(e)}")
        return jsonify({"error": "删除地址失败，请稍后重试！"}), 500


# 设为默认地址
@user_bp.route('/user_profile/user_address/set_default/<int:id>', methods=['GET', 'POST'])
def set_default(id):
    # 1. 登录验证
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    # 2. 校验地址是否存在且属于当前用户
    address = Address.query.filter_by(id=id, username=username).first()
    if not address:
        return jsonify({"error": "该地址不存在或无操作权限！"}), 404

    # 3. 设为默认：先把所有地址设为非默认，再把当前地址设为默认
    try:
        # 批量更新该用户所有地址为非默认
        Address.query.filter_by(username=username).update({"is_default": False})
        # 把当前地址设为默认
        address.is_default = True
        db.session.commit()
        return jsonify({"message": "已设为默认地址！"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"设为默认地址失败：{str(e)}")
        return jsonify({"error": "设为默认地址失败，请稍后重试！"}), 500


# 新建address
@user_bp.route('/user_profile/user_address/add', methods=['GET', 'POST'])
def add_address():
    # 步骤1：登录验证（仅登录用户可操作）
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    # 步骤2：获取并校验前端提交的JSON参数
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求参数不能为空！"}), 400

    # 2.1 必传字段校验（姓名/手机号/地区/详细地址）
    required_fields = ["name", "phone", "region", "detail"]
    for field in required_fields:
        # 去除首尾空格后校验是否为空
        if not data.get(field) or data.get(field).strip() == "":
            return jsonify({"error": f"{field} 不能为空！"}), 400

    # 2.2 手机号格式校验（11位有效手机号）
    phone = data.get("phone").strip()
    if not re.match(r'^\d{11}$', phone):
        return jsonify({"error": "手机号格式错误，请输入11位有效手机号！"}), 400

    # 步骤3：处理默认地址逻辑（一个用户仅能有一个默认地址）
    is_default = data.get("is_default", False)
    if is_default:
        # 将当前用户所有地址设为非默认
        Address.query.filter_by(username=username, is_default=True).update({"is_default": False})

    # 步骤4：新增地址到数据库（事务保障）
    try:
        new_address = Address(
            username=username,
            name=data.get("name").strip(),
            phone=phone,
            region=data.get("region").strip(),
            detail=data.get("detail").strip(),
            is_default=is_default
        )
        db.session.add(new_address)
        db.session.commit()  # 提交事务
        return jsonify({"message": "地址新增成功！", "address_id": new_address.id}), 201
    except Exception as e:
        db.session.rollback()  # 异常回滚，避免数据脏写
        print(f"新增地址失败：{str(e)}")
        return jsonify({"error": "新增地址失败，请稍后重试！"}), 500


# 更新已有地址
@user_bp.route('/user_profile/user_address/update/<int:id>', methods=['POST'])
def update_address(id):
    # 步骤1：登录验证
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    # 步骤2：校验待更新地址是否存在且属于当前用户（权限过滤）
    address = Address.query.filter_by(id=id, username=username).first()
    if not address:
        return jsonify({"error": "该地址不存在或无修改权限！"}), 404

    # 步骤3：获取并校验前端参数
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求参数不能为空！"}), 400

    # 3.1 必传字段校验
    required_fields = ["name", "phone", "region", "detail"]
    for field in required_fields:
        if not data.get(field) or data.get(field).strip() == "":
            return jsonify({"error": f"{field} 不能为空！"}), 400

    # 3.2 手机号格式校验
    phone = data.get("phone").strip()
    if not re.match(r'^\d{11}$', phone):
        return jsonify({"error": "手机号格式错误，请输入11位有效手机号！"}), 400

    # 步骤4：处理默认地址逻辑
    is_default = data.get("is_default", False)
    if is_default:
        Address.query.filter_by(username=username, is_default=True).update({"is_default": False})

    # 步骤5：更新地址信息（事务保障）
    try:
        address.name = data.get("name").strip()
        address.phone = phone
        address.region = data.get("region").strip()
        address.detail = data.get("detail").strip()
        address.is_default = is_default
        db.session.commit()  # 提交事务
        return jsonify({"message": "地址更新成功！"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"更新地址失败：{str(e)}")
        return jsonify({"error": "更新地址失败，请稍后重试！"}), 500


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
