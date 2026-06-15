# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] — 2026-06-16

### Added

- `hermes-skill` CLI toolchain (`cli` package)
  - `hermes-skill create <name>` — scaffold a new SKILL.md from templates (basic/advanced/minimal)
  - `hermes-skill validate <path>` — validate SKILL.md files against the Agent Skills standard
  - `hermes-skill list [path]` — list discovered skills with metadata (table/JSON output)
  - `hermes-skill soul generate` — generate SOUL.md persona templates (balanced/architect/pragmatist)
  - `hermes-skill soul read` — read and parse SOUL.md persona profiles
- Enhanced `SkillValidator` (v2)
  - SemVer validation for `version` field
  - Trigger keyword validation (non-empty, unique, ≥3 recommended)
  - Name-directory consistency check
  - Reserved name detection (claude, anthropic, etc.)
  - License and compatibility metadata validation
  - 6-dimension validation framework with configurable strictness
  - `--strict` mode requiring recommended fields
  - `--quiet` mode showing only failures
  - `--recursive` directory scanning
- Comprehensive documentation suite (`docs/`)
  - `QUICKSTART.md` — 10-minute first skill guide
  - `TUTORIAL.md` — deep-dive SKILL.md anatomy and advanced patterns
  - `FAQ.md` — real-world questions and answers
  - `CONTRIBUTING.md` — how to contribute skills, code, or docs
- 58 new tests (104 total, up from 46)
  - CLI integration tests (create, validate, list)
  - Validator enhancement tests (SemVer, triggers, metadata, structure)

### Changed

- Improved `SkillValidator` with 6 validation dimensions
- `pyproject.toml` now declares `cli` as an installable package

### Fixed

- `console_scripts` entry point corrected to `hermes-skill`

---

## [1.0.0] — 2026-06-14

### Added

- Initial release with 8 production-grade skills
  - `requirement-analyzer` — structured multi-turn requirement extraction
  - `spec-driven-dev` — seven-section PRD before implementation
  - `test-driven-dev` — RED-GREEN-REFACTOR with test pyramid
  - `debugger-coordinator` — multi-modal debugging coordination
  - `code-quality-guardian` — six-axis quality gate
  - `cicd-orchestrator` — GitHub Actions pipeline generation
  - `skill-curator` — self-evolving skill analysis engine
  - `persona-aware-coding` — SOUL.md-driven style adaptation
- Python library (`hermes_agent_skills`)
  - `SkillValidator` — SKILL.md validation
  - `EvolutionEngine` — self-evolution analysis
  - `SoulReader` — SOUL.md persona parsing
- 46 unit tests, all passing
- MIT License

[1.1.0]: https://github.com/Ow1onp/hermes-agent-skills/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Ow1onp/hermes-agent-skills/releases/tag/v1.0.0
