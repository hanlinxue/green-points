from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for

from apps.administrators.models import *
from apps.merchants.models import *
from apps.users.models import *
from exts import db

merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')


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
