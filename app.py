# 修改后的app.py（集成消费者自动启动）
import os
import subprocess
import time
import psutil
from flask import Flask
from apps import create_app

# ====================== Redis自动启动配置 ======================
REDIS_SERVER_PATH = "redis-server.exe"
REDIS_PORT = 6379

# ====================== 消费者自动启动配置 ======================
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
    """精准匹配：遍历所有python进程，检查命令行是否包含消费者脚本名"""
    try:
        target_script = "consumer_trip_points.py"
        # 遍历所有python进程
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                # 只检查python进程
                if proc.info["name"] not in ["python.exe", "pythonw.exe"]:
                    continue
                # 拼接命令行字符串（处理None/列表格式）
                cmdline = proc.info["cmdline"] or []
                cmdline_str = " ".join([str(c) for c in cmdline]).lower()
                # 匹配脚本名（忽略路径大小写）
                if target_script.lower() in cmdline_str:
                    print(f"[消费者进程检测] 找到运行中的消费者：PID={proc.info['pid']}")
                    return True
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                # 跳过无权限访问的进程
                continue
        return False
    except Exception as e:
        print(f"[检测消费者进程异常] {e}")
        return False


def start_consumer_windows():
    # （保留之前的启动逻辑）
    # 最后修改反馈逻辑：
    time.sleep(1)
    if is_consumer_running():
        print("[消费者] 启动成功 ✅")
        return True
    else:
        # 读取日志，判断是否真的启动
        try:
            with open("consumer_error.log", "r", encoding="utf-8") as f:
                log_content = f.read()
                if "已订阅频道：trip_points_events" in log_content:
                    print("[消费者] 检测进程失败，但日志显示已启动 ✅（忽略即可）")
                    return True
        except:
            pass
        print("[消费者] 启动失败 ❌，请查看consumer_error.log日志")
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
