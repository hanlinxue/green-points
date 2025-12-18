#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试提现申请 API
"""
import requests
import json

# 测试获取待审核提现申请
url = "http://127.0.0.1:5000/admin/api/admin/withdrawals/pending"

print("=" * 60)
print("测试提现申请 API")
print("=" * 60)

try:
    response = requests.get(url)
    print(f"\nURL: {url}")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n原始响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if data.get('success'):
            items = data.get('data', {}).get('items', [])
            print(f"\n提现申请数量: {len(items)}")

            for item in items:
                print(f"\n提现单号: {item.get('withdrawal_no')}")
                print(f"商户名: {item.get('merchantName')}")
                print(f"积分数量: {item.get('points')}")
                print(f"现金金额: {item.get('amount')}")
                print(f"创建时间: {item.get('createTime')}")
        else:
            print(f"API 返回失败: {data.get('message')}")
    else:
        print(f"请求失败")
        print(f"响应内容: {response.text}")

except Exception as e:
    print(f"请求异常: {e}")

# 也测试完整的 API
print("\n" + "=" * 60)
print("测试完整的提现申请 API")
print("=" * 60)

url2 = "http://127.0.0.1:5000/admin/api/withdrawals/pending"

try:
    response = requests.get(url2)
    print(f"\nURL: {url2}")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n原始响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if data.get('success'):
            items = data.get('data', {}).get('items', [])
            print(f"\n提现申请数量: {len(items)}")

            for item in items:
                print(f"\nID: {item.get('id')}")
                print(f"提现单号: {item.get('withdrawal_no')}")
                print(f"商户名: {item.get('merchantName')}")
                print(f"积分数量: {item.get('points')}")
                print(f"现金金额: {item.get('amount')}")
                print(f"状态: {item.get('status')}")
                print(f"创建时间: {item.get('createTime')}")
    else:
        print(f"请求失败")
        print(f"响应内容: {response.text}")

except Exception as e:
    print(f"请求异常: {e}")