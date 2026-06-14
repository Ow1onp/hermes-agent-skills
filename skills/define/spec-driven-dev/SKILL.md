---
name: spec-driven-dev
description: Use when starting a new feature, project, or significant refactor. Writes a comprehensive PRD/spec document before any implementation code, following the "spec-first, code-second" principle.
triggers: [spec, 规格, 设计文档, PRD, new feature, 新功能, 新项目, architecture, 架构, design doc]
version: 1.0.0
author: Ow1onp
---

# 规格驱动开发 (Spec-Driven Development)

## 1. 概述

规格驱动开发强制 "先写规格，再写代码"。一份好的 Spec 如同建筑蓝图——它让所有参与者（开发者、AI、审查者）在动手之前就达成共识。

与 Hermes Agent 的 `/skills` 命令体系深度集成：本技能可与 `requirement-analyzer` 串联使用（前者澄清需求，后者撰写规格），形成完整的需求→规格流水线。

## 2. 核心流程

### 2.1 Spec 文档七要素

每份 Spec 必须包含以下七个部分：

```
1. 概述 (Overview)
   └─ 一句话描述 + 背景动机 + 用户故事

2. 目标与非目标 (Goals & Non-Goals)
   ├─ Goals: 这次要达成的具体目标（3-5 条）
   └─ Non-Goals: 明确不做的事情（防止范围蔓延）

3. 技术设计 (Technical Design)
   ├─ 架构图（可用 ASCII 图或 Mermaid）
   ├─ 数据模型 / API 契约
   ├─ 关键算法或流程
   └─ 技术选型理由

4. 接口定义 (API/Interface Contract)
   ├─ 输入/输出 Schema（JSON Schema / Proto / TypeScript 类型）
   └─ 错误码和异常语义

5. 测试策略 (Testing Strategy)
   ├─ 单元测试覆盖目标
   ├─ 集成测试场景
   └─ E2E 测试关键路径

6. 上线计划 (Rollout Plan)
   ├─ 分阶段发布策略
   ├─ 回滚方案
   └─ 监控指标

7. 开放问题 (Open Questions)
   └─ 当前不确定、需要后续决策的事项
```

### 2.2 与 Hermes 工具链协作

```bash
# 加载相关技能形成流水线
/skill requirement-analyzer  # 先澄清需求
/skill spec-driven-dev       # 再撰写规格

# 利用 Hermes 的文件工具
# 将 Spec 写入项目目录
# write_file("docs/specs/feature-x.md", spec_content)

# 利用 Hermes 的 web_search 进行技术调研
# web_search("best practices for ...")
```

### 2.3 自进化机制

1. **规格准确性追踪**：记录开发过程中因规格错误导致的返工次数
2. **模板优化**：根据项目类型（API/CLI/前端/ML）自动调整 Spec 模板的侧重点
3. **遗漏检测**：分析哪些章节在实际开发中被证明最重要/最常被遗漏
4. **自动补全建议**：基于历史项目数据，在新 Spec 中提示常见遗漏项

### 2.4 身份感知

- 读取 `SOUL.md` 中定义的技术偏好（如 "偏好函数式编程" 或 "偏好简洁的代码"）
- 在 Spec 的 "技术设计" 章节体现这些偏好
- 在 "代码风格" 部分自然地融入 Agent 的人设风格

## 3. 门禁标准

- [ ] 七个章节完整，无跳过的占位符（如 "TODO"）
- [ ] 每个 Goal 都有对应的可验证验收标准
- [ ] API 契约包含完整的输入验证规则和错误语义
- [ ] 至少识别了 2 个需要后续决策的开放问题
- [ ] 如果涉及数据库变更，包含迁移计划
- [ ] Spec 已通过 `code-quality-guardian` 的文档审查
- [ ] 用户已审阅并批准 Spec

## 4. 常见逃避借口与反驳

| 借口 | 反驳 |
|------|------|
| "这功能很简单，不需要 Spec" | 简单功能的边界往往最模糊。一份 10 行的 Spec 就能避免 100 行的返工。 |
| "敏捷开发不需要文档" | 敏捷不等于无文档。敏捷追求 "刚好够的文档"——Spec 就是那个 "刚好够"。 |
| "我可以边写代码边想设计" | 边写边想 = 没有设计。代码会成为设计的受害者，而不是实现者。 |
| "Spec 写完就过时了" | 好的 Spec 是活文档——在发现新信息时更新，而不是写成后抛弃。 |
| "AI 写 Spec 不够好" | 这正是本技能的价值——提供结构化框架让 AI 写出工程师级别的 Spec。 |
