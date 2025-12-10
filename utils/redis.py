# -*- coding: utf-8 -*-
"""Redis连接工具：Windows适配，提供统一连接函数"""
import redis
from typing import Optional

# ====================== Redis配置（Windows版）======================
REDIS_CONFIG = {
    "host": "localhost",  # 本地Redis，无需修改
    "port": 6379,  # 默认端口，和自动启动的Redis一致
    "password": "",  # 无密码留空，有则填实际密码
    "db": 0,  # 数据库编号，新手不用改
    "socket_timeout": 5,  # 连接超时5秒
    "decode_responses": False  # 保持字节流，避免中文乱码
}


def get_redis_conn() -> Optional[redis.Redis]:
    """
    获取Redis连接对象
    返回：Redis连接对象 | None（连接失败）
    """
    try:
        # 创建Redis连接
        conn = redis.Redis(**REDIS_CONFIG)
        # 测试连接（执行ping命令）
        conn.ping()
        print("[Redis工具] 连接成功 ✅")
        return conn
    except Exception as e:
        print(f"[Redis工具] 连接失败 ❌：{str(e)}")
        return None


# 测试代码：直接运行该文件可验证连接
if __name__ == "__main__":
    get_redis_conn()
