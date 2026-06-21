# Hermes v2.0.0-beta — Task-First Workflow

> **Release:** v2.0.0-beta · **Date:** 2026-06-20
> **⚠️ Beta / Experimental** — Not production-ready. v1.1.0 remains stable.

---

## What is Hermes v2 Beta?

Hermes v2 adds a **natural-language frontend** to the Hermes Agent skill system. Instead of writing constraint-engineering prompts by hand, users say what they want in plain language.

```
v1:  User writes "## Authority\n你是 Release Manager\n## Mission\n..."
v2:  User says "帮我发布项目" → system handles everything automatically
```

---

## Why Task-First?

v1 exposed internal concepts (roles, skills, constraints) directly to users. This created friction:
- "Which role do I choose?" (8 personas)
- "Which skill do I load?" (8 SKILL.md files)
- "How do I write a constraint prompt?" (Authority, Mission, Constraints...)

**v2 inverts the model:** the user states the goal; the system figures out how.

---

## Features

### Three User Modes

| Mode | Input | Behavior |
|------|-------|----------|
| **Beginner** | "帮我发布项目" | Full auto: detect intent → select skills → generate constraints → execute |
| **Advanced** | "用 Release Manager 发布" | User picks persona; system handles the rest |
| **Expert** | `## Authority\n你是...` | Pure v1 — bypasses v2 pipeline entirely |

### Entity Extraction

v2 recognizes specifics in user input and injects them into the execution plan:
- **Technology:** "FastAPI", "Django", "React" → constraint prompt includes tech stack
- **File path:** "test_router.py" → debug workflow targets the right file
- **Version:** "v2.0.0" → release workflow uses the exact version
- **Document type:** "README" → docs workflow knows what to write

### Confidence Calibration

Every routing decision includes a confidence score (0–100%). Below 40% triggers a clarification question. Real-world dogfood inputs average **71.3%** confidence.

### 6 Built-in Tasks

| Task | Trigger (CN) | Trigger (EN) | Skills |
|------|-------------|-------------|--------|
| `publish_project` | 帮我发布项目 | publish the project | cicd-orchestrator, code-quality-guardian |
| `fix_bug` | 修复这个错误 | fix the bug | debugger-coordinator, code-quality-guardian |
| `create_project` | 创建一个项目 | create a project | requirement-analyzer, spec-driven-dev, test-driven-dev |
| `write_docs` | 写文档 | write docs | (auto-detect) |
| `review_code` | 检查代码 | review code | code-quality-guardian |
| `release_version` | 发布 v1.2.0 | release v1.2.0 | cicd-orchestrator, code-quality-guardian |

---

## Backward Compatibility

**v1 is unchanged.** All existing functionality works as before:

```bash
# v1 CLI — always available
hermes-skill validate skills/
hermes-skill create my-skill
hermes-skill list skills/

# v2 Beta — new entry point
python -m hermes_v2.cli "帮我发布项目"
```

- 8 SKILL.md files: **unmodified**
- `hermes-skill` CLI: **unchanged**
- v1 tests (104): **all passing**
- v2 is in `src/hermes_v2/` + `tasks/` — **no v1 files touched**

---

## Known Limitations

| Limitation | Impact | Plan |
|-----------|--------|------|
| Rule-based Router | May misfire on ambiguous inputs | LLM Router in Phase 2 |
| 6 task types | Limited coverage | Expand based on user feedback |
| No Persian/Farsi/etc. | CN + EN only | Language contributions welcome |
| Entity extraction is regex-based | Misses novel tech names | Expand knowledge base over time |
| CLI display is minimal | No rich output formatting | Improve in v2.1 |

---

## Try It

```bash
# Clone (if not already)
git clone https://github.com/Ow1onp/hermes-agent-skills.git
cd hermes-agent-skills

# Install (v1 way — still works)
pip install -e .

# v2 Beta — natural language
python -m hermes_v2.cli "创建一个 FastAPI 项目"
python -m hermes_v2.cli "帮我发布项目" --dry-run
python -m hermes_v2.cli "修复这个错误" --verbose

# Run all tests
python -m pytest tests/ -q
```

---

## Rollback

v2 is purely additive. To remove it:

```bash
# Option 1: Just don't use v2
# Keep using hermes-skill as before

# Option 2: Remove v2 files
rm -rf src/hermes_v2/ tasks/ tests/test_hermes_v2*.py docs/v2/

# Option 3: Stay on v1 tag
git checkout v1.1.0
```

**Zero data loss. Zero downtime. Zero v1 impact.**

---

## What's Next

- **Your feedback** → Open an Issue or Discussion
- **New task types** → Submit a Skill Request
- **Language support** → PRs welcome for new languages
- **v2.0.0 stable** → After Beta feedback cycle (4–6 weeks)

---

**This is Beta software.** APIs may change. Report issues on GitHub.
