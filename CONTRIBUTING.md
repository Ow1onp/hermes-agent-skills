# Contributing to hermes-agent-skills

Skills are plain Markdown. Anyone can write them. Here's how.

## Ways to Contribute

| You want to... | Best path |
|----------------|-----------|
| Submit a new skill | Create `skills/<phase>/<name>/SKILL.md` → validate → open PR |
| Improve an existing skill | Edit the SKILL.md → run tests → open PR |
| Report a bug | Open a [GitHub Issue](https://github.com/Ow1onp/hermes-agent-skills/issues) |
| Fix a bug or add a feature | Fork → branch → test → PR |
| Improve documentation | Edit files in `docs/` or README → PR |

## Quick Start for Skill Authors

```bash
# 1. Install the CLI
pip install hermes-agent-skills

# 2. Scaffold a new skill
hermes-skill create my-skill-name

# 3. Edit the generated SKILL.md

# 4. Validate
hermes-skill validate skills/<phase>/my-skill-name/SKILL.md

# 5. Run all tests
pytest tests/ -v

# 6. Open a PR
```

## Skill Format Requirements

Every SKILL.md must:

- Start with YAML frontmatter (`---` ... `---`)
- Include `name` (lowercase, hyphens, ≤64 chars), `description` (≤1024 chars)
- Recommended: `version` (SemVer), `author`, `triggers`
- Body must have at minimum: overview, core workflow, gate checklist

Run `hermes-skill validate` to check compliance before submitting.

## Code Contributions

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
cd hermes-agent-skills
pip install -e ".[dev]"
pytest tests/ -v
```

- Write tests for new functionality
- Keep PRs focused (one feature/fix per PR)
- All tests must pass before merge
- Follow existing code style

## Review Process

- Issues acknowledged within 24 hours
- PRs reviewed within 48 hours
- CI must pass (lint + test + skill validation)
