# consumer_trip_points.py - 最终版积分消费者（独立运行+自动启动Redis）
import sys
import os
import json
import time
import redis
import psutil
import subprocess
from datetime import datetime

# ====================== 1. 项目路径配置（必加！） ======================
# 将项目根目录加入Python路径（确保能导入apps、exts等模块）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# ====================== 2. Redis配置+自动启动（消费者独立用） ======================
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "password": "",
    "db": 0,
    "socket_timeout": 10
}
REDIS_SERVER_PATH = "redis-server.exe"
CHANNEL_NAME = "trip_points_events"


def is_redis_running():
    """消费者独立检测Redis状态"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == REDIS_CONFIG["port"] and conn.status == "LISTENING":
                return True
        result = subprocess.run(["redis-cli.exe", "ping"], capture_output=True, text=True, timeout=3, shell=True)
        return "PONG" in result.stdout
    except:
        return False


def start_redis_for_consumer():
    """消费者启动前自动启动Redis"""
    if is_redis_running():
        print(f"[{datetime.now()}] [消费者] Redis已运行 ", flush=True)
        return True
    try:
        print(f"[{datetime.now()}] [消费者] 启动Redis...", flush=True)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        subprocess.Popen([REDIS_SERVER_PATH], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True)
        time.sleep(3)
        if is_redis_running():
            print(f"[{datetime.now()}] [消费者] Redis启动成功 ", flush=True)
            return True
        else:
            print(f"[{datetime.now()}] [消费者] Redis启动失败 ，请手动启动！", flush=True)
            return False
    except Exception as e:
        print(f"[{datetime.now()}] [消费者] Redis启动异常：{e}", flush=True)
        return False


# ====================== 3. 加载Flask上下文（完整初始化） ======================
try:
    from apps import create_app
    from exts import db
    from apps.users.models import User, PointsFlow
    from apps.administrators.models import PointRule

    # 创建app并初始化上下文（关键！执行init_exts）
    app = create_app()
    app.app_context().push()
    print(f"[{datetime.now()}] [消费者] Flask上下文加载成功 ", flush=True)
except Exception as e:
    print(f"[{datetime.now()}] [消费者] 上下文加载失败 ：{e}", flush=True)
    sys.exit(1)


# ====================== 4. 核心积分发放函数（确保能进入） ======================
def consume_trip_points():
    """积分发放核心函数（现在能正常进入）"""
    # 前置：启动Redis
    if not start_redis_for_consumer():
        sys.exit(1)

    # 连接Redis
    redis_conn = None
    try:
        redis_conn = redis.Redis(**REDIS_CONFIG)
        redis_conn.ping()
        print(f"[{datetime.now()}] [消费者] Redis连接成功 ", flush=True)
    except Exception as e:
        print(f"[{datetime.now()}] [消费者] Redis连接失败 ：{e}", flush=True)
        sys.exit(1)

    # 订阅频道
    pubsub = redis_conn.pubsub()
    pubsub.subscribe(CHANNEL_NAME)
    print(f"[{datetime.now()}] [消费者] 已订阅频道：{CHANNEL_NAME}，等待事件...\n", flush=True)

    # 阻塞监听（确保能进入循环）
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                print(f"[{datetime.now()}] [消费者] 收到事件！开始处理...", flush=True)  # 验证是否进入函数
                # ========== 解析事件 ==========
                data = message["data"].decode("utf-8")
                event_data = json.loads(data)
                if event_data["event_type"] != "TripApprovedEvent":
                    continue

                trip_info = event_data["data"]
                username = trip_info["username"]
                trip_mode = trip_info["mode"]
                distance = trip_info["distance"]
                trip_id = trip_info["trip_id"]

                # ========== 计算积分 ==========
                rule = PointRule.query.filter_by(trip_mode=trip_mode).first()
                if not rule:
                    print(f"[{datetime.now()}] [消费者] 无{trip_mode}积分规则", flush=True)
                    continue

                carbon_reduction = distance * rule.carbon_reduction_coeff
                add_points = int(round(carbon_reduction * rule.point_exchange_coeff, 0))
                print("1")
                print(add_points)
                if add_points <= 0:
                    print(f"[{datetime.now()}] [消费者] 积分≤0：{add_points}", flush=True)
                    continue

                # ========== 更新用户积分 ==========
                # ========== 更新用户积分 ==========
                user = User.query.filter_by(username=username).first()
                if not user:
                    print(f"[{datetime.now()}] [消费者] 用户{username}不存在 ", flush=True)
                    continue

                # 验证初始值
                print(f"[{datetime.now()}] [消费者] 更新前 → now={user.now_points}，all={user.all_points}", flush=True)

                old_points = user.now_points
                # 显式更新，避免 += 隐性问题
                user.now_points = user.now_points + add_points
                user.all_points = user.all_points + add_points

                # 验证更新后的值
                print(f"[{datetime.now()}] [消费者] 更新后 → now={user.now_points}，all={user.all_points}", flush=True)

                # ========== 创建积分流水记录 ==========
                points_flow = PointsFlow(
                    username=username,
                    change_type="获得",
                    reason="出行",
                    points=add_points,
                    balance=user.now_points,
                    # 出行场景的字段
                    goods_id=None,
                    goods_name=None,
                    exchange_status=None
                )
                db.session.add(points_flow)

                # 提交事务
                db.session.commit()
                print(
                    f"[{datetime.now()}] [消费者] 积分发放成功！{username}：now={old_points}→{user.now_points}（+{add_points}），all={user.all_points - add_points}→{user.all_points}（+{add_points}）",
                    flush=True)

    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] [消费者] 手动停止", flush=True)
    except Exception as e:
        print(f"[{datetime.now()}] [消费者] 处理异常 ：{e}", flush=True)
        db.session.rollback()
    finally:
        pubsub.unsubscribe(CHANNEL_NAME)
        redis_conn.close()
        print(f"[{datetime.now()}] [消费者] 资源已释放", flush=True)


# ====================== 5. 启动消费者 ======================
if __name__ == "__main__":
    print("=" * 70, flush=True)
    print(f"[{datetime.now()}] 积分消费者启动", flush=True)
    print("=" * 70, flush=True)
    consume_trip_points()  # 确保调用核心函数
