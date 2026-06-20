# ⚡ Hermes Agent Skills

> 为 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 量身打造的开箱即用技能库——让 AI 助理真正掌握工程师的工作流。

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Hermes Compatible](https://img.shields.io/badge/hermes--agent-compatible-8A2BE2)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills Standard](https://img.shields.io/badge/standard-agent--skills-orange)](https://github.com/addyosmani/agent-skills)
[![Tests](https://img.shields.io/badge/tests-46%2F46%20passing-brightgreen)](tests/)
[![Version](https://img.shields.io/badge/version-1.1.0-informational)](https://github.com/Ow1onp/hermes-agent-skills/releases)

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

## 📦 Skill 工作流（8 个 SKILL.md）

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

## 🤖 Domain Agents（来自 HermesHub）

专业领域 Agent，每个包含 persona + memory + 可被 Hermes 工具系统调度的 Python Skills。

| Agent | 领域 | Skills | 安装 |
|-------|------|--------|------|
| **Python Pro** | Python 3.11+ 开发 | Code Review · Performance Profiling · Test Generation · Scaffolding · Type Checking | `cp -r agents/python-pro ~/.hermes/skills/` |
| **DevOps SRE** | 基础设施 & SRE | CI/CD Pipeline · Docker Optimization · K8s Deploy · Log Analysis | `cp -r agents/devops-sre ~/.hermes/skills/` |

## 🚀 快速开始

```bash
# 通过 hermes skills tap 安装（推荐）
hermes skills tap add Ow1onp/hermes-agent-skills

# 或克隆到本地
git clone https://github.com/Ow1onp/hermes-agent-skills.git

# 加载技能
/skill requirement-analyzer
/skill python-pro
```

## 📂 项目结构

```
hermes-agent-skills/
├── skills/                  # SKILL.md 工作流技能（Agent Skills 开放标准）
│   ├── define/ · build/ · verify/ · ship/ · evolve/
├── agents/                  # Domain Agents（来自 HermesHub）
│   ├── python-pro/          # persona.md + memory.md + 5 skills
│   └── devops-sre/          # persona.md + memory.md + 4 skills
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
