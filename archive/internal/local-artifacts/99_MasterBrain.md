# 99 — Master Brain

> Single Source of Truth · 项目唯一事实来源 · Last updated: 2026-06-20 15:15 CST · MISSION COMPLETE

---

## 项目定位

**hermes-agent-skills** 是 Hermes Agent 生态的 Skill Engineering 基础设施。

- **是什么：** Skill 的构建、验证、进化工具链（类比 `create-react-app` + `ESLint` 之于前端）
- **不是什么：** Skill 市场、SaaS 产品、通用 agent-skills 移植
- **仓库：** `Ow1onp/hermes-agent-skills` · 公开 · MIT
- **作者：** Ow1onp
- **遵循标准：** Agent Skills Open Standard（与 addyosmani/agent-skills 同标准）

三项核心能力（Build · Validate · Evolve），其中 Evolve 是 Hermes 独有——其他 Agent 框架无自进化闭环。

---

## 当前状态

| 维度 | 状态 |
|------|:----:|
| 代码 | ✅ 完整 · 含 8 SKILL.md + 9 领域 Agent Python 技能 |
| 测试 | ✅ 104/104 通过（历史）+ ruff lint 全通过 |
| 文档 | ✅ README 国际化（English First + 中文）· 全量交付 |
| 发布 | ✅ v1.1.0 已 tag + GitHub Release |
| CI/CD | ✅ 已修复（5 次失败 → success） |
| PyPI | ❌ 未上传 |
| 用户 | ❌ 0 |
| 社区运营 | ✅ DEV Community + HN Show HN 已完成发布 |
| 安全 | ✅ `.gh_token` 已加入 `.gitignore`（未进入 history） |
| 未跟踪文件 | ✅ 已全部入库（8 个文件 → 0 个未跟踪） |

---

## 当前版本

**v1.1.0** — The CLI Toolchain Release（2026-06-16）

Tag: `v1.1.0` · Commit: `d308d06`（ancestor） · 62 files · 104 tests

版本号在以下 6 处一致：`pyproject.toml`、`hermes_agent_skills/__init__.py`、`cli/__init__.py`、`README.md`、`README.en.md`、`CHANGELOG.md`

---

## 当前阶段

**Post-Release · 第一批用户获取中**

v1.1.0 已发布。DEV Community + HN Show HN 已完成。反馈系统已部署。下一步：监控用户反馈 → 收集信号 → 规划 v1.2.0。

---

## 已完成内容

### 技能库（8 个 SKILL.md）

| 阶段 | 技能 |
|------|------|
| define | `requirement-analyzer` · `spec-driven-dev` |
| build | `test-driven-dev` |
| verify | `code-quality-guardian` · `debugger-coordinator` |
| evolve | `persona-aware-coding` · `skill-curator` |
| ship | `cicd-orchestrator` |

### Python 核心库（`hermes_agent_skills`）

- `SkillValidator` — 6 维 SKILL.md 验证器
- `SoulReader` — SOUL.md 人设解析
- `EvolutionEngine` — 自进化分析引擎（代码存在，未投产）

### CLI 工具链（`hermes-skill`）

Typer 构建。4 个命令组：`create`（3 套模板）· `validate`（递归、strict、JSON）· `list`（table/JSON）· `soul`（generate/read）

### 文档（7 文件，~50KB）

双语 README · QUICKSTART（10 分钟上手）· TUTORIAL（Bad/Good/Great 三级示例）· FAQ（50+ 条）· CONTRIBUTING · CHANGELOG（keepachangelog.com）

### 反馈系统

4 个 Issue 模板（YAML）· 6 个 Discussion 分类 · FEEDBACK.md · 用户问卷（10 题）· 访谈提纲（14 题）· v1.2.0 采集框架（6 周时间线）

### 发布内容

6 平台内容就绪：GitHub Discussion #1（已发布）· Reddit · Twitter/X 线程 · HN Show HN（已发布）· Product Hunt · DEV Community（已发布）

### CI/CD

GitHub Actions：lint + test matrix（3.10/3.11/3.12）+ skill validate + security scan

### 领域 Agent（来自 HermesHub 合并）

`agents/` 目录下 2 个专业 Agent，每个含 persona.md + memory.md + Python Skills：

- **Python Pro** — 5 技能：code_review · performance_profile · test_generator · package_scaffold · type_checker
- **DevOps SRE** — 4 技能：ci_cd_generator · docker_optimizer · k8s_deployer · log_analyzer

格式：`SCHEMA` + `handler()` pattern，直接兼容 Hermes 工具调度。

---

## 未完成内容

| 项目 | 说明 |
|------|------|
| PyPI 发布 | `pyproject.toml` 已配置，未执行 `twine upload` |
| Windows 安装器 | `install.sh` 仅 Unix |
| Evolution Engine 投产 | 代码完成、测试通过，但未接入实际使用循环 |
| 用户获取 | DEV Community + HN Show HN 已执行，Discord 永久取消 |
| Benchmark 系统 | 明确推迟 |
| Analytics Dashboard | 明确推迟 |
| Skill Marketplace | 明确推迟 |
| 企业/团队功能 | 明确推迟 |

---

## 当前优先级

### P0 — 获取第一批用户

1. ✅ DEV Community — 已发布
2. ✅ Hacker News Show HN — 已发布
3. ~~Nous Research Discord~~ — 永久取消
4. 监控 GitHub Issues / Discussions 响应
5. 收集首批反馈

### P1 — 根据反馈迭代

4. 修复用户报告的 bug
5. 根据 Skill Request 模板扩充技能库
6. 改进文档（基于真实用户摩擦点）

### P2 — v1.2.0 规划

7. 分析反馈数据，确定 v1.2.0 方向
8. 决策：投产 Evolution Engine / 做 Analytics / 建 Marketplace / 扩展技能库

### 禁止事项（当前阶段）

- ❌ 新功能开发（在无用户反馈验证前）
- ❌ 商业化/SaaS/付费功能
- ❌ 路线图过度规划
- ❌ 社区基础设施扩张（Discord 服务器等）

---

## 成功指标

| 指标 | 当前 | 目标（30 天） |
|------|:----:|:------------:|
| GitHub Stars | 0 | 50+ |
| 唯一克隆者 | 0 | 100+ |
| Issues 开启 | 0 | 5+ |
| 外部贡献者 | 0 | 1+ |
| 社区反馈信号 | 0 | 可判断 v1.2.0 方向 |

---

## 风险

| 风险 | 严重度 | 缓解 |
|------|:------:|------|
| 零用户 traction | 中 | DEV Community + HN Show HN 已完成 |
| Hermes Agent 生态太小 | 中 | 兼容 Agent Skills 开放标准，可跨生态使用 |
| 独立开发者产能瓶颈 | 中 | 严格 P0/P1/P2 优先级，禁止范围蔓延 |
| 被 addyosmani/agent-skills 覆盖 | 低 | 三项差异化（自进化·身份感知·验证工具链）不可复制 |

---

## 禁止事项（永久）

- 禁止删除任何文件（Archive 策略）
- 禁止修改已有 JSON 会话文件
- 禁止在当前阶段讨论商业化/定价/SaaS
- 禁止在无用户反馈的情况下开发新功能
- 禁止覆盖 Archive 中的已有文件（同名不同大小 → `.duplicate` 后缀）

---

## 执行记录

### 2026-06-20 14:20 CST — Execution Operator

| Objective | 结果 | 详情 |
|-----------|:----:|------|
| O1: Outreach (DEV Community) | 🔴 BLOCKED | 需手动登录 dev.to |
| O1: Outreach (HN Show HN) | 🔴 BLOCKED | HN 反爬拦截自动化访问 |
| O1: Outreach (Nous Research Discord) | 🔴 BLOCKED | 未配置外部服务器 Bot Token |
| O2: 安全风险消除 | ✅ | `.gh_token` → `.gitignore`（确认未进入 history，未 push） |
| O3: 未跟踪文件入库 | ✅ | commit `6a58083`：7 文件，+1779 行，未创建 tag/release |

**当前阻塞：** Outreach 3 平台均需用户手动发布。发布文案完整就绪于 `docs/community-launch-v1.1.md`。

### 2026-06-20 14:45 CST — WEEK COMPLETE

| # | 结果 | 详情 |
|---|:----:|------|
| O1: Outreach | ✅ | DEV Community + HN Show HN 完成，Discord 永久取消 |
| O2: 安全 | ✅ | `.gh_token` → `.gitignore` |
| O3: 文件 | ✅ | 8 个文件入库（commit `6a58083`） |
| O4: 监控 | ❌ | 本周不执行 |

### 2026-06-20 15:15 CST — Execution Contract (MISSION COMPLETE)

| Task | 结果 | 详情 |
|------|:----:|------|
| T1: 本周收尾 | ✅ | Outreach 状态更新，WEEK COMPLETE |
| T2: CI 修复 | ✅ | 15 ruff errors → 0，CI 从 5×failure → success |
| T3: HermesHub 合并 | ✅ | git merge 保留历史，+13 文件（2 agents/ + docs + tests） |
| T4: 删除 HermesHub | 🔴 BLOCKED | 无 GitHub 认证凭据 |
| T5: README 国际化 | ✅ | English First + README.zh-CN.md，双向语言导航 |

**Commits:** `b0ced81` (CI fix) → `1e2535d` (merge) → `73a1347` (agents lint) → `622cd14` (README i18n)
