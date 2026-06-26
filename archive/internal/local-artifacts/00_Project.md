# 00 — Project Identity

## What It Is

**hermes-agent-skills** is an open-source Skill Engineering infrastructure for Hermes Agent. It provides the toolchain to build, validate, and evolve Agent Skills — not just a curated collection of skill files.

- **Repository:** `Ow1onp/hermes-agent-skills` (public, MIT license)
- **Current version:** v1.1.0
- **Author:** Ow1onp
- **Inspiration:** addyosmani/agent-skills (follows the Agent Skills Open Standard)

## Core Positioning

| Dimension | This project IS | This project IS NOT |
|-----------|----------------|---------------------|
| Purpose | Skill build/validate/evolve toolchain | Skill marketplace or SaaS |
| Scope | Hermes Agent native, deep integration | Generic multi-agent skill pack |
| Value | Quality assurance for skill authors | Content distribution for skill consumers |
| Model | `create-react-app` for skills, `ESLint` for SKILL.md | App Store for skills |

## Three Pillars

1. **Build** — CLI scaffolding, templates, best-practice conventions
2. **Validate** — 6-dimension SKILL.md conformance checker against Agent Skills Open Standard
3. **Evolve** — Self-evolution engine that analyzes usage data and proposes skill improvements (Hermes-unique capability)

## Key Differentiators vs addyosmani/agent-skills

| Feature | agent-skills | hermes-agent-skills |
|---------|-------------|---------------------|
| Self-evolving skills | Static files only | EvolutionEngine with 5-dimension health scoring |
| Persona awareness | None | SoulReader parses SOUL.md for style adaptation |
| Hermes integration | Generic format | `/curator`, `delegate_task`, memory, cron native |
| Validation toolchain | None | CLI + Python API, 6 validation dimensions |
| Chinese language support | None | Full zh templates + bilingual README/docs |

## Version History

**v1.0.0** (2026-06-14) — Initial release: 8 SKILL.md files + Python core library + 46 tests

**v1.1.0** (2026-06-16) — CLI toolchain release: `hermes-skill` CLI (create/validate/list/soul), enhanced 6-dimension validator, 5-document documentation suite, 104 tests

## What Was Deferred

Per explicit user directive during the CTO session, the following were removed from scope:

- Evolution Engine operationalization (code exists but not productionized)
- Skill Benchmark system
- Skill Analytics Dashboard
- SaaS/Marketplace features
- Enterprise team management
- Community infrastructure (Discord server, Discussion-heavy engagement)

## GitHub Metadata

- **Stars:** ~0 (pre-launch)
- **Topics (14):** `hermes-agent`, `agent-skills`, `ai-agent`, `skill-library`, `tdd`, `code-quality`, `cicd`, `software-engineering`, `self-evolving`, `persona-aware`, `python`, `markdown`, `developer-workflow`, `ai-assisted-development`
- **CI/CD:** GitHub Actions (lint + test matrix + skill validate + security scan)
