# Hermes v2 — Architecture Design

> **Role:** Chief Architect · **Date:** 2026-06-20
> **Status:** DESIGN PHASE | **⚠️ Beta / Experimental — not production-ready**

---

## Problem Statement

User testing on Hermes v1 revealed 5 friction points:

| # | Pain Point | Root Cause |
|---|-----------|------------|
| 1 | 频繁切换角色 | 每个任务需要指定 Role（Project Manager / Release Manager / Validator...） |
| 2 | 不知道用哪个角色 | 新用户面对 8+ 角色，决策瘫痪 |
| 3 | 不知道什么是约束工程 | Authority / Mission / Constraints / Success Criteria — 概念过载 |
| 4 | Prompt 编写门槛高 | 用户需要手动写结构化 Prompt，格式错误导致执行失败 |
| 5 | 能力强但使用成本高 | 系统 powerful 但 onboarding friction 阻止用户使用 |

**核心矛盾：** v1 的约束工程系统提供了精确性和可靠性，但以认知负担为代价。

---

## Design Philosophy

```
v1:  User ──► [Constraint Prompt] ──► [Skill Loader] ──► [Execution]
                  ↑ user must write

v2:  User ──► [NL Input] ──► [Intent Router] ──► [Orchestrator] ──► [Constraint Engine] ──► [Execution]
       "帮我发布"             自动识别意图           自动选择技能+角色      自动生成约束Prompt        v1引擎
```

**核心原则：** v2 不是替换 v1，而是为 v1 增加一个自然语言前端。v1 的约束工程仍然是底层引擎，只是用户不再需要直接接触它。

---

## 5-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  L1: Natural Language Interface          │
│   Input: "帮我发布项目" / "Fix this bug" / "Create..."   │
│   Output: raw text → L2                                  │
├─────────────────────────────────────────────────────────┤
│                  L2: Intent Router                       │
│   Classify: Release | Debug | Launch | Create | Docs ...  │
│   Output: intent_label + confidence + entities           │
├─────────────────────────────────────────────────────────┤
│                  L3: Skill Orchestrator                  │
│   intent → {persona, skills[], priority, mode}           │
│   Output: execution plan                                 │
├─────────────────────────────────────────────────────────┤
│                  L4: Constraint Engine                   │
│   execution plan → full constraint prompt (invisible)    │
│   Generates: Authority, Mission, Constraints, Rules      │
├─────────────────────────────────────────────────────────┤
│                  L5: Execution Layer                     │
│   Existing v1 Hermes Agent runtime                       │
│   Loads skills, executes tasks, returns results          │
└─────────────────────────────────────────────────────────┘
```

---

## Layer 1: Natural Language Interface

### Responsibility
接受任意自然语言输入，不做处理，直接传递。

### Input Examples
```
"帮我发布 v1.2.0"
"修复 tests/test_validator.py 的失败用例"
"创建一个新的 Agent 技能项目"
"检查代码质量"
"这个错误是什么意思：TypeError: ..."
"写一份本周的开发报告"
```

### No Parsing Here
L1 不做任何解析、分类或转换。所有智能在 L2-L4 完成。L1 的职责仅是接收和传递。

### Multi-turn Support
L1 需要支持澄清对话：
```
User:  "帮我发布"
System: "要发布哪个版本？当前是 v1.1.0"
User:  "v1.2.0"
System: [执行 Release 流程]
```

---

## Layer 2: Intent Router

### Responsibility
从自然语言中识别用户意图，输出结构化的 intent 标签。

### Intent Taxonomy

| Intent | 触发词（中文） | 触发词（English） | 默认 Mode |
|--------|--------------|------------------|:---------:|
| `release` | 发布、上线、发版、release | release, publish, ship, deploy | Advanced |
| `debug` | 修复、bug、错误、报错、调试 | fix, bug, error, debug, crash | Advanced |
| `create_project` | 创建项目、新建、初始化、scaffold | create project, new, init, scaffold | Beginner |
| `code_review` | 检查代码、review、代码质量 | review, check code, quality | Advanced |
| `docs` | 文档、README、写文档、注释 | docs, document, README, write docs | Beginner |
| `test` | 测试、跑测试、test、pytest | test, run tests, pytest | Advanced |
| `analyze` | 分析、评估、检查项目 | analyze, assess, evaluate, audit | Advanced |
| `feedback` | 反馈、用户反馈、收集意见 | feedback, user feedback, survey | Beginner |
| `launch` | 发布到社区、推广、宣传 | launch, promote, announce, post | Advanced |
| `general` | (fallback) | (fallback) | Beginner |

### Implementation Options

**Phase 1 (rule-based):**
```python
# Keyword + pattern matching, no ML dependency
INTENT_PATTERNS = {
    "release": [r"(发布|上线|发版|release|publish|ship|deploy)\s*(v?\d|项目|version)"],
    "debug":    [r"(修复|bug|错误|报错|调试|fix|debug|crash|error|traceback)"],
    "create_project": [r"(创建|新建|初始化|scaffold|create|new|init).*(项目|project)"],
    ...
}
```

**Phase 2 (LLM-based, later):**
- 使用轻量模型（如 DeepSeek-V2-Lite）做意图分类
- 延迟 <200ms
- 可选：用户可在设置中关闭 LLM Router，回退到规则引擎

### Output Schema
```json
{
  "intent": "release",
  "confidence": 0.92,
  "entities": {
    "version": "v1.2.0",
    "scope": "full"
  },
  "mode": "advanced",
  "needs_clarification": false,
  "clarification_question": null
}
```

---

## Layer 3: Skill Orchestrator

### Responsibility
将 intent 映射到具体需要加载的 persona（角色）和 skills。

### Intent → Persona + Skills 映射表

| Intent | Persona | Skills (ordered) | Priority |
|--------|---------|-----------------|:--------:|
| `release` | Release Manager | cicd-orchestrator → code-quality-guardian | P0 |
| `debug` | Debugger | debugger-coordinator → code-quality-guardian | P0 |
| `create_project` | Project Manager | requirement-analyzer → spec-driven-dev → test-driven-dev | P0 |
| `code_review` | Code Reviewer | code-quality-guardian | P1 |
| `docs` | Documentation Writer | (project context only) | P2 |
| `test` | Test Engineer | test-driven-dev | P1 |
| `analyze` | Project Manager | code-quality-guardian → skill-curator | P1 |
| `feedback` | Feedback Analyst | (FEEDBACK.md context) | P2 |
| `launch` | Launch Commander | (launch content context) | P1 |
| `general` | General Assistant | (auto-detect from project skills/) | P3 |

### Auto-Skill Discovery
对于 `general` intent，Orchestrator 扫描 `skills/` 目录中所有 SKILL.md 的 `trigger` 字段，自动匹配用户输入中的关键词：
```yaml
# skills/verify/debugger-coordinator/SKILL.md
trigger:
  - error
  - traceback
  - crash
  - 报错
  - 调试
```
匹配到 triggers → 自动加载该 skill。

### Mode Selection Logic
```
IF intent 在 [create_project, docs, feedback] → Beginner Mode
ELSE IF intent 在 [release, debug, code_review, test, analyze, launch] → Advanced Mode
ELSE IF user explicitly specifies persona → Advanced Mode (user choice)
ELSE → Beginner Mode (fallback)
```

---

## Layer 4: Constraint Engine

### Responsibility
自动生成标准约束工程 Prompt。用户永远不需要看到这个 Prompt。

### Template System
每个 intent 有一个约束模板。模板是声明式的，Engine 在运行时填充变量。

```
Template: release
──────────────────────────────────────────
## Authority
你是 {persona}。
你的职责是执行 {intent} 流程。
---
## Mission
{user_goal}
---
## Constraints
{auto_generated_constraints}
---
## Execution Rules
{execution_rules}
---
## Success Criteria
{success_criteria}
---
## Context
Project: {project_name} v{current_version}
Repo: {repo_url}
Last release: {last_release_tag}
```

### Constraint Generation Rules

| Intent | 自动生成的 Constraints |
|--------|----------------------|
| `release` | 禁止发布未完成功能 · 禁止承诺未来功能 · 必须通过所有测试 · 版本号 6 处一致 |
| `debug` | 禁止跳过根因分析 · 必须先理解再修复 · 禁止猜测性修改 · 修复后必须验证 |
| `create_project` | 使用标准项目结构 · 包含 README + LICENSE · 包含测试框架 · 包含 CI 配置 |
| `code_review` | 安全 > 性能 > 风格 · 每个问题附修复建议 · 不阻塞非阻塞性问题 |
| `docs` | 简洁优先 · 代码示例必须可运行 · 中英双语（如果项目支持） |
| `general` | 优先使用已有 Skill · 不确定时询问用户 · 执行前确认高风险操作 |

### Context Injection
Constraint Engine 自动注入项目上下文：
- 从 `pyproject.toml` 读取项目名、版本、依赖
- 从 `.git/config` 读取仓库 URL
- 从 `CHANGELOG.md` 读取最近发布
- 从 `FEEDBACK.md` 读取待处理反馈
- 从 memory 读取用户偏好

### Invisibility Guarantee
L4 的输出**不展示给用户**。用户只看到：
```
User:  "帮我发布 v1.2.0"
       ↓
       [L1 → L2 → L3 → L4 自动生成完整约束 Prompt，不可见]
       ↓
Hermes: "正在执行 Release 流程..."
        [执行结果]
```

---

## Layer 5: Execution Layer

### Responsibility
完全复用 v1 的 Hermes Agent 运行时。零改动。

L5 接收 L4 生成的完整约束 Prompt + L3 选择的 skills 列表，按 v1 原有流程执行。

### 与 v1 的兼容性
```
v2 Beginner Mode:  User NL → L1→L2→L3→L4→L5 (v1 runtime)
v2 Advanced Mode:  User NL + explicit persona → L2→L3→L4→L5 (v1 runtime)
v2 Expert Mode:    User writes constraint prompt → L5 directly (pure v1)
```

Expert Mode 完全绕过 L1-L4，等价于 v1 直接使用。

---

## User Modes

### Beginner Mode（默认）
- 触发：新用户 / `general` intent / `create_project` / `docs` / `feedback`
- 用户只输入目标，系统全自动
- 约束 Prompt 不可见
- 系统主动询问澄清问题

```
┌─ Beginner Mode ─────────────────────────┐
│                                          │
│  User: "帮我创建一个 Python 项目"         │
│                                          │
│  Hermes: "好的，项目叫什么名字？"          │
│  User: "my-api-server"                   │
│                                          │
│  Hermes: [自动执行 Project Creation]      │
│          [自动加载 requirement-analyzer]  │
│          [自动加载 spec-driven-dev]       │
│          [自动加载 test-driven-dev]       │
│                                          │
│  → 项目创建完成                           │
└──────────────────────────────────────────┘
```

### Advanced Mode
- 触发：用户指定 persona 或 intent 匹配到 advanced 类 intent
- 用户可以指定：`使用 Release Manager 发布项目`
- 系统自动生成约束，但用户可以追加额外指令
- 约束 Prompt 可选可见（`--verbose` 标志）

```
┌─ Advanced Mode ─────────────────────────┐
│                                          │
│  User: "使用 Release Manager 发布 v1.2"  │
│                                          │
│  Hermes: [匹配 persona: Release Manager] │
│          [加载 skills: cicd-orchestrator]│
│          [生成约束 Prompt]               │
│                                          │
│  User 可追加: "跳过 PyPI，只做 GitHub"    │
│  → 约束 Prompt 自动更新                  │
│                                          │
└──────────────────────────────────────────┘
```

### Expert Mode
- 触发：用户输入包含结构化约束字段（Authority / Mission / Constraints）
- 系统检测到约束 Prompt → 直接传递给 L5
- 完全等价于 v1 使用方式
- 零损失：所有 v1 用户无需改变使用习惯

```
┌─ Expert Mode ───────────────────────────┐
│                                          │
│  User: "## Authority                     │
│         你是 Release Manager             │
│         ## Mission                       │
│         发布 v1.2.0..."                  │
│                                          │
│  Hermes: [检测到约束 Prompt]             │
│          [绕过 L1-L4]                    │
│          [直接进入 L5 v1 执行]            │
│                                          │
└──────────────────────────────────────────┘
```

### Mode Detection Logic
```python
def detect_mode(user_input: str) -> Mode:
    # Expert: contains structured constraint headers
    if re.search(r'##\s*(Authority|Mission|Constraints|Success Criteria)', user_input):
        return Mode.EXPERT

    # Advanced: user explicitly names a persona
    if re.search(r'(使用|用|as|use)\s*(Release Manager|Debugger|Project Manager|Validator|Docs|Launch|Feedback)', user_input):
        return Mode.ADVANCED

    # Beginner: everything else
    return Mode.BEGINNER
```

---

## File Structure Changes

### Current (v1)
```
hermes-agent-skills/
├── skills/           # 8 SKILL.md
├── agents/           # 2 domain agents
├── src/
│   ├── cli/          # hermes-skill CLI
│   └── hermes_agent_skills/  # validator, evolution, soul_reader
├── tests/
├── docs/
└── benchmarks/
```

### Proposed (v2)
```
hermes-agent-skills/
├── skills/           # unchanged — 8 SKILL.md
├── agents/           # unchanged — 2 domain agents
├── src/
│   ├── cli/          # hermes-skill CLI (unchanged)
│   ├── hermes_agent_skills/  # validator, evolution, soul_reader (unchanged)
│   └── hermes_v2/            # NEW — v2 intelligence layer
│       ├── __init__.py
│       ├── interface.py      # L1: Natural Language Interface
│       ├── router.py         # L2: Intent Router
│       ├── orchestrator.py   # L3: Skill Orchestrator
│       ├── constraints.py    # L4: Constraint Engine
│       ├── modes.py          # Mode detection + switching
│       ├── intents/          # Intent definitions
│       │   ├── __init__.py
│       │   ├── release.py
│       │   ├── debug.py
│       │   ├── create_project.py
│       │   ├── code_review.py
│       │   └── ...
│       └── templates/        # Constraint templates
│           ├── release.yaml
│           ├── debug.yaml
│           ├── create_project.yaml
│           └── ...
├── tests/
│   ├── ...                   # existing tests (unchanged)
│   └── test_v2/              # NEW — v2 tests
│       ├── test_router.py
│       ├── test_orchestrator.py
│       └── test_constraints.py
├── docs/
│   ├── ...                   # existing docs
│   └── v2/                   # NEW — v2 documentation
│       ├── architecture.md   # this document
│       └── migration.md
└── benchmarks/               # unchanged
```

### Key Principle: Additive, Not Destructive
- 所有 v1 代码**零改动**
- v2 代码全部在 `src/hermes_v2/` 下
- v1 CLI (`hermes-skill`) 不受影响
- v2 作为可选层存在：`hermes run "帮我发布"` vs `hermes-skill validate skills/`

---

## Skill Upgrade Plan

### Current Skills — No Changes Required

所有 8 个现有 SKILL.md **不需要修改**。v2 的 Intent Router 和 Skill Orchestrator 在**外部**完成映射，不侵入 skill 文件。

### Optional Enhancement: trigger 字段

现有的 `trigger` 字段（如果存在）可用于自动匹配。建议为每个 skill 添加 `trigger` 列表以提升自动匹配精度：

```yaml
# skills/ship/cicd-orchestrator/SKILL.md
trigger:
  - release
  - publish
  - deploy
  - ship
  - 发布
  - 上线
  - 发版
  - CI/CD
```

**不需要立即添加** — v2 的 Orchestrator 有硬编码映射表作为 fallback。trigger 字段是可选的增强。

### New Skills for v2

不需要新增任何 skill。v2 的职责是让现有 8 个 skill 更容易被发现和使用，而不是增加新的。

---

## Backward Compatibility

### Guarantee: Zero Breaking Changes

| v1 Feature | v2 Status |
|-----------|:---------:|
| `hermes-skill create` | ✅ Unchanged |
| `hermes-skill validate` | ✅ Unchanged |
| `hermes-skill list` | ✅ Unchanged |
| `hermes-skill soul` | ✅ Unchanged |
| Direct constraint prompt | ✅ Expert Mode = pure v1 |
| SKILL.md format | ✅ Unchanged |
| Agent Skills Open Standard | ✅ Unchanged |
| CI/CD pipeline | ✅ Unchanged — tests, lint, validate |
| pyproject.toml | ✅ Unchanged |

### v2 Entry Point

新增一个入口命令，不替代现有 CLI：

```bash
# v1 — unchanged
hermes-skill validate skills/
hermes-skill create my-skill

# v2 — new
hermes run "帮我发布 v1.2.0"
hermes run "fix the failing test in test_validator.py"
hermes run "create a new agent project called my-agent"
```

`hermes run` 内部调用 L1→L2→L3→L4→L5，L5 调用 v1 运行时。

### Config

在 `pyproject.toml` 或 `config.yaml` 中增加可选配置：

```yaml
# Hermes v2 config (optional — defaults work for everyone)
hermes_v2:
  default_mode: beginner      # beginner | advanced | expert
  router:
    backend: rule             # rule | llm
    llm_model: null           # only used if backend=llm
  verbose: false              # show constraint prompt in advanced mode
  auto_clarify: true          # ask clarification questions
```

---

## Migration Plan

### Phase 1: Core Router (Week 1–2)
- 实现 L2 Intent Router（rule-based）
- 实现 L3 Skill Orchestrator（硬编码映射表）
- 实现 L4 Constraint Engine（模板填充）
- 实现 Mode Detection
- 覆盖 3 个 intents：`release`, `debug`, `create_project`

### Phase 2: Beginner Experience (Week 3–4)
- 完善 L1 多轮对话
- 覆盖剩余 intents：`code_review`, `docs`, `test`, `analyze`, `feedback`, `launch`
- 添加 `--verbose` 标志
- 添加中文 intent 支持
- 编写 v2 文档

### Phase 3: Polish & Launch (Week 5–6)
- 用户测试（让从未用过 v1 的人试用 v2 Beginner Mode）
- 收集反馈，调整 intent 匹配规则
- 可选：添加 LLM-based Router（Phase 2）
- v2.0.0 发布

### Phase 4: Evolution (post-launch)
- Intent Router 从规则引擎升级为 LLM 分类器
- 基于用户反馈自动调整 intent→skill 映射
- 约束模板从用户使用模式中自我优化

### Rollback Plan
v2 是纯增量。如果 v2 Router 出问题：
```bash
# 用户始终可以回到 v1
hermes-skill validate skills/     # v1 CLI — always works
# 或使用 Expert Mode（等价于 v1）
hermes run "## Authority\n你是 Release Manager\n..."
```

v2 代码在独立目录下，删除 `src/hermes_v2/` 即完全回退到 v1。

---

## Success Criteria Validation

| 标准 | v1 | v2 | 方法 |
|------|:--:|:--:|------|
| 用户不需要知道 Role 存在 | ❌ | ✅ | Beginner Mode 自动选择角色 |
| 用户不需要学习约束工程 | ❌ | ✅ | L4 自动生成约束 Prompt |
| 用户不需要编写复杂 Prompt | ❌ | ✅ | 用户只需说目标 |
| 系统自动选择 Skill | ❌ | ✅ | L3 Orchestrator + auto-discovery |
| 系统自动生成约束 | ❌ | ✅ | L4 Constraint Engine |
| 专家模式兼容 | ✅ | ✅ | Expert Mode = pure v1 |

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| Rule-based Router first, LLM later | 零延迟，零依赖，零成本。LLM Router 作为可选升级 |
| 不改动任何 v1 代码 | 保证零回归风险，v1 用户不受影响 |
| `hermes run` 而非修改 `hermes-skill` | 新入口 = 新心智模型。`hermes-skill` 保持为开发者工具 |
| 硬编码 intent→skill 映射 | 10 个 intent 的映射表不需要 ML。未来如果 intent 超过 50 个再考虑动态路由 |
| 约束模板用 YAML | 声明式，可读，可版本控制，非开发者也能修改 |
