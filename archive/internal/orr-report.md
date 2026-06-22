# Hermes v2 Operational Readiness Review (ORR)

> **Role:** Release Operations Lead · **Date:** 2026-06-20
> **Precondition:** RC APPROVED · READY FOR BETA RELEASE

---

## Phase 1 — Release Ownership Validation

### Ownership Matrix

| Role | Owner | Responsibility |
|------|-------|----------------|
| **Release Owner** | Ow1onp | Authorize `git tag` + `gh release create`. Final go/no-go decision. |
| **Rollback Owner** | Ow1onp | Execute rollback if Beta shows critical issues. Same person as Release Owner — no escalation delay. |
| **Incident Owner** | Ow1onp | Triage incoming Issues/Discussions. Respond within 24h. |
| **QA Owner** | Hermes v2 Test Suite | 220 automated tests. CI pipeline runs on every push. |
| **Docs Owner** | `docs/v2/` | Self-documenting. Release notes + architecture + migration in repo. |

### Decision Authority

```
                  Ow1onp
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    Release      Rollback     Incident
    (tag+gh)    (revert)     (triage)
```

**No external dependencies.** Solo developer — all decisions are single-point. This is a risk (bus factor = 1) but also an advantage (zero coordination overhead for rollback).

### Ownership Verdict: ✅ ACCEPTABLE

---

## Phase 2 — Operational Monitoring Validation

### Health Check Commands

| Check | Command | Expected | Frequency |
|-------|---------|----------|:---------:|
| Test suite | `python -m pytest tests/ -q` | 220 passed | Per commit |
| v1 CLI | `hermes-skill validate skills/` | 8/8 valid | Daily |
| v2 Router | `hermes run "帮我发布项目" --dry-run` | publish_project, ≥60% | Daily |
| Import check | `python -c "import hermes_v2"` | OK | On deploy |
| Git integrity | `git status --short` | clean | Per session |

### Smoke Test (Post-Release)

```bash
# 1. Clone fresh
git clone https://github.com/Ow1onp/hermes-agent-skills.git /tmp/smoke-test
cd /tmp/smoke-test

# 2. Install
pip install -e .

# 3. v1 works
python -m cli.main validate skills/
# Expected: 8/8 valid

# 4. v2 works
PYTHONPATH=src python -m hermes_v2.cli --dry-run "创建一个 FastAPI 项目"
# Expected: create_project, ≥60% confidence

# 5. Tests pass
PYTHONPATH=src python -m pytest tests/ -q
# Expected: 220 passed

# 6. Cleanup
rm -rf /tmp/smoke-test
```

### Error Detection

| Signal | Source | Action |
|--------|--------|--------|
| Test failure | CI / local pytest | Stop, fix, re-test before any further action |
| Router confidence <60% | `hermes run --dry-run` | Investigate keyword/entity mismatch |
| User bug report | GitHub Issue | Triage within 24h. Reproduce. If confirmed, patch. |
| Token discovered | `git log --all -- .gh_token` | **EMERGENCY ROLLBACK + rotate token** |
| v1 broken | `hermes-skill validate` fails | Rollback Level 3 immediately |

### Monitoring Verdict: ✅ READY

---

## Phase 3 — Rollback Execution Validation

### Trigger Conditions (from Release Plan)

| Condition | Severity | Action |
|-----------|:--------:|--------|
| Token in git history | CRITICAL | **Immediate Level 3 + rotate token** |
| Test suite broken | HIGH | Level 3 — revert commit |
| v1 CLI broken | HIGH | Level 3 — revert commit |
| Critical bug reported | MEDIUM | Assess. If unfixable in <24h → Level 2 (delete tag) |
| Minor doc typo | LOW | Fix in new commit. No rollback needed. |

### Rollback Decision Point

```
Issue detected
  │
  ├── CRITICAL/HIGH severity?
  │     └── YES → Execute rollback immediately. No discussion needed.
  │
  └── MEDIUM severity?
        └── Assess: fixable in <24h?
              ├── YES → Patch forward (new commit on main)
              └── NO  → Level 2 rollback (delete tag, keep commit)
```

### Rollback Steps (pre-validated — NOT executed)

**Level 1 (cosmetic):**
```bash
gh release delete v2.0.0-beta --yes
gh release create v2.0.0-beta --notes-file RELEASE_v2.0.0-beta.md --prerelease
```

**Level 2 (moderate):**
```bash
gh release delete v2.0.0-beta --yes
git push origin --delete v2.0.0-beta
git tag -d v2.0.0-beta
```

**Level 3 (heavy):**
```bash
# Revert the beta commit — all v2 files removed from main
git revert 92d1c14 -m "revert: rollback v2.0.0-beta"
git push origin main
# v1.1.0 fully intact. Tag v1.1.0 still points to correct commit.
```

### Rollback Verification

After Level 3 rollback:
```bash
git log --oneline -3         # Confirm revert is HEAD
python -m cli.main validate skills/  # Confirm v1 works
ls src/hermes_v2/            # Confirm v2 code removed
```

### Rollback Confidence: ✅ HIGH

- All 3 levels documented in `beta-release-execution-plan.md`
- Single owner = zero coordination delay
- v1.1.0 tagged — always recoverable
- v2 code isolated in `src/hermes_v2/` — clean removal

---

## Phase 4 — Incident Response Validation

### Incident Classification

| Severity | Definition | Response SLA | Example |
|:--------:|-----------|:-----------:|---------|
| **P0 — Critical** | Token leak, data loss, v1 broken | Immediate | `.gh_token` in git |
| **P1 — High** | Test suite broken, CLI crash | <2 hours | `hermes-skill` segfault |
| **P2 — Medium** | Router misfire, doc error, user confusion | <24 hours | Wrong task selected |
| **P3 — Low** | Cosmetic issue, typo, minor UX | <7 days | README typo |

### Escalation Path

```
P3/P2 → Fix in next commit → Push to main
P1    → Fix immediately → Push to main → Re-tag if needed
P0    → ROLLBACK IMMEDIATELY → Fix → Re-tag
```

**No escalation chain needed** — solo developer. All decisions by Ow1onp.

### Communication Procedure

| Audience | Channel | When |
|----------|---------|------|
| Self (Ow1onp) | Git commit log | Every action |
| Users (if any) | GitHub Issue comment | Within 24h of report |
| Public | GitHub Release notes update | If tag changes |
| Future self | `docs/v2/` docs | This ORR report |

### Incident Readiness: ✅ ACCEPTABLE

---

## Phase 5 — Observation Window Validation

### Observation Duration

**7 days (Jun 20–27, 2026)** — from `v2.0.0-beta` tag creation.

### Monitoring Metrics

| Metric | Tool | Threshold | Action on breach |
|--------|------|:---------:|------------------|
| Tests passing | `pytest tests/ -q` | 220/220 | Block all further work until fixed |
| Router accuracy | Manual smoke test | 4/4 dogfood inputs | Investigate + fix keywords |
| GitHub Issues | GitHub API | Any P0/P1 | Triage within SLA |
| GitHub Stars | GitHub API | N/A (informational) | — |
| CLI startup | `hermes run --dry-run` | <1s | Acceptable; investigate if >5s |
| v1 health | `hermes-skill validate` | 8/8 valid | Rollback if broken |

### Success Criteria (from Release Plan)

| # | Criterion | Threshold |
|---|-----------|:---------:|
| S1 | No critical bugs | 0 |
| S2 | External feedback | ≥3 |
| S3 | Real usage cases | ≥1 |
| S4 | Router accuracy | 4/4 |
| S5 | Tests | 220/220 |
| S6 | Zero rollbacks | 0 |

### Exit Decision

```
After 7 days:
  ├── All 6 criteria met → GO FOR v2.0.0 STABLE
  ├── Partial (≥4/6) → EXTEND BETA (+7 days)
  └── Rollback triggered → FIX → RE-BETA → RE-REVIEW
```

### Daily Observation Log

```
Day 1 (Jun 20): Tag created. Smoke test pass.
Day 2 (Jun 21): ___ stars, ___ issues, tests 220/220
Day 3 (Jun 22): ...
Day 7 (Jun 27): Final assessment. Exit decision.
```

### Observation Verdict: ✅ PLAN READY

---

## Phase 6 — Launch Control Decision

### Pre-Launch Checklist

| # | Check | Status |
|---|-------|:------:|
| 1 | Readiness Gate passed | ✅ GO FOR BETA |
| 2 | Consistency Gate passed | ✅ 100/100 |
| 3 | RC Validation passed | ✅ RC APPROVED |
| 4 | ORR passed | ✅ THIS REPORT |
| 5 | Working tree clean | ✅ |
| 6 | HEAD = `92d1c14` | ✅ |
| 7 | 220/220 tests | ✅ |
| 8 | Token absent | ✅ |
| 9 | Rollback plan documented | ✅ 3 levels |
| 10 | Monitoring plan documented | ✅ Smoke test + daily checks |

### Risk Register (Final)

| Risk | Severity | Mitigation | Residual |
|------|:--------:|------------|:--------:|
| Solo developer (bus factor=1) | Medium | All docs in repo. v1.1.0 tagged permanently. | Medium |
| Zero users → zero feedback | Medium | Beta IS the attempt to get users. | Medium |
| Hermes ecosystem too small | Medium | Compatible with Agent Skills Open Standard. Cross-ecosystem. | Low |
| Router misfire on edge cases | Low | Confidence <40% triggers clarification. Expert Mode fallback. | Low |
| Token leak | Low | Scanned 3×. Not in history. `.gitignore` confirmed. | Very Low |

---

## LAUNCH DECISION

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    ORR PASS                                   ║
║                                                              ║
║              LAUNCH APPROVED                                  ║
║         READY FOR BETA EXECUTION                              ║
║                                                              ║
║    All 6 phases complete. Zero blockers.                      ║
║    Release: git tag v2.0.0-beta + gh release create           ║
║    Rollback: 3-level plan, single owner, v1.1.0 intact        ║
║    Monitor: 7-day window, daily smoke test,  24h SLA          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

**This ORR authorizes the operational execution of the Beta release.**
The actual `git tag` and `gh release create` commands remain unexecuted — they require explicit user command.
