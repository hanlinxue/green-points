# 简单的Flask测试应用
from flask import Flask, jsonify, render_template
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps import create_app

# 创建应用实例（已经包含所有蓝图）
app = create_app()

@app.route('/')
def index():
    return render_template('users/products.html')

@app.route('/test-products')
def test_products():
    """测试商品API"""
    from apps.merchants.models import Goods
    from exts import db

    with app.app_context():
        goods = Goods.query.filter_by(status='on_shelf').limit(5).all()
        result = []
        for g in goods:
            result.append({
                'id': g.id,
                'goods_name': g.goods_name,
                'category': g.category,
                'need_points': g.need_points,
                'stock': g.stock
            })
        return jsonify(result)

if __name__ == '__main__':
    print("启动测试服务器...")
    print("访问 http://localhost:5001 查看商品页面")
    print("访问 http://localhost:5001/test-products 查看商品API数据")
    app.run(debug=True, port=5001)