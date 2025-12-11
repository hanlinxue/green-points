# 简单测试商品API
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from apps import create_app
from apps.merchants.models import Goods
from exts import db

# 创建应用实例
app = create_app()

@app.route('/')
def index():
    return """
    <h1>商品展示测试页面</h1>
    <p><a href="/api/products">点击这里查看商品API数据</a></p>
    <p><a href="/products-page">点击这里查看商品页面</a></p>
    """

@app.route('/api/products')
def get_products():
    """获取商品列表API"""
    try:
        with app.app_context():
            # 查询所有上架的商品
            goods_list = Goods.query.filter_by(status='on_shelf').order_by(Goods.create_time.desc()).limit(5).all()

            # 格式化返回数据
            result = []
            for goods in goods_list:
                result.append({
                    "id": goods.id,
                    "goods_name": goods.goods_name,
                    "description": goods.description[:100] + "..." if goods.description else "",
                    "category": goods.category,
                    "need_points": goods.need_points,
                    "stock": goods.stock,
                    "img_url": goods.img_url or "/static/img/default_product.png",
                    "status": goods.status
                })

            return jsonify({
                "success": True,
                "count": len(result),
                "data": result
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/products-page')
def products_page():
    """商品展示页面"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>商品展示测试</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .product { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .product h3 { margin: 0 0 10px 0; color: #333; }
            .product p { margin: 5px 0; color: #666; }
            .points { color: #ffc107; font-weight: bold; }
            .stock { color: #28a745; }
            button { background: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer; }
            button:disabled { background: #999; cursor: not-allowed; }
        </style>
    </head>
    <body>
        <h1>绿色积分商城</h1>
        <div id="loading">正在加载商品...</div>
        <div id="products"></div>

        <script>
            fetch('/api/products')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';

                    if (data.success && data.data.length > 0) {
                        const productsDiv = document.getElementById('products');
                        data.data.forEach(product => {
                            const productDiv = document.createElement('div');
                            productDiv.className = 'product';
                            productDiv.innerHTML = `
                                <h3>${product.goods_name}</h3>
                                <p><strong>分类：</strong>${product.category}</p>
                                <p><strong>描述：</strong>${product.description}</p>
                                <p class="points">所需积分：${product.need_points}</p>
                                <p class="stock">库存：${product.stock}</p>
                                <button onclick="alert('兑换功能开发中...')" ${product.stock <= 0 ? 'disabled' : ''}>
                                    ${product.stock <= 0 ? '已售罄' : '立即兑换'}
                                </button>
                            `;
                            productsDiv.appendChild(productDiv);
                        });
                    } else {
                        document.getElementById('products').innerHTML = '<p>暂无商品</p>';
                    }
                })
                .catch(error => {
                    document.getElementById('loading').textContent = '加载失败：' + error;
                });
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("测试服务器启动成功！")
    print("访问 http://localhost:5002 查看测试页面")
    print("访问 http://localhost:5002/api/products 查看商品API")
    app.run(debug=True, port=5002)