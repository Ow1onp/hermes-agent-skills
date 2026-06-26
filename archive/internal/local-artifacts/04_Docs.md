# 04 — Documentation

## Documentation Suite

5 core documents + 2 READMEs, totaling ~50KB of markdown, designed to get a Hermes new user from zero to their first skill in 10 minutes.

```
docs/
├── QUICKSTART.md         5.6 KB   10-minute first skill, copy-paste ready
├── TUTORIAL.md          16.6 KB   Deep-dive SKILL.md anatomy + patterns
├── FAQ.md               13.4 KB   50+ real questions, grouped by user intent
├── CONTRIBUTING.md       9.9 KB   Quality checklist + hub publish flow
├── README.md             6.2 KB   Docs index / landing page
├── community-launch-v1.1.md       Multi-platform launch content (6 platforms)
└── user-feedback-system.md        Feedback collection design (5 modules)
```

Root-level:
```
README.md                6.9 KB   Chinese primary (152 lines, complete)
README.en.md             4.7 KB   English showcase (98 lines, concise)
CHANGELOG.md             3.0 KB   keepachangelog.com format
CONTRIBUTING.md          1.8 KB   Root-level redirect
FEEDBACK.md              4.1 KB   User feedback guide
```

## README Strategy

Bilingual approach:
- **`README.md`** — Chinese primary version. Full content: project intro, lifecycle ASCII diagram, 8-skill table with Hermes-specific columns, self-evolution code example, SOUL.md example, slash-command bindings, project structure tree. 152 lines.
- **`README.en.md`** — English showcase version. Core points in lists and short sentences. 98 lines.

Both versions include: live badges (GitHub stars, license, tests passing), quick install one-liner, skill table.

## QUICKSTART — 10-Minute First Skill

Structure: each step annotated with time estimate (30s / 10s / 5min / 30s / 3min), totaling exactly 10 minutes. Fully copy-pasteable commands. No assumed knowledge.

Steps:
1. Install (pip / git clone) — 30s
2. Create first skill (`hermes-skill create my-first-skill`) — 10s
3. Understand the generated file — 5min
4. Validate (`hermes-skill validate`) — 30s
5. Install into Hermes — 3min

## TUTORIAL — Deep Dive

Covers every frontmatter field with **❌ Bad / ✅ Good / 🏆 Great** three-level examples. Sections:
- SKILL.md anatomy (YAML frontmatter → markdown body)
- Field reference (name, description, triggers, version, metadata)
- Progressive disclosure pattern
- Self-evolution annotations
- SOUL.md integration
- Hermes-specific features (`/curator`, `delegate_task`)

## FAQ — 50+ Items

Grouped by user intent, not by technical module:
- "I want to get started" — install, create, validate basics
- "I want to write better skills" — frontmatter tips, trigger design
- "I want to understand how skills load" — loading order, caching, session lifecycle
- "I want to compare with other systems" — vs Cursor Rules, vs Claude Code Skills, vs agent-skills
- "I ran into a problem" — common errors, validation failures, path issues

## CONTRIBUTING

Quality checklist for skill submissions:
- SKILL.md passes `hermes-skill validate --strict`
- All triggers are unique and non-empty
- Description starts with "Use when..."
- File is under 500 lines
- No absolute paths
- Version follows SemVer

## Key Design Decisions

- **No commercialization language** — zero mentions of "pricing", "subscription", "enterprise", "paid"
- **User-intent grouping** in FAQ, not technical grouping
- **All examples are real and runnable** — no pseudocode
- **对标三家** (benchmarked against three): agent-skills (format compatibility), Cursor Rules (loading model differences), Claude Code Skills (feature comparison table — acknowledges strengths of each without disparagement)
