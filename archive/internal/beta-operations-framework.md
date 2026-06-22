# Hermes v2 Beta Operations Framework

> **Role:** Beta Program Manager · **Date:** 2026-06-20
> **Precondition:** GO FOR BETA RELEASE · All gates closed
> **This document governs the Beta period until GA decision.**

---

## Phase 1 — Observation Window Design

### Timeline

```
Day 0  ─── Tag + Release created ─── Smoke test pass ─── Begin observation
Day 1  ─── First 24h check ─── Any immediate issues?
Day 3  ─── 72h check ─── Routing accuracy, user signals
Day 7  ─── Week 1 assessment ─── Go/No-Go for continue
Day 14 ─── Week 2 assessment ─── GA readiness evaluation
```

### Day 0 Checklist (Release Day)

| # | Action | Owner |
|---|--------|:----:|
| 1 | `git tag v2.0.0-beta 92d1c14 -m "..."` | Ow1onp |
| 2 | `git push origin main && git push origin v2.0.0-beta` | Ow1onp |
| 3 | `gh release create v2.0.0-beta --prerelease --notes-file RELEASE_v2.0.0-beta.md` | Ow1onp |
| 4 | Verify GitHub Release renders correctly | Ow1onp |
| 5 | Run smoke test (`pytest tests/ -q` → 220/220) | Ow1onp |
| 6 | Run v2 CLI smoke (`hermes run "帮我发布项目" --dry-run`) | Ow1onp |
| 7 | Log: `Day 0 complete. 220/220. CLI OK.` | Ow1onp |

### Daily Check Protocol

| Check | Command / Source | Green | Yellow | Red |
|-------|-----------------|:-----:|:------:|:---:|
| Tests | `pytest tests/ -q` | 220/220 | — | <220 |
| v1 CLI | `hermes-skill validate skills/` | 8/8 | — | <8 |
| v2 Router | `hermes run --dry-run` (4 dogfood inputs) | 4/4 | 3/4 | ≤2/4 |
| GitHub Issues | `gh issue list` | 0 new P0/P1 | 1 P2 | ≥1 P0/P1 |
| GitHub Stars | API | — | — | informational |
| Working tree | `git status --short` | clean | — | dirty |

### Observation Log Template

```
Day N (YYYY-MM-DD)
  Tests:     ___/220    v1: ___/8    Router: ___/4
  Issues:    ___ new (P0:___ P1:___ P2:___ P3:___)
  Stars:     ___ total
  Users:     ___ known active
  Notable:   (any user feedback, bugs, or decisions)
  Action:    (continue / investigate / fix / rollback)
```

---

## Phase 2 — Beta Success Metrics

| # | Metric | Type | Current | 7-Day Target | 14-Day Target | Measurement |
|---|--------|------|:------:|:-----------:|:------------:|-------------|
| M1 | **Test pass rate** | Health | 220/220 | 220/220 | 220/220 | `pytest tests/ -q` |
| M2 | **v1 backward compat** | Health | 8/8 valid | 8/8 | 8/8 | `hermes-skill validate skills/` |
| M3 | **Router accuracy** | Quality | 4/4 (71.3%) | ≥3/4 | 4/4 | Dogfood smoke test |
| M4 | **GitHub Stars** | Adoption | 1 | ≥5 | ≥10 | GitHub API |
| M5 | **External Issues** | Engagement | 0 | ≥1 | ≥3 | GitHub Issues (non-Ow1onp) |
| M6 | **External Discussions** | Engagement | 0 | ≥1 | ≥2 | GitHub Discussions |
| M7 | **Confirmed installs** | Adoption | 0 | ≥1 | ≥3 | User reports / clones |
| M8 | **Critical bugs** | Stability | 0 | 0 | 0 | P0 Issues |
| M9 | **Rollback count** | Stability | 0 | 0 | 0 | `git log` |
| M10 | **Response SLA met** | Operations | N/A | 100% | 100% | P0<immediate, P1<2h, P2<24h |

### Adoption Funnel (target)

```
100  repo visitors
  ↓  30% conversion
 30  clones / installs
  ↓  33% engagement
 10  Issues / Discussions / Stars
  ↓  10% contribution
  1  external PR or skill submission
```

---

## Phase 3 — Beta Failure Metrics

| # | Failure Condition | Severity | Automatic Action |
|---|------------------|:--------:|------------------|
| F1 | **Test suite broken** (<220 passing) | 🔴 CRITICAL | **Immediate freeze.** No commits until fixed. |
| F2 | **v1 CLI broken** (hermes-skill fails) | 🔴 CRITICAL | **Rollback Level 3.** v1.1.0 must work. |
| F3 | **Token in git** (`.gh_token` discovered) | 🔴 CRITICAL | **Rollback Level 3 + rotate token.** |
| F4 | **Security vulnerability** (reported) | 🔴 CRITICAL | **Immediate investigation.** Rollback if confirmed. |
| F5 | **Data loss** (user reports lost work) | 🔴 CRITICAL | **Rollback Level 3.** Root cause analysis required. |
| F6 | **>2 P1 bugs open simultaneously** | 🟠 HIGH | Feature freeze. Bug-fix only until cleared. |
| F7 | **Router accuracy <3/4 for 3+ days** | 🟡 MEDIUM | Investigate keywords. Patch if fixable <24h. |
| F8 | **Zero user engagement for 14 days** | 🟡 MEDIUM | Re-evaluate positioning. Consider pivot. |
| F9 | **>50% negative feedback ratio** | 🟡 MEDIUM | User survey. Determine if product/market fit exists. |
| F10 | **Install failure rate >30%** | 🟡 MEDIUM | Improve docs/installer. Add Windows support. |

### Failure Ratio Calculation

```
Negative Feedback Ratio = (bug_reports + complaints) / (total_feedback)
  < 20% → Healthy
  20–50% → Warning — investigate
  > 50% → Failure signal — re-evaluate
```

---

## Phase 4 — Rollback Governance

### Decision Matrix

| Trigger | Severity | Action | Authority | Reversible? |
|---------|:--------:|--------|:---------:|:-----------:|
| F1–F5 (CRITICAL) | P0 | **Rollback Level 3** (revert commit) | Ow1onp (automatic) | Yes — re-apply commit after fix |
| F6 (≥3 P1 bugs) | P1 | **Feature freeze** | Ow1onp | Yes — lift freeze when cleared |
| F7 (Router degraded) | P2 | **Investigate + patch** | Ow1onp | Yes — forward fix |
| F8 (Zero engagement) | P2 | **14-day assessment** | Ow1onp | N/A — strategic decision |
| F9 (Negative feedback) | P2 | **User survey** | Ow1onp | N/A — strategic decision |

### Rollback Execution Authority

```
Condition met → Ow1onp decides (no escalation needed)
  │
  ├── CRITICAL → Execute immediately. Log reason in commit.
  │
  ├── HIGH → Assess within 2 hours. Execute if unfixable.
  │
  └── MEDIUM → Assess within 24 hours. Patch or accept.
```

### Post-Rollback Protocol

1. **Log:** Document reason, timestamp, affected users in commit message
2. **Notify:** If external users exist, comment on relevant Issues
3. **Fix:** Create fix branch. Test. Merge.
4. **Re-tag:** Create new beta tag at fixed commit
5. **Re-assess:** Reset observation window from re-tag date

---

## Phase 5 — GA Readiness Criteria

### Exit Criteria (must satisfy ALL)

| # | Criterion | Threshold | Measurement |
|---|-----------|:---------:|-------------|
| G1 | **Critical bugs = 0** for ≥7 consecutive days | 0 | P0 Issues |
| G2 | **High bugs ≤ 1** for ≥7 consecutive days | ≤1 | P1 Issues |
| G3 | **Tests 220/220** for entire Beta period | 100% | pytest |
| G4 | **Router accuracy 4/4** for ≥7 consecutive days | 100% | Dogfood smoke test |
| G5 | **≥3 external feedback items** | ≥3 | Non-Ow1onp Issues/Discussions |
| G6 | **≥1 confirmed external install** | ≥1 | User reports, clone stats |
| G7 | **Zero rollbacks** in final 7 days | 0 | `git log` |
| G8 | **Observation window ≥14 days** | 14 days | Calendar |
| G9 | **All docs labeled Beta → Stable** | updated | README + docs/v2/ |
| G10 | **Negative feedback ratio <30%** | <0.3 | Feedback classification |

### GA Decision Flow

```
Day 14 assessment:
  │
  ├── G1–G10 ALL met → GO FOR GA (v2.0.0)
  │
  ├── G1–G7 met, G8–G10 partial → EXTEND BETA (+7 days)
  │     └── Day 21: re-assess
  │
  └── Any CRITICAL failure → ROLLBACK → FIX → RE-BETA
```

### v2.0.0 GA Release (future — not planned here)

Only after all G1–G10 criteria met:
- Bump `src/hermes_v2/__init__.py` version to `2.0.0`
- Update README badges: `version-2.0.0`
- Remove "Beta/Experimental" labels from docs
- Tag `v2.0.0` at stable commit
- Create GitHub Release (non-prerelease)

---

## Phase 6 — Beta Program Dashboard

### Status at Beta Start (Day 0)

| Category | Metric | Value |
|----------|--------|:----:|
| **Code** | Tests | 220/220 |
| **Code** | v1 backward compat | 8/8 valid |
| **Code** | Router accuracy | 4/4 (71.3% avg) |
| **Adoption** | GitHub Stars | 1 |
| **Adoption** | External Issues | 0 |
| **Adoption** | Known users | 0 |
| **Stability** | Critical bugs | 0 |
| **Stability** | Rollbacks | 0 |
| **Release** | Tag | v2.0.0-beta (pending) |
| **Release** | Commit | `92d1c14` |

### Dashboard Update Cadence

| Checkpoint | When | Action |
|-----------|------|--------|
| Day 0 | Release moment | Log initial state |
| Day 1 | +24h | First health check |
| Day 3 | +72h | Routing accuracy + user signals |
| Day 7 | +1 week | Go/No-Go for continue |
| Day 14 | +2 weeks | GA readiness evaluation |

### One-Page Status Card (fill daily)

```
┌─────────────────────────────────────────┐
│ HERMES V2 BETA — Day ___                │
│─────────────────────────────────────────│
│ Tests:  ___/220   Router: ___/4         │
│ Stars: ___        Issues: ___ new       │
│ Users: ___ known  Rollbacks: ___        │
│─────────────────────────────────────────│
│ Status:  🟢 HEALTHY / 🟡 WATCH / 🔴 CRIT │
│ Action:  continue / investigate / fix   │
└─────────────────────────────────────────┘
```

---

## Appendices

### A. Quick Reference — Key Commands

```bash
# Health check (daily)
python -m pytest tests/ -q
python -m cli.main validate skills/
PYTHONPATH=src python -m hermes_v2.cli --dry-run "帮我发布项目"

# Rollback (if needed)
# Level 1: gh release delete v2.0.0-beta --yes
# Level 2: + git push origin --delete v2.0.0-beta && git tag -d v2.0.0-beta
# Level 3: + git revert <commit> -m "rollback v2.0.0-beta"

# GitHub monitoring
gh issue list --state open
gh api repos/Ow1onp/hermes-agent-skills

# Version check
git tag --list
git log --oneline -5
```

### B. Contact & Escalation

| Role | Person | Response Time |
|------|--------|:------------:|
| Release Owner | Ow1onp | Immediate (CRITICAL) |
| Rollback Owner | Ow1onp | Immediate (CRITICAL) |
| Incident Responder | Ow1onp | <2h (P1), <24h (P2) |
| Community Manager | Ow1onp | <48h |

**All roles held by Ow1onp.** Solo developer — zero coordination overhead.

### C. Document Map

| Document | Purpose | Status |
|----------|---------|:------:|
| `docs/hermes-v2-mvp.md` | User-facing MVP overview | ✅ |
| `docs/v2/architecture.md` | Technical architecture | ✅ |
| `docs/v2/dogfood-report.md` | Validation findings | ✅ |
| `docs/v2/migration.md` | v1→v2 migration guide | ✅ |
| `docs/v2/beta-readiness-report.md` | Beta readiness gate | ✅ |
| `docs/v2/beta-release-execution-plan.md` | Release command plan | ✅ |
| `docs/v2/orr-report.md` | Operational readiness | ✅ |
| `docs/v2/beta-operations-framework.md` | **This document** | ✅ |
| `RELEASE_v2.0.0-beta.md` | Beta release notes | ✅ |

---

**This framework governs the Beta period from Day 0 to GA decision.**
All gates are closed. The next action is `git tag v2.0.0-beta`.
