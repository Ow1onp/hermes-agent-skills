# Quick Start: Create Your First Skill in 10 Minutes

> Goal: Go from zero to a working, reusable skill. No prior knowledge needed.

---

## Before You Start

You need Hermes Agent installed. Verify:

```bash
hermes --version
# Hermes Agent v0.15.x
```

If you don't have it: [Install Hermes Agent](https://hermes-agent.nousresearch.com/docs/)

---

## Step 1: Think of a Task You Repeat (30 seconds)

Pick something you've said to Hermes more than twice. Some ideas:

- "Summarize this article in 3 bullet points"
- "Create a git commit message from my staged changes"
- "Generate a pytest file for this module"
- "Check my code for common security issues"

We'll use a **code reviewer** skill for this tutorial. Every time you say "review this code", Hermes will follow your checklist.

---

## Step 2: Create the Skill Directory (10 seconds)

```bash
mkdir -p ~/.hermes/skills/code-review
```

That's the only directory you need. One folder, one file inside it.

---

## Step 3: Write Your First SKILL.md (5 minutes)

Create `~/.hermes/skills/code-review/SKILL.md`:

```markdown
---
name: code-review
description: Review code for security issues, bugs, and style problems. Use when the user asks for a code review, says "review this", or shares code for feedback.
version: 1.0.0
---

# Code Reviewer

## When to Use
Activate when the user:
- Says "review this code" or "code review"
- Pastes a code block and asks for feedback
- Mentions "security audit" or "bug check"

## Instructions

### 1. Security Scan (Always First)
- [ ] Check for hardcoded secrets (API keys, passwords, tokens)
- [ ] Check for SQL injection, XSS, and path traversal
- [ ] Verify input validation on all user-facing functions
- [ ] Flag any use of `eval()`, `exec()`, or `os.system()` with user input

### 2. Bug Detection
- [ ] Trace error paths — what happens when each function fails?
- [ ] Check null/undefined handling
- [ ] Look for off-by-one errors in loops
- [ ] Verify async/await — any missing awaits?

### 3. Style & Maintainability
- [ ] Functions longer than 30 lines? Suggest splitting
- [ ] Repeated logic? Suggest extraction
- [ ] Cryptic variable names? Suggest better ones

## Output Format

Present findings in three sections:

**🔴 CRITICAL** — Security issues or data loss risks. Fix before merging.
**🟡 WARNING** — Bugs or missing edge cases. Should fix.
**🟢 NOTE** — Style or maintainability suggestions. Nice to have.

Keep feedback actionable. Every issue must have:
- The specific line or function
- Why it's a problem
- A concrete fix suggestion
```

**What's happening here:**
- `name` — how you invoke it: `/code-review`
- `description` — what Hermes reads to auto-detect relevance
- `version` — track changes as you improve it
- Body — the actual checklist Hermes follows

---

## Step 4: Load the Skill (30 seconds)

In a Hermes session, type:

```
/skill code-review
```

Hermes responds showing the skill loaded. You can also load it at launch:

```bash
hermes --skills code-review
```

Now test it:

```
Review this code:

def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return db.execute(query)
```

Hermes should flag the SQL injection, missing error handling, and suggest parameterized queries — all following your checklist format.

---

## Step 5: Iterate & Improve (3 minutes)

Your first skill will work, but it won't be perfect. Here's how to make it better:

### Tighten the Description

The description controls when Hermes auto-activates the skill. If Hermes doesn't load it when you expect:

**Too narrow:**
```yaml
description: Review Python code.
```

**Better (specific keywords + triggers):**
```yaml
description: Review code for security issues, bugs, and style. Use when the user asks for a code review, says "review this", shares a PR diff, or mentions "security audit".
```

### Add Negative Triggers

Prevent the skill from loading when it shouldn't:

```markdown
## When NOT to Use
- Do NOT activate for simple "what does this line do?" questions
- Do NOT activate for code that the user explicitly says is pseudocode
```

### Pin What Works

When the skill is stable and useful, pin it so Curator won't archive it:

```bash
hermes curator pin code-review
```

---

## What You've Built

```
~/.hermes/skills/
└── code-review/
    └── SKILL.md          ← Your first skill. 50 lines. Reusable forever.
```

Every time you or anyone who shares this skill says "review this code", Hermes now has a concrete, repeatable checklist — not a vague "be helpful" instinct.

---

## Next Steps

| You want to... | Go here |
|----------------|---------|
| Add reference files, scripts, or templates | [Skill Tutorial →](TUTORIAL.md) |
| Share your skill with the community | [Contributing Guide →](CONTRIBUTING.md) |
| Understand progressive disclosure | [Skill Tutorial →](TUTORIAL.md) |
| Troubleshoot skill loading issues | [FAQ →](FAQ.md) |

---

## Quick Reference: Skill CLI Commands

```bash
# List installed skills
hermes skills list

# Load in session
/skill <name>

# Browse and install from hub
hermes skills browse
hermes skills install <name>

# Create a skill (from within a Hermes session — Hermes can write it for you)
"Save this workflow as a skill called deploy-staging"

# Lifecycle management
hermes curator status      # Check skill health
hermes curator pin <name>  # Protect from archival
```
