# 支持多环境API路径配置计划

## 1. 目标

- **开发环境**：使用 `/api/` 路径
- **生产环境**：使用 `/fundai/api/` 路径
- 自动根据环境切换，无需手动修改代码

---

## 2. 实施方案

### 方案：前端动态检测当前路径

**原理**：
- 前端通过 `window.location.pathname` 检测当前访问路径
- 如果路径以 `/fundai/` 开头，则 API 使用 `/fundai/api/`
- 否则默认使用 `/api/`

**优点**：
- 不需要修改后端代码
- 不需要配置环境变量
- 前端自动适配
- 开发体验好

---

## 3. 实施步骤

### 步骤1：修改前端 API_BASE 配置

**修改文件**：`fund-marketing-platform/frontend/index.html`

**原代码**（index.html:3634）：
```javascript
const API_BASE = '/api';
```

**修改后**：
```javascript
// 动态检测当前路径，自动适配API前缀
const API_BASE = window.location.pathname.startsWith('/fundai/')
    ? '/fundai/api'
    : '/api';
```

### 步骤2：验证本地开发环境

**测试场景1：本地开发**
- 启动服务：`bash manage.sh start`
- 访问：`http://localhost:5002/`
- 路径不包含 `/fundai/`
- API_BASE = `/api`
- API 调用：`/api/health` ✓

### 步骤3：验证生产环境

**测试场景2：生产环境**
- Nginx 配置：`/fundai/` → `http://localhost:5002/`
- 访问：`http://服务器地址/fundai/`
- 路径包含 `/fundai/`
- API_BASE = `/fundai/api`
- API 调用：`/fundai/api/health` ✓
- Nginx 不会拦截 `/fundai/api`，正确转发到后端

---

## 4. 详细代码修改

### 4.1 修改前端 index.html

**位置**：约第3634行

```javascript
// 原来的代码
const API_BASE = '/api';

// 修改后的代码
const API_BASE = window.location.pathname.startsWith('/fundai/')
    ? '/fundai/api'
    : '/api';
```

### 4.2 可选：后端添加健康检查路由（兼容两套路径）

**修改文件**：`fund-marketing-platform/backend/app.py`

为了更好的兼容性，可以在后端同时注册两套路由：

```python
# 原有路由（兼容开发环境）
app.register_blueprint(fund_bp, url_prefix='/api/fund')
app.register_blueprint(copy_bp, url_prefix='/api/copy')
# ... 其他路由

# 生产环境路由（可选，同时支持）
app.register_blueprint(fund_bp, url_prefix='/fundai/api/fund')
app.register_blueprint(copy_bp, url_prefix='/fundai/api/copy')
# ... 其他路由
```

**注意**：这样会导致路由重复，建议只使用一套路由。

---

## 5. 验证步骤

### 5.1 本地开发环境验证

```bash
# 1. 启动服务
bash fund-marketing-platform/manage.sh start

# 2. 访问前端
open http://localhost:5002/

# 3. 测试API
curl http://localhost:5002/api/health
# 应该返回：{"status": "ok", ...}

# 4. 检查浏览器控制台
# 确认 API_BASE = '/api'
```

### 5.2 生产环境验证

```bash
# 1. 部署到服务器

# 2. 配置 Nginx
# location /fundai/ {
#     proxy_pass http://localhost:5002/;
# }

# 3. 访问前端
open http://服务器地址/fundai/

# 4. 测试API
curl http://服务器地址/fundai/api/health
# 应该返回：{"status": "ok", ...}

# 5. 检查浏览器控制台
# 确认 API_BASE = '/fundai/api'
```

---

## 6. 优势分析

### 兼容性
- ✅ 开发环境：使用 `/api/`
- ✅ 生产环境：使用 `/fundai/api/`
- ✅ 自动检测，无需手动切换
- ✅ 不影响现有代码逻辑

### 可维护性
- ✅ 只需修改一处代码
- ✅ 后端代码无需修改
- ✅ 配置简单
- ✅ 易于理解和维护

### 风险评估
- **风险**：低
- **影响范围**：仅前端 API 调用
- **回滚方案**：简单，恢复原代码即可

---

## 7. 实施时间表

| 步骤 | 任务 | 预计时间 |
|------|------|----------|
| 1 | 修改前端 API_BASE 配置 | 5分钟 |
| 2 | 本地开发环境测试 | 10分钟 |
| 3 | 生产环境部署测试 | 10分钟 |

**总预计时间**：25分钟

---

## 8. 总结

通过在前端动态检测当前路径并自动适配 API 前缀，可以实现：
- **开发环境**：使用 `/api/`
- **生产环境**：使用 `/fundai/api/`
- **自动切换**：无需手动修改代码
- **简单易用**：只修改一处代码

这个方案既满足了开发体验，又解决了生产环境的路由冲突问题。