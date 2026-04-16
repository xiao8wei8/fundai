# 修改Git忽略规则计划

## 1. 目标

将之前被正确忽略的文件也添加到Git提交中，包括：
- `.trae/` - IDE临时文档
- `backend/data/` - 数据库和数据文件
- 其他之前被忽略的文件

---

## 2. 实施步骤

### 步骤1：修改.gitignore文件
移除或注释掉以下忽略规则：
- `.trae/` - IDE临时文档目录
- `data/*.db` - 数据库文件
- `data/*.sqlite` - SQLite数据库
- `*.log` - 日志文件（可能有用）
- 其他需要提交的文件规则

**保留的忽略规则**：
- 虚拟环境（venv/）
- Python缓存（__pycache__/）
- 环境变量（.env）
- 备份文件（*.bak）

---

### 步骤2：添加文件到暂存区
```bash
git add .
```

这将包括：
- `.trae/` 目录及其内容
- `backend/data/` 目录及其内容
- `data/` 目录及其内容
- 其他之前被忽略但现在需要提交的文件

---

### 步骤3：查看暂存区状态
```bash
git status
```

确认所有需要的文件已添加到暂存区。

---

### 步骤4：创建新的提交
```bash
git commit -m "feat: 添加项目文档和数据文件

- 添加.trae/文档目录（项目分析和计划文档）
- 添加data/目录（数据库和库文件）
- 添加backend/data/目录（数据库和库文件）
- 包含所有项目分析文档和部署计划"
```

---

## 3. 需要提交的文件清单

### 文档文件（.trae/）
- [ ] `fund_ai_branding_plan.md` - 品牌改造计划
- [ ] `fund_ai_gitignore_plan.md` - Git忽略计划
- [ ] `fund_ai_runtime_flow.md` - 运行流程说明
- [ ] `fund_marketing_platform_analysis.md` - 项目分析报告
- [ ] `fund_marketing_platform_deployment.md` - 部署文档
- [ ] `git_commit_plan.md` - 提交计划
- [ ] `*.json` - 临时锁文件

### 数据文件
- [ ] `fund-marketing-platform/backend/data/fund_marketing.db` - SQLite数据库
- [ ] `fund-marketing-platform/backend/data/library.json` - 素材库数据
- [ ] `fund-marketing-platform/data/fund_marketing.db` - 数据库副本

---

## 4. 预期结果

- ✅ .gitignore文件已更新
- ✅ 所有需要的文件已添加到Git
- ✅ 包含完整的项目文档
- ✅ 包含数据库和数据文件
- ✅ 提交信息清晰规范

---

## 5. 注意事项

1. **虚拟环境**: 仍不应提交（venv/）
2. **敏感信息**: .env文件仍不应提交
3. **缓存文件**: __pycache__仍不应提交
4. **备份文件**: *.bak仍不应提交
5. **数据文件**: 现在可以提交，方便演示和测试