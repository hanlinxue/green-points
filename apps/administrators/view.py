from flask import Blueprint, request, render_template, jsonify

from apps.administrators.models import Administrator
from exts import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/admin_index')
def admin_index():
    return render_template('administrator/admin.html')
