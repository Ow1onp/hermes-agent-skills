# Hermes v2 — Dogfood Evaluation Report

> **Evaluator:** Product Owner · **Date:** 2026-06-20
> **⚠️ Beta / Experimental** · **Rule:** 只观察，不修复。发现即记录。

---

## Summary

| Task | Input | Expected | Got | Confidence | UX Score |
|:----:|-------|----------|:---:|:----------:|:--------:|
| 1 | "创建一个 FastAPI 项目" | create_project | ✅ create_project | 36.7% | 6/10 |
| 2 | "修复 test_router.py 失败的问题" | fix_bug | ✅ fix_bug | 23.9% | 7/10 |
| 3 | "帮我发布 v2.0.0" | release_version | ✅ release_version | 57.9% | 8/10 |
| 4 | "帮我写 README" | write_docs | ✅ write_docs | 18.6% | 5/10 |

**Routing Accuracy: 4/4 correct (100%)**
**Average Confidence: 34.3%** (too low across the board)

---

## Task-by-Task Evaluation

### Task 1: "创建一个 FastAPI 项目"

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Routing Accuracy | 8/10 | Correct task (create_project). Wrong: "FastAPI" detail lost. |
| Constraint Quality | 6/10 | Generic create_project prompt. No "FastAPI" specificity. |
| User Experience | 6/10 | User said "FastAPI" — got generic project creation. |
| **Overall** | **6/10** | Routes correctly but drops critical user intent detail. |

**Finding: Intent entity loss**
The user specified a concrete technology ("FastAPI") but the constraint prompt only says "创建一个 Python 项目". The technology choice is not propagated into the constraint. A real user would be frustrated: they asked for FastAPI, got a generic project.

### Task 2: "修复 test_router.py 失败的问题"

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Routing Accuracy | 7/10 | Correct task (fix_bug). File path preserved. |
| Constraint Quality | 7/10 | Debugger workflow well-matched. File path in prompt. |
| User Experience | 7/10 | Natural input → correct debug workflow. Confidence low but usable. |
| **Overall** | **7/10** | Best performer among the 4. Debug workflow is the most mature. |

**Finding: Low confidence on compound query**
Only "修复" and "修" matched. "失败" not in keywords. "test_router.py" not parsed. Confidence 23.9% but still routed correctly — luck, not design. A different phrasing might have failed.

### Task 3: "帮我发布 v2.0.0"

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Routing Accuracy | 9/10 | Correct task (release_version). Version pattern bonus works. |
| Constraint Quality | 8/10 | Full release pipeline: bump → test → changelog → tag → release. |
| User Experience | 8/10 | "发布 v2.0.0" is intuitive. Generated prompt is actionable. |
| **Overall** | **8/10** | Strongest performer. Version number detection is the key differentiator. |

**Finding: Version pattern bonus is a crutch**
Only "发" matched as a keyword. The 57.9% confidence comes entirely from the +3.0 version pattern bonus. If the user said "发布下一个版本" (no version number), it would route to publish_project instead.

### Task 4: "帮我写 README"

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Routing Accuracy | 5/10 | Correct task but 18.6% confidence — barely above threshold. |
| Constraint Quality | 5/10 | Generic docs prompt. No project context injected. |
| User Experience | 5/10 | "帮我写 README" is common. 18.6% confidence feels broken. |
| **Overall** | **5/10** | Weakest performer. Only "README" matched. All other keyword misses. |

**Finding: write_docs has the weakest keyword coverage**
Only 1 keyword match ("README") from 7 Chinese keywords. The input is a common real-world phrase ("帮我写 README") but the keyword list doesn't cover it well.

---

## Failure Analysis

### 1. Entity Drop (Task 1) — 🔴 Critical

```
Input:  "创建一个 FastAPI 项目"
Router: create_project ✓
Prompt: "创建一个 Python 项目" ✗  (FastAPI lost)
```

**Impact:** User specifies a technology → system ignores it. This is the most common real-world case: "create a Django project", "create a React app", etc.

**Root cause:** No entity extraction in the router. Keywords match intent ("create", "project") but specific technologies are not captured.

**Severity:** High. Makes the system feel dumb even when routing correctly.

### 2. Confidence Crisis (All Tasks) — 🟡 Medium

```
Task 1: 36.7%  Task 2: 23.9%  Task 3: 57.9%  Task 4: 18.6%
Average: 34.3%
```

**Impact:** 3 of 4 tasks have confidence <40%. The clarification threshold (15%) is the only thing preventing false clarifications. The numbers don't inspire confidence.

**Root cause:** Rule-based matching produces low raw scores. The denominator (total keywords) drags scores down when only 1-2 keywords match.

### 3. Keyword Blindness (Task 2, 4) — 🟡 Medium

```
"修复 test_router.py 失败的问题" → matched: ["修复", "修"] only
"帮我写 README"               → matched: ["README"] only
```

**Impact:** Common phrases fail to match because the keyword lists are incomplete.

**Root cause:** Keyword lists are manually curated. No semantic understanding. "失败" is semantically "error" but isn't in the keyword list.

### 4. Generic Constraints (Task 1, 4) — 🟡 Medium

```
Task 1: Prompts for "创建项目" but user said "FastAPI 项目"
Task 4: Prompts for generic docs, no project name injection
```

**Impact:** Constraint prompt is too generic. The agent following this prompt wouldn't know it's a FastAPI project.

### 5. publish_project vs release_version Ambiguity — 🟢 Low (currently working)

"发布 v2.0.0" correctly routes to release_version thanks to version bonus.
But "帮我发布" (no version) routes to publish_project.
This is correct behavior but the boundary is fragile — dependent on a regex hack.

---

## User Experience Assessment

### What Works Well

- ✅ Natural language input is genuinely simple: "帮我发布 v2.0.0" just works
- ✅ Three modes auto-detect correctly (no user needs to choose)
- ✅ Constraint prompts are generated automatically, invisible to Beginner users
- ✅ Workflow steps are logically ordered and descriptive
- ✅ Success criteria are concrete and verifiable

### What Doesn't Work

- ❌ Specific details in user input are lost (entity drop)
- ❌ Confidence numbers are too low to trust
- ❌ Some common Chinese phrases miss keyword matches
- ❌ Constraint prompts don't reflect user's specific technology choices
- ❌ No project context auto-injection (project name, language, framework)

---

## Scorecard

| Dimension | Score | Weight | Weighted |
|-----------|:-----:|:------:|:--------:|
| Routing Accuracy | 8/10 | 40% | 3.2 |
| Constraint Quality | 6/10 | 30% | 1.8 |
| User Experience | 6/10 | 30% | 1.8 |
| **TOTAL** | | | **6.8/10** |

---

## Verdict

**Hermes v2 correctly routes 4/4 real-world tasks.** The architecture is sound. The Task-First model works.

**However, it's not production-ready.** Two critical issues block real usability:

1. **Entity drop** — user specifics are lost in routing
2. **Confidence crisis** — scores are too low to trust without manual verification

These are not architectural problems. They are data problems:
- Keyword lists need expansion (semantic coverage)
- Entity extraction needs to be added (not just intent classification)
- Confidence scoring needs recalibration (rule-based is inherently noisy)

---

## Next Steps (for future phase — NOT now)

*(Noted but not executed — Dogfood phase forbids code changes)*

1. Add entity extraction: `{technology: "FastAPI", framework: "FastAPI"}`
2. Expand keyword lists based on real user phrases observed in dogfood
3. Inject extracted entities into the constraint prompt
4. Recalibrate confidence scoring (normalize by matched-keyword count, not total)
5. Add auto project-context injection (name, language, framework from current dir)
