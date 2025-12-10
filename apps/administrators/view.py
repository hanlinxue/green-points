from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for

from apps.administrators.models import *
from apps.merchants.models import *
from apps.users.models import *
from exts import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/admin_index')
def admin_index():
    adminname = session.get("adminname")
    if not adminname:
        return redirect(url_for("user.index"))
    return render_template('administrator/admin.html')


@admin_bp.route('/admin_users')
def admin_users():
    adminname = session.get("adminname")
    if not adminname:
        return redirect(url_for("user.index"))
    return render_template('administrator/admin_users.html')


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
