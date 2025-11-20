from flask import Blueprint, request, render_template
user_bp = Blueprint('user', __name__)


@user_bp.route('/')
def index():
    return render_template('login/index.html')


@user_bp.route('/register')
def register():
    return render_template('login/register.html')


@user_bp.route('/forgot')
def forgot():
    return render_template('login/forgot.html')
