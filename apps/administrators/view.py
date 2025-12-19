import json

from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for

from apps.administrators.models import *
from apps.merchants.models import *
from apps.users.models import *
from exts import db
from utils.redis import get_redis_conn

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/admin_index')
def admin_index():
    adminname = session.get("adminname")
    if not adminname:
        return redirect(url_for("user.index"))
    return render_template('administrator/admin.html')


# 获取待审核记录
@admin_bp.route('/trips_pending', methods=['GET'])
def get_pending_trips():
    # 1. 管理员登录验证（你的原有逻辑）
    admin_username = session.get("adminname")
    if not admin_username:
        return jsonify({"success": False, "message": "管理员未登录！"}), 401

    # 2. 查询待审核记录（status=pending）
    try:
        pending_trips = UserTrip.query.filter_by(status="pending").order_by(UserTrip.create_time.desc()).all()
        trip_list = []
        for trip in pending_trips:
            trip_list.append({
                "id": trip.id,
                "username": trip.username,
                "period": trip.period,
                "mode": trip.mode,
                "distance": trip.distance,
                "note": trip.note or "",
                "create_time": trip.create_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({
            "success": True,
            "data": {"trips": trip_list},
            "message": "获取待审核记录成功"
        }), 200
    except Exception as e:
        print(f"[管理员接口] 获取待审核记录失败：{str(e)}")
        return jsonify({"success": False, "message": "服务器错误！"}), 500


# 审核出行记录
@admin_bp.route('/trips_pending/<int:trip_id>/decide', methods=['POST'])
def decide_trip(trip_id):
    # 1. 管理员登录验证
    admin_username = session.get("adminname")
    if not admin_username:
        return jsonify({"success": False, "message": "管理员未登录！"}), 401

    # 2. 接收审核参数
    try:
        data = request.get_json()
        approve = data.get("approve", False)
        reject_reason = data.get("rejectReason", "").strip()
    except Exception as e:
        return jsonify({"success": False, "message": "参数格式错误！"}), 400

    # 3. 处理审核逻辑
    try:
        trip = UserTrip.query.get(trip_id)
        if not trip:
            return jsonify({"success": False, "message": "出行记录不存在！"}), 404
        if trip.status != "pending":
            return jsonify({"success": False, "message": "该记录已审核，无需重复操作！"}), 400

        # 4. 更新审核状态
        trip.status = "approved" if approve else "rejected"
        trip.audit_time = datetime.now()
        trip.audit_admin = admin_username
        trip.reject_reason = reject_reason if not approve else None

        # 5. 审核通过：发布Redis积分事件（Windows适配）
        if approve:
            # 获取Redis连接
            redis_conn = get_redis_conn()
            if not redis_conn:
                return jsonify({"success": False, "message": "Redis连接失败，暂无法发放积分！"}), 500

            # 构造积分事件（确保编码正确）
            trip_event = {
                "event_type": "TripApprovedEvent",
                "data": {
                    "trip_id": trip.id,
                    "username": trip.username,
                    "mode": trip.mode,
                    "distance": trip.distance,
                    "audit_admin": admin_username,
                    "audit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "timestamp": datetime.now().timestamp()
            }

            # 发布到Redis频道（Windows下编码为utf-8）
            redis_conn.publish(
                "trip_points_events",  # 积分发放专属频道
                json.dumps(trip_event, ensure_ascii=False).encode("utf-8")
            )
            print(f"[管理员接口] 已发布积分事件：用户{trip.username}，记录ID{trip.id}")

        # 6. 提交数据库（仅更新审核状态，积分异步处理）
        db.session.commit()

        # 7. 返回响应
        if approve:
            message = f"审核通过！积分将发放至{trip.username}账户"
        else:
            message = f"审核驳回：{reject_reason or '无原因'}"
        return jsonify({"success": True, "message": message}), 200

    except Exception as e:
        db.session.rollback()
        print(f"[管理员接口] 审核失败：{str(e)}")
        return jsonify({"success": False, "message": "服务器错误！"}), 500


# %%
# 账户管理
@admin_bp.route('/admin_users')
def admin_users():
    adminname = session.get("adminname")
    if not adminname:
        return redirect(url_for("user.index"))
    return render_template('administrator/admin_users.html')


# %%
# API: 获取用户列表
@admin_bp.route('/api/users', methods=['GET'])
def get_users():
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        # 获取所有未被删除的用户
        users = User.query.filter_by(isdelete=False).all()
        user_list = []

        for user in users:
            # 判断用户状态（使用iscancel作为冻结状态）
            status = "frozen" if user.iscancel else "normal"

            user_info = {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "email": user.email,
                "phone": user.phone,
                "status": status,
                "now_points": user.now_points,
                "all_points": user.all_points,
                "use_points": user.use_points,
                "rdatetime": user.rdatetime.strftime("%Y-%m-%d %H:%M:%S") if user.rdatetime else None
            }
            user_list.append(user_info)

        return jsonify({
            "success": True,
            "users": user_list
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"获取用户列表失败: {str(e)}"
        }), 500


# %%
# API: 获取商户列表
@admin_bp.route('/api/merchants', methods=['GET'])
def get_merchants():
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        # 获取所有未被删除的商户
        merchants = Merchant.query.filter_by(isdelete=False).all()
        merchant_list = []

        for merchant in merchants:
            # 判断商户状态
            # 使用iscancel作为冻结状态
            # 对于新注册的商户，如果没有特殊审核字段，默认为normal状态
            if merchant.iscancel:
                status = "frozen"
            # 注意：如果Merchant模型有审核状态字段，应该在这里处理
            # 暂时使用模拟数据来支持审核功能演示
            elif hasattr(merchant, 'status') and merchant.status == 'pending':
                status = "pending"
            else:
                status = "normal"

            merchant_info = {
                "id": merchant.id,
                "username": merchant.username,
                "email": merchant.email,
                "phone": merchant.phone,
                "status": status,
                "now_points": merchant.now_points,
                "all_points": merchant.all_points,
                "use_points": merchant.use_points,
                "rdatetime": merchant.rdatetime.strftime("%Y-%m-%d %H:%M:%S") if merchant.rdatetime else None
            }
            merchant_list.append(merchant_info)

        return jsonify({
            "success": True,
            "merchants": merchant_list
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"获取商户列表失败: {str(e)}"
        }), 500


# %%
# API: 冻结用户
@admin_bp.route('/api/users/<int:user_id>/freeze', methods=['POST'])
def freeze_user(user_id):
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        if user.isdelete:
            return jsonify({"success": False, "message": "用户已被删除"}), 400

        user.iscancel = True
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "用户已冻结"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"冻结用户失败: {str(e)}"
        }), 500


# %%
# API: 解冻用户
@admin_bp.route('/api/users/<int:user_id>/unfreeze', methods=['POST'])
def unfreeze_user(user_id):
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        if user.isdelete:
            return jsonify({"success": False, "message": "用户已被删除"}), 400

        user.iscancel = False
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "用户已解冻"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"解冻用户失败: {str(e)}"
        }), 500


# %%
# API: 删除用户
@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404

        # 软删除用户
        user.isdelete = True
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "用户已删除"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"删除用户失败: {str(e)}"
        }), 500


# %%
# API: 冻结商户
@admin_bp.route('/api/merchants/<int:merchant_id>/freeze', methods=['POST'])
def freeze_merchant(merchant_id):
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            return jsonify({"success": False, "message": "商户不存在"}), 404

        if merchant.isdelete:
            return jsonify({"success": False, "message": "商户已被删除"}), 400

        merchant.iscancel = True
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "商户已冻结"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"冻结商户失败: {str(e)}"
        }), 500


# %%
# API: 解冻商户
@admin_bp.route('/api/merchants/<int:merchant_id>/unfreeze', methods=['POST'])
def unfreeze_merchant(merchant_id):
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            return jsonify({"success": False, "message": "商户不存在"}), 404

        if merchant.isdelete:
            return jsonify({"success": False, "message": "商户已被删除"}), 400

        merchant.iscancel = False
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "商户已解冻"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"解冻商户失败: {str(e)}"
        }), 500


# %%
# API: 删除商户
@admin_bp.route('/api/merchants/<int:merchant_id>', methods=['DELETE'])
def delete_merchant(merchant_id):
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            return jsonify({"success": False, "message": "商户不存在"}), 404

        # 软删除商户
        merchant.isdelete = True
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "商户已删除"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"删除商户失败: {str(e)}"
        }), 500


# %%
# API: 审核通过商户
@admin_bp.route('/api/merchant/approve/<int:merchant_id>', methods=['POST'])
def approve_merchant(merchant_id):
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            return jsonify({"success": False, "message": "商户不存在"}), 404

        if merchant.isdelete:
            return jsonify({"success": False, "message": "商户已被删除"}), 400

        # 如果Merchant模型有status字段，更新状态为approved
        if hasattr(merchant, 'status'):
            merchant.status = 'approved'

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "商户审核已通过"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"审核通过商户失败: {str(e)}"
        }), 500


# %%
# API: 审核拒绝商户
@admin_bp.route('/api/merchant/reject/<int:merchant_id>', methods=['POST'])
def reject_merchant(merchant_id):
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "未登录"}), 401

    try:
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            return jsonify({"success": False, "message": "商户不存在"}), 404

        if merchant.isdelete:
            return jsonify({"success": False, "message": "商户已被删除"}), 400

        # 如果Merchant模型有status字段，更新状态为rejected
        if hasattr(merchant, 'status'):
            merchant.status = 'rejected'

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "商户审核已拒绝"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"审核拒绝商户失败: {str(e)}"
        }), 500


# %%
# 积分兑换规则
@admin_bp.route('/point_rules')
def point_rules():
    adminname = session.get("adminname")
    if not adminname:
        return redirect(url_for("user.index"))
    return render_template('administrator/point_rules.html')


@admin_bp.route('/rules_show', methods=['GET', 'POST'])
def get_point_rules():
    try:
        point_rules = PointRule.query.all()
        rule_list = []
        for rule in point_rules:
            rule_list.append({
                "id": rule.id,
                "trip_mode": rule.trip_mode,
                "carbon_reduction_coeff": rule.carbon_reduction_coeff,
                "point_exchange_coeff": rule.point_exchange_coeff,
                "remark": rule.remark,  # 已返回备注字段
                "create_time": rule.create_time.strftime("%Y-%m-%d %H:%M:%S") if rule.create_time else None,
                "update_time": rule.update_time.strftime("%Y-%m-%d %H:%M:%S") if rule.update_time else None
            })
        return jsonify({
            "success": True,
            "message": "获取积分规则成功",
            "data": rule_list
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"获取积分规则失败：{str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取积分规则失败：{str(e)}",
            "data": []
        }), 500


# 2. POST 接口：保存积分规则（新增，处理remark字段）
@admin_bp.route('/save_rules', methods=['GET', 'POST'])
def save_point_rules():
    try:
        # 获取前端提交的JSON数据
        rule_data_list = request.get_json()
        if not isinstance(rule_data_list, list):
            return jsonify({
                "success": False,
                "message": "提交的数据格式错误，必须是数组",
                "data": []
            }), 400

        # 移除「清空所有规则」的逻辑，改为逐行判断更新/新增
        for rule_data in rule_data_list:
            trip_mode = rule_data.get("trip_mode")
            carbon_coeff = rule_data.get("carbon_reduction_coeff", 0.0)
            point_coeff = rule_data.get("point_exchange_coeff", 0.0)
            remark = rule_data.get("remark", "")  # 接收前端提交的备注

            # 校验必填字段
            if not trip_mode:
                return jsonify({
                    "success": False,
                    "message": f"缺少出行方式字段：{rule_data}",
                    "data": []
                }), 400

            # 核心逻辑：根据trip_mode查询已有规则
            existing_rule = PointRule.query.filter_by(trip_mode=trip_mode).first()

            if existing_rule:
                # 存在则覆盖更新字段
                existing_rule.carbon_reduction_coeff = carbon_coeff
                existing_rule.point_exchange_coeff = point_coeff
                existing_rule.remark = remark
                # update_time会自动更新（模型中onupdate=datetime.now），无需手动赋值
            else:
                # 不存在则新增规则
                new_rule = PointRule(
                    trip_mode=trip_mode,
                    carbon_reduction_coeff=carbon_coeff,
                    point_exchange_coeff=point_coeff,
                    remark=remark
                )
                db.session.add(new_rule)

        # 批量提交所有修改/新增
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "积分规则保存成功（重复出行方式已覆盖）",
            "data": []
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"保存积分规则失败：{str(e)}")
        return jsonify({
            "success": False,
            "message": f"保存积分规则失败：{str(e)}",
            "data": []
        }), 500


# 新增：DELETE接口 - 根据规则ID删除记录
@admin_bp.route('/rules_delete/<int:rule_id>', methods=['DELETE'])
def delete_point_rule(rule_id):
    try:
        # 根据ID查询规则
        rule = PointRule.query.get(rule_id)
        if not rule:
            return jsonify({
                "success": False,
                "message": f"未找到ID为{rule_id}的积分规则",
                "data": []
            }), 404

        # 删除记录
        db.session.delete(rule)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "积分规则删除成功",
            "data": []
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"删除积分规则失败：{str(e)}")
        return jsonify({
            "success": False,
            "message": f"删除积分规则失败：{str(e)}",
            "data": []
        }), 500


# 积分兑换汇率管理
@admin_bp.route('/exchange_rates_show', methods=['GET'])
def get_exchange_rates():
    """获取所有兑换汇率"""
    try:
        rates = PointsExchangeRate.query.all()
        rate_list = []
        for rate in rates:
            rate_list.append({
                "id": rate.id,
                "currency_code": rate.currency_code,
                "currency_name": rate.currency_name,
                "exchange_rate": float(rate.exchange_rate),
                "symbol": rate.symbol,
                "is_active": rate.is_active,
                "create_time": rate.rdatetime.strftime("%Y-%m-%d %H:%M:%S") if rate.rdatetime else None,
                "update_time": rate.udatetime.strftime("%Y-%m-%d %H:%M:%S") if rate.udatetime else None
            })
        return jsonify({"success": True, "data": rate_list}), 200
    except Exception as e:
        print(f"获取汇率失败：{str(e)}")
        return jsonify({"success": False, "message": "获取汇率失败"}), 500


@admin_bp.route('/save_exchange_rates', methods=['POST'])
def save_exchange_rates():
    """保存兑换汇率"""
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"success": False, "message": "参数格式错误！"}), 400

        for item in data:
            if item.get('id'):  # 更新现有记录
                rate = PointsExchangeRate.query.get(item['id'])
                if rate:
                    rate.exchange_rate = float(item['exchange_rate'])
                    rate.is_active = item.get('is_active', rate.is_active)
            else:  # 新增记录
                # 检查是否已存在相同货币
                existing = PointsExchangeRate.query.filter_by(currency_code=item['currency_code']).first()
                if not existing:
                    new_rate = PointsExchangeRate(
                        currency_code=item['currency_code'],
                        exchange_rate=float(item['exchange_rate']),
                        is_active=item.get('is_active', True)
                    )
                    db.session.add(new_rate)

        db.session.commit()
        return jsonify({"success": True, "message": "汇率保存成功！"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"保存汇率失败：{str(e)}")
        return jsonify({"success": False, "message": f"保存失败：{str(e)}"}), 500


@admin_bp.route('/exchange_rates_delete/<int:rateId>', methods=['POST'])
def delete_exchange_rate(rateId):
    """删除兑换汇率"""
    try:
        rate = PointsExchangeRate.query.get(rateId)
        if not rate:
            return jsonify({"success": False, "message": "汇率不存在！"}), 404

        db.session.delete(rate)
        db.session.commit()
        return jsonify({"success": True, "message": "删除成功！"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"删除汇率失败：{str(e)}")
        return jsonify({"success": False, "message": f"删除失败：{str(e)}"}), 500


# API路由 - 提供给前端JavaScript调用
@admin_bp.route('/api/points/records', methods=['GET'])
def api_get_points_records():
    """获取积分记录统计"""
    try:
        from apps.users.models import PointsFlow

        # 获取最近7天的积分记录
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=7)

        # 查询最近的积分流水
        records = PointsFlow.query.filter(
            PointsFlow.create_time >= start_date
        ).order_by(PointsFlow.create_time.desc()).limit(10).all()

        items = []
        for r in records:
            items.append({
                "time": r.create_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "type": r.change_type,
                "points": r.points,
                "username": r.username,
                "reason": r.reason,
                "balance": r.balance,
                "goods_id": r.goods_id,
                "goods_name": r.goods_name,
                "exchange_status": r.exchange_status
            })

        return jsonify({
            "success": True,
            "data": {
                "items": items
            }
        })
    except Exception as e:
        print(f"获取积分记录失败：{str(e)}")
        return jsonify({"success": False, "message": "获取积分记录失败"}), 500


@admin_bp.route('/api/withdrawals/pending', methods=['GET'])
def api_get_pending_withdrawals():
    """获取待审核的提现申请"""
    # 管理员登录验证
    adminname = session.get("adminname")
    if not adminname:
        return jsonify({"success": False, "message": "管理员未登录！"}), 401

    try:
        from apps.merchants.models import WithdrawalRecord

        pending = WithdrawalRecord.query.filter_by(status=0).all()
        count = len(pending)

        # 获取最近几个申请的详情
        items = []
        for w in pending:
            items.append({
                "id": w.id,
                "withdrawal_no": w.withdrawal_no,
                "merchantName": w.merchant_username,
                "merchantId": w.merchant_username,
                "points": w.points_amount,
                "amount": float(w.cash_amount),
                "createTime": w.create_time.strftime("%Y-%m-%d %H:%M") if w.create_time else None
            })

        return jsonify({
            "success": True,
            "data": {
                "items": items
            }
        })
    except Exception as e:
        print(f"获取待审核提现失败：{str(e)}")
        return jsonify({"success": False, "message": "获取提现申请失败"}), 500


@admin_bp.route('/api/admin/withdrawals/pending', methods=['GET'])
def api_admin_get_pending_withdrawals():
    """获取待审核的提现申请（admin路径）"""
    return api_get_pending_withdrawals()


@admin_bp.route('/api/admin/withdrawals/<int:id>/decide', methods=['POST'])
def api_admin_decide_withdrawal(id):
    """审核提现申请"""
    try:
        from apps.merchants.models import WithdrawalRecord

        data = request.get_json()
        approve = data.get("approve", False)
        reject_reason = data.get("rejectReason", "")

        withdrawal = WithdrawalRecord.query.get(id)
        if not withdrawal:
            return jsonify({"success": False, "message": "提现记录不存在！"}), 404

        if withdrawal.status != 0:
            return jsonify({"success": False, "message": "该提现申请已处理！"}), 400

        withdrawal.status = 1 if approve else 2  # 1-已处理 2-已拒绝
        # 更新审核时间
        withdrawal.approve_time = datetime.now()

        if not approve:
            withdrawal.admin_remark = reject_reason

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "审核成功！",
            "data": {
                "approved": approve,
                "withdrawal_no": withdrawal.withdrawal_no,
                "merchant_username": withdrawal.merchant_username,
                "points_amount": withdrawal.points_amount,
                "cash_amount": float(withdrawal.cash_amount)
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"审核提现失败：{str(e)}")
        return jsonify({"success": False, "message": "审核失败！"}), 500


# 测试页面
@admin_bp.route('/test_api')
def test_api():
    return render_template('administrator/test_admin_api.html')


# 简化版管理员页面
@admin_bp.route('/admin_simple')
def admin_simple():
    return render_template('administrator/admin_simple.html')


# 清洁版管理员主页
@admin_bp.route('/admin_clean')
def admin_clean():
    return render_template('administrator/admin_clean.html')


# 测试提现申请显示
@admin_bp.route('/test_withdrawal')
def test_withdrawal():
    return render_template('administrator/test_withdrawal_display.html')


# 管理员主页工作版本
@admin_bp.route('/admin_working')
def admin_working():
    adminname = session.get("adminname")
    if not adminname:
        return redirect(url_for("user.index"))
    return render_template('administrator/admin_working.html')


