# 01 — Architecture

## Repository Layout

```
hermes-agent-skills/
├── skills/                          # 8 SKILL.md files, 4 lifecycle phases
│   ├── define/
│   │   ├── requirement-analyzer/
│   │   └── spec-driven-dev/
│   ├── build/
│   │   └── test-driven-dev/
│   ├── verify/
│   │   ├── code-quality-guardian/
│   │   └── debugger-coordinator/
│   ├── evolve/
│   │   ├── persona-aware-coding/
│   │   └── skill-curator/
│   └── ship/
│       └── cicd-orchestrator/
├── src/
│   ├── hermes_agent_skills/         # Core Python library
│   │   ├── __init__.py              # Public API exports, __version__ = "1.1.0"
│   │   ├── models.py                # ValidationIssue, ValidationResult, ValidatorConfig
│   │   ├── validator.py             # 6-dimension SkillValidator
│   │   ├── evolution.py             # EvolutionEngine + EvolutionSuggestion
│   │   ├── soul_reader.py           # SoulReader + SoulProfile
│   │   └── cli.py                   # Standalone argparse CLI (v1.0.0 entry)
│   └── cli/                         # Typer-based CLI (v1.1.0 entry)
│       ├── main.py                  # Entry point: hermes-skill = cli.main:run
│       ├── commands/
│       │   ├── create.py            # Scaffold SKILL.md from templates
│       │   ├── validate.py          # Validate with SkillValidator
│       │   └── list.py              # List skills (table/JSON)
│       └── templates/
│           └── skill_templates.py   # TemplateEngine + 3 templates
├── tests/
│   ├── test_validator.py            # 52 tests (validator core)
│   ├── test_evolution.py            # 13 tests
│   ├── test_soul_reader.py          # 15 tests
│   ├── test_init.py                 # 5 tests
│   └── test_cli/
│       ├── conftest.py              # CliRunner + app fixtures
│       ├── test_create.py           # 7 tests
│       ├── test_validate.py         # 8 tests
│       └── test_list.py             # 6 tests
├── docs/
│   ├── QUICKSTART.md                # 10-minute first skill
│   ├── TUTORIAL.md                  # Deep-dive skill anatomy
│   ├── FAQ.md                       # 50+ items, grouped by intent
│   ├── CONTRIBUTING.md              # Quality checklist + hub flow
│   ├── README.md                    # Docs index
│   ├── community-launch-v1.1.md     # Multi-platform launch content
│   └── user-feedback-system.md      # Feedback collection design
├── .github/
│   ├── ISSUE_TEMPLATE/              # 4 YAML forms + config.yml
│   ├── DISCUSSION_TEMPLATE.md
│   └── workflows/ci.yml
├── pyproject.toml                   # Build config, deps, console_scripts
├── README.md                        # Chinese primary (152 lines)
├── README.en.md                     # English showcase (98 lines)
├── CHANGELOG.md                     # keepachangelog.com format
├── CONTRIBUTING.md                  # Root-level symlink target
├── FEEDBACK.md                      # User feedback guide
└── LICENSE                          # MIT
```

## Package Architecture

### `hermes_agent_skills` — Core Library

**Dependencies:** `pyyaml>=6.0`

Public API:
- `SkillValidator` — validate SKILL.md files
- `ValidationResult` / `ValidationIssue` / `IssueSeverity` / `ValidationDimension` / `ValidatorConfig` — data models
- `SoulReader` / `SoulProfile` — SOUL.md parsing
- `EvolutionEngine` / `EvolutionSuggestion` — self-evolution analysis

### `cli` — Typer CLI

**Dependencies:** `typer>=0.9`

Entry point: `hermes-skill = cli.main:run`

Command tree:
```
hermes-skill
├── create <name> [--category] [--template basic|advanced|minimal]
│                 [--output] [--soul] [--no-interactive]
├── validate [path] [--strict] [--recursive] [--quiet] [--format json|text]
├── list [path] [--format table|json] [--verbose] [--filter]
└── soul
    ├── generate [type] [--output]
    └── read [path]
```

## Skills Lifecycle

```
define ──▶ build ──▶ verify ──▶ ship
  │                    │
  └──── evolve ◀───────┘
```

8 skills cover the full software delivery lifecycle, each in a phase-specific subdirectory with its own SKILL.md. Each skill has triggers, Hermes-native slash-command bindings, and persona-aware directives.

## CI/CD

Single workflow `.github/workflows/ci.yml`:
- Lint (Python)
- Test matrix (Python 3.10/3.11/3.12)
- Skill validate (all SKILL.md files)
- Security scan
