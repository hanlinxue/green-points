# green-points（绿色积分/绿色出行积分平台）

一个面向课程实验的 Web 系统原型：将“绿色出行行为”转化为可量化的积分激励，并提供积分消费（兑换商品）、商户结算（提现）与运营审核（管理员）等配套能力。

- 角色：用户 / 商户 / 管理员
- 技术栈：Flask + SQLAlchemy + MySQL + Redis
- 运行方式：直接 `python app.py`（Windows 下会自动尝试启动 Redis 与积分消费者）

---

## 1. 功能概览

### 1.1 用户端
- 注册/登录
- 提交出行记录（待审核）
- 查看积分余额与积分流水（可追溯）
- 积分商城：浏览商品、兑换下单、扣减积分
- 地址/个人信息维护（如项目已实现）

### 1.2 商户端
- 商户登录
- 商品管理（上架/下架/编辑）
- 订单管理（查看兑换订单）
- 提现申请/查询（等待管理员审核）

### 1.3 管理员端
- 管理员登录
- 审核用户出行记录（通过/拒绝）
- 审核商户提现（通过/拒绝，留痕）
- 运营配置：汇率/规则等初始化脚本（如 `init_exchange_rates.py`）

---

## 2. 目录结构（核心）

```text
green_points/
├─ app.py                       # 入口：启动 Flask +（Windows）启动 Redis + 启动积分消费者
├─ consumer_trip_points.py       # 积分消费者：监听 Redis 队列/订阅，计算并写入积分
├─ settings.py                  # 配置：数据库连接等（请按本机修改）
├─ exts/                        # 扩展：SQLAlchemy / Migrate 初始化
├─ apps/
│  ├─ __init__.py               # create_app：注册蓝图
│  ├─ users/                    # 用户模块（models/view）
│  ├─ merchants/                # 商户模块（models/view）
│  └─ administrators/           # 管理员模块（models/view）
├─ migrations/                  # 数据库迁移
├─ templates/                   # 模板页面（Jinja2）
├─ static/                      # 静态资源（css/js/img）
├─ create_admin.py              # 初始化管理员账号（默认 admin / 123456）
├─ create_table_and_data.py     # 建表/插入默认汇率示例
├─ create_exchange_rate_table.sql
└─ insert_goods_final.py        # 初始化商品数据（如项目包含）
```

---

## 3. 环境依赖

- Python 3.9+（建议 3.10/3.11）
- MySQL 8.x（或 MariaDB）
- Redis 6.x+
- 主要 Python 包（根据源码导入整理）：
  - flask, flask-sqlalchemy, flask-migrate
  - sqlalchemy, pymysql
  - redis
  - werkzeug
  - psutil（app.py 用于检测/管理进程）
  - requests（部分测试脚本用）

> 本项目未提供 requirements.txt 时，可手动安装（见下方快速开始）。

---

## 4. 快速开始（Windows 推荐）

### 4.1 克隆并进入目录
```bash
git clone https://github.com/hanlinxue/green-points.git
cd green-points
```

### 4.2 创建虚拟环境并安装依赖
```bash
python -m venv .venv
.venv\Scripts\activate

pip install -U pip
pip install flask flask-sqlalchemy flask-migrate sqlalchemy pymysql redis werkzeug psutil requests
```

### 4.3 配置数据库连接
打开 `settings.py`，修改为你本机 MySQL 用户名/密码/库名，例如：
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:你的密码@127.0.0.1:3306/green_points"
```

在 MySQL 里创建数据库：
```sql
CREATE DATABASE IF NOT EXISTS green_points DEFAULT CHARSET utf8mb4;
```

### 4.4 初始化数据库（两种方式选其一）

**方式A：使用迁移（推荐）**
```bash
# 在项目根目录执行（确保能 import 到 apps.create_app）
flask --app app.py db upgrade
```

**方式B：运行项目自带初始化脚本（示例）**
```bash
python create_table_and_data.py
python create_admin.py
# 如需要初始化商户/商品/汇率等
python create_merchant_test.py
python init_exchange_rates.py
python insert_goods_final.py
```

### 4.5 启动项目
```bash
python app.py
```

- 默认 Web 服务：`http://127.0.0.1:5000/`
- 蓝图前缀：
  - 用户端：`/user/...`
  - 商户端：`/merchant/...`
  - 管理员端：`/admin/...`

> 说明：`app.py` 中包含 Windows 下自动启动 Redis 与消费者脚本的逻辑。若你已自行安装并启动 Redis，也可注释/关闭自动启动部分。

---

## 5. 默认账号（如已初始化）

- 管理员：`admin / 123456`（由 `create_admin.py` 创建）
- 测试商户：`Mtest_merchant / 123456`（由 `create_merchant_test.py` 创建，若脚本存在且已执行）
- 用户账号：可通过页面注册创建（或按项目脚本初始化）

---

## 6. 常见问题（FAQ）

### Q1：启动后访问报数据库连接失败？
- 检查 `settings.py` 的 `SQLALCHEMY_DATABASE_URI` 是否已改成你本机账号密码
- 确认 MySQL 服务已启动、数据库 `green_points` 已创建
- 确认已安装 `pymysql`

### Q2：Redis 相关报错？
- 确认 Redis 已启动，默认端口 6379 可访问
- Windows 下如果没安装 Redis，可用 Docker：
  ```bash
  docker run -d -p 6379:6379 --name redis redis:6
  ```

### Q3：会话经常失效？
- 当前 `create_app` 中 `SECRET_KEY = os.urandom(24)` 每次重启都会变化，重启后旧会话会失效。可以改成固定值（仅实验环境建议）。

---

## 7. 许可证
本项目许可证见 `LICENSE` 文件。

---

## 8. 贡献与说明
该项目用于课程实验原型展示，欢迎在 Issues 中反馈问题或提交 PR（按课程要求执行）。
