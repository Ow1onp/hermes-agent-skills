# 03 — CLI Toolchain

## Overview

`hermes-skill` is the Typer-based CLI for skill authoring. It provides scaffolding, validation, listing, and persona management — all from the terminal.

- **Entry point:** `hermes-skill = cli.main:run` (declared in `pyproject.toml`)
- **Package:** `src/cli/` — 7 files
- **Tests:** 21 tests in `tests/test_cli/`
- **Framework:** Typer ≥0.9
- **Python:** ≥3.10

## Command Tree

```
hermes-skill
├── create      Scaffold a new SKILL.md from templates
├── validate    Validate SKILL.md against Agent Skills Standard
├── list        List discovered skills with metadata
└── soul
    ├── generate   Generate a SOUL.md persona template
    └── read       Read and display a SOUL.md profile
```

## `create` — Scaffold a Skill

```bash
hermes-skill create <name> [OPTIONS]
```

Options:
- `--category`, `-c` — lifecycle phase (define/build/verify/evolve/ship)
- `--template`, `-t` — template preset: `basic` (default) | `advanced` | `minimal`
- `--output`, `-o` — output directory (default: current dir)
- `--soul` — auto-generate a companion SOUL.md
- `--no-interactive` — skip prompts, use defaults

### Templates

| Template | Sections | Use Case |
|----------|----------|----------|
| `basic` | Overview → Core Flow → Gate Criteria → Anti-Excuses | Standard skills (recommended) |
| `advanced` | + Multi-Phase Workflow + Quality Gates + Escalation | Complex multi-stage skills |
| `minimal` | Overview → Core Flow | Quick prototypes |

Template engine supports `{variable}` interpolation for: `name`, `description`, `category`, `version`, `author`. Generated SKILL.md is immediately validated; failures are reported inline.

## `validate` — Quality Check

```bash
hermes-skill validate [PATH] [OPTIONS]
```

Delegates to `SkillValidator` from `hermes_agent_skills`. Supports:
- Single file or recursive directory scan
- `--strict` — error on warnings
- `--quiet` — only show failures
- `--format json` — machine-readable output

## `list` — Inventory

```bash
hermes-skill list [PATH] [OPTIONS]
```

Options:
- `--format`, `-f` — `table` (default) or `json`
- `--verbose`, `-v` — show full metadata
- `--filter` — filter by name substring or category

Table output columns: Name, Version, Category, Status (valid/invalid), Description (truncated).

## `soul` — Persona Management

```bash
hermes-skill soul generate [TYPE] [--output PATH]
hermes-skill soul read [PATH]
```

Generate templates: `balanced` (default), `architect`, `pragmatist`. Read displays parsed profile fields.

## Implementation Details

- **`src/cli/main.py`** — Typer app with subcommand groups
- **`src/cli/commands/create.py`** — Interactive + non-interactive flow, delegates to TemplateEngine
- **`src/cli/commands/validate.py`** — Thin wrapper around SkillValidator, handles path resolution
- **`src/cli/commands/list.py`** — File system scan, parses frontmatter for metadata
- **`src/cli/templates/skill_templates.py`** — `TemplateEngine` class + `TemplateRegistry`

All commands return exit code 0 on success, non-zero on failures (validate returns 1 if any file invalid).

## Test Coverage

21 CLI tests:
- `test_create.py` (7) — basic/advanced/minimal templates, --no-interactive, --soul flag, output directory
- `test_validate.py` (8) — single file, recursive, --strict, --quiet, --format json, invalid file, directory, CLI exit codes
- `test_list.py` (6) — table format, JSON format, --verbose, --filter, empty directory, non-existent path
