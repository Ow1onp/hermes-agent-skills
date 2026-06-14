---
name: test-driven-dev
description: Use when implementing logic, fixing bugs, or changing behavior. Enforces strict RED-GREEN-REFACTOR cycle with the test pyramid (80/15/5) and Beyonce Rule — tests before code, always.
triggers: [tdd, test, 测试, 单元测试, unittest, bug fix, 修bug, implement, 实现, refactor, 重构]
version: 1.0.0
author: Ow1onp
---

# 测试驱动开发 (Test-Driven Development)

## 1. 概述

TDD 不是关于测试——是关于设计。先写测试迫使你在写代码之前就思考接口、边界和错误处理。结果是更清晰的设计、更少的 bug、更高的重构信心。

与 Hermes Agent 深度集成：利用 `delegate_task` 并行执行测试套件，利用 `terminal` 实时运行测试，利用 `/curator` 追踪测试质量趋势。

## 2. 核心流程

### 2.1 RED → GREEN → REFACTOR 循环

```
 RED                   GREEN                REFACTOR
 写一个失败的测试  →  写最小代码让测试通过  →  清理实现  →  重复
   ↓                     ↓                    ↓
 测试 FAIL            测试 PASS            测试仍 PASS
```

**RED 阶段铁律**：测试必须先失败。
- 如果测试一开始就通过，要么是测试写错了，要么是功能已存在。
- 必须亲眼看到红色（失败），才能信任绿色（通过）。

### 2.2 测试金字塔与 Hermes 并行执行

```
          ╱╲
         ╱  ╲         E2E (5%)   — delegate_task 被 Hermes 自动分派
        ╱    ╲
       ╱──────╲      集成测试 (15%) — terminal 工具直接执行
      ╱        ╲
     ╱──────────╲    单元测试 (80%) — 毫秒级，本地即时反馈
    ╱            ╲
   ╱──────────────╲
```

### 2.3 Prove-It 模式（Bug 修复专用）

```
1. 写一个复现 Bug 的失败测试
2. 确认测试失败 → Bug 确凿存在
3. 实现修复
4. 确认测试通过 → Bug 已修复
5. 运行全量测试 → 无回归
```

```python
# 示例：Bug "完成任务时没设置 completed_at"
def test_complete_task_sets_completed_at():
    # 1. RED: 复现 Bug
    task = create_task(title="Test")
    completed = complete_task(task.id)
    assert completed.status == "completed"
    assert completed.completed_at is not None  # ← 这行应该失败

# 2. GREEN: 最小修复
def complete_task(id: str) -> Task:
    return db.tasks.update(id, {
        "status": "completed",
        "completed_at": datetime.now(),  # ← 修复：补上遗漏的字段
    })
```

### 2.4 Hermes 工具链集成

```bash
# 在 Hermes 会话中运行测试套件
terminal(command="pytest tests/ -v --tb=short", timeout=120)

# 使用 delegate_task 并行运行慢速集成测试
delegate_task(
    goal="Run integration tests for auth module",
    context="Run: pytest tests/integration/test_auth.py -v",
    toolsets=["terminal", "file"]
)

# 利用 Hermes 记忆追踪项目的测试覆盖率趋势
# memory(action="add", content="auth 模块测试覆盖率: 92% (2026-06-14)")
```

### 2.5 自进化机制

1. **测试质量评分**：追踪测试的 "杀虫剂效应"——如果一个测试运行 50 次从未失败，它可能过于宽松
2. **覆盖率盲区检测**：自动识别项目中测试覆盖率最低的模块，建议优先补测
3. **测试模式库**：积累项目特定的测试模式（如 "所有 API 端点必须有 401 测试"）
4. **反馈优化**：如果某类 Bug 反复出现，建议增加对应的测试场景

### 2.6 身份感知

- 读取 `SOUL.md` 中的代码风格偏好
- 测试命名风格跟随 SOUL 定义（如 `should_xxx` vs `test_xxx` vs `it_xxx`）
- 断言风格适配（assertive vs descriptive）

## 3. 门禁标准

- [ ] 每一个新的行为变更都有对应的失败→通过测试记录
- [ ] 单元测试占比 ≥ 70%（测试金字塔底部）
- [ ] 所有测试通过，无 skip/xfail 的 "先跳过以后修"
- [ ] Bug 修复必须有 Prove-It 模式的测试
- [ ] 测试不依赖外部服务（外部依赖用 mock，集成测试除外）
- [ ] 测试命名清晰表达 "测什么 + 期望什么"

## 4. 常见逃避借口与反驳

| 借口 | 反驳 |
|------|------|
| "这个太简单了，不需要测试" | "太简单" 是 bug 最喜欢的藏身之处。简单的 getter 今天可能变成复杂逻辑的明天。 |
| "测试写起来太慢了" | 不写测试的代码快 30%，但调试慢 300%。总时间算下来，TDD 更快。 |
| "我先写代码，之后再补测试" | "之后"永远不会来。这是软件工程最大的谎言之一。 |
| "AI 写的代码不需要测试" | AI 写的代码更需要测试——AI 没有 "这看起来不对" 的直觉。 |
| "测试跑得太慢" | 慢的是集成/E2E 测试，不是单元测试。80% 的单元测试应该在毫秒级完成。 |
