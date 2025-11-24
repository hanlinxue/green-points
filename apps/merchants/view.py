from flask import Blueprint, request, render_template, jsonify

from apps.merchants.models import Merchant
from exts import db

merchant_bp = Blueprint('merchant', __name__)