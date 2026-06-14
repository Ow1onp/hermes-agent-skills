# ⚡ Hermes Agent Skills

> 为 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 量身打造的开箱即用技能库——让 AI 助理真正掌握工程师的工作流。

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Hermes Compatible](https://img.shields.io/badge/hermes--agent-compatible-8A2BE2)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills Standard](https://img.shields.io/badge/standard-agent--skills-orange)](https://github.com/addyosmani/agent-skills)
[![Tests](https://img.shields.io/badge/tests-46%2F46%20passing-brightgreen)](tests/)
[![Version](https://img.shields.io/badge/version-1.0.0-informational)](https://github.com/Ow1onp/hermes-agent-skills/releases)

---

```
  DEFINE           BUILD          VERIFY           SHIP           EVOLVE
 ┌────────┐     ┌────────┐     ┌─────────┐     ┌────────┐     ┌──────────┐
 │需求分析 │ ──▶ │TDD 开发│ ──▶ │多模态调试│ ──▶ │CI/CD   │ ──▶ │自进化策展 │
 │规格驱动 │     │        │     │代码门禁  │     │编排    │     │身份感知  │
 └────────┘     └────────┘     └─────────┘     └────────┘     └──────────┘
```

## ✨ 特点

- **🧬 自进化** — 技能不是静态文件。内置的 `EvolutionEngine` 从五个维度评估技能健康度，自动检测过时技能并提出改进建议，直接对接 Hermes 的 `/curator` 学习循环。
- **🎭 身份感知** — 读取 `SOUL.md` 文件，动态适配代码风格、注释密度、命名规范和架构决策，让产出的代码真正"像这个人写的"。
- **🔗 命令体系原生** — 每个技能都深度引用 Hermes 独有的工具 (`/skills`、`delegate_task`、`browser`+`terminal`+`vision` 联动、持久记忆)，而非泛泛的通用指令。
- **📐 开放标准** — 全部 `SKILL.md` 文件遵循 [Agent Skills 开放标准](https://github.com/addyosmani/agent-skills)，由自带的 `SkillValidator` 保证格式合法性。

## 🧠 什么是「Agent Skills 开放标准」？

Agent Skills 是一套由 Addy Osmani 提出的规范，将资深工程师的工作流、质量门禁和最佳实践编码为结构化的 Markdown 文件（`SKILL.md`）。AI Agent 加载这些技能后，就能在每个开发阶段一致地遵循高标准——而非凭"感觉"做事。

`hermes-agent-skills` 在此基础上，充分发挥 Hermes Agent 的独特能力：

| 标准能力 | Hermes 增强 |
|---------|------------|
| 静态技能文件 | 自进化闭环——技能随使用自动优化 |
| 通用 Agent 指令 | Hermes 工具链深度引用 (`/curator`, `delegate_task`) |
| 统一风格输出 | 身份感知——SOUL.md 驱动个性化适配 |

## 📦 技能列表

| 技能 | 阶段 | 描述 | Hermes 专有特性 |
|:---|:---|:---|:---|
| `requirement-analyzer` | 定义 | 五轮结构化对话，澄清模糊需求至 95% 清晰度 | 持久记忆跨会话保持上下文 |
| `spec-driven-dev` | 规格 | 七要素 Spec 文档，代码先行 | `/skills` 串联形成工作流 |
| `test-driven-dev` | 构建 | RED-GREEN-REFACTOR 循环 + 测试金字塔 | `delegate_task` 并行测试执行 |
| `debugger-coordinator` | 验证 | 五步调试法 + 多模态工具协调 | `browser`+`terminal`+`vision` 联动 |
| `code-quality-guardian` | 评审 | 六轴质量门禁（安全/复杂度/风格/覆盖/文档/依赖） | `patch` 自动修复 + `/curator` 追踪 |
| `cicd-orchestrator` | 交付 | GitHub Actions 流水线生成与优化 | `cronjob` 定时 + `webhook` 触发 |
| `skill-curator` | 进化 | 四阶段策展：采集→分析→建议→执行 | 直接对接 `/curator` 系统 |
| `persona-aware-coding` | 身份 | SOUL.md 驱动的全流程代码风格适配 | Hermes 原生身份系统 |

## 🚀 快速开始

**方式一：通过 `hermes skills tap` 安装（推荐）**

```bash
hermes skills tap add Ow1onp/hermes-agent-skills
hermes skills browse          # 浏览全部技能
hermes skills install requirement-analyzer
```

**方式二：克隆到本地**

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
cp -r hermes-agent-skills/skills/* ~/.hermes/skills/
```

**方式三：会话中直接加载**

在 Hermes 对话中输入：

```bash
/skill requirement-analyzer
/skill test-driven-dev
```

## 🔗 深度适配 Hermes Agent

三项能力让这套技能不同于通用的 agent-skills：

**1. 自进化闭环**

```python
from hermes_agent_skills import EvolutionEngine

engine = EvolutionEngine()
engine.record_task(TaskExecutionRecord(
    task_description="修复登录超时 Bug",
    skills_used=["debugger-coordinator", "test-driven-dev"],
    retries=2, user_corrections=1, success=True, duration_seconds=300,
))
# 分析 → 如果同类超时 Bug 出现 3 次以上，建议创建专项技能
suggestions = engine.analyze()
```

**2. SOUL.md 身份感知**

```yaml
# ~/.hermes/SOUL.md
name: "严谨架构师"
coding_style:
  naming: snake_case
  prefer: [type_hints, custom_exceptions, immutability]
comment_style: "代码即文档"
architecture_preference: "六边形架构"
```

加载 `persona-aware-coding` 后，所有生成的代码、注释、文档将自动适配此风格。

**3. 斜杠命令体系**

```bash
/skill requirement-analyzer   # 加载技能
/curator status               # 查看技能健康度
/curator run                  # 触发自进化审查
```

## 📂 项目结构

```
hermes-agent-skills/
├── skills/                  # 技能文件（Agent Skills 开放标准）
│   ├── define/              # 定义阶段
│   ├── build/               # 构建阶段
│   ├── verify/              # 验证阶段
│   ├── ship/                # 交付阶段
│   └── evolve/              # 进化阶段
├── src/hermes_agent_skills/ # Python 核心库
│   ├── validator.py         # SKILL.md 验证器
│   ├── evolution.py         # 自进化引擎
│   └── soul_reader.py       # SOUL.md 解析器
├── tests/                   # 单元测试
├── scripts/                 # 安装 & 工具脚本
└── .github/workflows/       # CI/CD
```

## 📄 许可证

[MIT](LICENSE) © [Ow1onp](https://github.com/Ow1onp)

## 🤝 贡献

技能文件采用纯 Markdown 格式，欢迎提交 Issue 和 Pull Request。

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
# 在 skills/<阶段>/<名称>/SKILL.md 下创建你的技能
# 验证：pytest tests/test_validator.py -v
# 提交 PR
```
