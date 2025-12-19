import re
import redis
import json
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for, g

from apps.administrators.models import *
from apps.merchants.models import *
from apps.users.models import *
from exts import db

user_bp = Blueprint('user', __name__, url_prefix='/user')


# %%
# Redis连接
def get_redis_conn():
    """获取Redis连接（复用）"""
    if not hasattr(g, 'redis_conn'):
        g.redis_conn = redis.Redis(
            host='localhost',  # 本地Redis，生产环境改地址
            port=6379,
            db=0,
            decode_responses=False
        )
    return g.redis_conn


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


# 获取商品列表API
@user_bp.route('/products', methods=['GET'])
def get_products():
    try:
        # 查询所有上架的商品
        goods_list = Goods.query.filter_by(status='on_shelf').order_by(Goods.create_time.desc()).all()

        # 格式化返回数据
        result = []
        for goods in goods_list:
            # 处理图片URL，如果没有则使用默认图片
            img_url = goods.img_url if goods.img_url else '/static/img/default_product.png'

            result.append({
                "id": goods.id,
                "goods_name": goods.goods_name,
                "description": goods.description,
                "category": goods.category,
                "need_points": goods.need_points,
                "stock": goods.stock,
                "stock_warning": goods.stock_warning,
                "img_url": img_url,
                "status": goods.status,
                "create_time": goods.create_time.strftime("%Y-%m-%d %H:%M:%S") if goods.create_time else ""
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"查询商品列表失败：{str(e)}")
        return jsonify({"error": "获取商品列表失败，请稍后重试！"}), 500

# %%个人中心
# 个人中心
@user_bp.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    username = session.get("username")
    if not username:
        return redirect(url_for("user.index"))
    return render_template('users/user_profile.html')



# 个人资料展示
@user_bp.route('/user_info', methods=['GET', 'POST'])
def user_info():
    username = session.get("username")
    print(f"[DEBUG] Session username: {username}")
    if not username:
        return jsonify({"error": "未登录"}), 401

    user = User.query.filter_by(username=username).first()
    print(f"[DEBUG] Found user: {user}")
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


# 用户兑换商品API
@user_bp.route('/api/orders', methods=['POST'])
def create_exchange_order():
    """用户兑换商品创建订单"""
    # 1. 登录验证
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "用户未登录"}), 401

    try:
        # 2. 获取请求数据
        data = request.get_json()
        if not data or not data.get('productId') or not data.get('address'):
            return jsonify({"success": False, "message": "参数不完整"}), 400

        product_id = data['productId']
        address = data['address']
        quantity = data.get('quantity', 1)  # 默认数量为1

        # 3. 查询商品信息
        from apps.merchants.models import Goods
        goods = Goods.query.filter_by(id=product_id, status="on_shelf").first()

        if not goods:
            return jsonify({"success": False, "message": "商品不存在或已下架"}), 404

        # 4. 检查库存
        if goods.stock < quantity:
            return jsonify({"success": False, "message": f"库存不足，当前库存：{goods.stock}"}), 400

        # 5. 查询用户信息
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        # 6. 计算总积分并检查是否足够
        total_points_needed = goods.need_points * quantity
        if user.now_points < total_points_needed:
            return jsonify({"success": False, "message": "积分不足"}), 400

        # 7. 扣除积分、减少库存并创建兑换记录
        from datetime import datetime

        # 扣除用户积分
        user.now_points -= total_points_needed

        # 减少商品库存
        goods.stock -= quantity

        # 创建积分流水记录
        points_flow = PointsFlow(
            username=username,
            change_type="扣除",
            reason="兑换商品",
            points=-total_points_needed,  # 负数表示扣除
            balance=user.now_points,  # 变动后的积分余额
            goods_id=goods.id,
            goods_name=goods.goods_name,
            exchange_status="待发货",
            create_time=datetime.now()
        )

        # 同时创建商户订单记录
        from apps.merchants.models import Order
        from apps.users.models import Address
        import uuid

        # 生成订单号
        order_no = f"EX{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

        # 查找或创建地址记录
        address_id = None
        if address:
            # 解析地址字符串 "姓名 / 电话 / 详细地址"
            parts = address.split(' / ')
            if len(parts) >= 3:
                name = parts[0].strip()
                phone = parts[1].strip()
                detail_address = ' / '.join(parts[2:]).strip()

                # 查找已有地址
                existing_address = Address.query.filter_by(
                    username=username,
                    name=name,
                    phone=phone,
                    detail=detail_address
                ).first()

                if existing_address:
                    address_id = existing_address.id
                else:
                    # 如果没有找到匹配的地址，自动创建一个新地址
                    new_address = Address(
                        username=username,
                        name=name,
                        phone=phone,
                        region="",  # 兑换时输入的地址可能没有单独的地区字段
                        detail=detail_address,
                        is_default=False
                    )
                    db.session.add(new_address)
                    db.session.flush()  # 获取新地址的ID，但不提交整个事务
                    address_id = new_address.id

        # 创建订单记录
        order = Order(
            order_no=order_no,
            user_username=username,
            goods_id=goods.id,
            merchant_username=goods.merchant_username,
            address_id=address_id,
            point_amount=total_points_needed,
            order_status=1,  # 已扣积分
            pay_time=datetime.now(),
            create_time=datetime.now()
        )

        # 保存到数据库
        db.session.add(points_flow)
        db.session.add(order)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"兑换成功！兑换数量：{quantity}",
            "data": {
                "points_flow_id": points_flow.id,
                "order_id": order.id,
                "order_no": order_no,
                "goods_name": goods.goods_name,
                "quantity": quantity,
                "points_used": total_points_needed,
                "remaining_points": user.now_points,
                "address": address,
                "merchant_username": goods.merchant_username
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"[兑换失败] 错误详情：{str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"兑换失败：{str(e)}"}), 500


# 用户订单管理API
@user_bp.route('/api/orders', methods=['GET'])
def get_user_orders():
    """获取用户的所有订单"""
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "用户未登录"}), 401

    try:
        # 查询用户的所有订单
        from apps.merchants.models import Order
        orders = Order.query.filter_by(
            user_username=username,
            is_delete=0
        ).order_by(Order.create_time.desc()).all()

        result = []
        for order in orders:
            # 查询商品信息
            goods = Goods.query.filter_by(id=order.goods_id).first()

            # 查询地址信息
            address_info = "地址信息不完整"
            if order.address_id:
                address = Address.query.filter_by(id=order.address_id).first()
                if address:
                    # 组合地址信息，如果region为空就不显示
                    address_parts = [address.name, address.phone]
                    if address.region:
                        address_parts.append(address.region)
                    if address.detail:
                        address_parts.append(address.detail)
                    address_info = " / ".join(address_parts)

            # 状态映射
            status_map = {
                0: {"code": "pending", "text": "创建中"},
                1: {"code": "paid", "text": "已支付"},
                2: {"code": "accepted", "text": "商户已接单"},
                3: {"code": "shipped", "text": "已发货"},
                4: {"code": "completed", "text": "已完成"},
                5: {"code": "cancelled", "text": "已取消"},
                6: {"code": "refunded", "text": "已退款"}
            }

            status_info = status_map.get(order.order_status, {"code": "unknown", "text": "未知状态"})

            result.append({
                "id": order.id,
                "order_no": order.order_no,
                "goods_id": order.goods_id,
                "goods_name": goods.goods_name if goods else "商品已删除",
                "quantity": 1,  # 兑换商品默认数量为1
                "point_amount": order.point_amount,
                "merchant_username": order.merchant_username,
                "address_info": address_info,
                "status_code": status_info["code"],
                "status_text": status_info["text"],
                "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S") if order.create_time else "",
                "pay_time": order.pay_time.strftime("%Y-%m-%d %H:%M:%S") if order.pay_time else "",
                "ship_time": order.ship_time.strftime("%Y-%m-%d %H:%M:%S") if order.ship_time else "",
                "logistics_no": order.logistics_no,
                "logistics_company": order.logistics_company
            })

        return jsonify({"success": True, "orders": result}), 200

    except Exception as e:
        print(f"获取用户订单失败：{str(e)}")
        return jsonify({"success": False, "message": "获取订单失败"}), 500


@user_bp.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    """获取订单详情"""
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "用户未登录"}), 401

    try:
        from apps.merchants.models import Order
        order = Order.query.filter_by(
            id=order_id,
            user_username=username,
            is_delete=0
        ).first()

        if not order:
            return jsonify({"success": False, "message": "订单不存在"}), 404

        # 查询商品信息
        goods = Goods.query.filter_by(id=order.goods_id).first()

        # 查询地址信息
        address_info = "地址信息不完整"
        if order.address_id:
            address = Address.query.filter_by(id=order.address_id).first()
            if address:
                # 组合地址信息，如果region为空就不显示
                address_parts = [address.name, address.phone]
                if address.region:
                    address_parts.append(address.region)
                if address.detail:
                    address_parts.append(address.detail)
                address_info = " / ".join(address_parts)

        # 状态映射
        status_map = {
            0: {"code": "pending", "text": "创建中"},
            1: {"code": "paid", "text": "已支付"},
            2: {"code": "accepted", "text": "商户已接单"},
            3: {"code": "shipped", "text": "已发货"},
            4: {"code": "completed", "text": "已完成"},
            5: {"code": "cancelled", "text": "已取消"},
            6: {"code": "refunded", "text": "已退款"}
        }

        status_info = status_map.get(order.order_status, {"code": "unknown", "text": "未知状态"})

        result = {
            "id": order.id,
            "order_no": order.order_no,
            "goods_id": order.goods_id,
            "goods_name": goods.goods_name if goods else "商品已删除",
            "quantity": 1,
            "point_amount": order.point_amount,
            "merchant_username": order.merchant_username,
            "address_info": address_info,
            "status_code": status_info["code"],
            "status_text": status_info["text"],
            "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S") if order.create_time else "",
            "pay_time": order.pay_time.strftime("%Y-%m-%d %H:%M:%S") if order.pay_time else "",
            "ship_time": order.ship_time.strftime("%Y-%m-%d %H:%M:%S") if order.ship_time else "",
            "logistics_no": order.logistics_no,
            "logistics_company": order.logistics_company
        }

        return jsonify(result), 200

    except Exception as e:
        print(f"获取订单详情失败：{str(e)}")
        return jsonify({"success": False, "message": "获取订单详情失败"}), 500


@user_bp.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消订单并退款"""
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "用户未登录"}), 401

    try:
        from apps.merchants.models import Order
        order = Order.query.filter_by(
            id=order_id,
            user_username=username,
            is_delete=0
        ).first()

        if not order:
            return jsonify({"success": False, "message": "订单不存在"}), 404

        # 检查是否可以取消
        if order.order_status not in [0, 1]:  # 只能取消"创建中"或"已支付"的订单
            return jsonify({"success": False, "message": "该订单状态不允许取消"}), 400

        from datetime import datetime

        # 更新订单状态
        order.order_status = 5  # 已取消
        order.cancel_time = datetime.now()
        order.cancel_reason = "用户主动取消"

        # 退还用户积分
        user = User.query.filter_by(username=username).first()
        if user:
            user.now_points += order.point_amount
            user_balance = user.now_points
        else:
            user_balance = 0

        # 创建积分退款流水（安全处理商品可能被删除的情况）
        goods = Goods.query.filter_by(id=order.goods_id).first()
        goods_name = goods.goods_name if goods else "已删除商品"

        refund_flow = PointsFlow(
            username=username,
            change_type="获得",
            reason="订单取消退款",
            points=order.point_amount,
            balance=user_balance,
            goods_id=order.goods_id,
            goods_name=f"退款：{goods_name}",
            exchange_status="已退款",
            create_time=datetime.now()
        )

        # 恢复商品库存
        if goods:
            goods.stock += 1

        # 保存到数据库
        db.session.add(refund_flow)
        db.session.commit()

        return jsonify({"success": True, "message": "订单已取消，积分已退还"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"取消订单失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"取消订单失败：{str(e)}"}), 500


@user_bp.route('/api/orders/<int:order_id>/refund', methods=['POST'])
def request_refund(order_id):
    """申请退款"""
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "用户未登录"}), 401

    try:
        from apps.merchants.models import Order
        order = Order.query.filter_by(
            id=order_id,
            user_username=username,
            is_delete=0
        ).first()

        if not order:
            return jsonify({"success": False, "message": "订单不存在"}), 404

        # 检查是否可以申请退款
        if order.order_status not in [2, 3]:  # 只能对"已接单"或"已发货"的订单申请退款
            return jsonify({"success": False, "message": "该订单状态不允许申请退款"}), 400

        # 获取退款原因
        data = request.get_json()
        refund_reason = data.get('reason', '用户申请退款') if data else '用户申请退款'

        from datetime import datetime

        # 更新订单状态为退款申请中
        order.order_status = 6  # 已退款
        order.cancel_time = datetime.now()
        order.cancel_reason = refund_reason
        order.remark = f"退款原因: {refund_reason}"

        # 退还用户积分
        user = User.query.filter_by(username=username).first()
        if user:
            user.now_points += order.point_amount
            user_balance = user.now_points
        else:
            user_balance = 0

        # 创建积分退款流水（安全处理商品可能被删除的情况）
        goods = Goods.query.filter_by(id=order.goods_id).first()
        goods_name = goods.goods_name if goods else "已删除商品"

        refund_flow = PointsFlow(
            username=username,
            change_type="获得",
            reason="订单退款",
            points=order.point_amount,
            balance=user_balance,
            goods_id=order.goods_id,
            goods_name=f"退款：{goods_name}",
            exchange_status="已退款",
            create_time=datetime.now()
        )

        # 恢复商品库存
        if goods:
            goods.stock += 1

        # 保存到数据库
        db.session.add(refund_flow)
        db.session.commit()

        return jsonify({"success": True, "message": f"退款已处理，原因：{refund_reason}"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"申请退款失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"申请退款失败：{str(e)}"}), 500


@user_bp.route('/api/orders/<int:order_id>/receive', methods=['POST'])
def confirm_receive(order_id):
    """确认收货"""
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "用户未登录"}), 401

    try:
        from apps.merchants.models import Order
        order = Order.query.filter_by(
            id=order_id,
            user_username=username,
            is_delete=0
        ).first()

        if not order:
            return jsonify({"success": False, "message": "订单不存在"}), 404

        # 检查是否可以确认收货
        if order.order_status != 3:  # 只能对"已发货"的订单确认收货
            return jsonify({"success": False, "message": "该订单状态不允许确认收货"}), 400

        from datetime import datetime

        # 更新订单状态
        order.order_status = 4  # 已完成
        order.finish_time = datetime.now()

        db.session.commit()

        return jsonify({"success": True, "message": "已确认收货，订单完成"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"确认收货失败：{str(e)}")
        return jsonify({"success": False, "message": "确认收货失败"}), 500


# %%收货地址
# 用户订单管理页面
@user_bp.route('/user_orders_enhanced', methods=['GET'])
def user_orders_enhanced():
    """用户订单管理页面"""
    username = session.get("username")
    if not username:
        return redirect(url_for("user.login"))
    return render_template('users/user_orders_enhanced.html')


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

    # 3. 硬删除地址（即使被订单引用也删除）
    try:
        from apps.merchants.models import Order

        # 查找所有引用该地址的订单
        orders_with_address = Order.query.filter_by(
            address_id=id,
            is_delete=0
        ).all()

        # 将引用该地址的订单的address_id设为null（解除外键约束）
        for order in orders_with_address:
            order.address_id = None

        # 删除地址
        db.session.delete(address)
        db.session.commit()

        message = f"地址删除成功！已解除 {len(orders_with_address)} 个订单的地址引用。"
        return jsonify({"message": message}), 200

    except Exception as e:
        db.session.rollback()
        print(f"删除地址失败：{str(e)}")
        import traceback
        traceback.print_exc()
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


# 显示提交的出行记录
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

        # 3. 构造返回数据（新增审核状态+单条记录积分）
        result = []
        # 预查询所有积分规则（避免循环内多次查询数据库，提升性能）
        point_rules = {rule.trip_mode: rule for rule in PointRule.query.all()}

        for trip in trip_list:
            # 基础字段（保留原有逻辑）
            create_time = trip.create_time.strftime("%Y-%m-%d %H:%M:%S") if trip.create_time else ""
            # 初始化单条记录赚取的积分（默认0）
            earned_points = 0

            # 仅审核通过时计算该记录的积分
            if trip.status == "approved":
                # 匹配该出行方式的积分规则
                rule = point_rules.get(trip.mode)
                if rule:
                    # 计算积分（和你审核时发放积分的逻辑完全一致）
                    carbon_reduction = trip.distance * rule.carbon_reduction_coeff
                    earned_points = int(round(carbon_reduction * rule.point_exchange_coeff, 0))

            # 构造单条记录（新增所有需要的字段）
            result.append({
                "id": trip.id,
                "period": trip.period,
                "mode": trip.mode,
                "distance": trip.distance,
                "note": trip.note or "",  # 空值处理为""，避免前端undefined
                "create_time": create_time,
                # 新增审核相关字段
                "status": trip.status,  # pending/approved/rejected
                "reject_reason": trip.reject_reason or "",  # 驳回原因，空则返回""
                "audit_time": trip.audit_time.strftime("%Y-%m-%d %H:%M:%S") if trip.audit_time else "",  # 审核时间格式化
                # 新增单条记录赚取的积分（仅approved时有值）
                "earned_points": earned_points
            })

        # 4. 返回200状态码 + JSON数组（保持原有格式）
        return jsonify(result), 200

    except Exception as e:
        # 异常处理：打印错误，返回空数组（避免前端进catch弹窗）
        print(f"查询用户出行记录失败：{str(e)}")
        return jsonify([]), 200


@user_bp.route('/user_trip/sub_trips', methods=['GET', 'POST'])
def submit_user_trip():
    # 1. 校验用户登录态（你的原有逻辑，保留）
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "请先登录！"}), 401

    # 2. 接收并校验请求参数（你的原有逻辑，保留）
    try:
        data = request.get_json()
        period = data.get("period", "").strip()
        mode = data.get("mode", "").strip()
        distance = float(data.get("distance", 0))
        note = data.get("note", "").strip()
    except Exception as e:
        return jsonify({"success": False, "message": "参数格式错误！"}), 400

    # 3. 业务规则校验（你的原有逻辑，保留）
    # 3.1 周期格式校验（YYYY-MM-DD - YYYY-MM-DD）
    period_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}\s+-\s+\d{4}-\d{2}-\d{2}$')
    if not period or not period_pattern.match(period):
        return jsonify({"success": False, "message": "出行周期格式错误（示例：2025-11-01 - 2025-11-07）！"}), 400

    # 3.2 出行方式校验（仅允许指定值）
    allowed_modes = ["walk", "run", "bike", "bus", "subway", "car"]
    if mode not in allowed_modes:
        return jsonify({"success": False, "message": "不支持的出行方式！"}), 400

    # 3.3 里程校验（≥0.1公里）
    if distance < 0.1:
        return jsonify({"success": False, "message": "里程必须≥0.1公里！"}), 400

    # 4. 保存出行记录到数据库（修改：新增status=pending）
    try:
        new_trip = UserTrip(
            username=username,
            period=period,
            mode=mode,
            distance=distance,
            note=note,
            create_time=datetime.now(),
            status="pending"  # 新增：标记为审核中（也可在模型设default，这里显式传更清晰）
        )
        db.session.add(new_trip)
        db.session.commit()

        # 6. 返回成功响应（修改提示语：强调审核中）
        return jsonify({
            "success": True,
            "message": "出行记录提交成功！该记录正在审核中，一个工作日内完成审核～"
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"提交出行记录失败：{str(e)}")
        return jsonify({"success": False, "message": "服务器错误，提交失败！"}), 500




# 退出登录
@user_bp.route('/user_out', methods=['GET', 'POST'])
def user_out():
    return render_template('login/index.html')


# API: 获取当前登录用户信息
@user_bp.route('/api/current_user', methods=['GET'])
def get_current_user():
    """获取当前登录用户的信息"""
    try:
        # 检查管理员
        adminname = session.get("adminname")
        if adminname:
            from apps.administrators.models import Administrator
            admin = Administrator.query.filter_by(adminname=adminname).first()
            if admin:
                return jsonify({
                    "role": "admin",
                    "roleText": "系统管理员",
                    "id": admin.adminname,
                    "name": admin.adminname
                })

        # 检查商户
        merchantname = session.get("merchantname")
        if merchantname:
            from apps.merchants.models import Merchant
            merchant = Merchant.query.filter_by(username=merchantname).first()
            if merchant:
                return jsonify({
                    "role": "merchant",
                    "roleText": "商户",
                    "id": merchant.username,
                    "name": merchant.username
                })

        # 检查用户
        username = session.get("username")
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                return jsonify({
                    "role": "user",
                    "roleText": "用户",
                    "id": user.username,
                    "name": user.nickname or user.username
                })

        return jsonify({"error": "未登录"}), 401

    except Exception as e:
        print(f"获取用户信息失败：{str(e)}")
        return jsonify({"error": "获取用户信息失败"}), 500
