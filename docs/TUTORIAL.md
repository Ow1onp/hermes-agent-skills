# Skill Tutorial: From Template to Production

> Deep dive into SKILL.md anatomy, progressive disclosure, skill lifecycle, and advanced patterns.

---

## Table of Contents

1. [Anatomy of a SKILL.md](#anatomy-of-a-skillmd)
2. [Progressive Disclosure in Practice](#progressive-disclosure-in-practice)
3. [Writing Effective Instructions](#writing-effective-instructions)
4. [Using Supporting Files](#using-supporting-files)
5. [Skill Lifecycle](#skill-lifecycle)
6. [Advanced Patterns](#advanced-patterns)
7. [Debugging Skills](#debugging-skills)

---

## Anatomy of a SKILL.md

Every skill is a directory containing at least a `SKILL.md` file. The file has two required parts and several optional ones.

### The Full Skeleton

```yaml
---
# ── REQUIRED ──
name: my-skill                    # lowercase, hyphens, ≤64 chars
description: A clear description of what this skill does and when to use it.  # ≤1024 chars

# ── RECOMMENDED ──
version: 1.0.0
author: your-name-or-org
license: MIT

# ── OPTIONAL ──
platforms: [macos, linux]         # Restrict to specific OS
metadata:
  hermes:
    tags: [tag1, tag2]            # Discovery and categorization
    category: devops              # Organize in skill browser
    related_skills: [other-skill] # Cross-reference
    requires_toolsets: [terminal] # Only show when these toolsets are enabled
    fallback_for_toolsets: [web]  # Show as fallback when these toolsets are missing
required_environment_variables:   # Secure env-var setup
  - name: EXAMPLE_API_KEY
    prompt: Your Example API key
    help: Get one at https://example.com/keys
    required_for: full functionality
---

# Skill Title (H1)

## When to Use
- Trigger 1
- Trigger 2

## When NOT to Use
- Anti-trigger 1

## Procedure
1. Step one
2. Step two

## Common Pitfalls
- Pitfall → Fix

## Verification Checklist
- [ ] Check 1
- [ ] Check 2
```

### Field Reference

| Field | Required | Purpose | Example |
|-------|:--------:|---------|---------|
| `name` | ✅ | How you invoke it: `/skill-name`. Must be lowercase, hyphens only, ≤64 chars. | `pdf-extractor` |
| `description` | ✅ | The most important field. Controls auto-activation. Must answer both "what" and "when". ≤1024 chars. | `Extracts text and tables from PDF files. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.` |
| `version` | — | Semver. Bump when you make meaningful changes. | `1.2.0` |
| `author` | — | You or your org. | `@yourname` |
| `license` | — | SPDX identifier or short name. | `MIT` |
| `platforms` | — | Restrict to specific operating systems. Omit for all platforms. | `[macos, linux]` |
| `metadata.hermes.tags` | — | Discovery tags for `hermes skills browse`. | `[python, testing]` |
| `metadata.hermes.requires_toolsets` | — | Only show skill when these toolsets are available. | `[browser, vision]` |
| `metadata.hermes.fallback_for_toolsets` | — | Show skill as fallback when these toolsets are missing. | `[web]` |
| `required_environment_variables` | — | Securely prompt user for missing env vars on load (CLI only — never in messaging platforms). | See skeleton above |

### The Description: Your Most Important 1024 Characters

The description does double duty:
1. **Shown in skill browser** — users decide whether to install
2. **Used for auto-activation** — Hermes matches it against the user's request

**Bad description:**
```yaml
description: Helps with git.
```

**Good description:**
```yaml
description: Create well-formatted git commits with conventional commit messages. Use when the user asks to commit changes, mentions "git commit", or finishes a code change and needs to create a commit.
```

**Great description (keywords + triggers + domain):**
```yaml
description: Deploy applications to Vercel with zero-downtime configuration. Handles environment variables, custom domains, and preview deployments. Use when the user says "deploy", "ship", "go live", "push to production", or mentions Vercel or deployment.
```

The rule: if a user who's never seen your skill says something — would the description match? Write for that person.

---

## Progressive Disclosure in Practice

Hermes loads skills in three tiers. Design your skill to work with this system.

### Level 0: Metadata (~100 tokens)

At session start, Hermes loads the `name` and `description` of every installed skill. This is the "menu" — Hermes knows what's available but hasn't read the instructions yet.

**Design rule:** Your description must be enough for Hermes to know *when* to load the full skill.

### Level 1: Full SKILL.md Body (< 500 lines recommended)

Loaded when the skill is invoked or auto-detected as relevant. This is your main content.

**Design rules:**
- Keep it under 500 lines. If you're going over, move details to reference files (Level 2).
- Put the most important instructions at the top. Models attend more to early content.
- Use numbered lists for procedures, bullet points for options.

### Level 2: Supporting Files (on demand)

```yaml
my-skill/
├── SKILL.md              # Required: the entry point
├── references/           # Loaded when SKILL.md references them
│   ├── advanced-usage.md
│   └── examples.md
├── scripts/              # Executable code (Python, Bash)
│   └── validate.py
├── templates/            # File templates
│   └── config.yaml.j2
└── assets/               # Static resources
    └── logo.png
```

**Design rules:**
- Reference files with relative paths: `[advanced usage](references/advanced-usage.md)`
- Keep individual reference files focused — smaller files = less wasted context
- Scripts should be self-contained with helpful error messages
- Never chain references deeper than one level from SKILL.md

### Token Budget Example

| Level | 10 skills | 50 skills | 100 skills |
|-------|----------|----------|------------|
| Metadata only | ~1K tokens | ~5K tokens | ~10K tokens |
| One skill loaded | ~1.5K tokens | ~5.5K tokens | ~10.5K tokens |
| All skills loaded | ~15K tokens | ~75K tokens | ~150K tokens |

This is why progressive disclosure matters: 50 installed skills costs 5K tokens at startup, not 75K.

---

## Writing Effective Instructions

### Be Specific, Not Aspirational

**Aspirational (bad):**
```markdown
Write clean, secure, well-tested code.
```

**Specific (good):**
```markdown
- Every function must handle errors explicitly — catch, log, re-raise with context
- Functions longer than 30 lines → extract into smaller units
- All user input must pass through a validation function before touching business logic
- Add a test for the happy path AND the two most likely failure modes
```

The first is a wish. The second is a checklist Hermes can execute.

### Provide the Alternative, Not Just the Prohibition

**Prohibition-only (bad):**
```markdown
Never use global variables.
```

**With alternative (good):**
```markdown
Never use global variables. Instead, use dependency injection — pass shared state
through function parameters or a configuration object. If multiple functions need
the same data, create a class that holds it.
```

Negative constraints without alternatives create dead ends.

### Use Examples

Abstract rules are easy to misinterpret. Concrete examples anchor behavior:

```markdown
## Commit Message Format

Use conventional commits:

✅ Good:
```
feat: add rate limiting middleware
fix: handle null user in profile endpoint
refactor: extract auth logic to separate module
```

❌ Bad:
```
fixed the bug
updates
WIP
```
```

### Structure for Skimmability

Models process instructions sequentially. Front-load what matters:

```markdown
## Instructions

### 1. ALWAYS DO THIS FIRST (Critical)
### 2. Then do this (Important)
### 3. Finally, check these (Nice to have)

## Output Format
[Exact format specification]

## Edge Cases
[What to do when things go wrong]
```

---

## Using Supporting Files

### References: For Deep Knowledge

Move detailed documentation out of SKILL.md to keep the main file lean:

**SKILL.md:**
```markdown
# Deployment Skill

## Quick Deploy
1. Run `scripts/deploy.py --target production`
2. See [full deployment guide](references/production-guide.md) for custom domains and SSL

## Troubleshooting
Common issues: [troubleshooting guide](references/troubleshooting.md)
```

**references/production-guide.md:**
```markdown
# Production Deployment Guide

## Custom Domains
...
```

### Scripts: For Executable Logic

Scripts are run by Hermes via the terminal tool:

```python
# scripts/validate_config.py
"""Validate deployment configuration. Exit 0 on success, 1 on failure."""
import sys, json, os

config_path = sys.argv[1] if len(sys.argv) > 1 else "deploy.json"

try:
    with open(config_path) as f:
        config = json.load(f)
    
    errors = []
    if "target" not in config:
        errors.append("Missing 'target' field")
    if "version" not in config:
        errors.append("Missing 'version' field")
    
    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    
    print("Configuration valid.")
except FileNotFoundError:
    print(f"Config file not found: {config_path}")
    sys.exit(1)
```

### Templates: For Generated Files

Store file templates that Hermes will populate:

```
templates/
├── dockerfile.j2
├── workflow.yml.j2
└── component.tsx.j2
```

---

## Skill Lifecycle

Skills in Hermes have a lifecycle managed by the **Curator**:

```
CREATE ──▶ ACTIVE ──▶ STALE ──▶ ARCHIVED
  │           │          │
  │           └── PINNED (exempt from all auto-transitions)
  │
  └── Created by agent or user
```

### Phases

| Phase | Trigger | Behavior |
|-------|---------|----------|
| **Create** | `skill_manage(action='create')` or Hermes auto-creates after complex task | Skill is written to `~/.hermes/skills/` |
| **Active** | Skill is used | Curator tracks usage count, patch count, last activity |
| **Stale** | No usage for N days (default: 30) | Curator flags for review. Skill still loads normally. |
| **Archived** | Stale for additional N days (default: 60) | Curator moves to `.archive/`. **Not deleted** — restorable anytime. |
| **Pinned** | `hermes curator pin <name>` | Exempt from ALL automatic transitions. Use for skills you always want available. |

### Curator Commands

```bash
hermes curator status          # Health overview of all skills
hermes curator run             # Trigger a manual review cycle
hermes curator pin <name>      # Protect a skill from archival
hermes curator unpin <name>    # Allow normal lifecycle
hermes curator archive <name>  # Manually archive
hermes curator restore <name>  # Restore from archive
hermes curator backup          # Create a pre-archive snapshot
```

### The Self-Improvement Loop

This is what makes Hermes skills different from static prompt files:

1. **Complex task completed** → Hermes offers to save the approach as a skill
2. **Skill created** → Instructions captured from real, successful experience
3. **Skill loaded next time** → Same task, faster, with proven workflow
4. **Skill improved during use** → Hermes patches the skill when it discovers edge cases or better approaches
5. **Curator monitors** → Tracks usage, detects staleness, manages lifecycle

This loop means your skills get better the longer you run Hermes — no manual maintenance needed.

---

## Advanced Patterns

### Platform-Specific Skills

Some skills only make sense on specific operating systems:

```yaml
---
name: macos-shortcuts
description: Create macOS keyboard shortcuts and automations. Use when the user wants to automate macOS workflows.
platforms: [macos]
---
```

```yaml
---
name: winget-installer
description: Install Windows packages via winget. Use when setting up a new Windows dev environment.
platforms: [windows]
---
```

When `platforms` is set, the skill only appears on matching systems. Omit the field to make a skill available everywhere.

### Conditional Activation

Skills can automatically show or hide based on available toolsets:

```yaml
# This skill only appears when the browser toolset is enabled
metadata:
  hermes:
    requires_toolsets: [browser, terminal]
```

```yaml
# This skill appears as a fallback when the web search toolset is missing
# (e.g., when the user hasn't set up a search API key)
metadata:
  hermes:
    fallback_for_toolsets: [web]
```

Real use case: the built-in `duckduckgo-search` skill uses `fallback_for_toolsets: [web]`. When you have a web search API key configured, Hermes uses the native `web_search` tool and the DDG skill stays hidden. When you don't, the DDG skill appears as a free alternative.

### Hermes-Native Tool Patterns

Skills can reference Hermes-specific tools for capabilities that don't exist in other agents:

**Persistent memory across sessions:**
```markdown
## Procedure
1. Use `session_search` to check if we've discussed this topic before
2. If yes, load the context from `memory` before proceeding
3. After completing the task, save key decisions to `memory` so future sessions benefit
```

**Parallel task execution:**
```markdown
## Procedure
1. Use `delegate_task` to run tests on 3 subagents in parallel:
   - Agent A: unit tests
   - Agent B: integration tests
   - Agent C: linting and type checking
2. Collect results and present a unified report
```

**Scheduled automation:**
```markdown
## Procedure
1. Create a `cronjob` that runs daily at 9am
2. The job fetches the latest data, runs analysis, and delivers results to Telegram
```

### Chaining Skills

Multiple skills can form a workflow:

```bash
# In a Hermes session:
/skill requirement-analyzer    # Clarify what to build
/skill test-driven-dev         # Write tests first, then code
/skill code-quality-guardian   # Review before commit
/skill cicd-orchestrator       # Set up deployment
```

Or chain them in a cron job:

```bash
hermes cron create "0 9 * * *" \
  --prompt "Run requirement-analyzer on the current sprint backlog, then test-driven-dev on new items" \
  --skills requirement-analyzer,test-driven-dev
```

---

## Debugging Skills

### "My skill doesn't load when I expect it to"

**Diagnosis:** The description isn't matching the user's language.

**Fix:** Add the exact phrases users use to the description. Test by asking Hermes: "What skills do you have for [topic]?"

```yaml
# Before
description: Creates git commits.

# After
description: Create well-formatted git commits. Use when the user says "commit", "git commit", "save my changes", "commit this", or asks to commit code.
```

### "My skill loads when it shouldn't"

**Diagnosis:** The description is too broad.

**Fix:** Add a "When NOT to Use" section in the body, or tighten the description:

```markdown
## When NOT to Use
- Do NOT activate for questions about git history or viewing commits
- Do NOT activate when the user is just discussing what to commit (deploy phase only)
```

### "My changes to SKILL.md aren't taking effect"

Skills are cached at session start. After editing, reload:

```
/reload-skills
```

Or start a new session.

### "Hermes ignores parts of my instructions"

**Diagnosis:** Instructions too long or poorly structured.

**Fix:** 
- Keep SKILL.md under 500 lines
- Put critical instructions first
- Use numbered steps, not dense paragraphs
- Move details to reference files

---

## Verification Checklist

After creating or editing a skill, verify:

- [ ] `name` is lowercase, hyphens only, ≤64 chars
- [ ] `description` answers both "what" and "when" in ≤1024 chars
- [ ] File starts with `---` on line 1 (no leading whitespace or BOM)
- [ ] Frontmatter closes with `\n---\n`
- [ ] Body has at minimum: when to use, procedure, pitfalls
- [ ] Total file under 500 lines (or details moved to reference files)
- [ ] Skill loads with `/skill <name>` in a Hermes session
- [ ] Hermes correctly activates/deactivates the skill based on context
- [ ] Tested on all target platforms (if `platforms` is set)
