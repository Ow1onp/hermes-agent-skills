# Contributing Guide

> Skills are plain Markdown. Anyone can write them. Everyone benefits. Here's how to contribute yours.

---

## Ways to Contribute

| You want to... | Best path |
|----------------|-----------|
| Share a skill you wrote | Publish to the Skills Hub → |
| Improve an existing skill | Open a PR or submit feedback → |
| Report a bug in the skills system | Open a GitHub issue → |
| Add to the official skill catalog | PR to [hermes-agent-skills](https://github.com/Ow1onp/hermes-agent-skills) → |
| Write documentation | PR to this docs/ directory → |

---

## Publishing a Skill to the Hub

The Skills Hub is the community marketplace for Hermes skills. Publishing takes 2 minutes.

### Step 1: Verify Your Skill

Run through the [Tutorial Verification Checklist](TUTORIAL.md#verification-checklist). At minimum:

```bash
# Check file structure
ls ~/.hermes/skills/your-skill/
# Should show: SKILL.md (+ optional references/, scripts/, templates/)

# Load it in a session
/skill your-skill
# Does it load? Does Hermes follow the instructions?

# Test auto-activation
hermes -q "A query that should trigger your skill"
# Does Hermes load it automatically?
```

### Step 2: Local Validation

If you have the `hermes-agent-skills` Python library:

```bash
cd E:/Projects/hermes-agent-skills
python -m pytest tests/test_validator.py -v -k "your_skill_name"
```

Or validate manually:

```python
import yaml, pathlib

path = pathlib.Path("~/.hermes/skills/your-skill/SKILL.md").expanduser()
content = path.read_text()

# Check frontmatter
assert content.startswith("---"), "Must start with ---"
parts = content.split("---", 2)
assert len(parts) >= 3, "Missing closing ---"
fm = yaml.safe_load(parts[1])
assert "name" in fm, "Missing 'name' field"
assert "description" in fm, "Missing 'description' field"
assert len(fm["description"]) <= 1024, f"Description too long: {len(fm['description'])} chars"
assert len(fm["name"]) <= 64, f"Name too long: {len(fm['name'])} chars"

# Check body
body = parts[2].strip()
assert body, "Body is empty"

print("✅ Validation passed")
```

### Step 3: Publish

```bash
hermes skills publish ~/.hermes/skills/your-skill/
```

Or, if your skill is in a GitHub repo:

```bash
# Users can install directly from your repo:
hermes skills tap add your-username/your-skills-repo
hermes skills browse
hermes skills install your-skill
```

---

## Contributing to Official Skill Collections

### hermes-agent-skills (Community Collection)

The [hermes-agent-skills](https://github.com/Ow1onp/hermes-agent-skills) repo maintains production-grade skills organized by development phase:

```
skills/
├── define/       # Requirement analysis, spec writing
├── build/        # Coding patterns, TDD
├── verify/       # Debugging, code review, quality gates
├── ship/         # CI/CD, deployment
└── evolve/       # Skill curation, persona adaptation
```

**Pull request checklist:**

- [ ] Skill placed in the correct phase directory: `skills/<phase>/<name>/SKILL.md`
- [ ] Frontmatter valid (name, description required; version, author, license recommended)
- [ ] Description starts with "Use when..." and includes trigger keywords
- [ ] Body structured: Overview → When to Use → Procedure → Pitfalls → Verification
- [ ] Hermes-native tool references where applicable (`delegate_task`, `session_search`, `memory`, `/curator`)
- [ ] No broken relative links to reference files
- [ ] Tested in a live Hermes session (loads, activates, produces correct output)
- [ ] If Python scripts included, compatible with Python 3.9+ (no `X | Y` union syntax)

**Commit format:**
```
feat: add <skill-name> skill

<One-line description of what the skill does>
```

### Hermes Agent Core (Bundled Skills)

Skills in the main [Hermes Agent](https://github.com/NousResearch/hermes-agent) repo ship with every installation. These follow stricter standards — see the [main repo's CONTRIBUTING.md](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md).

---

## Skill Quality Standards

### Minimum Viable Skill

Every skill, no matter how simple, must have:

| Element | Requirement |
|---------|-------------|
| **Valid frontmatter** | YAML parses, `name` + `description` present, `description` ≤ 1024 chars |
| **Non-empty body** | Actual instructions after frontmatter |
| **Clear activation** | Description makes it obvious when the skill should load |

### Production-Grade Skill

For skills you want others to depend on:

| Element | Requirement |
|---------|-------------|
| **Complete frontmatter** | name, description, version, author, license, metadata.tags |
| **Structured body** | Overview → When to Use → Procedure → Pitfalls → Verification |
| **Explicit triggers AND anti-triggers** | "Use when X" AND "Do NOT use when Y" |
| **Concrete examples** | At least one worked example of input → output |
| **Error handling** | What to do when prerequisites aren't met (missing API keys, unavailable tools) |
| **Test coverage** | Skill validated in a real Hermes session on target platforms |
| **Documentation** | Complex workflows explained in reference files, not crammed into SKILL.md |

### What Makes a Skill "Hermes-Native"

A skill that fully leverages Hermes's capabilities (vs a generic prompt that works anywhere):

```markdown
## Procedure (Hermes-Native)

1. **Check memory first**: Use `session_search` to find past discussions of this topic
2. **Parallelize heavy work**: Use `delegate_task` to run analysis on 3 subagents simultaneously
3. **Persist learnings**: After completion, save key decisions to `memory` for future sessions
4. **Schedule follow-up**: If this task needs repeating, offer to create a `cronjob`
5. **Track in Curator**: The `/curator` system will monitor this skill's usage and suggest improvements
```

---

## Review Guidelines for Maintainers

When reviewing a skill contribution:

### Blocking Issues (Must Fix)

- [ ] Frontmatter doesn't parse (invalid YAML, missing `---` delimiters)
- [ ] `name` or `description` missing
- [ ] Description > 1024 characters
- [ ] Body is empty
- [ ] Skill is a duplicate of an existing skill (merge instead)
- [ ] Contains hardcoded secrets or API keys

### Quality Issues (Should Fix)

- [ ] Description doesn't include trigger keywords
- [ ] No "When NOT to Use" section (likely to over-activate)
- [ ] Instructions are aspirational, not specific
- [ ] Missing pitfall documentation for known edge cases
- [ ] File > 500 lines without using reference files for overflow
- [ ] Python scripts use Python 3.10+ syntax without `from __future__ import annotations`

### Nice to Have

- [ ] Hermes-native tool references (memory, delegate_task, session_search, cronjob)
- [ ] Platform declaration if OS-specific
- [ ] `requires_toolsets` or `fallback_for_toolsets` for conditional activation
- [ ] Version history in the skill or repo

---

## Directory Conventions

### User-Local Skills

```
~/.hermes/skills/
├── my-skill/
│   ├── SKILL.md
│   └── references/
│       └── advanced.md
└── another-skill/
    └── SKILL.md
```

These are personal to you. Hermes creates and manages skills here.

### Community Collection

```
hermes-agent-skills/skills/
├── define/
│   ├── requirement-analyzer/
│   │   └── SKILL.md
│   └── spec-driven-dev/
│       └── SKILL.md
├── build/
│   └── test-driven-dev/
│       ├── SKILL.md
│       ├── references/
│       │   └── patterns.md
│       └── scripts/
│           └── coverage-check.py
├── verify/
├── ship/
└── evolve/
```

Phase-based organization. Each skill in its own directory under the appropriate phase.

---

## Writing Scripts for Skills

Scripts go in `scripts/` and should be self-contained:

### Python Scripts

```python
#!/usr/bin/env python3
"""One-line description of what this script does.

Usage: python scripts/my_script.py <arg1> [arg2]
Exit codes: 0 = success, 1 = user error, 2 = system error
"""
import sys
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/my_script.py <required_arg>", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Do the work
        result = {"status": "ok", "data": "..."}
        print(json.dumps(result))
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
```

**Requirements:**
- Print JSON output to stdout (structured data)
- Print errors to stderr
- Use meaningful exit codes (0, 1, 2)
- Python 3.9+ compatible (no `X | Y` union syntax — use `Optional[Union[X, Y]]`)
- No external dependencies unless declared in skill metadata

### Bash Scripts

```bash
#!/usr/bin/env bash
set -euo pipefail

# One-line description
# Usage: bash scripts/my_script.sh <arg1>
```

**Requirements:**
- `set -euo pipefail` at the top
- Check prerequisites at the start
- Print errors to stderr (`>&2 echo "error"`)

---

## Getting Help

- **Skill not working?** Check the [FAQ](FAQ.md) first
- **Format questions?** See the [Tutorial](TUTORIAL.md#anatomy-of-a-skillmd)
- **Hermes tool reference?** Load `skill_view('hermes-agent')` in any Hermes session
- **Want feedback on your skill?** Open a draft PR and ask for review
- **Found a bug in the skills system?** [Open an issue](https://github.com/NousResearch/hermes-agent/issues)
