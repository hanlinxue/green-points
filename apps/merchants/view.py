from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from datetime import datetime

from apps.administrators.models import *
from apps.merchants.models import *
from apps.users.models import *
from exts import db
import uuid

merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')


def check_and_update_zero_stock_products():
    """
    检查所有上架商品的库存，如果库存为0则自动改为已售罄状态
    """
    try:
        # 查询所有上架状态的商品
        on_shelf_products = Goods.query.filter_by(status=GoodsStatusEnum.ON_SHELF.value).all()

        updated_count = 0
        for product in on_shelf_products:
            if product.stock == 0:
                product.status = GoodsStatusEnum.SOLD_OUT.value
                product.update_time = datetime.now()
                updated_count += 1
                print(f"[AUTO] 商品 {product.goods_name} (ID: {product.id}) 库存为0，自动状态更改为已售罄")

        if updated_count > 0:
            db.session.commit()
            print(f"[AUTO] 批量更新完成，共更新 {updated_count} 个商品状态为已售罄")

        return updated_count
    except Exception as e:
        print(f"[AUTO] 检查库存状态失败：{str(e)}")
        db.session.rollback()
        return 0




@merchant_bp.route('/merchant_oder', methods=['GET', 'POST'])
def merchant_order():
    username = session.get("username")
    if not username:
        return redirect(url_for("user.index"))
    return render_template('merchants/merchant_orders.html')


@merchant_bp.route('/merchant_product', methods=['GET', 'POST'])
def merchant_product():
    username = session.get("username")
    if not username:
        return redirect(url_for("user.index"))
    return render_template('merchants/merchant_products.html')


@merchant_bp.route('/merchant_withdraw', methods=['GET', 'POST'])
def merchant_withdraw():
    username = session.get("username")
    if not username:
        return redirect(url_for("user.index"))
    return render_template('merchants/merchant_withdraw.html')




@merchant_bp.route('/merchant_out', methods=['GET', 'POST'])
def merchant_out():
    # 清除session
    session.clear()
    # 重定向到用户首页
    return redirect("/user")


@merchant_bp.route('/merchant_info', methods=['GET'])
def get_merchant_info():
    """获取当前商户的积分信息"""
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "未登录"}), 401

    merchant = Merchant.query.filter_by(username=username).first()
    if not merchant:
        return jsonify({"success": False, "message": "商户不存在"}), 404

    return jsonify({
        "success": True,
        "now_points": merchant.now_points,
        "all_points": merchant.all_points,
        "use_points": merchant.use_points
    }), 200


# %%商品管理API
# 获取商户商品列表
@merchant_bp.route('/merchant_products', methods=['GET'])
def get_merchant_products():
    """获取当前商户的所有商品"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 检查当前商户商品的库存状态（可选，性能考虑可以降低频率）
        # 每次请求都检查可能会影响性能，可以考虑定期批量检查
        # 这里改为只检查当前商户的商品，减少查询范围
        merchant_products = Goods.query.filter_by(merchant_username=username, status=GoodsStatusEnum.ON_SHELF.value).all()
        for product in merchant_products:
            if product.stock == 0:
                product.status = GoodsStatusEnum.SOLD_OUT.value
                product.update_time = datetime.now()
                print(f"[AUTO] 商户 {username} 商品 {product.goods_name} 库存为0，自动状态更改为已售罄")

        # 如果有更新，提交事务
        if any(product.stock == 0 for product in merchant_products):
            db.session.commit()

        # 查询当前商户的所有商品
        products = Goods.query.filter_by(merchant_username=username).order_by(Goods.create_time.desc()).all()

        # 格式化返回数据
        result = []
        for product in products:
            result.append({
                "id": product.id,
                "goods_name": product.goods_name,
                "description": product.description,
                "category": product.category,
                "need_points": product.need_points,
                "stock": product.stock,
                "stock_warning": product.stock_warning,
                "img_url": product.img_url,
                "status": product.status,
                "create_time": product.create_time.strftime("%Y-%m-%d %H:%M:%S") if product.create_time else "",
                "update_time": product.update_time.strftime("%Y-%m-%d %H:%M:%S") if product.update_time else ""
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"查询商户商品失败：{str(e)}")
        return jsonify({"error": "获取商品列表失败，请稍后重试！"}), 500


# 创建新商品（上架商品）
@merchant_bp.route('/merchant_products', methods=['POST'])
def create_merchant_product():
    """商户上架新商品"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    if not request.is_json:
        return jsonify({"error": "请求格式错误，请提交JSON数据！"}), 400

    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ["goods_name", "need_points", "stock"]
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({"error": f"{field} 不能为空！"}), 400

        # 验证数据格式
        goods_name = data.get("goods_name", "").strip()
        description = data.get("description", "").strip()
        category = data.get("category", "通用").strip()
        need_points = float(data.get("need_points", 0))
        stock = int(data.get("stock", 0))
        stock_warning = int(data.get("stock_warning", 10))
        img_url = data.get("img_url", "").strip()

        if not goods_name:
            return jsonify({"error": "商品名称不能为空！"}), 400
        if need_points <= 0:
            return jsonify({"error": "所需积分必须大于0！"}), 400
        if stock < 0:
            return jsonify({"error": "库存不能为负数！"}), 400

        # 创建商品
        new_product = Goods(
            merchant_username=username,
            goods_name=goods_name,
            description=description,
            category=category,
            need_points=need_points,
            stock=stock,
            stock_warning=stock_warning,
            img_url=img_url if img_url else None,
            status=GoodsStatusEnum.ON_SHELF.value,
            create_time=datetime.now(),
            update_time=datetime.now()
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify({
            "message": "商品上架成功！",
            "product_id": new_product.id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"创建商品失败：{str(e)}")
        return jsonify({"error": "商品上架失败，请稍后重试！"}), 500


# 更新商品信息
@merchant_bp.route('/merchant_products/<int:product_id>', methods=['PUT'])
def update_merchant_product(product_id):
    """更新商品信息"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    if not request.is_json:
        return jsonify({"error": "请求格式错误，请提交JSON数据！"}), 400

    try:
        # 查询商品并验证权限
        product = Goods.query.filter_by(id=product_id, merchant_username=username).first()
        if not product:
            return jsonify({"error": "商品不存在或无权限修改！"}), 404

        data = request.get_json()

        # 更新字段（允许部分更新）
        if "goods_name" in data:
            goods_name = data["goods_name"].strip()
            if not goods_name:
                return jsonify({"error": "商品名称不能为空！"}), 400
            product.goods_name = goods_name

        if "description" in data:
            product.description = data["description"].strip()

        if "category" in data:
            product.category = data["category"].strip() or "通用"

        if "need_points" in data:
            need_points = float(data["need_points"])
            if need_points <= 0:
                return jsonify({"error": "所需积分必须大于0！"}), 400
            product.need_points = need_points

        if "stock" in data:
            stock = int(data["stock"])
            if stock < 0:
                return jsonify({"error": "库存不能为负数！"}), 400
            product.stock = stock

            # 自动状态检查：库存为0时自动改为已售罄
            if stock == 0 and product.status == GoodsStatusEnum.ON_SHELF.value:
                product.status = GoodsStatusEnum.SOLD_OUT.value
                print(f"[AUTO] 商品 {product.goods_name} 库存为0，自动状态更改为已售罄")

        if "stock_warning" in data:
            stock_warning = int(data["stock_warning"])
            if stock_warning < 0:
                return jsonify({"error": "预警库存不能为负数！"}), 400
            product.stock_warning = stock_warning

        if "img_url" in data:
            img_url = data["img_url"].strip()
            product.img_url = img_url if img_url else None

        # 更新时间
        product.update_time = datetime.now()

        db.session.commit()

        return jsonify({"message": "商品信息更新成功！"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"更新商品失败：{str(e)}")
        return jsonify({"error": "商品更新失败，请稍后重试！"}), 500


# 更新商品状态（上架/下架）
@merchant_bp.route('/merchant_products/<int:product_id>/status', methods=['PUT'])
def update_product_status(product_id):
    """更新商品状态（上架/下架）"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    if not request.is_json:
        return jsonify({"error": "请求格式错误，请提交JSON数据！"}), 400

    try:
        # 查询商品并验证权限
        product = Goods.query.filter_by(id=product_id, merchant_username=username).first()
        if not product:
            return jsonify({"error": "商品不存在或无权限修改！"}), 404

        data = request.get_json()
        new_status = data.get("status")

        # 验证状态值
        valid_statuses = [status.value for status in GoodsStatusEnum]
        if new_status not in valid_statuses:
            return jsonify({"error": "无效的商品状态！"}), 400

        product.status = new_status
        product.update_time = datetime.now()

        db.session.commit()

        status_text = {
            "on_shelf": "上架",
            "off_shelf": "下架",
            "sold_out": "售罄"
        }

        return jsonify({
            "message": f"商品状态已更新为：{status_text.get(new_status, new_status)}！"
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"更新商品状态失败：{str(e)}")
        return jsonify({"error": "状态更新失败，请稍后重试！"}), 500


# 删除商品
@merchant_bp.route('/merchant_products/<int:product_id>', methods=['DELETE'])
def delete_merchant_product(product_id):
    """删除商品（物理删除，从数据库中彻底删除）"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 查询商品并验证权限
        product = Goods.query.filter_by(id=product_id, merchant_username=username).first()
        if not product:
            return jsonify({"error": "商品不存在或无权限删除！"}), 404

        # 记录要删除的商品信息，用于日志
        product_name = product.goods_name

        # 检查是否有未完成的订单
        from apps.merchants.models import Order
        pending_orders = Order.query.filter_by(
            goods_id=product_id,
            is_delete=0
        ).filter(
            Order.order_status.in_([0, 1, 2, 3])  # 未完成的订单状态
        ).count()

        if pending_orders > 0:
            return jsonify({"error": f"该商品有 {pending_orders} 个未完成订单，无法删除！"}), 400

        # 物理删除：从数据库中彻底删除商品
        db.session.delete(product)
        db.session.commit()

        print(f"[DELETE] 商户 {username} 物理删除商品: {product_name} (ID: {product_id})")

        return jsonify({"message": f"商品 '{product_name}' 已永久删除！"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"删除商品失败：{str(e)}")
        return jsonify({"error": "商品删除失败，请稍后重试！"}), 500


# 检查并更新零库存商品状态
@merchant_bp.route('/check_stock_status', methods=['POST'])
def check_stock_status():
    """
    手动触发检查所有商品库存状态，库存为0的商品自动改为已售罄
    """
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        updated_count = check_and_update_zero_stock_products()
        return jsonify({
            "message": f"库存检查完成，共更新 {updated_count} 个商品状态为已售罄",
            "updated_count": updated_count
        }), 200
    except Exception as e:
        print(f"手动检查库存状态失败：{str(e)}")
        return jsonify({"error": "库存状态检查失败，请稍后重试！"}), 500


# 获取商户统计信息
@merchant_bp.route('/merchant_stats', methods=['GET'])
def get_merchant_stats():
    """获取商户统计信息"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 查询商户信息
        merchant = Merchant.query.filter_by(username=username).first()
        if not merchant:
            return jsonify({"error": "商户不存在！"}), 404

        # 统计商品数量
        on_shelf_count = Goods.query.filter_by(
            merchant_username=username,
            status=GoodsStatusEnum.ON_SHELF.value
        ).count()

        # 统计待处理订单
        pending_orders_count = Order.query.filter_by(
            merchant_username=username,
            is_delete=0
        ).filter(
            Order.order_status.in_([1, 2])  # 已扣积分待接单，或已接单待发货
        ).count()

        return jsonify({
            "points": merchant.now_points,
            "products": on_shelf_count,
            "orders": pending_orders_count
        }), 200

    except Exception as e:
        print(f"获取商户统计失败：{str(e)}")
        return jsonify({"error": "获取统计信息失败，请稍后重试！"}), 500


# %%订单管理API
# 获取商户订单列表
@merchant_bp.route('/merchant_orders', methods=['GET'])
def get_merchant_orders():
    """获取当前商户的订单列表"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 查询当前商户的订单
        orders = Order.query.filter_by(
            merchant_username=username,
            is_delete=0
        ).order_by(Order.create_time.desc()).all()

        result = []
        for order in orders:
            # 查询商品信息
            goods = Goods.query.filter_by(id=order.goods_id).first()

            # 查询用户信息
            user = User.query.filter_by(username=order.user_username).first()

            # 查询收货地址
            address = None
            if order.address_id:
                address = Address.query.filter_by(id=order.address_id).first()

            # 状态映射
            status_map = {
                0: "创建中",
                1: "已扣积分",
                2: "商户已接单",
                3: "已发货",
                4: "完成",
                5: "取消",
                6: "已退款"
            }

            result.append({
                "id": order.id,
                "order_no": order.order_no,
                "user_nickname": user.nickname if user else order.user_username,
                "user_phone": user.phone if user else "",
                "goods_name": goods.goods_name if goods else "商品已删除",
                "goods_img": goods.img_url if goods else "",
                "point_amount": order.point_amount,
                "order_status": order.order_status,
                "order_status_text": status_map.get(order.order_status, "未知状态"),
                "logistics_no": order.logistics_no,
                "logistics_company": order.logistics_company,
                "address_info": {
                    "name": address.name if address else "",
                    "phone": address.phone if address else "",
                    "region": address.region if address else "",
                    "detail": address.detail if address else ""
                } if address else None,
                "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S") if order.create_time else "",
                "pay_time": order.pay_time.strftime("%Y-%m-%d %H:%M:%S") if order.pay_time else "",
                "ship_time": order.ship_time.strftime("%Y-%m-%d %H:%M:%S") if order.ship_time else "",
                "finish_time": order.finish_time.strftime("%Y-%m-%d %H:%M:%S") if order.finish_time else "",
                "remark": order.remark
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"查询订单列表失败：{str(e)}")
        return jsonify({"error": "获取订单列表失败，请稍后重试！"}), 500


# 接单
@merchant_bp.route('/merchant_orders/<int:order_id>/accept', methods=['POST'])
def accept_order(order_id):
    """商户接单"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 查询订单并验证权限
        order = Order.query.filter_by(
            id=order_id,
            merchant_username=username,
            is_delete=0
        ).first()

        if not order:
            return jsonify({"error": "订单不存在或无权限操作！"}), 404

        # 验证订单状态
        if order.order_status != 1:  # 已扣积分状态才能接单
            return jsonify({"error": "订单状态不允许接单！"}), 400

        # 更新订单状态
        order.order_status = 2  # 商户已接单
        order.update_time = datetime.now()

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "接单成功！"
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"接单失败：{str(e)}")
        return jsonify({"error": "接单失败，请稍后重试！"}), 500


# 发货
@merchant_bp.route('/merchant_orders/<int:order_id>/ship', methods=['POST'])
def ship_order(order_id):
    """商户发货"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    if not request.is_json:
        return jsonify({"error": "请求格式错误，请提交JSON数据！"}), 400

    try:
        data = request.get_json()
        logistics_no = data.get('logistics_no', '').strip()
        logistics_company = data.get('logistics_company', '').strip()

        # 验证必填字段
        if not logistics_no:
            return jsonify({"error": "物流单号不能为空！"}), 400

        if not logistics_company:
            return jsonify({"error": "物流公司不能为空！"}), 400

        # 查询订单并验证权限
        order = Order.query.filter_by(
            id=order_id,
            merchant_username=username,
            is_delete=0
        ).first()

        if not order:
            return jsonify({"error": "订单不存在或无权限操作！"}), 404

        # 验证订单状态
        if order.order_status != 2:  # 已接单状态才能发货
            return jsonify({"error": "订单状态不允许发货！"}), 400

        # 更新订单状态
        order.order_status = 3  # 已发货
        order.logistics_no = logistics_no
        order.logistics_company = logistics_company
        order.ship_time = datetime.now()
        order.update_time = datetime.now()

        # 更新用户积分流水中的兑换状态
        user_flow = PointsFlow.query.filter_by(
            username=order.user_username,
            goods_id=order.goods_id,
            points=-order.point_amount
        ).filter(
            PointsFlow.create_time >= order.create_time
        ).first()

        if user_flow:
            user_flow.exchange_status = "已发货"

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "发货成功！"
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"发货失败：{str(e)}")
        return jsonify({"error": "发货失败，请稍后重试！"}), 500


# 完成订单
@merchant_bp.route('/merchant_orders/<int:order_id>/complete', methods=['POST'])
def complete_order(order_id):
    """完成订单"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 查询订单并验证权限
        order = Order.query.filter_by(
            id=order_id,
            merchant_username=username,
            is_delete=0
        ).first()

        if not order:
            return jsonify({"error": "订单不存在或无权限操作！"}), 404

        # 验证订单状态
        if order.order_status != 3:  # 已发货状态才能完成
            return jsonify({"error": "订单状态不允许完成！"}), 400

        # 更新订单状态
        order.order_status = 4  # 完成
        order.finish_time = datetime.now()
        order.update_time = datetime.now()

        # 更新用户积分流水中的兑换状态
        user_flow = PointsFlow.query.filter_by(
            username=order.user_username,
            goods_id=order.goods_id,
            points=-order.point_amount
        ).filter(
            PointsFlow.create_time >= order.create_time
        ).first()

        if user_flow:
            user_flow.exchange_status = "已完成"

        # 将积分转给商户
        merchant = Merchant.query.filter_by(username=username).first()
        if merchant:
            merchant.now_points += order.point_amount  # 增加商户当前积分
            merchant.all_points += order.point_amount  # 增加商户总积分

            # 创建商户积分获得流水
            merchant_flow = PointsFlow(
                username=username,
                change_type="获得",
                reason="订单完成-商品销售",
                points=order.point_amount,
                balance=merchant.now_points,
                goods_id=order.goods_id,
                goods_name=user_flow.goods_name if user_flow else f"订单ID:{order.id}",
                exchange_status="已完成",
                create_time=datetime.now()
            )
            db.session.add(merchant_flow)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "订单已完成！"
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"完成订单失败：{str(e)}")
        return jsonify({"error": "操作失败，请稍后重试！"}), 500


# 取消订单
@merchant_bp.route('/merchant_orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消订单"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    if not request.is_json:
        return jsonify({"error": "请求格式错误，请提交JSON数据！"}), 400

    try:
        data = request.get_json()
        cancel_reason = data.get('cancel_reason', '').strip()

        # 查询订单并验证权限
        order = Order.query.filter_by(
            id=order_id,
            merchant_username=username,
            is_delete=0
        ).first()

        if not order:
            return jsonify({"error": "订单不存在或无权限操作！"}), 404

        # 验证订单状态
        if order.order_status in [4, 5]:  # 已完成或已取消不能再次取消
            return jsonify({"error": "订单状态不允许取消！"}), 400

        # 退还用户积分
        if order.order_status == 1:  # 已扣积分的需要退还
            user = User.query.filter_by(username=order.user_username).first()
            if user:
                user.now_points += order.point_amount
                user.use_points -= order.point_amount

                # 创建退还积分流水
                refund_flow = PointsFlow(
                    username=order.user_username,
                    change_type="获得",
                    reason="订单取消退还",
                    points=order.point_amount,
                    balance=user.now_points,
                    goods_id=order.goods_id,
                    goods_name=Goods.query.filter_by(id=order.goods_id).first().goods_name if Goods.query.filter_by(id=order.goods_id).first() else ""
                )
                db.session.add(refund_flow)

            # 扣除商户积分
            merchant = Merchant.query.filter_by(username=username).first()
            if merchant:
                merchant.now_points -= order.point_amount
                merchant.all_points -= order.point_amount

                # 创建商户扣除流水
                merchant_flow = PointsFlow(
                    username=username,
                    change_type="扣除",
                    reason="订单取消扣除",
                    points=-order.point_amount,
                    balance=merchant.now_points,
                    goods_id=order.goods_id,
                    goods_name=Goods.query.filter_by(id=order.goods_id).first().goods_name if Goods.query.filter_by(id=order.goods_id).first() else ""
                )
                db.session.add(merchant_flow)

            # 恢复商品库存
            goods = Goods.query.filter_by(id=order.goods_id).first()
            if goods:
                goods.stock += 1
                if goods.stock > 0 and goods.status == GoodsStatusEnum.SOLD_OUT.value:
                    goods.status = GoodsStatusEnum.ON_SHELF.value

        # 更新订单状态
        order.order_status = 5  # 取消
        order.cancel_time = datetime.now()
        order.cancel_reason = cancel_reason
        order.update_time = datetime.now()

        # 更新用户积分流水中的兑换状态
        user_flow = PointsFlow.query.filter_by(
            username=order.user_username,
            goods_id=order.goods_id,
            points=-order.point_amount
        ).filter(
            PointsFlow.create_time >= order.create_time
        ).first()

        if user_flow:
            user_flow.exchange_status = "已取消"

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "订单已取消！"
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"取消订单失败：{str(e)}")
        return jsonify({"error": "取消订单失败，请稍后重试！"}), 500


# %%提现相关API
@merchant_bp.route('/api/get-merchant-points', methods=['GET'])
def get_merchant_points():
    """获取商户积分余额和兑换汇率"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 获取商户信息
        merchant = Merchant.query.filter_by(username=username).first()
        if not merchant:
            return jsonify({"error": "商户不存在！"}), 404

        # 获取当前有效的积分兑换汇率
        exchange_rate_obj = PointsExchangeRate.query.filter_by(
            is_active=True,
            currency_code='CNY'  # 人民币
        ).first()

        if not exchange_rate_obj:
            return jsonify({"error": "积分兑换汇率未设置！"}), 500

        exchange_rate = float(exchange_rate_obj.exchange_rate)  # 1积分=X元

        return jsonify({
            "points": merchant.now_points,
            "exchangeRate": exchange_rate,
            "currencySymbol": exchange_rate_obj.symbol
        }), 200

    except Exception as e:
        print(f"获取商户积分失败：{str(e)}")
        return jsonify({"error": "获取积分信息失败，请稍后重试！"}), 500


@merchant_bp.route('/api/process-withdrawal', methods=['POST'])
def process_withdrawal():
    """处理商户提现申请"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    if not request.is_json:
        return jsonify({"error": "请求格式错误，请提交JSON数据！"}), 400

    try:
        data = request.get_json()
        withdraw_points = int(data.get('withdrawAmount', 0))  # 前端传的是积分数量

        # 验证提现积分数量
        if withdraw_points <= 0:
            return jsonify({"error": "提现积分数量必须大于0！"}), 400

        # 获取商户信息并验证积分余额
        merchant = Merchant.query.filter_by(username=username).first()
        if not merchant:
            return jsonify({"error": "商户不存在！"}), 404

        if merchant.now_points < withdraw_points:
            return jsonify({"error": "积分余额不足！"}), 400

        # 获取当前有效的积分兑换汇率
        exchange_rate_obj = PointsExchangeRate.query.filter_by(
            is_active=True,
            currency_code='CNY'
        ).first()

        if not exchange_rate_obj:
            return jsonify({"error": "积分兑换汇率未设置！"}), 500

        exchange_rate = float(exchange_rate_obj.exchange_rate)
        cash_amount = withdraw_points * exchange_rate  # 计算实际提现金额

        # 生成提现单号
        withdrawal_no = f"WD{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"

        # 创建提现记录
        withdrawal = WithdrawalRecord(
            withdrawal_no=withdrawal_no,
            merchant_username=username,
            points_amount=withdraw_points,
            cash_amount=cash_amount,
            exchange_rate=exchange_rate,
            status=0,  # 待审核
            create_time=datetime.now()
        )
        db.session.add(withdrawal)

        # 扣减商户积分
        merchant.now_points -= withdraw_points
        merchant.use_points += withdraw_points

        # 创建积分流水记录
        points_flow = PointsFlow(
            username=username,
            change_type="提现",
            reason=f"积分提现申请（单号：{withdrawal_no}）",
            points=-withdraw_points,
            balance=merchant.now_points,
            goods_id=None,
            goods_name="积分提现"
        )
        db.session.add(points_flow)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "提现申请已提交，请等待审核！",
            "withdrawal_no": withdrawal_no,
            "cash_amount": float(cash_amount)
        }), 200

    except ValueError:
        return jsonify({"error": "提现积分数量格式错误！"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"处理提现申请失败：{str(e)}")
        return jsonify({"error": "提现申请失败，请稍后重试！"}), 500


@merchant_bp.route('/api/withdrawal-records', methods=['GET'])
def get_withdrawal_records():
    """获取商户提现记录"""
    username = session.get("username")
    if not username:
        return jsonify({"error": "未登录，请先登录！"}), 401

    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # 限制每页最大数量

        # 查询提现记录
        records = WithdrawalRecord.query.filter_by(
            merchant_username=username
        ).order_by(
            WithdrawalRecord.create_time.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # 格式化返回数据
        records_list = []
        for record in records.items:
            records_list.append({
                'id': record.id,
                'withdrawal_no': record.withdrawal_no,
                'points_amount': record.points_amount,
                'cash_amount': float(record.cash_amount),
                'exchange_rate': float(record.exchange_rate),
                'status': record.status,
                'bank_account': record.bank_account,
                'bank_name': record.bank_name,
                'account_holder': record.account_holder,
                'remark': record.remark,
                'admin_remark': record.admin_remark,
                'create_time': record.create_time.isoformat() if record.create_time else None,
                'approve_time': record.approve_time.isoformat() if record.approve_time else None,
                'complete_time': record.complete_time.isoformat() if record.complete_time else None
            })

        return jsonify({
            "success": True,
            "records": records_list,
            "pagination": {
                "page": records.page,
                "pages": records.pages,
                "per_page": records.per_page,
                "total": records.total,
                "has_next": records.has_next,
                "has_prev": records.has_prev
            }
        }), 200

    except Exception as e:
        print(f"获取提现记录失败：{str(e)}")
        return jsonify({"error": "获取提现记录失败，请稍后重试！"}), 500
