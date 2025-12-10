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
