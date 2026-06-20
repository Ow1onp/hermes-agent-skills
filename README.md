# ⚡ Hermes Agent Skills

> Production-grade skills + domain agents for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — self-evolving, persona-aware, slash-command native.

[中文文档](./README.zh-CN.md) | English

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Hermes Compatible](https://img.shields.io/badge/hermes--agent-compatible-8A2BE2)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills Standard](https://img.shields.io/badge/standard-agent--skills-orange)](https://github.com/addyosmani/agent-skills)
[![Tests](https://img.shields.io/badge/tests-46%2F46%20passing-brightgreen)](tests/)
[![Version](https://img.shields.io/badge/version-1.1.0-informational)](https://github.com/Ow1onp/hermes-agent-skills/releases)

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
| **Python Pro** | Python 3.11+ | Code Review · Performance Profiling · Test Generation · Scaffolding · Type Checking | `cp -r agents/python-pro ~/.hermes/skills/` |
| **DevOps SRE** | Infrastructure | CI/CD Pipeline · Docker Optimization · K8s Deploy · Log Analysis | `cp -r agents/devops-sre ~/.hermes/skills/` |

Domain agents use the `SCHEMA` + `handler()` pattern directly compatible with Hermes's tool dispatch system. Skills activate only when your intent matches — no context pollution.

## 🚀 Quick Start

```bash
# Recommended: install via hermes skills tap
hermes skills tap add Ow1onp/hermes-agent-skills
hermes skills browse
hermes skills install requirement-analyzer

# Or clone locally
git clone https://github.com/Ow1onp/hermes-agent-skills.git

# Load a workflow skill
/skill requirement-analyzer

# Load a domain agent
/skill python-pro
```

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
├── agents/                  # Domain agents (from HermesHub)
│   ├── python-pro/          # persona.md + memory.md + 5 skills
│   └── devops-sre/          # persona.md + memory.md + 4 skills
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
