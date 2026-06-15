# Hermes Skills

> Write once. Load on demand. Get better every time.

A **Skill** is a self-contained Markdown file that teaches Hermes how to handle a specific task — deploy to production, review a PR, generate a changelog, or anything else you do repeatedly. Skills are Hermes's procedural memory: they capture what works and replay it when needed.

---

## Why Skills?

### The Problem

Without skills, you have three bad options:

| Approach | Problem |
|----------|---------|
| **Repeat yourself** | "Remember to use pytest with `-n 4`" — every. single. session. |
| **Cram everything into system prompt** | Your context budget burns on rules that only matter 5% of the time. |
| **Maintain a giant CLAUDE.md** | 2000 lines covering every edge case. The model skims it. |

### The Solution

Skills load **only when relevant**. Hermes sees skill metadata (~100 tokens each) at session start. When a task matches, the full instructions load. When the task is done, the skill unloads. Your context stays clean; Hermes stays focused.

---

## Hermes Skills vs. The Field

Hermes Skills implement the [Agent Skills open standard](https://agentskills.io/specification) — the same `SKILL.md` format used by Claude Code, Codex CLI, Cursor, and 32+ other tools. But Hermes adds several layers on top:

| Capability | Anthropic Skills | Cursor Rules | Claude Code Skills | **Hermes Skills** |
|------------|:---:|:---:|:---:|:---:|
| `SKILL.md` open standard | ✅ | ✅ (via `.mdc`) | ✅ | ✅ |
| Load on demand (progressive disclosure) | ✅ | ✅ | ✅ | ✅ |
| Slash-command invocation | ✅ | — | ✅ | ✅ |
| Natural-language auto-activation | ✅ | ✅ | ✅ | ✅ |
| **Agent creates skills from experience** | — | — | — | ✅ |
| **Self-improvement loop (Curator)** | — | — | — | ✅ |
| **Persistent memory integration** | — | — | — | ✅ |
| **Skill lifecycle automation** | — | — | — | ✅ |
| Built-in skill marketplace (hub) | — | — | Plugin marketplace | ✅ |
| Platform-specific skills (macOS/Linux/Windows) | — | — | — | ✅ |
| Conditional activation (requires/fallback toolsets) | — | — | — | ✅ |
| Secure env-var setup on load | — | — | — | ✅ |

**What makes Hermes different:**

- **Self-improving** — after solving a complex task, Hermes can save the approach as a new skill automatically. That skill loads next time, and improves with use.
- **Curator** — a background process tracks skill usage, detects staleness, and suggests improvements. Skills are living documents, not write-once artifacts.
- **Memory-aware** — skills can reference information stored in Hermes's persistent memory, so they adapt to *your* environment and preferences across sessions.

---

## The 30-Second Skill

A skill is a directory with a single `SKILL.md` file:

```
my-first-skill/
└── SKILL.md
```

The `SKILL.md` has two parts: **YAML frontmatter** (metadata) and **Markdown body** (instructions).

```markdown
---
name: greet-user
description: Greet the user by name and ask what they need help with today.
---

# Greet User

When the user says hello, hi, or starts a new session:

1. Greet them warmly by name if you know it
2. Ask one specific question about what they'd like to work on
3. Keep it under 3 sentences — no walls of text
```

That's it. Put this file in `~/.hermes/skills/greet-user/SKILL.md`, type `/greet-user` in any Hermes session, and it works.

---

## How Skills Load (Progressive Disclosure)

Hermes loads skill information in three levels to stay token-efficient:

```
Level 0: Metadata only (~100 tokens/skill)
  └─ name + description. Always visible. Hermes uses this to decide
     whether a skill is relevant to your current task.

Level 1: Full SKILL.md body
  └─ Loaded when you invoke the skill (/skill-name) or when Hermes
     detects it's relevant. All instructions, examples, guidelines.

Level 2: Supporting files
  └─ References, scripts, templates, assets. Loaded on demand when
     the skill's instructions reference them.
```

This means you can have 50 skills installed and they cost you ~5K tokens at startup — not 250K.

---

## Key Features

### 🔧 Hermes-Native Tool Integration

Skills aren't generic prompts. They know Hermes's specific tools:

```markdown
## Procedure
1. Use `delegate_task` to run tests in parallel on 3 subagents
2. If tests fail, use `session_search` to find the last time this test broke
3. Save the fix as a `memory` entry so future sessions learn from it
```

### 🧬 Self-Evolving

After completing a complex task (5+ tool calls, errors overcome), Hermes can automatically create a skill capturing what worked. The next time a similar task comes up, the skill loads — and the cycle compounds.

### 🎯 Conditional Activation

Skills can auto-show or auto-hide based on what tools are available:

```yaml
requires_toolsets: [browser, terminal]   # Only show when browser+terminal are enabled
fallback_for_toolsets: [web]             # Show as fallback when web search is missing
```

### 📂 Skill Lifecycle (Curator)

Hermes's built-in Curator tracks skill usage, flags idle skills as stale, archives unused ones, and backs up everything. Skills are never deleted — the most destructive action is archive, and pinned skills are exempt from all auto-transitions.

---

## Quick Links

| You want to... | Read this |
|----------------|-----------|
| Create your first skill in 10 minutes | [Quick Start →](QUICKSTART.md) |
| Understand SKILL.md in depth | [Skill Tutorial →](TUTORIAL.md) |
| Contribute a skill to the community | [Contributing Guide →](CONTRIBUTING.md) |
| Find answers to common questions | [FAQ →](FAQ.md) |
| Browse the official skill catalog | `hermes skills browse` |

---

## Repository

This documentation is part of [hermes-agent-skills](https://github.com/Ow1onp/hermes-agent-skills) — a collection of production-grade skills for Hermes Agent.

**Skills are plain Markdown. Anyone can write them. Everyone benefits.**
