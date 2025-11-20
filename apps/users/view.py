from flask import Blueprint, request, render_template
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
    return render_template('login/register.html')


@user_bp.route('/forgot')
def forgot():
    return render_template('login/forgot.html')
