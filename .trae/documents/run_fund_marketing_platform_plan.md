# 启动海富通基金营销平台项目计划

## 现状分析

### 之前遇到的问题
1. **Python环境问题**：系统安装的Python版本与Flask/依赖包版本不兼容
   - 当前Python：`/opt/homebrew/Cellar/python@3.14/3.14.3_1`
   - 已安装的包在：`~/.local/lib/python3.12/site-packages`
   - 存在版本冲突：Werkzeug与Flask版本不兼容

2. **依赖包问题**：
   - `Flask==2.0.1` 需要特定版本的Werkzeug
   - `requests==2.26.0` 与其他全局包冲突
   - `python-dotenv==0.19.0` 版本过低

## 解决方案

### 方案一：使用虚拟环境（推荐）
```bash
# 1. 创建虚拟环境
cd fund-marketing-platform/backend
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python app.py
```

### 方案二：使用正确的Python版本
```bash
# 使用Python 3.12（与已安装包兼容）
/opt/homebrew/bin/python3.12 fund-marketing-platform/backend/app.py
```

## 实施步骤

### 步骤1：创建虚拟环境
- 进入backend目录
- 使用Python 3.12创建虚拟环境
- 激活虚拟环境

### 步骤2：安装依赖
- 在虚拟环境中安装requirements.txt中的依赖
- 确保所有包版本兼容

### 步骤3：修复代码问题
- 恢复Flask-CORS支持（如需要）
- 确保所有导入正确

### 步骤4：启动服务
- 运行python app.py
- 检查服务是否在5002端口启动

### 步骤5：验证服务
- 访问 http://localhost:5002/api/health
- 确认返回正常状态

## 预期结果
- 服务成功启动
- 健康检查接口正常响应
- 前端页面可访问