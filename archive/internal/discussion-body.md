Hey everyone 👋

I've been using [Hermes Agent](https://github.com/NousResearch/hermes-agent) daily for a few months now, and I kept running into the same three problems. So I built something to fix them.

---

## Why I Built This

**Problem 1: Skills rot silently.** I'd write a SKILL.md, use it for a week, then discover it was broken three weeks later because a tool name changed or a command stopped working. There was no feedback loop — no way to know a skill was decaying until it failed mid-task.

**Problem 2: Output didn't feel like mine.** Every code-generating session produced clean, correct code — but it wasn't *my* code. Wrong naming convention, comments where I wouldn't put them, architecture decisions I wouldn't make. I was spending more time reformatting AI output than writing the original task.

**Problem 3: Generic skills waste Hermes' potential.** Most agent skills target "any agent" and end up being glorified system prompts. They can't use slash commands, can't spawn sub-agents, can't coordinate multi-modal tools. On Hermes, that leaves most of the platform's power on the table.

So I built **[hermes-agent-skills](https://github.com/Ow1onp/hermes-agent-skills)** — a skill pack that's deeply integrated with Hermes Agent's unique capabilities, with self-evolution and persona awareness baked in from day one.

---

## What Hermes-Agent-Skills Provides

Eight skills covering the full development lifecycle, plus a Python toolchain and CLI:

```
  DEFINE           BUILD          VERIFY           SHIP           EVOLVE
 ┌────────┐     ┌────────┐     ┌─────────┐     ┌────────┐     ┌──────────┐
 │需求分析 │ ──▶ │TDD 开发│ ──▶ │多模态调试│ ──▶ │CI/CD   │ ──▶ │自进化策展 │
 │规格驱动 │     │        │     │代码门禁  │     │编排    │     │身份感知  │
 └────────┘     └────────┘     └─────────┘     └────────┘     └──────────┘
```

| Skill | Phase | What it does | Hermes-only feature |
|---|---|---|---|
| `requirement-analyzer` | Define | 5-round structured clarification | Persistent memory across sessions |
| `spec-driven-dev` | Spec | 7-element spec docs, code-first | `/skills` chaining for workflows |
| `test-driven-dev` | Build | RED-GREEN-REFACTOR with test pyramid | `delegate_task` parallel execution |
| `debugger-coordinator` | Verify | 5-step debugging workflow | `browser`+`terminal`+`vision` tri-tool |
| `code-quality-guardian` | Review | 6-axis quality gate | `patch` auto-fix + `/curator` tracking |
| `cicd-orchestrator` | Ship | GitHub Actions generation | `cronjob` scheduling + `webhook` triggers |
| `skill-curator` | Evolve | 4-stage curation pipeline | Direct `/curator` system integration |
| `persona-aware-coding` | Identity | Code style adaptation | Native SOUL.md persona system |

---

## Key Features

### 1. Skill Validator

The `SkillValidator` checks every SKILL.md against the Agent Skills Standard — frontmatter structure, YAML syntax, name format, description length, body content, and file size. It catches issues before your agent loads a broken skill.

```bash
hermes-skill validate skills/ --strict --recursive
```

Outputs a pass/fail report per file with specific error messages. `--quiet` mode only shows files with problems. `--strict` enforces recommended fields like `version`, `author`, and `triggers`.

Backed by 46 tests covering edge cases (unicode in descriptions, missing frontmatter closers, oversized files, empty bodies).

### 2. hermes-skill CLI

A Typer-based CLI that ships with the pip package:

```bash
# Scaffold a standards-compliant SKILL.md with an interactive wizard
hermes-skill create my-debug-workflow -c verify -t advanced

# Validate one file or an entire directory tree
hermes-skill validate skills/ --recursive

# List all discovered skills with metadata (table or JSON)
hermes-skill list skills/ -f json

# Generate or read SOUL.md persona files
hermes-skill soul generate architect
hermes-skill soul read ~/.hermes/SOUL.md
```

Three templates (`basic`, `advanced`, `minimal`) with interactive variable prompting. Non-interactive mode for scripting.

### 3. Agent Skills Standard Support

All 8 SKILL.md files follow the [open standard](https://github.com/addyosmani/agent-skills) proposed by Addy Osmani. This means:

- Anyone can fork these skills and adapt them to other agent runtimes
- The format is versioned and validated programmatically
- The validator is a standalone Python module you can use in your own projects
- Skills are plain Markdown — no lock-in, no proprietary format

But the format is just the container. What makes these skills different is the runtime behavior.

### 4. SOUL.md Awareness

Define your coding identity in one file:

```yaml
# ~/.hermes/SOUL.md
name: "严谨架构师"
coding_style:
  naming: snake_case
  prefer: [type_hints, custom_exceptions, immutability]
comment_style: "代码即文档"
architecture_preference: "六边形架构"
```

Load `persona-aware-coding` and every skill that generates code adapts — naming conventions, comment density, architecture patterns, type hint usage, even commit message style. The `SoulReader` parses SOUL.md at runtime and injects the profile into skill execution context.

Generate one in seconds:
```bash
hermes-skill soul generate pragmatist
```

### 5. Self-Evolving Skill Foundation

The `EvolutionEngine` tracks five dimensions per skill:

- **Usage frequency** (30-day window) — is anyone actually using this?
- **Success rate** — does it complete tasks without errors?
- **User corrections** — how often does a human have to step in?
- **Freshness** — days since last update (stale = risky)
- **Command validity** — do the embedded tool references still resolve?

Each dimension feeds a health score (0–1). Skills below 0.5 get flagged for review. Below 0.3 are candidates for archival. The engine surfaces suggestions through Hermes' native `/curator` system:

```bash
/curator status    # health dashboard
/curator run       # trigger review cycle
```

This is the foundation — right now it's analysis and suggestion. The next step is automatic patching of low-risk issues (see roadmap).

---

## Example Workflow

Here's what a real session looks like with the full skill chain loaded:

```
User: "I need to add OAuth login to my FastAPI app, but the requirements are fuzzy."

Step 1: /skill requirement-analyzer
  → 5 rounds of structured Q&A
  → Output: 95% clarity requirements doc saved to memory

Step 2: /skill spec-driven-dev
  → 7-element spec: overview, constraints, API contract, data model,
    error handling, test strategy, rollout plan
  → Code scaffolding generated

Step 3: /skill test-driven-dev
  → RED phase: write failing tests for OAuth endpoints
  → delegate_task spawns parallel workers for unit + integration tests
  → GREEN phase: implement minimum passing code
  → REFACTOR phase: clean up, verify tests still pass

Step 4: /skill code-quality-guardian
  → 6-axis review: security, complexity, style, coverage, docs, deps
  → patch auto-fixes low-risk issues (import ordering, type annotations)
  → Flags: missing rate-limiting on /token endpoint

Step 5: /skill cicd-orchestrator
  → Generates .github/workflows/ci.yml with test matrix
  → Sets up cronjob for nightly dependency audit

Step 6: /skill skill-curator
  → Analyzes this session's skill usage
  → Suggests: "requirement-analyzer took 3 corrections this session —
    consider updating its OAuth-specific guidance"
```

Each skill passes context through Hermes' persistent memory, so the next skill picks up where the last one left off.

---

## Roadmap

What I'm working on next (rough priority order):

1. **Automatic skill patching** — let EvolutionEngine apply low-risk fixes (update tool names, refresh command syntax) without human intervention
2. **Skill dependency graph** — `requirement-analyzer` output feeds `spec-driven-dev`; make these dependencies explicit and auto-chainable
3. **More skills** — thinking about `api-documenter`, `database-migration-planner`, `security-auditor`
4. **Skill marketplace concept** — a registry where people can publish, rate, and discover skills; the validator becomes a quality gate for listing
5. **Cross-agent skill portability** — translate Hermes-specific tool references to equivalent calls on other agent platforms while preserving the skill logic

No dates — this is a side project. But I'm actively working on #1 and #3.

---

## Looking For Feedback

This is v1.1.0 and it works for my workflow. But I built it for me, so I'm sure there are use cases I haven't thought of. Specifically:

- **If you use Hermes Agent** — what's the task you keep doing manually that a skill should handle? What's your biggest friction point?
- **If you've written your own SKILL.md files** — what did you wish the format supported? What broke over time?
- **If you've tried other agent skill systems** — what did they get right? What made you stop using them?

I'm not precious about any of this. If the CLI is awkward, the skills are too opinionated, or the whole concept doesn't click — tell me. That's more useful than a star.

---

## Questions For The Community

1. **Skill Requests** — What skill would make you actually install this? Drop a scenario you hit regularly and I'll prioritize building it.

2. **Feature Requests** — What's missing from the CLI? The validator? The evolution engine? If you could add one thing, what would it be?

3. **Bug Reports** — If you try installing and something breaks (especially on Windows — most of my testing is there), open an issue or drop a comment here. `pip install` issues, validation false positives, encoding problems — all fair game.

4. **Format feedback** — Does the SKILL.md format feel right? Too much structure? Not enough? The Agent Skills Standard is still evolving and I'd love data points from people actually writing skills.

---

**Install:**
```bash
pip install hermes-agent-skills
```

**Repo:** [github.com/Ow1onp/hermes-agent-skills](https://github.com/Ow1onp/hermes-agent-skills)

46 tests. MIT license. Python 3.10+.

Thanks for reading. Even if you just lurk, I appreciate you taking the time.
