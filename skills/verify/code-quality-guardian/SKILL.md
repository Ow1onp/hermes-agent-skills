---
name: code-quality-guardian
description: Use before merging or committing code. Performs six-axis code quality gating — security, complexity, style, test coverage, documentation, and dependency health. Blocks low-quality code from entering the main branch.
triggers: [review, 审查, code review, 代码审查, quality, 质量, lint, merge, 合并, PR, pull request, before commit, 提交前]
version: 1.0.0
author: Ow1onp
---

# 代码质量守护者 (Code Quality Guardian)

## 1. 概述

代码质量不是可选项——它是软件可维护性的基石。本技能在代码进入主分支之前，执行六轴质量门禁，系统性拦截低质量代码。每个轴都有明确的通过/失败标准，不给 "以后优化" 留借口。

与 Hermes Agent 深度集成：利用 `patch` 工具自动修复低悬果实，利用 `delegate_task` 并行审查多个文件，利用 `/curator` 追踪项目质量趋势。

## 2. 核心流程

### 2.1 六轴质量门禁

```
┌──────────────────────────────────────────────────┐
│         代码质量六轴门禁 (Six-Axis Gate)           │
├──────────┬──────────┬──────────┬─────────────────┤
│ 🔒 安全   │ 📐 复杂度 │ 🎨 风格  │ ✅ 测试覆盖     │
│ Security │Complexity│  Style   │Test Coverage   │
├──────────┼──────────┼──────────┼─────────────────┤
│ 📝 文档   │ 📦 依赖   │          │                 │
│   Docs   │   Deps   │          │                 │
└──────────┴──────────┴──────────┴─────────────────┘
```

### 2.2 各轴检查标准

**🔒 安全 (Security)**
- 无硬编码密钥/密码/Token
- 无 SQL 注入风险（使用参数化查询）
- 无 XSS 风险（输出编码）
- 敏感操作有授权检查
- 文件上传有类型/大小限制

```bash
# Hermes 工具集成
search_files(pattern="(api_key|password|secret|token)\s*=\s*['"]", target="content")
# 利用 Hermes 的 search_files 进行安全模式扫描
```

**📐 复杂度 (Complexity)**
- 单函数 ≤ 30 行（超过拆分为子函数）
- 圈复杂度 ≤ 10
- 嵌套深度 ≤ 3 层
- 单文件 ≤ 500 行
- 函数参数 ≤ 5 个（超过用配置对象）

**🎨 风格 (Style)**
- 一致的命名规范（snake_case / camelCase）
- 无注释掉的代码（用 Git 历史）
- 无 `console.log` / `print` 调试残留
- import 顺序规范（标准库 → 第三方 → 本地）

**✅ 测试覆盖 (Test Coverage)**
- 新增代码行覆盖率 ≥ 80%
- 关键路径有集成测试
- 无 skip/xfail 的 "临时跳过"

**📝 文档 (Documentation)**
- 公开 API 有 docstring/JSDoc
- 复杂逻辑有行内注释解释 "为什么" 而非 "做什么"
- README/CHANGELOG 已更新

**📦 依赖 (Dependencies)**
- 无已知漏洞的依赖版本
- 无未使用的依赖
- 依赖版本锁定（lockfile 已更新）

### 2.3 Hermes 工具链集成

```bash
# 加载技能
/skill code-quality-guardian

# 自动审查流程
# 1. 搜索安全漏洞
search_files(pattern="password\s*=", target="content", path="src/")

# 2. 运行 linter
terminal(command="ruff check src/", timeout=30)

# 3. 运行测试并检查覆盖率
terminal(command="pytest --cov=src/ --cov-report=term-missing", timeout=120)

# 4. 依赖审计
terminal(command="pip-audit", timeout=60)

# 5. 用 patch 工具自动修复低悬果实
patch(path="src/bad.py", old_string="print(f'debug: {x}')", new_string="")
```

### 2.4 自进化机制

1. **质量趋势面板**：追踪每次审查的六轴得分，可视化质量变化
2. **高频违规模式库**：自动识别项目中最频繁的质量违规，生成团队培训建议
3. **门禁阈值自适应**：根据项目成熟度动态调整阈值（新项目宽松，核心模块严格）
4. **自动修复规则积累**：将已验证的自动修复模式（如删除 debug print）沉淀为规则

### 2.5 身份感知

- 读取 `SOUL.md` 中的代码风格偏好
- 风格轴的检查标准自动适配（如偏好函数式 → 检查 immutable 模式）
- 注释和文档的语言风格跟随 SOUL 人设
- 门禁严格程度可随 SOUL 配置（"严苛架构师" vs "务实工程师"）

## 3. 门禁标准

- [ ] 六轴全部绿灯（或红灯有记录的豁免理由）
- [ ] 新增的安全漏洞 = 0
- [ ] 新增代码测试覆盖率 ≥ 80%
- [ ] 无 `# TODO: fix later` 或 `FIXME` 残留
- [ ] 所有自动修复已应用（lint fix, import sort 等）

## 4. 常见逃避借口与反驳

| 借口 | 反驳 |
|------|------|
| "就改了一行，不需要审查" | 一行代码可以引入安全漏洞（如 SQL 注入）。每行代码都一视同仁。 |
| "这个 lint 规则太严格了，先跳过" | 今天的"跳过"是明天的技术债。每条 lint 规则背后都是一个真实的 Bug 案例。 |
| "测试覆盖率不够，但手动测过了" | 手动测试不可重复、不可自动化、不可审计。自动测试是唯一的真相来源。 |
| "依赖警告不重要，能跑就行" | Heartbleed 和 Log4Shell 都来自"不重要"的依赖。安全漏洞不会提前通知你。 |
| "AI 写的代码质量已经很高了" | AI 最擅长产生看起来正确但有隐蔽 Bug 的代码。AI 写的代码需要更严格的审查，而非更宽松。 |
