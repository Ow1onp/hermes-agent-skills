# ⚡ HermesHub

> Professional domain Agent marketplace for Hermes Agent — a plug-and-play AI specialist task force.

[中文文档](./README.zh-CN.md) | English

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Hermes Compatible](https://img.shields.io/badge/hermes--agent-compatible-8A2BE2)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills](https://img.shields.io/badge/standard-agent--skills-orange)](https://github.com/addyosmani/agent-skills)
[![Version](https://img.shields.io/badge/version-1.0.0-informational)](https://github.com/Ow1onp/hermes-agent-skills/releases)

---

```
  Python Pro                           DevOps SRE
 ┌──────────────────────────┐        ┌──────────────────────────┐
 │ Code Review · Performance │        │ CI/CD Pipeline · Docker  │
 │ Test Gen · Scaffold · Type│  ──▶   │ K8s Deploy · Log Analyze │
 │ Persona + Skills System   │        │ Persona + Skills System   │
 └──────────────────────────┘        └──────────────────────────┘
```

## ✨ Features

- **🎯 Plug-and-Play** — Each Agent is a self-contained bundle of persona, memory, and skills. Load only what you need — no pollution of the conversation context.
- **🧩 Progressive Loading** — Skills are injected into context only when activated by user intent. Token consumption stays low while capability scales.
- **📋 Declarative Identity** — Agent identity is defined through persona.md (behavioral boundaries) and memory.md (domain constraints), aligned with Hermes Agent's native personality mechanism.
- **🔒 Security Built-In** — Every Skill includes input validation, structured error handling, and audit-ready output. No hardcoded credentials, no command injection surfaces.

## 🧠 What is HermesHub?

HermesHub draws architectural inspiration from the [wshobson/agents](https://github.com/wshobson/agents) ecosystem — plugin-based isolation, progressive context loading, and tiered model strategy — but is purpose-built for Hermes Agent. Each Agent is a complete capability package, not just a prompt template:

- **Persona** — "Who you are": behavioral rules, tone, tool constraints, domain scope
- **Memory** — "What you know": hard constraints, ecosystem facts, security rules, anti-patterns
- **Skills** — "What you can do": JSON Schema interfaces + Python implementations, dispatched by Hermes' native tool system

## 📦 Agents

| Agent | Domain | Skills | Status |
|-------|--------|--------|--------|
| **Python Pro** | Python 3.11+ development expert | Code review, performance profiling, test generation, project scaffolding, type checking | ✅ v0.1.0 |
| **DevOps SRE** | Infrastructure & site reliability | CI/CD generation, Docker optimization, K8s deployment, log analysis | ✅ v0.1.0 |

### Python Pro — Skills

| Skill | Description | Activation |
|-------|-------------|------------|
| `code_review.py` | Security audit + PEP 8 + performance anti-patterns + maintainability scoring | "Review this code for issues" |
| `performance_profile.py` | CPU / memory / I/O / async bottleneck analysis | "Why is this code slow?" |
| `test_generator.py` | Pytest generation from function signatures and docstrings | "Write tests for this function" |
| `package_scaffold.py` | pyproject.toml + directory layout + Docker + CI generation | "Create a new Python project" |
| `type_checker.py` | Type annotation audit + auto-generation + Protocol suggestions | "Add type hints to this code" |

### DevOps SRE — Skills

| Skill | Description | Activation |
|-------|-------------|------------|
| `ci_cd_generator.py` | GitHub Actions / GitLab CI pipeline generation | "Set up CI/CD for this project" |
| `docker_optimizer.py` | Dockerfile review + multi-stage build optimization + hardening | "Optimize my Dockerfile" |
| `k8s_deployer.py` | Deployment + Service + Ingress + HPA + PDB generation | "Generate K8s manifests" |
| `log_analyzer.py` | JSON / plaintext / Apache / Nginx / syslog log analysis | "Analyze these error logs" |

## 🚀 Quick Start

### Prerequisites

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed and configured
- Python 3.9+ (skills are tested on Python 3.9–3.12)

### Installation

```bash
# Clone the repository
git clone https://github.com/Ow1onp/HermesHub.git

# Install the Agent(s) you need into Hermes' skills directory
cp -r HermesHub/agents/python-pro ~/.hermes/skills/python-pro/
cp -r HermesHub/agents/devops-sre ~/.hermes/skills/devops-sre/
```

### Usage

**Option 1: Load in-session**

In an active Hermes Agent session:
```
/skill python-pro
```

The Agent immediately adopts the Python Pro persona and gains access to all five Python skills.

**Option 2: Preload at startup**

```bash
hermes -s python-pro -s devops-sre
```

**Option 3: As a scheduled specialist**

```bash
hermes cron create "every 4h" \
  --skills python-pro \
  --prompt "Review the latest Python commits and generate a security report"
```

### Skill Activation

Skills are progressively loaded — they activate only when your intent matches. For example:

> **You:** "Review this code for security vulnerabilities"
> → Hermes loads `code_review.py` skill

> **You:** "Generate a Dockerfile for my FastAPI app"
> → Hermes loads `docker_optimizer.py` skill

## 🔗 Deep Hermes Agent Integration

HermesHub leverages Hermes Agent's native mechanisms:

- **Persona injection** — `persona.md` files are compatible with Hermes' personality system
- **Memory persistence** — `memory.md` constraints can be persisted via the `memory` tool, surviving across sessions
- **Skill auto-registration** — Each `.py` skill uses the `SCHEMA` + `handler()` pattern, directly compatible with Hermes' tool dispatch
- **Profile isolation** — Create separate Hermes Profiles per Agent for completely isolated execution environments

## 📂 Project Structure

```
HermesHub/
├── README.md                     # English documentation (this file)
├── README.zh-CN.md               # Chinese documentation
├── LICENSE                       # MIT
├── agents/
│   ├── python-pro/
│   │   ├── persona.md            # Python Pro identity
│   │   ├── memory.md             # Domain constraints & ecosystem knowledge
│   │   └── skills/               # 5 skills (~89 KB)
│   └── devops-sre/
│       ├── persona.md
│       ├── memory.md
│       └── skills/               # 4 skills (~54 KB)
├── tests/
│   ├── python-pro/test_cases.md  # 22 test cases
│   └── devops-sre/test_cases.md  # 16 test cases
└── docs/
    └── architecture.md           # Design decisions & architecture
```

## 📄 License

MIT — see [LICENSE](./LICENSE) for details.
