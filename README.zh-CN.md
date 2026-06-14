# ⚡ HermesHub

> 为 Hermes Agent 打造的即插即用专业领域 Agent 集合

[English](./README.md) | 中文文档

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Hermes Compatible](https://img.shields.io/badge/hermes--agent-compatible-8A2BE2)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills](https://img.shields.io/badge/standard-agent--skills-orange)](https://github.com/addyosmani/agent-skills)
[![Version](https://img.shields.io/badge/version-1.0.0-informational)](https://github.com/Ow1onp/hermes-agent-skills/releases)

---

```
  Python Pro                           DevOps SRE
 ┌──────────────────────────┐        ┌──────────────────────────┐
 │ 代码审查 · 性能分析       │        │ CI/CD 流水线 · Docker     │
 │ 测试生成 · 脚手架 · 类型  │  ──▶   │ K8s 部署 · 日志分析       │
 │ Persona + Skills 体系     │        │ Persona + Skills 体系     │
 └──────────────────────────┘        └──────────────────────────┘
```

## ✨ 特点

- **🎯 即插即用** — 每个 Agent 是独立的 persona + memory + skills 套装，按需加载，不污染对话上下文
- **🧩 渐进式加载** — Skills 仅在用户意图匹配时注入上下文，保持低 token 消耗、高响应速度
- **📋 声明式定义** — persona.md（身份锚定）和 memory.md（领域约束）通过 Markdown 声明，与 Hermes Agent 原生机制对齐
- **🔒 安全内建** — 所有 Skill 包含输入验证、结构化错误处理和审计输出，无硬编码凭证

## 🧠 什么是 HermesHub？

HermesHub 借鉴了 [wshobson/agents](https://github.com/wshobson/agents) 生态的架构理念（插件化隔离、渐进式上下文、分层模型策略），但专为 Hermes Agent 原生打造。每个 Agent 不是简单的 prompt 模板，而是完整的能力包：

- **Persona（身份）** — "你是谁"、"禁止做什么"、"必须怎么做"
- **Memory（记忆）** — 领域硬约束、安全规则、反模式知识、格式规范
- **Skills（技能）** — JSON Schema 接口 + Python 实现，通过 Hermes 工具调度系统触发

## 📦 已包含的 Agent

| Agent | 领域 | Skills | 状态 |
|-------|------|--------|------|
| **Python Pro** | Python 3.11+ 开发专家 | 代码审查、性能分析、测试生成、项目脚手架、类型检查 | ✅ v0.1.0 |
| **DevOps SRE** | 基础设施与站点可靠性 | CI/CD 生成、Docker 优化、K8s 部署、日志分析 | ✅ v0.1.0 |

### Python Pro — 技能列表

| Skill | 描述 | 触发条件 |
|-------|------|----------|
| `code_review.py` | 安全审计 + PEP 8 + 性能反模式 + 可维护性评分 | "审查这段代码" |
| `performance_profile.py` | CPU / 内存 / IO / 异步瓶颈分析 | "这段代码为什么慢？" |
| `test_generator.py` | 从函数签名和 docstring 生成 pytest 测试 | "为这个函数写测试" |
| `package_scaffold.py` | pyproject.toml + 目录结构 + Docker + CI | "创建新的 Python 项目" |
| `type_checker.py` | 类型注解审计 + 自动生成 + Protocol 建议 | "给这段代码加类型注解" |

### DevOps SRE — 技能列表

| Skill | 描述 | 触发条件 |
|-------|------|----------|
| `ci_cd_generator.py` | GitHub Actions / GitLab CI 流水线生成 | "为这个项目配置 CI/CD" |
| `docker_optimizer.py` | Dockerfile 审查 + 多阶段构建 + 安全加固 | "优化我的 Dockerfile" |
| `k8s_deployer.py` | Deployment + Service + Ingress + HPA + PDB | "生成 K8s 部署清单" |
| `log_analyzer.py` | JSON / 文本 / Apache / Nginx / syslog 日志分析 | "分析这些错误日志" |

## 🚀 快速开始

### 前提条件

- 已安装 [Hermes Agent](https://github.com/NousResearch/hermes-agent)
- Python 3.9+（Skills 在 Python 3.9–3.12 上测试通过）

### 安装

```bash
# 克隆仓库
git clone https://github.com/Ow1onp/HermesHub.git

# 将需要的 Agent 安装到 Hermes skills 目录
cp -r HermesHub/agents/python-pro ~/.hermes/skills/python-pro/
cp -r HermesHub/agents/devops-sre ~/.hermes/skills/devops-sre/
```

### 使用方式

**方式 1：会话中加载**

在 Hermes Agent 会话中输入：
```
/skill python-pro
```

Agent 立即获得 Python Pro 的身份和全部五项技能。

**方式 2：启动时预加载**

```bash
hermes -s python-pro -s devops-sre
```

**方式 3：作为定时专业 Agent**

```bash
hermes cron create "每4小时" \
  --skills python-pro \
  --prompt "审查最近的 Python 提交并生成安全报告"
```

### Skill 激活方式

Skill 是渐进式加载的 — 只有当你提出匹配的意图时才会触发。例如：

> **你：** "帮我审查这段代码的安全性"
> → Hermes 自动加载 `code_review.py` skill

> **你：** "给我的 FastAPI 项目生成 Dockerfile"
> → Hermes 自动加载 `docker_optimizer.py` skill

## 🔗 深度适配 Hermes Agent

HermesHub 深度利用了 Hermes Agent 的以下机制：

- **Persona 注入** — `persona.md` 文件兼容 Hermes 的 personality 系统
- **Memory 持久化** — `memory.md` 约束可通过 `memory` 工具持久化，跨会话生效
- **Skill 自注册** — 每个 `.py` skill 使用 `SCHEMA` + `handler()` 模式，直接对接 Hermes 工具调度
- **Profile 隔离** — 可为不同 Agent 创建独立的 Hermes Profile，实现完全隔离

## 📂 项目结构

```
HermesHub/
├── README.md                     # 英文文档
├── README.zh-CN.md               # 中文文档（本文件）
├── LICENSE                       # MIT
├── agents/
│   ├── python-pro/
│   │   ├── persona.md            # Python Pro 身份定义
│   │   ├── memory.md             # 领域约束与生态知识
│   │   └── skills/               # 5 个技能 (~89 KB)
│   └── devops-sre/
│       ├── persona.md
│       ├── memory.md
│       └── skills/               # 4 个技能 (~54 KB)
├── tests/
│   ├── python-pro/test_cases.md  # 22 个测试用例
│   └── devops-sre/test_cases.md  # 16 个测试用例
└── docs/
    └── architecture.md           # 架构设计文档
```

## 📄 许可证

MIT — 详见 [LICENSE](./LICENSE)。
