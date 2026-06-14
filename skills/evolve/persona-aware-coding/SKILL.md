---
name: persona-aware-coding
description: Use before starting any code generation task. Reads Hermes Agent's SOUL.md to dynamically adapt code style, comment tone, documentation voice, and architectural decisions to match the agent's defined persona.
triggers: [persona, 人设, soul, character, 角色, style, 风格, tone, 语气, who am I, identity, 我是谁]
version: 1.0.0
author: Ow1onp
---

# 身份感知编码 (Persona-Aware Coding)

## 1. 概述

同一个功能，由不同风格的工程师实现，会产生截然不同的代码。本技能读取 Hermes Agent 的 `SOUL.md` 文件（Agent 的人设定义文件），在代码生成的每一个环节动态适配风格、语气和架构决策，使产出的代码真正 "像这个人写的"，而非 "像 AI 写的"。

这是 hermes-agent-skills 相对于通用 agent-skills 项目的核心差异化能力——Hermes Agent 有原生的身份系统，本技能将其应用到代码生成全流程。

## 2. 核心流程

### 2.1 SOUL.md 解析与映射

```yaml
# ~/.hermes/SOUL.md 示例
name: "严谨架构师"
traits:
  - 偏好显式优于隐式
  - 重视错误处理
  - 代码即文档
coding_style:
  naming: snake_case
  max_line_length: 100
  prefer: [type_hints, dataclasses, dependency_injection]
  avoid: [magic_numbers, global_state, premature_optimization]
comment_style: "解释为什么，不解释做什么"
test_style: "describe/it 风格"
architecture_preference: "分层架构 + 依赖注入"
```

### 2.2 代码生成全流程适配

```
┌───────────────────────────────────────────────────────┐
│              SOUL.md 驱动的代码生成流水线               │
├───────────────┬───────────────────────────────────────┤
│ 命名风格       │ SOUL.naming → snake_case / camelCase │
│ 类型系统       │ SOUL.type_hints → 是否使用类型标注    │
│ 错误处理       │ SOUL.error_style → try/except / Result│
│ 注释密度       │ SOUL.comment_density → 稀疏 / 详细    │
│ 注释语气       │ SOUL.tone → 正式 / 口语 / 技术极客     │
│ 架构模式       │ SOUL.architecture → 分层 / 六边形 / MVC│
│ 测试风格       │ SOUL.test_style → describe/it / test_ │
│ 提交信息       │ SOUL.commit_style → 规范 / 简洁       │
└───────────────┴───────────────────────────────────────┘
```

### 2.3 风格适配示例

**场景**: 写一个用户认证中间件

| 维度 | "严谨架构师" 风格 | "极简黑客" 风格 | "教学导师" 风格 |
|------|------------------|----------------|----------------|
| 命名 | `authenticate_user()` | `auth()` | `check_if_user_is_logged_in()` |
| 类型 | 完整 type hints | 无类型标注 | 关键处有标注 + 注释 |
| 错误 | 自定义异常类 | `return None` | 详细错误消息 + 建议 |
| 注释 | 无（代码自解释） | 无 | 行内解释设计决策 |
| 文档 | 完整 docstring | 无 | 教程式文档 + 示例 |

### 2.4 Hermes 工具链集成

```bash
# 检查 SOUL.md 是否存在
read_file("~/.hermes/SOUL.md")

# 如果不存在，引导用户创建
# 使用 clarify 工具询问人设偏好
clarify(
    question="你希望我以什么风格编写代码？",
    choices=[
        "严谨架构师 — 类型安全、显式错误处理、分层架构",
        "敏捷实干家 — 实用主义、够用就好、快速迭代",
        "极简黑客 — 最少代码、最大效果、不废话",
        "教学导师 — 详细注释、解释设计决策、可读性优先"
    ]
)

# 加载身份感知技能
/skill persona-aware-coding

# 可通过记忆持久化人设偏好
memory(action="add", target="user", content="编码风格偏好: 严谨架构师型")
```

### 2.5 自进化机制

1. **风格一致性评分**：分析最近 N 次代码生成，检查风格是否与 SOUL.md 一致
2. **人设漂移检测**：如果用户的代码风格在变化，建议更新 SOUL.md
3. **最佳实践融合**：当 SOUL 偏好与社区最佳实践冲突时，提出平衡建议
4. **跨项目风格学习**：用户在多个项目中的编码习惯自动归纳到 SOUL.md

### 2.6 身份感知

本技能自身也受 SOUL.md 影响——它是一个 "自指" 技能：

- 如果 SOUL.md 定义 Agent 为 "严谨型" → 本技能的输出更系统化
- 如果 SOUL.md 定义 Agent 为 "创意型" → 本技能允许更多风格实验
- 如果 SOUL.md 不存在 → 使用中性默认值，并提示用户创建

## 3. 门禁标准

- [ ] SOUL.md 已成功读取或已引导用户创建
- [ ] 生成的代码在命名、注释、错误处理三个维度与 SOUL 一致
- [ ] 如果某个风格选择可能有问题（如 SOUL 偏好与安全最佳实践冲突），已向用户提出警告
- [ ] 代码风格的一致性可被自动验证（如通过 lint 规则）
- [ ] 如果 SOUL.md 中未定义某维度（如 commit_style），已使用合理的行业默认值

## 4. 常见逃避借口与反驳

| 借口 | 反驳 |
|------|------|
| "代码风格不重要，能跑就行" | 代码是写给人看的，只是顺便让机器执行。风格不一致的代码库是认知负荷的地狱。 |
| "我没有 SOUL.md，就用默认的" | 没有 SOUL 的 Agent 就像没有性格的演员——能表演，但没有灵魂。花 3 分钟定义它。 |
| "AI 写的代码风格都一样，改不了" | 这正是本技能存在的意义。AI 可以模仿任何风格，只需要明确的指令——SOUL.md 就是那个指令。 |
| "风格一致性是小事" | 在 10 万行代码库里，风格不一致不是小事——它让你每次打开新文件都要重新适应。 |
| "不同项目应该用不同风格" | 正确！SOUL.md 支持项目级覆盖（`SOUL.md` 放在项目根目录而非 `~/.hermes/`）。 |
