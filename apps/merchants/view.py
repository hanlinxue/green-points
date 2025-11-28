from flask import Blueprint, request, render_template, jsonify

from apps.merchants.models import Merchant
from exts import db

merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')


@merchant_bp.route('/merchant_index', methods=['GET', 'POST'])
def merchant_index():
    return render_template("merchants/merchant.html")


@merchant_bp.route('/merchant_oder', methods=['GET', 'POST'])
def merchant_order():
    return render_template('merchants/merchant_orders.html')


@merchant_bp.route('/merchant_product', methods=['GET', 'POST'])
def merchant_product():
    return render_template('merchants/merchant_products.html')


@merchant_bp.route('/merchant_withdraw', methods=['GET', 'POST'])
def merchant_withdraw():
    return render_template('merchants/merchant_withdraw.html')


@merchant_bp.route('/merchant_out', methods=['GET', 'POST'])
def merchant_out():
    return render_template('login/index.html')
