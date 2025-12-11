# 修改后的app.py（集成消费者自动启动）
import os
import subprocess
import time
import psutil
import redis
from flask import Flask
from apps import create_app

# ====================== Redis自动启动配置 ======================
REDIS_SERVER_PATH = "redis-server.exe"
REDIS_PORT = 6379

# ====================== 消费者自动启动配置 ======================
REDIS_CONFIG = {
    "host": "localhost",    # Redis服务器地址（本地填localhost）
    "port": 6379,           # Redis端口（默认6379，无需修改）
    "password": "",         # Redis密码（无密码则留空）
    "db": 0,                # Redis数据库编号（默认0，和消费者保持一致）
    "socket_timeout": 10    # 连接超时时间（和消费者保持一致）
}

# 2. Redis订阅频道名（和消费者脚本中的CHANNEL_NAME完全一致）
CHANNEL_NAME = "trip_points_events"  # 积分事件频道名，必须和消费者里的一模一样


CONSUMER_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "consumer_trip_points.py")
CONSUMER_PROCESS_NAME = "python.exe"  # Windows下消费者进程名


def is_redis_running():
    """检测Redis是否运行"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == REDIS_PORT and conn.status == "LISTENING":
                return True
        result = subprocess.run(["redis-cli.exe", "ping"], capture_output=True, text=True, timeout=3, shell=True)
        return "PONG" in result.stdout
    except:
        return False


def start_redis_windows():
    """自动启动Redis"""
    if is_redis_running():
        print("[Redis] 已运行 ✅")
        return True
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        subprocess.Popen([REDIS_SERVER_PATH], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True)
        time.sleep(3)
        return is_redis_running()
    except Exception as e:
        print(f"[Redis启动失败] {e}")
        return False


def is_consumer_running():
    """精准匹配消费者进程"""
    try:
        target_script = "consumer_trip_points.py"
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["name"] not in ["python.exe", "pythonw.exe"]:
                    continue
                cmdline = proc.info["cmdline"] or []
                cmdline_str = " ".join([str(c) for c in cmdline]).lower()
                if target_script.lower() in cmdline_str:
                    print(f"[消费者进程检测] 找到运行中的消费者：PID={proc.info['pid']}")
                    return True
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
        return False
    except Exception as e:
        print(f"[检测消费者进程异常] {e}")
        return False


def start_consumer_windows():
    """启动消费者（无日志文件依赖，通过Redis订阅者检测是否启动）"""
    if is_consumer_running():
        print("[消费者] 启动成功 ✅")
        return True
    try:
        print("[消费者] 启动中...")
        # 恢复隐藏窗口（常驻进程不需要显示窗口）
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        # 启动进程（不捕获输出，也不生成日志文件）
        subprocess.Popen(
            ["python", CONSUMER_SCRIPT_PATH],
            startupinfo=startupinfo,
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # 避免被Flask终止
        )

        # 等待1秒，让进程完成启动
        time.sleep(1)

        # 第一步：检测进程（原有逻辑）
        if is_consumer_running():
            print("[消费者] 启动成功 ✅")
            return True
        # 第二步：通过Redis检测订阅者（替代日志文件）
        else:
            try:
                # 连接Redis，查看目标频道的订阅者数量
                redis_conn = redis.Redis(**REDIS_CONFIG)
                # 获取频道订阅者信息
                pubsub_num = redis_conn.pubsub_numsub(CHANNEL_NAME)
                # pubsub_num返回格式：[(b'trip_points_events', 订阅者数量), ...]
                subscriber_count = pubsub_num[0][1] if pubsub_num else 0
                if subscriber_count > 0:
                    print("[消费者] 进程检测失败，但Redis检测到订阅者 ✅（忽略即可）")
                    return True
            except Exception as e:
                print(f"[Redis检测订阅者异常] {e}")

        # 所有检测都失败
        print("[消费者] 启动失败 ❌，请手动启动消费者脚本")
        return False
    except Exception as e:
        print(f"[消费者启动异常] {e}")
        return False

# ====================== 启动Flask ======================
if __name__ == '__main__':
    # 1. 启动Redis
    start_redis_windows()
    # 2. 启动积分消费者
    start_consumer_windows()
    # 3. 启动Flask Web服务
    app = create_app()
    app.run(debug=True, port=5000)
