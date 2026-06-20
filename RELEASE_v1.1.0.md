# 🧬 hermes-agent-skills v1.1.0 — The CLI Toolchain Release

> Ship skills like you ship code. Validate, scaffold, and audit — all from the terminal.

---

## Release Summary

v1.1.0 transforms `hermes-agent-skills` from a curated skill collection into a **full developer toolchain**. The centerpiece is `hermes-skill` — a Typer-powered CLI that brings the same rigor to skill authoring that you already apply to code. Scaffold standards-compliant `SKILL.md` files from templates, validate them against the Agent Skills Open Standard with 6-dimension analysis, and audit entire skill repositories with a single command.

Under the hood, the `SkillValidator` received its most significant upgrade yet, growing from 2 to 6 validation dimensions with configurable strictness, SemVer checking, reserved-name detection, and recursive directory scanning. The test suite has more than doubled — 104 tests, all passing, covering every CLI path and validator edge case.

And because great tooling deserves great documentation: `v1.1.0` ships with a full 5-document documentation suite — Quick Start, Tutorial, FAQ, Contributing Guide, and an overhauled bilingual README — so your first skill is 10 minutes away, not an afternoon of reading specs.

---

## ✨ Highlights

| | |
|---|---|
| **`hermes-skill` CLI** | Create, validate, and list skills from the terminal — Typer-native, `--help` everywhere |
| **6-Dimension Validator** | Frontmatter syntax, SemVer compliance, trigger quality, name-directory consistency, reserved name detection, license metadata |
| **Scaffolding Templates** | `basic`, `advanced`, `minimal` — pick the right starting point for any skill |
| **104 Tests (↑126%)** | Full CLI integration coverage + validator edge cases, all passing |
| **Documentation Suite** | Quick Start, Tutorial, FAQ, and Contributing Guide — engineered for progressive disclosure |

---

## Added

### `hermes-skill` CLI

| Command | Description |
|---|---|
| `hermes-skill create <name>` | Scaffold a new `SKILL.md` from templates (`basic` / `advanced` / `minimal`) with `--category` and `--no-interactive` flags |
| `hermes-skill validate <path>` | Validate one or more skills with `--strict` (require all recommended fields), `--quiet` (only failures), and `--recursive` (scan directories) |
| `hermes-skill list [path]` | List discovered skills with `--format table` or `--format json`, featuring status icons, dimensions, and scores |
| `hermes-skill soul generate` | Generate `SOUL.md` persona templates (`balanced` / `architect` / `pragmatist`) |
| `hermes-skill soul read` | Read and parse `SOUL.md` files into structured output |

### Enhanced `SkillValidator` (v2)

- **6 validation dimensions** with individual pass/fail/warn results:
  1. Frontmatter syntax (`---` delimiters, YAML parsing)
  2. Required fields (`name`, `description`, `version`)
  3. Field constraints (name format regex, description ≤1024 chars)
  4. Semantic validity (SemVer compliance, lowercase-hyphen names)
  5. Recommended quality (≥3 triggers, resolution checklist, metadata block)
  6. Structural integrity (name-directory match, reserved name detection)
- `--strict` mode requiring all recommended quality fields
- `--quiet` mode showing only failures
- `--recursive` flag for directory-wide audit
- Reserved name detection (`claude`, `anthropic`, `openai`, etc.)
- License and compatibility metadata validation

### Documentation (`docs/`)

| Document | Description |
|---|---|
| `QUICKSTART.md` | 10-minute guide — install, create your first skill, validate, iterate |
| `TUTORIAL.md` | Deep dive into SKILL.md anatomy, advanced patterns, and integration tricks |
| `FAQ.md` | 40+ real-world Q&As grouped by user intent (getting started, authoring, troubleshooting) |
| `CONTRIBUTING.md` | How to contribute skills, code, docs, or templates — with style guide and PR checklist |

### Tests

- 58 new tests bringing the suite from 46 → **104** (↑126%)
- CLI integration tests for `create`, `validate`, and `list` (`tests/test_cli/`)
- Validator edge-case tests: SemVer parsing, trigger validation, reserved names, metadata constraints
- All 104 tests pass on Python 3.10–3.12

---

## Changed

- **`SkillValidator`** — Refactored from 2D to 6D validation framework with configurable strictness and structured result objects
- **`pyproject.toml`** — `cli` package declared as installable; entry point `hermes-skill = cli.main:run`
- **`README.md`** — Bilingual split: Chinese (primary) + English (`README.en.md` showcase) with modern aesthetic

## Fixed

- **`console_scripts` entry point** — Corrected to `hermes-skill` (was `hermes-skills` in v1.0.0 scaffolding)

---

## Documentation

| Resource | Link |
|---|---|
| 📖 README (中文) | [README.md](https://github.com/Ow1onp/hermes-agent-skills/blob/v1.1.0/README.md) |
| 📖 README (English) | [README.en.md](https://github.com/Ow1onp/hermes-agent-skills/blob/v1.1.0/README.en.md) |
| ⚡ Quick Start | [docs/QUICKSTART.md](https://github.com/Ow1onp/hermes-agent-skills/blob/v1.1.0/docs/QUICKSTART.md) |
| 🎓 Tutorial | [docs/TUTORIAL.md](https://github.com/Ow1onp/hermes-agent-skills/blob/v1.1.0/docs/TUTORIAL.md) |
| ❓ FAQ | [docs/FAQ.md](https://github.com/Ow1onp/hermes-agent-skills/blob/v1.1.0/docs/FAQ.md) |
| 🤝 Contributing | [CONTRIBUTING.md](https://github.com/Ow1onp/hermes-agent-skills/blob/v1.1.0/CONTRIBUTING.md) |
| 📋 Changelog | [CHANGELOG.md](https://github.com/Ow1onp/hermes-agent-skills/blob/v1.1.0/CHANGELOG.md) |

---

## Installation

### pip (recommended)

```bash
pip install hermes-agent-skills==1.1.0
```

### From source

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
cd hermes-agent-skills
git checkout v1.1.0
pip install -e ".[dev]"
```

### Verify

```bash
hermes-skill --help
hermes-skill validate . --recursive --quiet
```

---

## Compatibility

| | Minimum | Recommended |
|---|---|---|
| **Python** | 3.10 | 3.11+ |
| **Operating System** | Linux, macOS, Windows | — |
| **Hermes Agent** | Any version with `/skills` support | Latest release |
| **Agent Skills Standard** | v1.0.0 | v1.0.0 |

### Dependencies

- `pyyaml >= 6.0`
- `typer >= 0.9`
- No system-level dependencies required

---

## Future Roadmap

The project is converging toward a **Skill Analytics SaaS** — think "npm audit for AI agent skills." The CLI toolchain in v1.1.0 is the first building block.

### v1.2.0 — Analytics & Quality Scoring (Q3 2026)

- `hermes-skill score` — multi-axis quality scoring with letter grades
- `hermes-skill diff` — semantic diff between skill versions
- `hermes-skill stats` — aggregate metrics across skill collections
- Pre-commit hook integration (`hermes-skill validate` as a git hook)

### v1.3.0 — Marketplace & Discovery (Q4 2026)

- `hermes-skill search <query>` — discover community skills
- `hermes-skill install <name>` — one-command skill installation
- Skill registry with version resolution
- Compatibility matrix (skill × Hermes version × OS)

### v2.0.0 — SaaS Platform (2027)

- Web dashboard with real-time skill health monitoring
- Automatic evolution suggestions via LLM analysis
- Team collaboration — shared skill collections with permissions
- Enterprise SSO and audit logging

---

**Full Changelog**: [`v1.0.0...v1.1.0`](https://github.com/Ow1onp/hermes-agent-skills/compare/v1.0.0...v1.1.0)

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/Ow1onp">Ow1onp</a> · <a href="https://github.com/Ow1onp/hermes-agent-skills/blob/v1.1.0/LICENSE">MIT</a> · <a href="https://agentskills.io/specification">Agent Skills Standard</a></sub>
</p>
