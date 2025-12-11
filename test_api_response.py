# 测试API响应
import requests
import json

def test_api():
    """测试商品API"""
    try:
        response = requests.get('http://localhost:5002/api/products')
        if response.status_code == 200:
            data = response.json()
            print("\n=== API测试成功 ===")
            print(f"状态: {data.get('success')}")
            print(f"商品数量: {data.get('count')}")

            if data.get('success') and data.get('data'):
                print("\n商品列表:")
                for idx, product in enumerate(data['data'][:3], 1):
                    print(f"\n{idx}. {product['goods_name']}")
                    print(f"   分类: {product['category']}")
                    print(f"   积分: {product['need_points']}")
                    print(f"   库存: {product['stock']}")
                    print(f"   状态: {product['status']}")
        else:
            print(f"\nAPI请求失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"\n连接失败: {e}")
        print("请确保测试服务器正在运行在 http://localhost:5002")

if __name__ == "__main__":
    test_api()