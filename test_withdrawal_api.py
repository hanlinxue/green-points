from apps import create_app
from apps.merchants.models import WithdrawalRecord, Merchant
from exts import db

app = create_app()

with app.app_context():
    try:
        # 查询待审核的提现申请
        withdrawals = WithdrawalRecord.query.filter_by(status=0).order_by(WithdrawalRecord.create_time.desc()).all()

        print(f"Found {len(withdrawals)} pending withdrawals")

        items = []
        for w in withdrawals:
            # 获取商户信息
            merchant = Merchant.query.filter_by(username=w.merchant_username).first()

            item = {
                "id": w.id,
                "withdrawal_no": w.withdrawal_no,
                "merchantId": w.merchant_username,
                "merchantName": w.merchant_username,
                "points": w.points_amount,
                "amount": float(w.cash_amount),
                "bankAccount": w.bank_account,
                "bankName": w.bank_name,
                "accountHolder": w.account_holder,
                "createTime": w.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": w.status
            }
            items.append(item)
            print(f"Withdrawal: {item}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()