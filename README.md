# ⚡ Hermes Agent Skills

> Production-grade skills + domain agents for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — self-evolving, persona-aware, slash-command native.

[中文文档](./README.zh-CN.md) | English

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
 │  Spec  │ ──▶ │  TDD   │ ──▶ │  Debug  │ ──▶ │ CI/CD  │ ──▶ │ Curator  │
 │Design  │     │  Code  │     │  Gate   │     │ Deploy │     │ Persona  │
 └────────┘     └────────┘     └─────────┘     └────────┘     └──────────┘
```

## ✨ Features

- **🧬 Self-evolving** — Skills aren't static. The built-in `EvolutionEngine` tracks 5 health dimensions (usage frequency, success rate, corrections, freshness, command validity), scores each skill, and surfaces improvement suggestions through Hermes's native `/curator` system.
- **🎭 Persona-aware** — Drop a `SOUL.md` in your Hermes config and every code-generating skill adapts — naming, comments, architecture. Your agent writes code that looks like *you* wrote it.
- **🔗 Hermes-native** — Every skill leverages Hermes-specific tools: `delegate_task`, `browser`+`terminal`+`vision` coordination, persistent memory, `/curator`, `cronjob`, `webhook`.
- **📐 Open standard** — All `SKILL.md` files follow the [Agent Skills Open Standard](https://github.com/addyosmani/agent-skills). Validated by the bundled `SkillValidator`.

## 🧪 Hermes v2 Beta — Task-First Interface

> v1.1.0 remains stable and supported alongside v2.

Hermes v2 adds a natural-language frontend: say what you want, the system handles roles, skills, and constraints automatically.

```bash
# v2 Beta — natural language
python -m hermes_v2.cli "帮我发布项目"
python -m hermes_v2.cli "创建一个 FastAPI 项目"
python -m hermes_v2.cli "修复这个错误"

# v1 — always available
hermes-skill validate skills/
```

**Three modes:** Beginner (auto) · Advanced (choose persona) · Expert (pure v1). See [Hermes v2 MVP docs](docs/hermes-v2-mvp.md).

**v1 is unchanged.** v2 is additive — all existing skills, CLI commands, and workflows work as before.

## 📦 Workflow Skills (8 SKILL.md)

| Skill | Phase | Description | Hermes-specific |
|:---|:---|:---|:---|
| `requirement-analyzer` | Define | Structured multi-turn requirement extraction | Cross-session persistent memory |
| `spec-driven-dev` | Define | Seven-section PRD before any code | `/skills` pipeline chaining |
| `test-driven-dev` | Build | RED-GREEN-REFACTOR + test pyramid | `delegate_task` parallel testing |
| `debugger-coordinator` | Verify | Multi-modal debugging (5-step method) | `browser`+`terminal`+`vision` coordination |
| `code-quality-guardian` | Verify | Six-axis quality gate | `patch` auto-fix + `/curator` tracking |
| `cicd-orchestrator` | Ship | GitHub Actions workflow generation | `cronjob` + `webhook` triggers |
| `skill-curator` | Evolve | Collect → Analyze → Propose → Execute | Direct `/curator` integration |
| `persona-aware-coding` | Evolve | SOUL.md-driven style adaptation | Native Hermes identity system |

## 🤖 Domain Agents (from HermesHub)

Plug-and-play specialist agents — each is a self-contained bundle of persona, memory, and dispatchable Python skills.

| Agent | Domain | Skills | Install |
|-------|--------|--------|---------|
| **Python Pro** | Python 3.11+ | Code Review · Performance Profiling · Test Generation · Scaffolding · Type Checking | `hermes skills install Ow1onp/hermes-agent-skills/skills/agents/python-pro` |
| **DevOps SRE** | Infrastructure | CI/CD Pipeline · Docker Optimization · K8s Deploy · Log Analysis | `hermes skills install Ow1onp/hermes-agent-skills/skills/agents/devops-sre` |

Domain agents use the `SCHEMA` + `handler()` pattern directly compatible with Hermes's tool dispatch system. Skills activate only when your intent matches — no context pollution.

## 🚀 Quick Start

```bash
# Recommended: install via hermes skills tap
hermes skills tap add Ow1onp/hermes-agent-skills
hermes skills browse
hermes skills install Ow1onp/hermes-agent-skills/skills/define/requirement-analyzer
hermes skills install Ow1onp/hermes-agent-skills/skills/agents/python-pro
hermes skills install Ow1onp/hermes-agent-skills/skills/agents/devops-sre

# Load a workflow skill
/skill requirement-analyzer

# Load domain agents
/skill python-pro
/skill devops-sre
```

`hermes skills tap add Ow1onp/hermes-agent-skills` points Hermes at the repo's
`skills/` tree. Workflow skills live under phase folders such as `define/` and
`build/`; domain agents are exposed through installable wrappers under
`skills/agents/`. The top-level `agents/` tree remains the source bundle for
agent persona, memory, and handler code. Manual copying to `~/.hermes/skills/`
is only a local debugging fallback.

Short-name installs such as `hermes skills install python-pro` may work once
Hermes's registry/index resolver has refreshed, but the full GitHub identifiers
above are the deterministic install path.

## 🔗 Hermes Integration

```python
# Self-evolution engine
from hermes_agent_skills import EvolutionEngine
engine = EvolutionEngine()
engine.record_task(...)
suggestions = engine.analyze()  # detects stale skills, recurring patterns

# Persona-aware coding
profile = SoulReader().read("~/.hermes/SOUL.md")
print(profile.get_code_prompt_hint())
```

## 📂 Project Structure

```
hermes-agent-skills/
├── skills/                  # SKILL.md workflow skills (Agent Skills standard)
│   ├── define/ · build/ · verify/ · ship/ · evolve/
│   └── agents/              # Hermes-installable domain agent wrappers
├── agents/                  # Domain agents (from HermesHub)
│   ├── python-pro/          # SKILL.md + persona.md + memory.md + 5 handlers
│   └── devops-sre/          # SKILL.md + persona.md + memory.md + 4 handlers
├── src/hermes_agent_skills/ # Python library
│   ├── validator.py         # SKILL.md validator
│   ├── evolution.py         # Self-evolution engine
│   └── soul_reader.py       # SOUL.md persona parser
├── src/cli/                 # hermes-skill CLI (Typer)
├── tests/                   # 46 tests, all passing
├── scripts/                 # Utility scripts
└── .github/workflows/       # CI/CD (lint + test matrix + validate + security)
```

## 📄 License

[MIT](LICENSE) © [Ow1onp](https://github.com/Ow1onp)

## 🤝 Contributing

Skills are plain Markdown. Issues and PRs welcome.

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
# Create your skill at skills/<phase>/<name>/SKILL.md
pytest tests/test_validator.py -v
# Open a PR
```
