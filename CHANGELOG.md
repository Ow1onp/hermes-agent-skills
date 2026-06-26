# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] — 2026-06-20

### Added
- **Hermes v2 Task-First Interface**: Natural-language task execution. Say "帮我发布项目" instead of writing constraint prompts.
- **8 task types**: publish_project, fix_bug, create_project, write_docs, review_code, release_version, install_project, analyze_results.
- **3 user modes**: Beginner (auto), Advanced (choose persona), Expert (pure v1 constraint prompts).
- **Entity Extraction**: Auto-detects technology (FastAPI, Django, Unreal), file paths, versions, doc types from user input.
- **Confidence Calibration**: Every routing has a confidence score. Below 40% triggers clarification.
- **Layer 8 Result Evaluator**: Validates execution plans for completeness, safety, and entity preservation.
- **CI Install Gate**: Smoke test verifies wheel build + install + imports + v1/v2 CLI on every push.

### Changed
- README badges show both v1 (1.1.0) and v2 (2.0.0) versions.
- `pyproject.toml` now includes `hermes_v2` package.

### Fixed
- Entity drop: user-specified technologies now preserved in constraint prompts.
- Version bonus overpowering creation intent: capped when technology context present.
- Synonym routing: added 接口/后端/服务/API keywords to create_project.

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
