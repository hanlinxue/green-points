"""
短信服务配置
支持多个短信服务提供商
"""

# 选择短信服务提供商
# 可选值：'debug', 'aliyun', 'ihuyi', 'ronglian'
SMS_PROVIDER = 'debug'  # 默认使用调试模式

# ========================================
# 阿里云短信服务配置
# ========================================
ALIYUN = {
    'ACCESS_KEY_ID': "your_access_key_id",
    'ACCESS_KEY_SECRET': "your_access_key_secret",
    'SIGN_NAME': "绿行积分",
    'TEMPLATE_CODE': "SMS_xxxxxxx",
    'REGION_ID': "cn-hangzhou",
    'BUSINESS_NAME': "GreenPoints"
}

# ========================================
# 互亿无线短信服务配置
# 官网：https://www.ihuyi.com/
# ========================================
IHUYI = {
    'API_ID': "your_api_id",
    'API_KEY': "your_api_key"
}

# ========================================
# 容联云通讯短信服务配置
# 官网：https://www.yuntongxun.com/
# ========================================
RONGLIAN = {
    'ACCOUNT_SID': "your_account_sid",
    'AUTH_TOKEN': "your_auth_token",
    'APP_ID': "your_app_id",
    'TEMPLATE_ID': 1  # 模板ID，默认为1
}

# ========================================
# 腾讯云短信服务配置（待实现）
# ========================================
TENCENT = {
    'SECRET_ID': "your_secret_id",
    'SECRET_KEY': "your_secret_key",
    'SDK_APP_ID': "your_sdk_app_id",
    'SIGN_NAME': "绿行积分",
    'TEMPLATE_ID': "your_template_id"
}

# ========================================
# 华为云短信服务配置（待实现）
# ========================================
HUAWEI = {
    'APP_KEY': "your_app_key",
    'APP_SECRET': "your_app_secret",
    'APP_SECRET': "your_app_secret",
    'SIGNATURE_NAME': "绿行积分",
    'TEMPLATE_ID': "your_template_id"
}

# ========================================
# 使用说明
# ========================================

# 1. 选择服务商
#    - 开发/测试：使用 'debug' 模式，验证码打印在控制台
#    - 个人开发者：推荐 'ihuyi'（互亿无线），门槛低，价格便宜
#    - 企业用户：可以选择 'aliyun'、'ronglian' 或 'tencent'

# 2. 配置对应的参数
#    - 修改 SMS_PROVIDER 为您选择的服务商
#    - 填写对应的配置信息（如API ID、API Key等）
#    - 保存文件并重启应用

# 3. 各服务商官网和注册说明
#    - 互亿无线：https://www.ihuyi.com/（最低充值5元，适合个人开发者）
#    - 容联云通讯：https://www.yuntongxun.com/（需要实名认证）
#    - 阿里云短信：https://dysms.console.aliyun.com/（需要企业认证或个人资质）
#    - 腾讯云短信：https://cloud.tencent.com/product/sms（需要实名认证）
#    - 华为云短信：https://www.huaweicloud.com/product/msgsms.html（需要实名认证）

# 4. 切换服务商示例
#    # 使用互亿无线
#    SMS_PROVIDER = 'ihuyi'
#    IHUYI['API_ID'] = 'your_actual_api_id'
#    IHUYI['API_KEY'] = 'your_actual_api_key'
#
#    # 使用容联云
#    SMS_PROVIDER = 'ronglian'
#    RONGLIAN['ACCOUNT_SID'] = 'your_actual_sid'
#    RONGLIAN['AUTH_TOKEN'] = 'your_actual_token'
#    RONGLIAN['APP_ID'] = 'your_actual_app_id'

# 5. 安全建议
#    - 不要将配置文件提交到代码仓库
#    - 生产环境建议使用环境变量
#    - 定期更换API密钥

# 6. 测试方法
#    from utils.sms_manager import send_verification_code
#    success, message = send_verification_code('13800138000', '123456')
#    print(f"发送结果：{success}, {message}")