# ⚡ Hermes Agent Skills

> Production-grade skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — self-evolving, persona-aware, slash-command native.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Hermes Compatible](https://img.shields.io/badge/hermes--agent-compatible-8A2BE2)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills](https://img.shields.io/badge/standard-agent--skills-orange)](https://github.com/addyosmani/agent-skills)
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

- **🧬 Self-evolving** — skills improve over time via built-in `EvolutionEngine` (5-dimension health scoring, staleness detection, auto-suggestions). Feeds directly into Hermes's `/curator` loop.
- **🎭 Persona-aware** — reads `SOUL.md` to adapt naming, comments, and architecture to the agent's identity.
- **🔗 Hermes-native** — every skill references Hermes-specific tools: `delegate_task`, `browser`+`terminal`+`vision`, persistent memory, `/curator`.
- **📐 Open standard** — all `SKILL.md` files follow the [Agent Skills spec](https://github.com/addyosmani/agent-skills). Validated by the bundled `SkillValidator`.

## 📦 Skills

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

## 🚀 Quick Start

```bash
# Recommended: install via hermes skills tap
hermes skills tap add Ow1onp/hermes-agent-skills
hermes skills browse
hermes skills install requirement-analyzer

# Or clone locally
git clone https://github.com/Ow1onp/hermes-agent-skills.git
cp -r hermes-agent-skills/skills/* ~/.hermes/skills/

# Load in-session
/skill requirement-analyzer
/skill test-driven-dev
```

## 🔗 Hermes Integration

```python
# Self-evolution engine
from hermes_agent_skills import EvolutionEngine
engine = EvolutionEngine()
engine.record_task(...)
suggestions = engine.analyze()  # detects stale skills, recurring mistakes

# Persona-aware coding
profile = SoulReader().read("~/.hermes/SOUL.md")
print(profile.get_code_prompt_hint())
```

## 📂 Structure

```
skills/                     # SKILL.md files (Agent Skills standard)
├── define/                 # requirement-analyzer, spec-driven-dev
├── build/                  # test-driven-dev
├── verify/                 # debugger-coordinator, code-quality-guardian
├── ship/                   # cicd-orchestrator
└── evolve/                 # skill-curator, persona-aware-coding
src/hermes_agent_skills/    # Python library (validator, evolution, soul_reader)
tests/                      # 46 tests, all passing
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
