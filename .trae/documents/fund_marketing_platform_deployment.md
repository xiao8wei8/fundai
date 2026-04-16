# 海富通基金营销平台服务器部署文档

## 1. 环境准备

### 1.1 服务器要求
- **操作系统**: Linux (Ubuntu 20.04+ 或 CentOS 7+)
- **Python版本**: Python 3.12+
- **内存**: 至少 2GB
- **磁盘空间**: 至少 10GB
- **网络**: 可访问互联网（用于获取基金数据和AI服务）

### 1.2 系统环境配置

#### Ubuntu/Debian 系统
```bash
# 更新系统
apt update && apt upgrade -y

# 安装依赖
apt install -y python3 python3-venv python3-pip git nginx supervisor

# 安装构建依赖
apt install -y build-essential libssl-dev libffi-dev python3-dev
```

#### CentOS/RHEL 系统
```bash
# 更新系统
yum update -y

# 安装依赖
yum install -y python3 python3-venv python3-pip git nginx

# 安装构建依赖
yum install -y gcc gcc-c++ make openssl-devel libffi-devel python3-devel
```

## 2. 项目部署

### 2.1 克隆项目
```bash
# 创建项目目录
mkdir -p /opt/fund-marketing-platform
cd /opt/fund-marketing-platform

# 克隆代码
# 假设代码存储在Git仓库中
git clone <repository-url> .

# 或者直接复制代码
# cp -r /path/to/fund-marketing-platform/* .
```

### 2.2 配置环境变量
创建 `.env` 文件，配置敏感信息：

```bash
# 创建.env文件
cat > .env << EOF
# 系统密钥
SECRET_KEY=your_secure_secret_key

# MiniMax API密钥（可选）
MINIMAX_TOKEN=your_minimax_token

# 服务配置
PORT=5002
DEBUG=False
EOF
```

### 2.3 安装依赖
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 验证安装
pip list
```

### 2.4 初始化数据库
```bash
# 激活虚拟环境（如果未激活）
source venv/bin/activate

# 运行初始化脚本
python -c "
from app import app
from models import db
with app.app_context():
    db.create_all()
    from models import User
    if User.query.count() == 0:
        from routes.auth import seed_users
        from routes.audit import seed_audit_data
        from routes.team import seed_team_members
        seed_users()
        seed_audit_data()
        seed_team_members()
        print('=== Initial data seeded ===')
"
```

## 3. 服务配置

### 3.1 Nginx 配置
创建 Nginx 配置文件：

```bash
# 创建Nginx配置
cat > /etc/nginx/sites-available/fund-marketing-platform << EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件直接处理（可选）
    location /static/ {
        alias /opt/fund-marketing-platform/frontend/;
        expires 30d;
    }
    
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/fund-marketing-platform /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

### 3.2 Supervisor 配置
创建 Supervisor 配置文件，确保服务自动启动：

```bash
# 创建Supervisor配置
cat > /etc/supervisor/conf.d/fund-marketing-platform.conf << EOF
[program:fund-marketing-platform]
command=/opt/fund-marketing-platform/backend/venv/bin/python /opt/fund-marketing-platform/backend/app.py
directory=/opt/fund-marketing-platform/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/fund-marketing-platform.log
stderr_logfile=/var/log/fund-marketing-platform-error.log
environment=
    PATH="/opt/fund-marketing-platform/backend/venv/bin:%(ENV_PATH)s",
    MINIMAX_TOKEN="%(ENV_MINIMAX_TOKEN)s"
EOF

# 重新加载Supervisor
supervisorctl reread
supervisorctl update
supervisorctl start fund-marketing-platform

# 查看状态
supervisorctl status fund-marketing-platform
```

## 4. 安全配置

### 4.1 防火墙设置
```bash
# Ubuntu/Debian
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables-save > /etc/iptables/rules.v4

# CentOS/RHEL
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### 4.2 HTTPS 配置（推荐）
使用 Let's Encrypt 配置 HTTPS：

```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com

# 自动续期配置
crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

## 5. 监控和维护

### 5.1 日志管理
```bash
# 查看服务日志
tail -f /var/log/fund-marketing-platform.log

# 查看错误日志
tail -f /var/log/fund-marketing-platform-error.log

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 5.2 定期维护
创建维护脚本：

```bash
cat > /opt/fund-marketing-platform/maintenance.sh << EOF
#!/bin/bash

# 日志轮转
find /var/log -name "fund-marketing-platform*.log" -type f -exec truncate -s 0 {} 

# 清理缓存
rm -rf /opt/fund-marketing-platform/backend/__pycache__/

# 重启服务
supervisorctl restart fund-marketing-platform

echo "Maintenance completed at $(date)"
EOF

chmod +x /opt/fund-marketing-platform/maintenance.sh

# 添加到crontab
crontab -e
# 添加以下行（每天凌晨执行）
0 0 * * * /opt/fund-marketing-platform/maintenance.sh >> /var/log/maintenance.log 2>&1
```

## 6. 常见问题处理

### 6.1 服务启动失败
```bash
# 查看错误日志
tail -f /var/log/fund-marketing-platform-error.log

# 检查端口占用
netstat -tulpn | grep 5002

# 重启服务
supervisorctl restart fund-marketing-platform
```

### 6.2 数据库连接问题
```bash
# 检查数据库文件权限
chmod 644 /opt/fund-marketing-platform/backend/data/fund_marketing.db

# 检查数据库目录权限
chown -R www-data:www-data /opt/fund-marketing-platform/backend/data/
```

### 6.3 API 访问问题
```bash
# 测试健康检查接口
curl http://localhost:5002/api/health

# 检查网络连接
ping fund.eastmoney.com
ping api.minimax.chat

# 检查防火墙规则
iptables -L
```

## 7. 部署验证

### 7.1 功能验证
1. **访问前端**: `http://your-domain.com`
2. **健康检查**: `http://your-domain.com/api/health`
3. **基金数据**: `http://your-domain.com/api/fund/list`
4. **文案生成**: `POST http://your-domain.com/api/copy/generate`

### 7.2 性能测试
```bash
# 测试API响应时间
ab -n 100 -c 10 http://localhost:5002/api/health

# 测试并发性能
ab -n 1000 -c 50 http://localhost:5002/api/fund/search?q=163406
```

## 8. 扩展建议

### 8.1 负载均衡
如果流量较大，可配置多个实例并使用Nginx负载均衡：

```bash
# Nginx负载均衡配置
upstream fund_marketing {
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
    server 127.0.0.1:5004;
}

server {
    location / {
        proxy_pass http://fund_marketing;
        # 其他配置...
    }
}
```

### 8.2 数据库优化
对于生产环境，建议使用PostgreSQL或MySQL：

```bash
# 修改config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/fund_marketing'
# 或
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/fund_marketing'
```

### 8.3 缓存优化
使用Redis提高性能：

```bash
# 安装Redis
apt install redis-server

# 添加Redis缓存支持
pip install redis

# 在代码中使用Redis缓存
# 示例：替换内存缓存为Redis
```

## 9. 部署清单

- [ ] 服务器环境准备
- [ ] 项目代码部署
- [ ] 环境变量配置
- [ ] 依赖安装
- [ ] 数据库初始化
- [ ] Nginx配置
- [ ] Supervisor配置
- [ ] 防火墙设置
- [ ] HTTPS配置
- [ ] 服务启动
- [ ] 功能验证
- [ ] 性能测试
- [ ] 监控配置

## 10. 紧急联系人

| 角色 | 姓名 | 联系方式 | 职责 |
|------|------|----------|------|
| 系统管理员 | 管理员 | admin@example.com | 服务器维护 |
| 开发人员 | 开发者 | dev@example.com | 代码维护 |
| 业务负责人 | 负责人 | business@example.com | 业务支持 |

---

**部署完成后，请确保定期备份数据库和配置文件，以防止数据丢失。**