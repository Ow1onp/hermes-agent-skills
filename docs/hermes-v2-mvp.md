# Hermes v2 MVP — Task-First Agent Interface

> **Status:** MVP Hardened · **Version:** 2.0.0-alpha · **Date:** 2026-06-20

---

## What is Hermes v2?

Hermes v2 is a **natural-language frontend** for the Hermes Agent skill system. It lets users say what they want in plain language — no roles, no skills, no constraint engineering required.

```
v1:  User ──► [Write constraint prompt manually] ──► [Load skills] ──► [Execute]
v2:  User ──► "帮我发布项目" ──► [Auto-everything] ──► [Execute]
```

---

## Why Task First, Not Skill First?

v1 exposed the system's internal concepts to users:
- "Choose a role" (Project Manager? Release Manager? Debugger?)
- "Load a skill" (which SKILL.md do I need?)
- "Write constraints" (Authority, Mission, Constraints, Success Criteria...)

**This is wrong.** Users think in tasks, not skills.

| v1 (Skill First) | v2 (Task First) |
|------------------|-----------------|
| "我需要用 Release Manager 角色" | "帮我发布项目" |
| "加载 cicd-orchestrator skill" | (auto) |
| "写 Authority / Mission / Constraints" | (auto) |

v2 inverts the model: the user states the goal; the system figures out how.

---

## Three User Modes

### Beginner Mode（默认）
For users who just want results.

```
Input:  "帮我发布项目"
        ↓
System: [auto-detect: publish_project]
        [auto-select: Project Manager → Release Manager → Launch Commander]
        [auto-load: cicd-orchestrator, code-quality-guardian]
        [auto-generate: 5 constraints, 4 success criteria]
        [execute]
```

User never sees: roles, skills, constraints, workflow steps.

### Advanced Mode
For users who want to specify a persona.

```
Input:  "使用 Release Manager 发布 v1.2.0"
        ↓
System: [detect persona: Release Manager]
        [auto-complete: skills, constraints, workflow]
        [execute]
```

User can optionally see the generated prompt with `--verbose`.

### Expert Mode
For v1 power users. Full control.

```
Input:  "## Authority\n你是 Release Manager\n## Mission\n发布 v1.2.0"
        ↓
System: [detect: Expert Mode]
        [bypass v2 pipeline]
        [execute raw constraint prompt — pure v1 behavior]
```

Zero functionality loss. 100% backward compatible.

---

## Example Input/Output

### Example 1: Publish a Project

```
$ hermes run "帮我发布项目"

📦 Hermes v2 · 6 tasks loaded

Mode:     BEGINNER
Task:     发布项目 (publish_project)
Confidence: 46%
Steps:    3
Skills:   cicd-orchestrator, code-quality-guardian

Workflow:
  1. [Project Manager] 检查项目状态、版本号一致性、未完成事项
  2. [Release Manager] 执行发布流程、tag、GitHub Release
  3. [Launch Commander] 发布社区公告（DEV、HN、Reddit 等）

Success Criteria:
  ✓ 版本号在所有文件中一致
  ✓ GitHub Release 创建成功
  ✓ CHANGELOG 已更新
  ✓ 社区公告已发布（至少 1 个平台）

→ Executing with 3 step(s)...
```

### Example 2: Fix a Bug

```
$ hermes run "fix the failing test"

Mode:     BEGINNER
Task:     Fix Bug (fix_bug)
Confidence: 30%
Steps:    4
Skills:   debugger-coordinator, code-quality-guardian

Workflow:
  1. [Debugger] 复现错误、收集上下文、读取日志
  2. [Debugger] 分析根因、定位代码、理解错误
  3. [Debugger] 实施修复、最小改动
  4. [Code Reviewer] 验证修复、检查副作用、运行测试
```

### Example 3: Expert Mode (v1 compatible)

```
$ hermes run "## Authority
你是 Release Manager
## Mission
发布 v1.2.0
## Constraints
必须通过所有测试
禁止跳过 CI
## Success Criteria
版本号 6 处一致
测试全部通过"

[EXPERT] Raw constraint prompt detected.
  Bypassing NL pipeline. Executing directly.

→ Delegate to Hermes v1 execution engine
```

---

## What's Inside

```
tasks/                          ← 6 task definitions (YAML)
  publish_project.yaml          ← "帮我发布项目"
  fix_bug.yaml                  ← "修复这个错误"
  create_project.yaml           ← "创建一个项目"
  write_docs.yaml               ← "写文档"
  review_code.yaml              ← "检查代码"
  release_version.yaml          ← "发布 v1.2.0"

src/hermes_v2/
  task_registry.py              ← YAML loader
  router.py                     ← Intent Router (rule-based, CN+EN)
  orchestrator.py               ← Task Orchestrator
  constraints.py                ← Constraint Engine
  modes.py                      ← Mode detection + dispatch
  cli.py                        ← hermes run command

tests/
  test_hermes_v2_router.py      ← 31 tests
  test_hermes_v2_orchestrator.py ← 17 tests
  test_hermes_v2_modes.py       ← 16 tests
  test_hermes_v2_constraints.py ← 20 tests
  test_hermes_v2_e2e.py         ← 21 tests
```

---

## How to Migrate from v1 to v2

### As a v1 Expert User
**Do nothing.** Your existing workflow works unchanged. Expert Mode is v1.

### As a New User
Start with `hermes run "your task"`. No learning curve.

### As a Developer
Add new task definitions as YAML files in `tasks/`. The router picks them up automatically.

```yaml
# tasks/my_new_task.yaml
task_id: my_new_task
label:
  zh: 我的新任务
  en: My New Task
intent:
  keywords_zh: [关键词1, 关键词2]
  keywords_en: [keyword1, keyword2]
workflow:
  - persona: Assistant
    step: 1_do_it
    description: 执行任务
required_skills: []
constraints: [规则1, 规则2]
success_criteria: [标准1, 标准2]
default_mode: beginner
```

---

## Success Criteria

- [x] 普通用户可以直接输入 "帮我发布项目"
- [x] 系统自动完成 Project Manager → Release Manager → Launch Commander
- [x] 无需用户指定角色
- [x] 无需用户编写约束工程 Prompt
- [x] 三种模式（Beginner / Advanced / Expert）均可工作
- [x] Expert Mode 完全兼容 v1
- [x] 6 个任务覆盖常见场景
- [x] All tests passing
