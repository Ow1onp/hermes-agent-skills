# Migration Plan — Hermes v1 → v2

> **Status:** v2 MVP ready · **⚠️ Beta / Experimental** · **Breaking changes:** ZERO

---

## What Changes

| Aspect | v1 | v2 |
|--------|:--:|:--:|
| How to start a task | Write constraint prompt manually | Say it in natural language |
| Skill selection | User picks skill explicitly | System auto-selects |
| Role selection | User must know roles | System auto-assigns persona |
| Constraint writing | User must write constraints | System auto-generates |
| Expert users | N/A (everyone is expert) | Expert Mode = pure v1 |

## What Does NOT Change

| Aspect | Status |
|--------|:------:|
| All 8 SKILL.md files | Unchanged |
| `hermes-skill` CLI (create, validate, list) | Unchanged |
| Skill Validator | Unchanged |
| Evolution Engine | Unchanged |
| SoulReader | Unchanged |
| CI/CD pipeline | Unchanged |
| pyproject.toml | Unchanged |
| Agent Skills Open Standard | Unchanged |

---

## How to Migrate

### As a v1 User (Expert)

**You don't need to do anything.** Your existing workflow works unchanged:

```bash
# v1 way — still works
hermes-skill validate skills/

# v2 Expert Mode — identical to v1
hermes run "## Authority
你是 Release Manager
## Mission
发布 v1.2.0
..."
```

v2 adds `hermes run` **alongside** `hermes-skill`. Nothing is removed.

### As a New User (Beginner)

Start directly with v2. No learning curve:

```bash
# Just say what you want
hermes run "帮我发布项目"
hermes run "修复 test_validator.py 的错误"
hermes run "创建一个叫 my-bot 的项目"
```

The system handles everything. You never need to know about roles or constraints.

### As an Intermediate User (Advanced)

Transition from Beginner to Advanced when you want more control:

```bash
# Beginner (auto)
hermes run "发布 v1.2.0"

# Advanced (specify persona)
hermes run "使用 Release Manager 发布 v1.2.0"

# Advanced with verbose
hermes run --verbose "使用 Release Manager 发布 v1.2.0"
# Shows the generated constraint prompt
```

---

## Migration Timeline

```
Week 1–2:  v2 MVP ships
           - 6 task definitions
           - Rule-based Intent Router
           - Task Orchestrator
           - All 3 modes

Week 3–4:  User testing
           - 5 new users try Beginner Mode
           - Collect feedback on routing accuracy
           - Tune keyword lists

Week 5:    Polish
           - Fix routing edge cases
           - Add more task definitions
           - Write v2 documentation

Week 6:    v2.0.0 release
           - Stable tag
           - GitHub Release
           - Announce alongside v1
```

---

## Rollback

v2 is pure additive. To roll back:

```bash
# Option 1: Just don't use v2
# Keep using hermes-skill as before

# Option 2: Remove v2 code
rm -rf src/hermes_v2/
rm -rf tasks/

# Option 3: Pin to v1 tag
git checkout v1.1.0
```

Zero data loss. Zero downtime. Zero impact on existing workflows.

---

## FAQ

**Q: Will my existing SKILL.md files break?**
A: No. v2 doesn't modify any skill files. It reads them the same way v1 does.

**Q: Do I need to learn constraint engineering?**
A: No. Beginner Mode hides all constraints. Advanced Mode shows them optionally (`--verbose`). Expert Mode uses them directly.

**Q: What if the Router picks the wrong task?**
A: Use Advanced Mode and specify the persona: `hermes run "使用 Release Manager 发布"`. Or use Expert Mode for full control.

**Q: Can I add my own task definitions?**
A: Yes. Add a YAML file to `tasks/` following the schema. The Router picks it up automatically.

**Q: Is v2 slower than v1?**
A: Negligible. The Router adds <1ms (rule-based keyword matching). No LLM calls.
