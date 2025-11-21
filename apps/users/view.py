import re

from flask import Blueprint, request, render_template, jsonify

user_bp = Blueprint('user', __name__)


@user_bp.route('/')
def index():
    return render_template('login/index.html')


@user_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('id')
        user_email = data.get('email')
        user_phone = data.get('phone')
        user_password = data.get('password')

        if not re.match(r'^\d{11}$', user_phone):
            return jsonify({"message": "手机号格式错误，请输入11位数字"}), 400
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, user_email):
            return jsonify({"message": "邮箱格式错误，请输入有效的邮箱地址"}), 400

        password_pattern = r'^(?=.*[A-Za-z])(?=.*\d).{11,}$'
        if not re.match(password_pattern, user_password):
            return jsonify({
                "message": "密码强度不够！密码必须由数字和字母组成，且长度不少于11位。"
            }), 400

        return jsonify({
            "message": "注册成功,即将返回登录页面!",
            "user_id": user_id
        }), 200
    return render_template('login/register.html')


@user_bp.route('/forgot')
def forgot():
    return render_template('login/forgot.html')
