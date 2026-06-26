# 05 — Release History

## v1.0.0 (2026-06-14)

Initial release. Commit `d308d06`, 23 files, 2,883 lines.

### Contents

- **8 SKILL.md files** across 4 lifecycle phases: define (2), build (1), verify (2), evolve (2), ship (1)
- **Python core library** (`hermes_agent_skills`): `SkillValidator`, `EvolutionEngine`, `SoulReader`
- **46 unit tests**, all passing
- **README.md** — 9,500+ character full documentation
- **CI/CD** — GitHub Actions workflow (lint + test matrix + skill validate + security)
- **Install script** — `scripts/install.sh` (Unix)
- **MIT License**

### Post-Release Fixes

19 test failures were fixed immediately after initial commit:
- `ValidationResult.valid` missing default value (`= False`)
- `comment_density` not recognizing Chinese keywords
- Template names reverted to Chinese (务实工程师/严谨架构师/敏捷实干家)
- `.gitignore` `build/` → `/build/` to not block `skills/build/`

### README Evolution

The README went through 3 iterations:
1. Initial pure Chinese version (250+ lines, heavy emoji)
2. Bilingual rewrite (142 lines, zh + en inline, ASCII lifecycle diagram, 4-column skill table)
3. Split into `README.md` (zh, 152 lines) + `README.en.md` (en, 98 lines), removed community infrastructure references

## v1.1.0 (2026-06-16)

The CLI Toolchain Release. Tag `v1.1.0`, published as full GitHub Release.

### New in v1.1.0

| Category | Items |
|----------|-------|
| **CLI** | `hermes-skill create/validate/list/soul` (Typer, 7 source files) |
| **Validator** | Enhanced to 6 dimensions (SemVer, triggers, reserved names, recursive scanning, strict mode) |
| **Documentation** | 5 new docs (QUICKSTART, TUTORIAL, FAQ, CONTRIBUTING, docs/README) |
| **Tests** | 58 new tests, total 104 (up from 46) |
| **Config** | `pyproject.toml` updated: `typer>=0.9`, `console_scripts`, `packages = ["hermes_agent_skills", "cli"]` |
| **Changelog** | `CHANGELOG.md` in keepachangelog.com format |
| **Feedback** | `.github/ISSUE_TEMPLATE/` (4 YAML forms + config.yml), `FEEDBACK.md` |

### Release Process

Pre-release audit identified 5 blockers, all resolved:
1. Version number consistency across 6 files → all `1.1.0`
2. `console_scripts` entry point → `hermes-skill = cli.main:run`
3. `CHANGELOG.md` created
4. `CONTRIBUTING.md` added to root
5. `docs/` directory tracked in git

### GitHub Release

Published at `https://github.com/Ow1onp/hermes-agent-skills/releases/tag/v1.1.0`

- Title: "v1.1.0 — The CLI Toolchain Release"
- Draft: false
- Prerelease: false
- Body: 9 sections (~7,500 chars), covering highlights, CLI feature list, validator dimensions, documentation suite, upgrade guide, and full changelog

### Test Suite

```
104 passed in 0.28s
  test_validator.py     52 tests
  test_evolution.py     13 tests
  test_soul_reader.py   15 tests
  test_init.py           5 tests
  test_cli/             21 tests (7 create + 8 validate + 6 list)
  ─────────────────────────
  Total: 104 passed, 0 failed
```

### What Was Not Released

- PyPI publication — package not yet uploaded
- Windows installer — `install.sh` remains Unix-only
- Evolution Engine — code exists but not operationalized
- Benchmark / Analytics — explicitly deferred per user directive
