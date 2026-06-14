# ⚡ HermesHub

> 为 Hermes Agent 打造的原生专业领域 Agent 市场 — 即插即用的 AI 专家特遣队

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Hermes Compatible](https://img.shields.io/badge/hermes-compatible-brightgreen.svg)](https://github.com/NousResearch/hermes-agent)
[![Version](https://img.shields.io/badge/version-0.1.0-informational.svg)](https://github.com/Ow1onp/hermes-hub)

---

```
  Python Pro                           DevOps SRE
 ┌──────────────────────────┐        ┌──────────────────────────┐
 │ Code Review · Performance │        │ CI/CD Pipeline · Docker  │
 │ Test Gen · Scaffold · Type│  ──▶   │ K8s Deploy · Log Analyze │
 │ Persona + Skills 体系     │        │ Persona + Skills 体系     │
 └──────────────────────────┘        └──────────────────────────┘
```

## ✨ 特点

- **🎯 即插即用** — 每个 Agent 是独立的 persona + memory + skills 套装，按需加载，不污染上下文
- **🧩 渐进式加载** — Skills 只在触发时才注入上下文，保持低 token 消耗、高响应速度
- **📋 声明式定义** — Persona（身份锚定）和 Memory（领域约束）通过 Markdown 声明，与 Hermes Agent 的人格机制一脉相承
- **🔒 安全内建** — 所有 Skill 包含输入验证、异常处理和审计日志，杜绝命令注入和密钥泄露

## 🧠 什么是 HermesHub？

HermesHub 参考了 wshobson/agents 项目的核心理念（插件化、渐进式上下文加载、分层模型策略），但专为 Hermes Agent 原生打造。每个 Agent 不是一个简单的 prompt template，而是一个完整的能力包：

- **Persona（身份）** — "你是谁"、"禁止做什么"、"必须怎么做"的行为红线
- **Memory（记忆）** — 领域硬约束、格式规则、生态知识
- **Skills（技能）** — 带 JSON Schema 接口和 Python 实现的工具能力

## 📦 Agent 列表

| Agent | 领域 | Skills | 状态 |
|-------|------|--------|------|
| **Python Pro** | Python 3.11+ 开发专家 | 代码审查、性能分析、测试生成、项目脚手架、类型检查 | ✅ v0.1.0 |
| **DevOps SRE** | 运维与站点可靠性工程 | CI/CD 生成、Docker 优化、K8s 部署、日志分析 | ✅ v0.1.0 |

### Python Pro Skills

| Skill | 描述 | 触发条件 |
|-------|------|----------|
| `code_review.py` | 安全审计 + PEP 8 + 性能反模式 + 可维护性检查 | 用户请求代码审查/安全检查 |
| `performance_profile.py` | CPU/内存/IO/异步性能瓶颈分析 | 用户询问性能优化/性能分析 |
| `test_generator.py` | 从函数签名和 docstring 生成 pytest 测试 | 用户需要生成测试/单元测试 |
| `package_scaffold.py` | 生成 pyproject.toml + 目录结构 + CI/Docker | 用户新建 Python 项目 |
| `type_checker.py` | 类型注解审计 + 自动生成 + Protocol 建议 | 用户检查类型安全/添加类型 |

### DevOps SRE Skills

| Skill | 描述 | 触发条件 |
|-------|------|----------|
| `ci_cd_generator.py` | GitHub Actions / GitLab CI 流水线生成 | 用户设置 CI/CD / 迁移 CI 平台 |
| `docker_optimizer.py` | Dockerfile 审查 + 多阶段构建 + 安全加固 | 用户优化 Docker / 审查 Dockerfile |
| `k8s_deployer.py` | Deployment + Service + Ingress + HPA + PDB | 用户部署到 Kubernetes |
| `log_analyzer.py` | JSON/文本/Apache/Nginx/syslog 日志分析 | 用户排查日志/分析错误/生成事件报告 |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/Ow1onp/hermes-hub.git

# 复制你想要使用的 Agent 到 Hermes skills 目录
cp -r hermes-hub/agents/python-pro ~/.hermes/skills/python-pro/
```

### 使用方式

**方式 1：在会话中手动加载**

在 Hermes Agent 会话中输入：
```
/skill python-pro
```

加载后，Agent 会读取该技能包中的 persona 和 skills，自动获得 Python Pro 的身份和能力。

**方式 2：启动时预加载**

```bash
hermes -s python-pro
```

**方式 3：作为 Cron Job 的专业 Agent**

```bash
hermes cron create "every 4h" \
  --skills python-pro \
  --prompt "审查最近提交的 Python 代码，生成安全报告"
```

### 加载特定 Skill

Skill 是渐进式加载的 — 只有当你提出匹配的意图时才会触发。例如：

> 用户："帮我审查这段代码的安全性"
> → Hermes 自动加载 `code_review.py` skill

> 用户："生成这个项目的 Dockerfile"
> → Hermes 自动加载 `docker_optimizer.py` skill

## 🔗 深度适配 Hermes Agent

HermesHub 深度利用了 Hermes Agent 的以下机制：

- **Persona 注入** — Persona 文件可以被 Hermes 的 personality 系统直接读取
- **Memory 持久化** — Memory 中的硬约束可以通过 `memory` 工具持久化，跨会话生效
- **Skill 自注册** — 每个 `.py` skill 文件通过 `SCHEMA` 和 `handler()` 模式与 Hermes 的工具调度系统对接
- **Profile 隔离** — 可以为不同 Agent 创建独立的 Hermes Profile，实现完全隔离的运行环境

## 📂 项目结构

```
hermes-hub/
├── README.md                     # 本文件
├── LICENSE                       # MIT
├── agents/
│   ├── python-pro/
│   │   ├── persona.md            # Python Pro 身份定义
│   │   ├── memory.md             # 领域硬约束与生态知识
│   │   └── skills/
│   │       ├── code_review.py    # 代码审查与安全审计
│   │       ├── performance_profile.py  # 性能分析
│   │       ├── test_generator.py       # 测试生成
│   │       ├── package_scaffold.py     # 项目脚手架
│   │       └── type_checker.py         # 类型检查
│   └── devops-sre/
│       ├── persona.md
│       ├── memory.md
│       └── skills/
│           ├── ci_cd_generator.py      # CI/CD 流水线
│           ├── docker_optimizer.py     # Docker 优化
│           ├── k8s_deployer.py         # K8s 部署
│           └── log_analyzer.py         # 日志分析
├── tests/
│   ├── python-pro/
│   │   └── test_cases.md         # 22 个测试用例
│   └── devops-sre/
│       └── test_cases.md         # 16 个测试用例
└── docs/
    └── architecture.md           # 架构设计文档
```

## 📄 许可证

MIT License © 2025 Ow1onp

## 🤝 贡献

欢迎 Issue 和 PR。如果你有专业领域想贡献新的 Agent，请参考 `docs/architecture.md` 中的开发规范。

---

**赞助支持：** [爱发电 @Gakkiopl](https://afdian.com/a/Gakkiopl)
