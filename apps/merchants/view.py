from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from datetime import datetime

from apps.administrators.models import *
from apps.merchants.models import *
from apps.users.models import *
from exts import db

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


@merchant_bp.route('/merchant_index', methods=['GET', 'POST'])
def merchant_index():
    username = session.get("username")
    if not username:
        return redirect(url_for("user.index"))
    return render_template("merchants/merchant.html")


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
    username = session.get("username")
    if not username:
        return redirect(url_for("user.index"))
    return render_template('login/index.html')


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
