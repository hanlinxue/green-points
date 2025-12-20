"""
阿里云短信服务工具类
用于发送短信验证码
"""

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525.QuerySendDetailsRequest
import json
from .sms_config import (
    ACCESS_KEY_ID,
    ACCESS_KEY_SECRET,
    SIGN_NAME,
    TEMPLATE_CODE,
    REGION_ID,
    BUSINESS_NAME
)


class AliyunSMS:
    """阿里云短信服务类"""

    def __init__(self):
        """初始化阿里云客户端"""
        # 初始化 AcsClient
        self.client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION_ID)
        self.business_name = BUSINESS_NAME

    def send_sms(self, phone_numbers, template_param=None, out_id=None):
        """
        发送短信

        Args:
            phone_numbers (str): 手机号，多个手机号用逗号分隔
            template_param (dict): 模板变量，例如 {'code': '123456'}
            out_id (str): 外部流水号，可选

        Returns:
            dict: 发送结果
        """
        # 创建请求
        request = SendSmsRequest.SendSmsRequest()

        # 设置请求参数
        request.set_PhoneNumbers(phone_numbers)
        request.set_SignName(SIGN_NAME)
        request.set_TemplateCode(TEMPLATE_CODE)

        # 设置模板参数
        if template_param:
            request.set_TemplateParam(json.dumps(template_param))

        # 设置外部流水号（可选）
        if out_id:
            request.set_OutId(out_id)

        try:
            # 发送请求
            response = self.client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))

            # 打印发送结果（调试用）
            print(f"[{self.business_name}] 短信发送结果：")
            print(f"  - 手机号：{phone_numbers}")
            print(f"  - 发送状态：{'成功' if result.get('Code') == 'OK' else '失败'}")
            print(f"  - 返回码：{result.get('Code')}")
            print(f"  - 返回消息：{result.get('Message')}")
            print(f"  - 请求ID：{result.get('RequestId')}")
            print(f"  - 业务流水号：{result.get('BizId')}")

            return result

        except ServerException as e:
            print(f"[{self.business_name}] 短信发送失败（服务器异常）：")
            print(f"  - HTTP状态码：{e.get_http_status()}")
            print(f"  - 错误码：{e.get_error_code()}")
            print(f"  - 错误消息：{e.get_error_msg()}")
            return {
                "Code": e.get_error_code(),
                "Message": e.get_error_msg(),
                "RequestId": None,
                "BizId": None
            }
        except Exception as e:
            print(f"[{self.business_name}] 短信发送失败（其他异常）：{str(e)}")
            return {
                "Code": "UNKNOWN_ERROR",
                "Message": str(e),
                "RequestId": None,
                "BizId": None
            }

    def send_verification_code(self, phone_number, code):
        """
        发送验证码短信

        Args:
            phone_number (str): 手机号
            code (str): 验证码

        Returns:
            tuple: (success: bool, message: str)
        """
        # 构造模板参数
        template_param = {
            "code": code
        }

        # 生成外部流水号（用于追踪）
        import time
        import uuid
        out_id = f"{self.business_name}_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # 发送短信
        result = self.send_sms(phone_number, template_param, out_id)

        # 判断是否发送成功
        if result.get('Code') == 'OK':
            return True, "验证码发送成功"
        else:
            # 错误码对照表
            error_messages = {
                "isv.BUSINESS_LIMIT_CONTROL": "短信发送频率超限，请稍后再试",
                "isv.DAY_LIMIT_CONTROL": "今日短信发送次数已达上限",
                "isv.MOBILE_NUMBER_ILLEGAL": "手机号格式不正确",
                "isv.AMOUNT_NOT_ENOUGH": "账户余额不足",
                "isv.SMS_TEMPLATE_ILLEGAL": "短信模板不合法",
                "isv.SMS_SIGN_ILLEGAL": "短信签名不合法",
                "isv.INVALID_PARAMETERS": "参数错误",
                "isv.PRODUCT_UNSUBSCRIBE": "产品未开通",
                "isv.PRODUCT_UNSUBSCRIBED": "服务未开通",
                "isp.RAM_PERMISSION_DENY": "RAM权限不足",
                "Forbidden.Access": "访问被禁止，请检查签名和模板状态",
                "InvalidParameter": "参数错误",
                "InvalidDayuStatus.Malformed": "账户状态异常",
                "InvalidSendStatus": "短信发送状态异常",
                "InvalidTemplateCode.Malformed": "模板格式错误",
                "InvalidPhoneNumber.Malformed": "手机号格式错误",
                "MissingParameter": "缺少参数",
                "Sdk.NumberTooMany": "手机号数量过多",
                "UnsupportedOperation": "不支持的操作"
            }

            error_code = result.get('Code', 'UNKNOWN_ERROR')
            error_msg = error_messages.get(error_code, result.get('Message', '未知错误'))

            return False, f"短信发送失败：{error_msg}（错误码：{error_code}）"

    def query_send_details(self, phone_number, date, biz_id=None, page_size=10, current_page=1):
        """
        查询短信发送记录

        Args:
            phone_number (str): 手机号
            date (str): 日期，格式为yyyyMMdd
            biz_id (str): 业务流水号，可选
            page_size (int): 每页显示数量，默认10
            current_page (int): 当前页码，默认1

        Returns:
            dict: 查询结果
        """
        request = QuerySendDetailsRequest.QuerySendDetailsRequest()

        # 设置查询参数
        request.set_PhoneNumbers(phone_number)
        request.set_SendDate(date)
        request.set_PageSize(page_size)
        request.set_CurrentPage(current_page)

        if biz_id:
            request.set_BizId(biz_id)

        try:
            response = self.client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))

            print(f"[{self.business_name}] 短信记录查询结果：")
            print(f"  - 手机号：{phone_number}")
            print(f"  - 查询日期：{date}")
            print(f"  - 查询状态：{'成功' if result.get('Code') == 'OK' else '失败'}")
            print(f"  - 返回码：{result.get('Code')}")

            return result

        except Exception as e:
            print(f"[{self.business_name}] 查询短信记录失败：{str(e)}")
            return {
                "Code": "ERROR",
                "Message": str(e)
            }


# 创建全局短信服务实例
sms_service = AliyunSMS()


# 便捷函数
def send_verification_code(phone_number, code):
    """
    发送验证码（便捷函数）

    Args:
        phone_number (str): 手机号
        code (str): 验证码

    Returns:
        tuple: (success: bool, message: str)
    """
    return sms_service.send_verification_code(phone_number, code)