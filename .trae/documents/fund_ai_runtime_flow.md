# Fund AI 项目运行流程说明

## 1. 项目结构

```
fundai/
├── fund-marketing-platform/
│   ├── backend/          # 后端代码
│   │   ├── app.py       # 主应用入口
│   │   ├── config.py    # 配置文件
│   │   ├── models.py    # 数据库模型
│   │   ├── routes/      # API路由
│   │   ├── services/    # 外部服务
│   │   ├── data/        # 数据库文件
│   │   └── venv/        # 虚拟环境
│   ├── frontend/        # 前端代码
│   │   └── index.html   # 前端单页面
│   ├── manage.sh        # 服务管理脚本
│   └── README.md        # 项目说明
└── .gitignore           # Git忽略文件
```

## 2. 运行流程

### 方式一：使用管理脚本（推荐）

#### 步骤1：进入项目目录
```bash
cd /Users/xiaojunwei/Workspace/fundai/fund-marketing-platform
```

#### 步骤2：启动服务
```bash
bash manage.sh start
```

**脚本执行流程**:
1. 进入 backend 目录
2. 尝试激活虚拟环境 (`venv/bin/activate`)
3. 在后台运行 `python3 app.py`
4. 等待2秒
5. 调用健康检查接口 `/api/health` 验证服务是否启动成功
6. 如果成功，显示服务访问地址

#### 步骤3：验证服务
```bash
bash manage.sh test
```

#### 步骤4：停止服务
```bash
bash manage.sh stop
```

---

### 方式二：手动运行（开发调试）

#### 步骤1：进入后端目录
```bash
cd /Users/xiaojunwei/Workspace/fundai/fund-marketing-platform/backend
```

#### 步骤2：激活虚拟环境
```bash
source venv/bin/activate
```

#### 步骤3：启动应用
```bash
python app.py
```

**应用启动流程**:
1. 创建 Flask 应用实例
2. 配置 CORS 支持
3. 加载配置 (从 `config.py`)
4. 初始化数据库 (SQLAlchemy)
5. 创建数据库表（如果不存在）
6. 初始化种子数据（如果数据库为空）
7. 注册所有 Blueprint 路由
8. 启动开发服务器，监听 `0.0.0.0:5002`

#### 步骤4：访问服务
打开浏览器访问：http://localhost:5002

---

## 3. 内部数据流

### 3.1 前端访问流程

```
用户浏览器
    ↓
http://localhost:5002/
    ↓
Flask 路由 (app.py:49)
    ↓
返回 index.html (静态文件)
    ↓
前端加载 Chart.js 和 Font Awesome CDN
    ↓
显示 Fund AI 界面
```

### 3.2 API 请求流程

```
前端 JavaScript
    ↓
fetch('/api/health')
    ↓
Flask Blueprint 路由
    ↓
路由处理函数
    ↓
业务逻辑处理
    ↓
可能调用外部服务:
  - EastmoneyService (获取基金数据)
  - MiniMaxService (生成文案)
    ↓
返回 JSON 响应
    ↓
前端处理响应并更新界面
```

### 3.3 外部服务调用

#### 基金数据获取
```
EastmoneyService
    ↓
访问 fund.eastmoney.com (HTTP请求)
    ↓
解析HTML/JavaScript代码
    ↓
提取基金数据
    ↓
缓存到内存 (1小时有效期)
    ↓
返回格式化的JSON数据
```

#### AI文案生成
```
MiniMaxService
    ↓
访问 api.minimax.chat (HTTPS POST)
    ↓
发送提示词和基金信息
    ↓
等待AI生成文案
    ↓
解析响应
    ↓
返回生成的文案
    ↓
(如果失败) 回退到模板生成
```

---

## 4. 数据库流程

### 4.1 启动时初始化
```
应用启动
    ↓
db.init_app(app)
    ↓
创建数据库表
    ↓
检查用户表是否为空
    ↓
如果为空:
  - seed_users() - 创建初始用户
  - seed_audit_data() - 创建审核数据
  - seed_team_members() - 创建团队成员
```

### 4.2 运行时数据库操作
```
API请求
    ↓
使用 SQLAlchemy ORM
    ↓
查询/写入 SQLite 数据库
    ↓
数据库文件: backend/data/fund_marketing.db
```

---

## 5. 端口和URL

### 本地端口
| 端口 | 用途 |
|------|------|
| 5002 | Flask Web服务 |

### 访问URL

| URL | 说明 |
|-----|------|
| http://localhost:5002/ | 前端页面 |
| http://localhost:5002/api/health | 健康检查 |
| http://localhost:5002/api/fund/list | 基金列表 |
| http://localhost:5002/api/fund/search | 基金搜索 |
| http://localhost:5002/api/copy/generate | 文案生成 |
| http://localhost:5002/api/library/list | 素材库 |
| http://localhost:5002/api/team/members | 团队成员 |
| http://localhost:5002/api/auth/login | 用户登录 |

### 外部API

| 服务 | URL |
|------|-----|
| 东方财富 | https://fund.eastmoney.com/* |
| MiniMax | https://api.minimax.chat/* |
| Chart.js CDN | https://cdn.bootcdn.net/* |
| Font Awesome CDN | https://cdnjs.cloudflare.com/* |

---

## 6. 环境变量

### 配置文件位置
`fund-marketing-platform/backend/config.py`

### 主要配置项
| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| PORT | 5002 | 服务端口 |
| DEBUG | True | 调试模式 |
| SECRET_KEY | (随机密钥) | Flask密钥 |
| MINIMAX_TOKEN | (预配置) | MiniMax API密钥 |
| CACHE_DURATION | 3600 | 缓存时间(秒) |

---

## 7. 常见操作

### 重启服务
```bash
cd fund-marketing-platform
bash manage.sh stop
bash manage.sh start
```

### 查看服务日志
```bash
# 如果使用后台方式运行，查看终端7的输出
# 或检查终端历史记录
```

### 重置数据库
```bash
cd backend/data
rm fund_marketing.db
# 重启服务会自动重新创建数据库和种子数据
```

### 手动健康检查
```bash
curl http://localhost:5002/api/health
```

### 访问前端
直接在浏览器打开：http://localhost:5002

---

## 8. 故障排查

### 问题：服务无法启动
1. 检查端口是否被占用：`lsof -i :5002`
2. 检查虚拟环境是否存在：`ls -la backend/venv/`
3. 查看错误日志

### 问题：API返回500
1. 检查数据库文件权限
2. 检查外部API连接：`ping fund.eastmoney.com`
3. 检查MiniMax token是否有效

### 问题：前端无法加载
1. 检查服务是否运行：`curl http://localhost:5002`
2. 检查浏览器控制台错误
3. 检查CDN资源是否可访问