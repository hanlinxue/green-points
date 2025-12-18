import requests
import json

# 测试提现功能
def test_withdrawal():
    # 先登录获取session
    session = requests.Session()

    # 登录商户账号
    login_data = {
        "id": "Mtest_merchant",  # 商户账号
        "password": "123456"      # 密码
    }

    try:
        # 执行登录
        login_response = session.post('http://127.0.0.1:5000/user/login', json=login_data)
        print(f"登录状态码: {login_response.status_code}")
        print(f"登录响应: {login_response.text[:500]}")

        if login_response.status_code == 200:
            # 获取商户积分信息
            points_response = session.get('http://127.0.0.1:5000/merchant/api/get-merchant-points')
            print(f"\n获取积分状态码: {points_response.status_code}")
            print(f"获取积分响应: {points_response.text}")

            if points_response.status_code == 200:
                points_data = points_response.json()
                print(f"\n当前积分: {points_data.get('points', 0)}")
                print(f"当前汇率: {points_data.get('exchangeRate', 0)}")

                # 测试提现申请
                withdraw_data = {
                    "withdrawAmount": 100  # 提现100积分
                }

                withdraw_response = session.post(
                    'http://127.0.0.1:5000/merchant/api/process-withdrawal',
                    json=withdraw_data
                )
                print(f"\n提现申请状态码: {withdraw_response.status_code}")
                print(f"提现申请响应: {withdraw_response.text}")

    except Exception as e:
        print(f"测试出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_withdrawal()