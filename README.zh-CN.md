# ⚡ Hermes Agent Skills

> 为 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 量身打造的生产级技能库与领域 Agent 集合——自进化、身份感知、斜杠命令原生。

[English](./README.md) | 中文文档

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Hermes Compatible](https://img.shields.io/badge/hermes--agent-compatible-8A2BE2)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills Standard](https://img.shields.io/badge/standard-agent--skills-orange)](https://github.com/addyosmani/agent-skills)
[![Tests](https://img.shields.io/badge/tests-224%2F224%20passing-brightgreen)](tests/)
[![Version](https://img.shields.io/badge/v1-1.1.0-informational)](https://github.com/Ow1onp/hermes-agent-skills/releases)
[![v2](https://img.shields.io/badge/v2-2.0.0-blue)](docs/hermes-v2-mvp.md)

---

```
  DEFINE           BUILD          VERIFY           SHIP           EVOLVE
 ┌────────┐     ┌────────┐     ┌─────────┐     ┌────────┐     ┌──────────┐
 │需求分析 │ ──▶ │TDD 开发│ ──▶ │多模态调试│ ──▶ │CI/CD   │ ──▶ │自进化策展 │
 │规格驱动 │     │        │     │代码门禁  │     │编排    │     │身份感知  │
 └────────┘     └────────┘     └─────────┘     └────────┘     └──────────┘
```

## ✨ 特点

- **🧬 自进化** — 技能不是静态文件。内置 `EvolutionEngine` 从五个维度评估技能健康度（使用频率、成功率、纠正次数、新鲜度、命令有效性），自动检测过时技能并提出改进建议，直接对接 Hermes 的 `/curator` 学习循环。
- **🎭 身份感知** — 在 Hermes 配置中放置 `SOUL.md`，所有代码生成技能自动适配你的风格：命名规范、注释密度、架构偏好。让 Agent 写出的代码真正"像你写的"。
- **🔗 命令体系原生** — 每个技能深度引用 Hermes 独有工具：`delegate_task`、`browser`+`terminal`+`vision` 联动、持久记忆、`/curator`、`cronjob`、`webhook`。
- **📐 开放标准** — 全部 `SKILL.md` 文件遵循 [Agent Skills 开放标准](https://github.com/addyosmani/agent-skills)，由自带的 `SkillValidator` 保证格式合法性。

## 🧪 Hermes v2 Beta — 任务优先界面

> v1.1.0 与 v2 并行可用，保持稳定。

Hermes v2 增加自然语言前端：直接说需求，系统自动处理角色、技能和约束。

```bash
# v2 Beta — 自然语言
python -m hermes_v2.cli "帮我发布项目"
python -m hermes_v2.cli "创建一个 FastAPI 项目"
python -m hermes_v2.cli "修复这个错误"

# v1 — 始终可用
hermes-skill validate skills/
```

**三种模式：** 入门（自动）· 高级（指定角色）· 专家（纯 v1）。详见 [Hermes v2 MVP 文档](docs/hermes-v2-mvp.md)。

**v1 无任何改动。** v2 是纯增量——所有现有技能、CLI 命令和工作流保持不变。

## 📦 工作流技能（8 个 SKILL.md）

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

## 🤖 领域 Agent（来自 HermesHub）

即插即用的专业 Agent——每个都是 persona + memory + 可调度 Python 技能的独立套装。

| Agent | 领域 | 技能 | 安装 |
|-------|------|------|------|
| **Python Pro** | Python 3.11+ 开发 | 代码审查 · 性能分析 · 测试生成 · 脚手架 · 类型检查 | `hermes skills install python-pro` |
| **DevOps SRE** | 基础设施 & SRE | CI/CD 流水线 · Docker 优化 · K8s 部署 · 日志分析 | `hermes skills install devops-sre` |

领域 Agent 使用 `SCHEMA` + `handler()` 模式，直接兼容 Hermes 的工具调度系统。技能仅在用户意图匹配时激活——不污染对话上下文。

## 🚀 快速开始

```bash
# 推荐：通过 hermes skills tap 安装
hermes skills tap add Ow1onp/hermes-agent-skills
hermes skills browse
hermes skills install requirement-analyzer
hermes skills install python-pro
hermes skills install devops-sre

# 加载工作流技能
/skill requirement-analyzer

# 加载领域 Agent
/skill python-pro
/skill devops-sre
```

`hermes skills tap add Ow1onp/hermes-agent-skills` 会让 Hermes 扫描仓库的
`skills/` 树。工作流技能位于 `define/`、`build/` 等阶段目录；领域 Agent
通过 `skills/agents/` 下的 wrapper 暴露给 tap。顶层 `agents/` 仍保留为
persona、memory 和 handler 源包；手动复制到 `~/.hermes/skills/` 仅作为本地调试 fallback。

## 🔗 Hermes 深度集成

```python
# 自进化引擎
from hermes_agent_skills import EvolutionEngine
engine = EvolutionEngine()
engine.record_task(...)
suggestions = engine.analyze()  # 检测过时技能、重复错误模式

# 身份感知编码
profile = SoulReader().read("~/.hermes/SOUL.md")
print(profile.get_code_prompt_hint())
```

## 📂 项目结构

```
hermes-agent-skills/
├── skills/                  # SKILL.md 工作流技能（Agent Skills 开放标准）
│   ├── define/ · build/ · verify/ · ship/ · evolve/
│   └── agents/              # Hermes 可正式安装的领域 Agent wrapper
├── agents/                  # 领域 Agent（来自 HermesHub）
│   ├── python-pro/          # SKILL.md + persona.md + memory.md + 5 handlers
│   └── devops-sre/          # SKILL.md + persona.md + memory.md + 4 handlers
├── src/hermes_agent_skills/ # Python 核心库
│   ├── validator.py         # SKILL.md 验证器
│   ├── evolution.py         # 自进化引擎
│   └── soul_reader.py       # SOUL.md 人设解析器
├── src/cli/                 # hermes-skill CLI（Typer）
├── tests/                   # 46 个测试，全部通过
├── scripts/                 # 工具脚本
└── .github/workflows/       # CI/CD（lint + 测试矩阵 + 验证 + 安全扫描）
```

## 📄 许可证

[MIT](LICENSE) © [Ow1onp](https://github.com/Ow1onp)

## 🤝 贡献

技能文件采用纯 Markdown 格式，欢迎提交 Issue 和 Pull Request。

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
# 在 skills/<阶段>/<名称>/SKILL.md 下创建你的技能
pytest tests/test_validator.py -v
# 提交 PR
```
