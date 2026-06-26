# 08 — Feedback System

## Deployed Artifacts

All feedback infrastructure lives in the repository at `Ow1onp/hermes-agent-skills`:

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml              # Structured bug report form
│   ├── feature_request.yml         # Problem → Solution → Alternatives
│   ├── skill_request.yml           # Skill-specific request form
│   ├── documentation_issue.yml     # Docs quality feedback
│   └── config.yml                  # Blank issue disabled, redirects to Discussions
├── DISCUSSION_TEMPLATE.md          # 4 category templates
FEEDBACK.md                         # User-facing guide (repo root)
```

## GitHub Issues Templates

### Bug Report (`bug_report.yml`)
Fields collected: Environment (OS, Python version), Hermes Version, Skill Version, Reproduction Steps (textarea), Expected Behavior, Actual Behavior, Additional Context.

### Feature Request (`feature_request.yml`)
Four-stage structured form: **Problem** (what pain point) → **Proposed Solution** → **Alternatives Considered** → **Importance/Impact**. Problem field is required — prevents "add X feature" without justification.

### Skill Request (`skill_request.yml`)
Project-specific template: Skill Name, Lifecycle Phase (dropdown: define/build/verify/evolve/ship), Use Case/Problem, Expected Workflow, Hermes-Specific Capabilities to Leverage.

### Documentation Issue (`documentation_issue.yml`)
Covers 5 issue types: Missing docs, Unclear explanation, Outdated content, Error in docs, Translation needed. Page URL field for precise targeting.

### `config.yml`
Blank issues disabled. Users directed to Discussions for questions/ideas, or the specific template for structured reports.

## GitHub Discussion Categories (6)

| Category | Purpose | Feeds Into |
|----------|---------|------------|
| Announcements | Release notes, project updates | — |
| Ideas | Feature brainstorming | v1.2.0 roadmap |
| Q&A | User questions, troubleshooting | FAQ expansion |
| Show & Tell | User-built skills, integrations | Community showcase |
| Feedback | General feedback, experience reports | Product insights |
| Community | Off-topic, introductions | — |

## User Survey (10 Questions)

Structure: Identity → Usage → Satisfaction → Open Feedback

1. Role (developer, team lead, student, other)
2. How did you find hermes-agent-skills?
3. Which skills have you used?
4. Have you used the CLI toolchain?
5. Satisfaction rating (1–10) on skills
6. Satisfaction rating (1–10) on validator
7. What's missing?
8. Which v1.2.0 direction matters most? (Marketplace / Analytics / Evolution — multi-choice)
9. Would you recommend to a colleague? (NPS question)
10. Open feedback

## First User Interview Guide (14 Questions)

30–45 minute semi-structured interview, 5 stages:
1. **Icebreaker** (2 min) — background, Hermes experience
2. **First Experience** (5 min) — onboarding friction, first skill creation
3. **Deep Usage** (10 min) — which skills used, workflow integration, CLI usage
4. **Needs Exploration** (10 min) — pain points, missing capabilities, comparison with alternatives
5. **Forward Look** (5 min) — v1.2.0 priorities, willingness to pay (Marketplace probe)

Includes interview recording template.

## v1.2.0 Feedback Collection Framework

### Three Collection Channels

| Channel | Type | Frequency |
|---------|------|-----------|
| GitHub Issues | Passive — always on | Continuous |
| User Survey | Active — Google Form | Every 2 weeks |
| User Interviews | Active — video call | Monthly, 3–5 per cycle |

### 6-Week Timeline

- Week 1–2: Observe (watch Issues, zero intervention)
- Week 3–4: Collect (distribute survey, schedule interviews)
- Week 5: Analyze (synthesize findings, generate report)
- Week 6: Decide (prioritize backlog, plan v1.2.0 scope)

### Label System

```
type: bug / feature / skill-request / docs
priority: P0 (critical) / P1 (high) / P2 (medium) / P3 (low)
status: needs-triage / accepted / in-progress / completed / wontfix
```

### Key Metrics (7)

- Stars growth rate (weekly)
- Unique cloners (GitHub traffic)
- Issues opened (by type)
- Issue resolution time (median days)
- Survey response rate
- NPS score (baseline from Q9)
- Returning users (repeat issue/discussion participants)

### Feedback Report Template

Standardized output format: Executive Summary → Quantitative Data → Qualitative Themes → Prioritized Action Items → Recommendations.

## Future Extension Hooks

Feedback system is designed to scale into:
- **Skill Marketplace** — "Skill Request" template doubles as demand signal
- **Skill Analytics** — usage data collection points in survey Q8
- **Evolution Engine** — feedback on skill quality feeds evolution scoring

These are signal-collection points only; no implementation exists.
