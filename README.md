# hermes-agent-skills

**Production-grade skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent).**  
深度适配 Hermes Agent 的开箱即用技能集——自进化、身份感知、斜杠命令原生集成。

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-green)](https://www.python.org/)
[![Hermes Agent](https://img.shields.io/badge/hermes--agent-compatible-8A2BE2)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills](https://img.shields.io/badge/standard-agent--skills-orange)](https://github.com/addyosmani/agent-skills)
[![Tests](https://img.shields.io/badge/tests-46%2F46%20passing-brightgreen)](tests/)

---

```
  DEFINE           BUILD          VERIFY           SHIP           EVOLVE
 ┌────────┐     ┌────────┐     ┌─────────┐     ┌────────┐     ┌──────────┐
 │需求分析 │ ──▶ │TDD 开发│ ──▶ │多模态调试│ ──▶ │CI/CD   │ ──▶ │自进化策展 │
 │规格驱动 │     │        │     │代码门禁  │     │编排    │     │身份感知  │
 └────────┘     └────────┘     └─────────┘     └────────┘     └──────────┘
```

## Features · 特性

- **Self-evolving** · 自进化 — skills are not static; the built-in `EvolutionEngine` scores health across 5 dimensions, detects staleness, and proposes improvements that feed directly into Hermes's `/curator` learning loop.
- **Persona-aware** · 身份感知 — reads `SOUL.md` to dynamically adapt code style, comment density, naming conventions, and architectural decisions to match the agent's defined persona.
- **Hermes-native** · 命令体系集成 — every skill references Hermes-specific tools (`/skills`, `delegate_task`, `browser`+`terminal`+`vision` coordination, persistent memory) rather than generic instructions.
- **Open standard** · 开放标准 — all `SKILL.md` files follow the [Agent Skills specification](https://github.com/addyosmani/agent-skills), verified by the bundled `SkillValidator`.

## Quick Start · 快速开始

**Install via `hermes skills tap` (recommended · 推荐):**

```bash
hermes skills tap add Ow1onp/hermes-agent-skills
hermes skills browse
hermes skills install requirement-analyzer
```

**Clone & copy locally · 本地克隆:**

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
cp -r hermes-agent-skills/skills/* ~/.hermes/skills/
```

**Load a skill in-session · 会话中加载:**

```bash
/skill requirement-analyzer
/skill test-driven-dev
/skill code-quality-guardian
```

## Skills · 技能列表

| Skill · 技能 | Phase · 阶段 | What it does · 职责 | Hermes-specific · 独有特性 |
|---|---|---|---|
| `requirement-analyzer` | Define · 定义 | Five-round structured dialogue to extract true requirements | Persistent memory across sessions |
| `spec-driven-dev` | Define · 规格 | Seven-section PRD/Spec before any implementation code | `/skills` pipeline chaining |
| `test-driven-dev` | Build · 构建 | Strict RED-GREEN-REFACTOR with test pyramid (80/15/5) | `delegate_task` parallel test execution |
| `debugger-coordinator` | Verify · 验证 | Five-step debugging using multi-modal tool matrix | `browser` + `terminal` + `vision` coordination |
| `code-quality-guardian` | Verify · 评审 | Six-axis quality gate (security/complexity/style/coverage/docs/deps) | Auto-fix via `patch` + `/curator` tracking |
| `cicd-orchestrator` | Ship · 交付 | GitHub Actions workflow generation & optimization | `cronjob` scheduled pipelines + `webhook` triggers |
| `skill-curator` | Evolve · 进化 | Four-phase curation: collect → analyze → propose → execute | Direct `/curator` integration |
| `persona-aware-coding` | Evolve · 身份 | SOUL.md-driven full-stack style adaptation | Native identity system |

## Hermes Integration · 深度适配

Three capabilities that set these skills apart from generic agent-skills:

**1. Self-evolution loop · 自进化闭环**

```python
from hermes_agent_skills import EvolutionEngine

engine = EvolutionEngine()
engine.record_task(TaskExecutionRecord(
    task_description="Fix login timeout bug",
    skills_used=["debugger-coordinator", "test-driven-dev"],
    retries=2, user_corrections=1, success=True, duration_seconds=300,
))
suggestions = engine.analyze()
# → [{action: "create", reason: "3+ similar timeout bugs detected, consider a skill"}]
```

**2. Persona-aware adaptation · SOUL.md 身份感知**

```yaml
# ~/.hermes/SOUL.md
name: "严谨架构师"
coding_style:
  naming: snake_case
  prefer: [type_hints, custom_exceptions, immutability]
comment_style: "代码即文档"
architecture_preference: "六边形架构"
```

Load `persona-aware-coding` — all generated code, comments, and docs automatically adopt this style.

**3. Slash-command native · 斜杠命令体系**

```bash
/skill requirement-analyzer      # Load a skill
/curator status                  # Check skill health
/curator run                     # Trigger self-evolution review
hermes skills tap add Ow1onp/hermes-agent-skills  # Add skill source
```

## Python API

```python
from hermes_agent_skills import SkillValidator, SoulReader, EvolutionEngine

# Validate SKILL.md files
validator = SkillValidator(strict=False)
result = validator.validate_directory("skills/")
print(result[0].summary())  # [VALID] skills/build/test-driven-dev/SKILL.md

# Read agent persona
profile = SoulReader().read("~/.hermes/SOUL.md")
print(profile.naming_convention)  # snake_case
print(profile.get_code_prompt_hint())
```

## Contributing · 贡献指南

Skills are plain Markdown — contributions welcome.  
技能文件采用纯 Markdown 格式，欢迎贡献。

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
# Create your skill under skills/<phase>/<name>/SKILL.md
# Validate: pytest tests/test_validator.py -v
# Open a PR
```

- Issues responded within 24h · Issue 24 小时内回复
- PRs reviewed within 48h · PR 48 小时内完成 Review

## License · 协议

MIT © [Ow1onp](https://github.com/Ow1onp)
