# Hermes v2 Beta Release Execution Plan

> **Role:** Release Orchestrator · **Date:** 2026-06-20
> **Status:** PLAN ONLY — NO EXECUTION
> **HEAD:** `92d1c14` · **Existing tags:** v1.0.0, v1.1.0

---

## Phase 1 — Pre-Release Freeze Checklist

| # | Check | Current | Required | Go? |
|---|-------|:-------:|:--------:|:---:|
| 1 | Working tree clean | clean | clean | ✅ |
| 2 | Tests passing | 220/220 | 220/220 | ✅ |
| 3 | Release notes exist | `RELEASE_v2.0.0-beta.md` | present | ✅ |
| 4 | README Beta label | EN + zh-CN | both | ✅ |
| 5 | Token not in git | absent | absent | ✅ |
| 6 | `.gitignore` has token | yes | yes | ✅ |
| 7 | No staged changes | 0 staged | 0 staged | ✅ |
| 8 | v1 CLI functional | validate/create/list/soul | all 4 | ✅ |
| 9 | v1 code unchanged | 0 diff | 0 diff | ✅ |
| 10 | CI config present | `.github/workflows/ci.yml` | present | ✅ |
| 11 | No `__pycache__` tracked | 0 tracked | 0 tracked | ✅ |
| 12 | Version consistency | v1=1.1.0, v2=2.0.0-alpha | consistent | ✅ |

**Freeze verdict: ALL CHECKS PASS ✅**

---

## Phase 2 — Beta Artifact Definition

### Included in v2.0.0-beta

| Category | Artifacts | Count |
|----------|-----------|:----:|
| **Core** | `src/hermes_v2/` — 7 Python modules | 7 files |
| **Tasks** | `tasks/` — 6 YAML task definitions | 6 files |
| **Tests** | `tests/test_hermes_v2_*.py` — 5 test files | 5 files (116 tests) |
| **Docs** | `docs/v2/` — architecture, dogfood, migration, beta report | 4 files |
| **Docs** | `docs/hermes-v2-mvp.md` | 1 file |
| **Docs** | `docs/growth/` — 4 growth validation docs | 4 files |
| **Docs** | `docs/reports/validation-report-v1.1.0.md` | 1 file |
| **Benchmarks** | `benchmarks/` — 3 benchmarks + 2 results | 5 files |
| **Scenarios** | `tests/user-scenarios/` — 7 scenario scripts | 7 files |
| **Release** | `RELEASE_v2.0.0-beta.md` | 1 file |
| **README** | `README.md`, `README.zh-CN.md` (updated) | 2 files |

**Total: 44 files in `92d1c14`**

### NOT Included (explicitly excluded)

| Item | Reason |
|------|--------|
| Marketplace | Forbidden by MasterBrain |
| SaaS / commercialization | Forbidden |
| Agent Hub | Forbidden |
| Evolution Engine (production) | Code exists, not activated |
| Analytics Dashboard | Deferred |
| New SKILL.md files | No new skills in this release |
| PyPI package | Not uploaded yet |
| Windows installer | `install.sh` only |
| LLM-based Router | Phase 2 future work |
| Additional task types | 6 is MVP scope |

---

## Phase 3 — Release Command Plan

> ⚠️ **ALL COMMANDS ARE PLANS ONLY. DO NOT EXECUTE.**

### Step 1: Final Verification

```bash
# Verify clean state
git status
# Expected: nothing to commit, working tree clean

# Run all tests one final time
python -m pytest tests/ -q
# Expected: 220 passed

# Confirm HEAD is correct commit
git log --oneline -1
# Expected: 92d1c14 beta: prepare Hermes v2 task-first workflow
```

**Rollback:** N/A — read-only verification.

### Step 2: Create Beta Tag

```bash
git tag v2.0.0-beta -m "Hermes v2.0.0-beta: task-first natural-language interface

- Natural-language task execution (6 task types)
- Entity extraction (technology, file path, version, doc type)
- 3 user modes: Beginner, Advanced, Expert
- 220 tests passing (104 v1 + 116 v2)
- Zero v1 breakage — fully additive
- Backward compatible with v1.1.0"
```

**Expected:** Tag `v2.0.0-beta` created at `92d1c14`.

**Rollback:**
```bash
git tag -d v2.0.0-beta          # delete local
git push origin --delete v2.0.0-beta  # delete remote (if pushed)
```

### Step 3: Push Tag + Commit

```bash
# Push commit (if not already pushed)
git push origin main

# Push tag
git push origin v2.0.0-beta
```

**Expected:** Remote has tag `v2.0.0-beta`.

**Rollback:** See Phase 4.

### Step 4: Create GitHub Release

```bash
gh release create v2.0.0-beta \
  --title "Hermes v2.0.0-beta — Task-First Natural Language Interface" \
  --notes-file RELEASE_v2.0.0-beta.md \
  --prerelease \
  --target 92d1c14
```

**Expected:** GitHub Release created with "Pre-release" flag.

**Rollback:**
```bash
gh release delete v2.0.0-beta --yes
```

### Step 5: Verify GitHub Release

- Check https://github.com/Ow1onp/hermes-agent-skills/releases
- Confirm tag `v2.0.0-beta` appears
- Confirm "Pre-release" label visible
- Confirm release notes render correctly
- Confirm asset list matches Artifact Matrix

---

## Phase 4 — Rollback Strategy

### Level 1: Delete GitHub Release (lightest)

**Trigger:** Release notes error, formatting issue, wrong target.

```bash
gh release delete v2.0.0-beta --yes
# Re-create with corrected notes
gh release create v2.0.0-beta --notes-file RELEASE_v2.0.0-beta.md --prerelease
```

**Impact:** Tag remains. Commit remains. Only Release metadata changes.

### Level 2: Delete Tag + Release (moderate)

**Trigger:** Wrong commit tagged, tag name typo, premature release.

```bash
# 1. Delete GitHub Release
gh release delete v2.0.0-beta --yes

# 2. Delete remote tag
git push origin --delete v2.0.0-beta

# 3. Delete local tag
git tag -d v2.0.0-beta

# 4. (Optional) Re-tag correct commit
git tag v2.0.0-beta <correct-commit> -m "..."
git push origin v2.0.0-beta
```

**Impact:** Tag and Release removed. Commit on main preserved. v1 tags unaffected.

### Level 3: Revert Commit (heaviest)

**Trigger:** Critical bug discovered, security issue, v1 breakage.

```bash
# Option A: Revert commit (preserves history)
git revert 92d1c14 -m "revert: rollback v2.0.0-beta"
git push origin main

# Option B: Force-reset (destroys history — LAST RESORT)
git reset --hard cc49fc2    # commit before beta
git push origin main --force
```

**Impact:** All v2 files removed from main. GitHub Release will point to orphaned tag (delete separately). v1.1.0 fully intact.

### Rollback Decision Tree

```
Issue detected
  ├── Cosmetic (typo, formatting) → Level 1
  ├── Wrong commit/tag name       → Level 2
  └── Critical bug/security       → Level 3
```

---

## Phase 5 — Observation Window

### Duration: 7 Days (Jun 20–27)

### Monitoring Channels

| Channel | Frequency | Looking For |
|---------|:---------:|-------------|
| GitHub Issues | Daily | Bug reports, feature requests, confusion |
| GitHub Discussions | Daily | Questions, feedback, usage stories |
| GitHub Stars | Daily | Adoption signal |
| `tests/` | Per commit | 220/220 must hold |
| CLI self-test | Daily | `hermes run "帮我发布项目" --dry-run` |

### Alert Thresholds

| Metric | Green | Yellow | Red |
|--------|:-----:|:------:|:---:|
| Critical bugs | 0 | 1 | ≥2 |
| Test failures | 0 | 0 | ≥1 |
| CLI routing accuracy | 100% | ≥80% | <80% |
| User confusion reports | 0 | 1–2 | ≥3 |
| Token exposure | 0 | 0 | ≥1 |

### Observation Log Template

```
Day N (Jun N)
  Stars: N   Issues: N   Discussions: N
  Tests: 220/220
  Notable: (any user feedback or issues)
```

---

## Phase 6 — Beta Success Criteria

### Exit Criteria

| # | Criterion | Threshold | Measuring |
|---|-----------|:---------:|-----------|
| S1 | No critical bugs | 0 | GitHub Issues labeled `bug` |
| S2 | ≥3 external feedback items | 3+ | Issues + Discussions from non-Ow1onp users |
| S3 | ≥1 real usage case | 1+ | User reports actual task completion |
| S4 | Routing accuracy maintained | 4/4 dogfood inputs | Self-test |
| S5 | 220/220 tests | all passing | pytest |
| S6 | No rollback triggered | 0 rollbacks | Git log |

### Beta Exit Paths

```
After 7 days:
  ├── All criteria met → GO FOR v2.0.0 STABLE
  ├── Partial criteria → EXTEND BETA (+7 days)
  │     └── After 14 days:
  │           ├── Criteria met → GO FOR v2.0.0 STABLE
  │           └── Still not met → RE-EVALUATE (pivot or descope)
  └── Critical bug found → ROLLBACK → FIX → RE-BETA
```

### v2.0.0 Stable Criteria (future)

- Beta observation complete (7–14 days)
- All 6 Beta success criteria met
- User feedback incorporated into v2.1 plan
- Confidence score ≥80/100 on real-world usage
- At least 1 external contributor or tester

---

## Execution Authorization

| Stage | Status | Authorization |
|-------|:------:|---------------|
| Pre-Release Freeze | ✅ Complete | — |
| Release Consistency Gate | ✅ Passed (100/100) | — |
| Beta Release Execution | ⏳ PLANNED | **Requires manual `git tag` + `gh release create`** |
| Observation Window | ⏳ PLANNED | 7 days post-release |
| v2.0.0 Stable | ⏳ PLANNED | After Beta criteria met |

---

**This plan does NOT execute the release.** It documents the steps required.
Tag creation and GitHub Release creation are manual actions requiring the user's explicit command.
