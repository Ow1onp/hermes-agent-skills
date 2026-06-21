# First 10 Users Plan — Hermes-Agent-Skills

> **Phase:** Growth Validation · **Date:** 2026-06-20 · **Target:** 10 real developers in 30 days

---

## Current State

| Metric | Value |
|--------|:-----:|
| Published platforms | DEV Community ✅ · HN Show HN ✅ |
| Content-ready platforms | Reddit · Twitter/X · Product Hunt |
| Cancelled platforms | Discord (user decision) |
| GitHub Stars | 1 |
| Issues from externals | 0 |
| Discussions active | 0 |
| Days since first post | ~4 (DEV/HN posted ~June 16–17) |

---

## Strategy: 3-Phase Funnel

```
AWARENESS  →  INSTALL  →  FEEDBACK
(posts)       (clone/    (issues/
               pip)       discussions)
```

## Phase 1: Amplify Existing Posts (Days 1–3)

DEV Community + HN Show HN are live but produced zero traction.
Root causes: low visibility, no upvotes, no social proof.

### Actions
| # | Action | Platform | Effort |
|---|--------|----------|:------:|
| 1.1 | Cross-post HN link to Twitter/X with thread | X | 15 min |
| 1.2 | Post to r/programming + r/opensource | Reddit | 20 min |
| 1.3 | Comment on related DEV posts (Hermes/Agent/AI tools) | DEV | 30 min |
| 1.4 | Share in Chinese developer communities (V2EX, 掘金) | CN | 20 min |

## Phase 2: New Platform Launches (Days 3–7)

### Remaining Platforms (content ready in `docs/community-launch-v1.1.md`)

| # | Platform | Audience | Best Time (UTC) | Format |
|---|----------|----------|:---------------:|--------|
| 2.1 | **Reddit** r/programming | 6M devs | Tue 14:00 | Text post |
| 2.2 | **Twitter/X** | AI/OSS crowd | Wed 16:00 | Thread (5 tweets) |
| 2.3 | **Product Hunt** | Early adopters | Thu 00:01 PST | Launch listing |
| 2.4 | **V2EX** (中文) | Chinese devs | Fri 10:00 CST | 分享创造 |

### Priority Order (by audience size × relevance)
1. **Reddit** — largest addressable audience, highest viral potential
2. **Product Hunt** — highest credibility signal, long shelf life
3. **Twitter/X** — network effects if picked up by AI influencers
4. **V2EX** — targeted Chinese developer audience

## Phase 3: Engagement & Retention (Days 7–30)

Once first users arrive:

| # | Action | Trigger |
|---|--------|---------|
| 3.1 | Respond to every Issue within 24h | First issue opened |
| 3.2 | Respond to every Discussion within 48h | First discussion |
| 3.3 | Thank every stargazer (if <50 stars) | Daily check |
| 3.4 | Add "Used by" section to README | ≥3 confirmed users |
| 3.5 | Write "How I use hermes-agent-skills" blog | ≥5 confirmed users |

---

## User Profile (Who are the first 10?)

| Persona | Where to find them | Value prop |
|---------|-------------------|------------|
| **Hermes Agent user** | Nous Research community, Hermes GitHub | "Skills that understand Hermes tools natively" |
| **AI tooling dev** | r/programming, HN | "CLI toolchain for skill engineering" |
| **Python backend dev** | DEV, Reddit | "3 templates, validate in <1s" |
| **Chinese indie dev** | V2EX, 掘金 | "自进化的 AI 技能工程工具" |
| **Open-source maintainer** | GitHub Explore, HN | "Standard-compliant, MIT licensed" |

---

## Conversion Funnel Targets

```
                   1000  views (combined platforms)
                      ↓  10% CTR
                    100  repo visits
                      ↓  30% install rate
                     30  clones / pip installs
                      ↓  33% engagement rate
                     10  Issues/Discussions/Stars
                      ↓  10% contributor rate
                      1  external PR
```

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|:----------:|------------|
| Low HN/DEV engagement | High | Reddit + Product Hunt are larger audiences |
| Hermes ecosystem too small | Medium | Emphasize "Agent Skills Open Standard" — framework-agnostic |
| Chinese platforms shadow-ban | Low | Use 分享创造 format, not marketing language |
| Negative HN comments | Medium | Prepare responses; don't engage with trolls |

---

## Weekly Checkpoints

| Week | Target | Check |
|:----:|--------|-------|
| 1 | 3+ new stars, 1+ issue | Reddit + PH posted |
| 2 | 5+ stars, 2+ issues, 1+ discussion | X thread monitoring |
| 3 | 8+ stars, 3+ issues, first external comment | Engagement response |
| 4 | 10+ stars, 5+ issues, 1+ external contributor | Evaluate v1.2.0 |

---

## Decision Gates

| Gate | Condition | Action |
|------|-----------|--------|
| **Continue** | ≥3 stars by Day 7 | Post to remaining platforms |
| **Pivot messaging** | <3 stars by Day 7 | Rewrite titles/hooks, re-post |
| **Re-evaluate** | 0 external users by Day 14 | Consider: is the problem real? |
| **Accelerate** | ≥10 stars by Day 14 | Start v1.2.0 planning |
