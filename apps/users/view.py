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


# %%注册及登录
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

            session["username"] = merchant.username
            session["password"] = merchant.password
            session["phone"] = merchant.phone
            session["email"] = merchant.email

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

            session["adminname"] = admin.adminname
            session["password"] = admin.password
            session["phone"] = admin.phone
            session["email"] = admin.email
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


# %%用户界面
# products.html
@user_bp.route('/user_index', methods=['GET', 'POST'])
def user_index():
    username = session.get("username")
    if not username:
        return redirect(url_for("user.index"))
    return render_template('users/products.html')


# 个人中心
@user_bp.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    username = session.get("username")
    if not username:
        return redirect(url_for("user.index"))
    return render_template('users/user_profile.html')


# %%个人中心
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


# 显示积分
@user_bp.route('/user_profile/user_points', methods=['GET', 'POST'])
def get_user_points():
    # 1. 登录验证：校验用户是否已登录（session中是否有username）
    username = session.get("username")
    if not username:
        # 返回401状态码，前端res.ok会识别为失败，进入catch
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 2. 查询当前用户的积分数据（容错：用户无积分记录则初始化）
        user = User.query.filter_by(username=username).first()

        # 3. 构造返回数据（和前端接收的字段完全匹配）
        result = {
            "points": user.now_points,  # 当前积分
            "earned": user.all_points,  # 总获得积分
            "used": user.use_points  # 总使用积分
        }

        # 4. 返回200状态码 + JSON数据（前端res.ok为true）
        return jsonify(result), 200

    except Exception as e:
        # 捕获所有异常（数据库错误、查询失败等）
        print(f"查询用户积分失败：{str(e)}")
        # 返回500状态码 + 错误信息，前端进入catch
        return jsonify({"error": "积分数据查询失败，请稍后重试！"}), 500


# 积分流水
@user_bp.route('/user_profile/user_history', methods=['GET', 'POST'])
def get_history():
    # 1. 登录验证
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 2. 查询当前用户所有积分流水（按时间倒序，最新的在前）
        flow_list = PointsFlow.query.filter_by(username=username) \
            .order_by(PointsFlow.create_time.desc()) \
            .all()

        # 3. 构造返回数据（适配前端渲染，格式化时间）
        result = []
        for flow in flow_list:
            # 统一格式化时间（比如：2025-12-08 14:30:25）
            create_time = flow.create_time.strftime("%Y-%m-%d %H:%M:%S") if flow.create_time else ""

            result.append({
                "id": flow.id,
                "change_type": flow.change_type,  # 获得/扣除
                "reason": flow.reason,  # 出行/兑换商品/积分过期等
                "points": flow.points,  # 变动数量
                "balance": flow.balance,  # 变动后余额
                "create_time": create_time,  # 格式化后的时间
                # 兑换专属字段（非兑换场景为null，前端可忽略）
                "goods_name": flow.goods_name,
                "exchange_status": flow.exchange_status
            })

        # 4. 返回空数组（无数据）或流水列表，状态码200
        return jsonify(result), 200

    except Exception as e:
        print(f"查询积分流水失败：{str(e)}")
        return jsonify({"error": "积分流水查询失败，请稍后重试！"}), 500


# 兑换记录
@user_bp.route('/user_profile/user_orders', methods=['GET', 'POST'])
def get_exchange_orders():
    # 1. 登录验证
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 2. 筛选兑换相关记录（reason=兑换商品 + goods_id不为空）
        order_list = PointsFlow.query.filter(
            PointsFlow.username == username,
            PointsFlow.reason == "兑换商品",
            PointsFlow.goods_id.isnot(None)  # 仅筛选有商品ID的兑换记录
        ).order_by(PointsFlow.create_time.desc()).all()

        # 3. 构造兑换记录专属返回数据（适配前端渲染）
        result = []
        for order in order_list:
            create_time = order.create_time.strftime("%Y-%m-%d %H:%M:%S") if order.create_time else ""

            result.append({
                "order_id": order.id,  # 用流水ID作为订单ID
                "goods_name": order.goods_name,  # 兑换商品名称
                "use_points": abs(order.points),  # 消耗的积分（取绝对值，因为扣除是负数）
                "exchange_time": create_time,  # 兑换时间
                "status": order.exchange_status or "已兑换",  # 兑换状态（默认已兑换）
                "goods_id": order.goods_id  # 商品ID（前端可选）
            })

        # 4. 返回空数组（无兑换记录）或兑换列表，状态码200
        return jsonify(result), 200

    except Exception as e:
        print(f"查询兑换记录失败：{str(e)}")
        return jsonify({"error": "兑换记录查询失败，请稍后重试！"}), 500


# %%收货地址
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


# %%用户出行
# 提交出行
@user_bp.route('/user_trip', methods=['GET', 'POST'])
def user_trip():
    username = session.get("username")
    if not username:
        return redirect(url_for("user.login"))
    return render_template('users/user_trip.html')


@user_bp.route('/user_trip/get_trips', methods=['GET', 'POST'])
def get_trips():
    # 1. 登录验证：从session获取用户名（未登录返回空数组，避免前端弹窗）
    username = session.get("username")
    if not username:
        return jsonify([]), 200  # 未登录返回空数组，前端显示“暂无出行记录”

    try:
        # 2. 查询当前用户的出行记录（按创建时间倒序，最新的在前）
        trip_list = UserTrip.query.filter_by(username=username) \
            .order_by(UserTrip.create_time.desc()) \
            .all()

        # 3. 构造返回数据（字段完全匹配前端需要的period/mode/distance/note）
        result = []
        for trip in trip_list:
            # 格式化创建时间（可选，前端可展示）
            create_time = trip.create_time.strftime("%Y-%m-%d %H:%M:%S") if trip.create_time else ""
            result.append({
                "id": trip.id,
                "period": trip.period,
                "mode": trip.mode,
                "distance": trip.distance,
                "note": trip.note,
                "create_time": create_time  # 可选：前端可选择是否展示
            })

        # 4. 返回200状态码 + JSON数组（前端走then块，不弹窗）
        return jsonify(result), 200

    except Exception as e:
        # 异常处理：打印错误，返回空数组（避免前端进catch弹窗）
        print(f"查询用户出行记录失败：{str(e)}")
        return jsonify([]), 200


# 退出登录
@user_bp.route('/user_out', methods=['GET', 'POST'])
def user_out():
    return render_template('login/index.html')
