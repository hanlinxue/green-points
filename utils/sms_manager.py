"""
短信服务管理器
支持多个短信服务提供商，方便切换和扩展
"""

import importlib
import json
from typing import Dict, Tuple, Optional
from abc import ABC, abstractmethod


class SMSProvider(ABC):
    """短信提供商抽象基类"""

    @abstractmethod
    def send_verification_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """
        发送验证码

        Args:
            phone_number: 手机号
            code: 验证码

        Returns:
            tuple: (success: bool, message: str)
        """
        pass


class DebugSMS(SMSProvider):
    """调试模式短信服务（仅打印到控制台）"""

    def send_verification_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """发送验证码到控制台"""
        print(f"[调试模式] 短信验证码")
        print(f"手机号：{phone_number}")
        print(f"验证码：{code}（5分钟内有效）")
        return True, "验证码已发送（开发模式）"


class IhuyiSMS(SMSProvider):
    """互亿无线短信服务"""

    def __init__(self):
        self.api_id = None
        self.api_key = None

    def configure(self, api_id: str, api_key: str):
        """配置互亿无线参数"""
        self.api_id = api_id
        self.api_key = api_key

    def send_verification_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """发送验证码"""
        if not self.api_id or not self.api_key:
            return False, "互亿无线未配置"

        import urllib.request
        import urllib.parse

        url = 'http://106.ihuyi.com/webservice/sms.php?method=Submit'
        data = {
            'account': self.api_id,
            'password': self.api_key,
            'mobile': phone_number,
            'content': f'您的验证码是：{code}。请不要把验证码泄露给其他人。',
            'format': 'json'
        }

        try:
            req = urllib.request.Request(url, urllib.parse.urlencode(data).encode('utf-8'))
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode('utf-8'))

            if result.get('code') == 2:
                return True, "验证码发送成功"
            else:
                return False, f"发送失败：{result.get('msg', '未知错误')}"
        except Exception as e:
            return False, f"发送异常：{str(e)}"


class RonglianSMS(SMSProvider):
    """容联云通讯短信服务"""

    def __init__(self):
        self.acc_id = None
        self.acc_token = None
        self.app_id = None
        self.template_id = None

    def configure(self, acc_id: str, acc_token: str, app_id: str, template_id: str = 1):
        """配置容联云参数"""
        self.acc_id = acc_id
        self.acc_token = acc_token
        self.app_id = app_id
        self.template_id = template_id

    def send_verification_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """发送验证码"""
        if not all([self.acc_id, self.acc_token, self.app_id]):
            return False, "容联云通讯未配置"

        try:
            # 动态导入容联SDK
            from ronglian_sms_sdk import SmsSDK

            sdk = SmsSDK(self.acc_id, self.acc_token, self.app_id)
            resp = sdk.sendMessage(self.template_id, phone_number, (code, '5'))

            if resp.get('statusCode') == '000000':
                return True, "验证码发送成功"
            else:
                return False, f"发送失败：{resp.get('statusMsg', '未知错误')}"
        except ImportError:
            return False, "请安装容联SDK：pip install ronglian_sms_sdk"
        except Exception as e:
            return False, f"发送异常：{str(e)}"


class SMSManager:
    """短信服务管理器"""

    def __init__(self, provider: str = 'debug'):
        """
        初始化短信管理器

        Args:
            provider: 短信服务商 ('debug', 'aliyun', 'ihuyi', 'ronglian')
        """
        self.provider = provider
        self.client = self._get_provider(provider)

    def _get_provider(self, provider: str) -> SMSProvider:
        """获取短信服务提供商实例"""
        providers = {
            'debug': DebugSMS(),
            'ihuyi': IhuyiSMS(),
            'ronglian': RonglianSMS(),
            'aliyun': None  # 阿里云在sms_service.py中实现
        }

        if provider == 'aliyun':
            try:
                from .sms_service import AliyunSMS
                return AliyunSMS()
            except Exception as e:
                print(f"阿里云短信服务加载失败：{str(e)}，使用调试模式")
                return DebugSMS()

        provider_instance = providers.get(provider)
        if provider_instance is None:
            print(f"未知的短信服务商：{provider}，使用调试模式")
            return DebugSMS()

        return provider_instance

    def send_verification_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """
        发送验证码

        Args:
            phone_number: 手机号
            code: 验证码

        Returns:
            tuple: (success: bool, message: str)
        """
        return self.client.send_verification_code(phone_number, code)

    def configure_provider(self, **kwargs):
        """
        配置短信服务提供商参数

        Args:
            **kwargs: 配置参数
        """
        if hasattr(self.client, 'configure'):
            self.client.configure(**kwargs)


# 全局短信管理器实例
_sms_manager = None


def get_sms_manager(provider: Optional[str] = None) -> SMSManager:
    """
    获取短信管理器实例（单例模式）

    Args:
        provider: 短信服务商，如果为None则使用配置文件中的默认值

    Returns:
        SMSManager: 短信管理器实例
    """
    global _sms_manager

    if _sms_manager is None or provider is not None:
        # 尝试从配置文件读取默认提供商
        if provider is None:
            try:
                from .sms_config import SMS_PROVIDER
                provider = SMS_PROVIDER
            except:
                provider = 'debug'

        _sms_manager = SMSManager(provider)

    return _sms_manager


def send_verification_code(phone_number: str, code: str) -> Tuple[bool, str]:
    """
    发送验证码（便捷函数）

    Args:
        phone_number: 手机号
        code: 验证码

    Returns:
        tuple: (success: bool, message: str)
    """
    manager = get_sms_manager()
    return manager.send_verification_code(phone_number, code)


# 配置示例
if __name__ == "__main__":
    # 使用调试模式
    sms = SMSManager('debug')
    success, message = sms.send_verification_code('13800138000', '123456')
    print(f"调试模式：{success}, {message}")

    # 配置互亿无线
    ihuyi = SMSManager('ihuyi')
    ihuyi.configure_provider(
        api_id='your_api_id',
        api_key='your_api_key'
    )
    # success, message = ihuyi.send_verification_code('13800138000', '123456')

    # 配置容联云
    ronglian = SMSManager('ronglian')
    ronglian.configure_provider(
        acc_id='your_acc_id',
        acc_token='your_acc_token',
        app_id='your_app_id',
        template_id=1
    )
    # success, message = ronglian.send_verification_code('13800138000', '123456')