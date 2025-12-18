import requests
import json

# 测试获取提现记录
def test_withdrawal_records():
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

        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"登录成功: {login_result.get('message')}")

            # 获取提现记录
            records_response = session.get('http://127.0.0.1:5000/merchant/api/withdrawal-records')
            print(f"\n获取提现记录状态码: {records_response.status_code}")

            if records_response.status_code == 200:
                records_data = records_response.json()
                print(f"\n提现记录总数: {records_data.get('pagination', {}).get('total', 0)}")

                records = records_data.get('records', [])
                if records:
                    print("\n提现记录列表:")
                    for i, record in enumerate(records, 1):
                        print(f"\n记录 {i}:")
                        print(f"  提现单号: {record.get('withdrawal_no')}")
                        print(f"  提现积分: {record.get('points_amount')}")
                        print(f"  提现金额: {record.get('cash_amount')}元")
                        print(f"  汇率: {record.get('exchange_rate')}")
                        print(f"  状态: {record.get('status')} (0-待审核 1-审核通过 2-审核拒绝 3-提现完成 4-提现失败)")
                        print(f"  申请时间: {record.get('create_time')}")
                else:
                    print("暂无提现记录")
            else:
                print(f"获取提现记录失败: {records_response.text}")
        else:
            print(f"登录失败: {login_response.text}")

    except Exception as e:
        print(f"测试出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_withdrawal_records()