# FAQ

> Real questions. Real answers. Organized by what you're trying to do.

---

## Getting Started

### What's the difference between a Skill and a tool?

**Skills tell Hermes WHAT to do.** Tools are HOW it does it.

A skill might say "review this code for security issues, check for SQL injection, output findings as CRITICAL/WARNING/NOTE." Hermes uses tools (`read_file`, `search_files`, `terminal`) to execute those instructions.

Think of it as: **Skills = Standard Operating Procedures. Tools = Hands.**

### How is this different from putting instructions in CLAUDE.md or .cursorrules?

CLAUDE.md and .cursorrules are **always loaded** — they consume tokens in every session, even when irrelevant.

Skills load **only when needed**. Progressive disclosure means you can have 50 skills and they cost ~5K tokens at startup, not 250K.

| | System Prompt / CLAUDE.md | Skills |
|---|---|---|
| When loaded | Every session, always | Only when relevant |
| Context cost | Paid on every interaction | Paid only when activated |
| Best for | Universal standards (code style, conventions) | Specific workflows (deploy, review, debug) |
| Maintenance | You edit manually | Hermes can improve skills automatically |

### Can I use my Claude Code or Cursor skills in Hermes?

Yes — if they follow the [Agent Skills open standard](https://agentskills.io/specification) (SKILL.md with YAML frontmatter).

Copy the skill directory to `~/.hermes/skills/`. Some Claude Code-specific features (like `!` dynamic context injection) aren't supported. Hermes-native features (persistent memory, delegate_task, cronjob) are Hermes-only.

### I've never written a skill. How hard is it?

You just wrote one by reading the [Quick Start](QUICKSTART.md). Skills are Markdown files — if you can write a checklist, you can write a skill.

---

## Writing Skills

### How long should a SKILL.md be?

**Under 500 lines.** If you're going over, move detailed reference material to `references/*.md` files.

| File size | When to use |
|-----------|-------------|
| 50-100 lines | Simple workflows (commit message generation, basic code review) |
| 100-300 lines | Medium complexity (deployment procedures, debugging protocols) |
| 300-500 lines | Complex domains (full CI/CD orchestration, multi-phase analysis) |
| 500+ lines | Split — move details to reference files |

### What makes a good description?

A good description does two things:

1. **Says what the skill does** (the "what")
2. **Lists when to use it** (the "when")

```yaml
# ❌ Too vague
description: Helps with deployment.

# ❌ Only says what
description: Deploy applications to production.

# ✅ What + When
description: Deploy applications to Vercel, AWS, or Docker with zero-downtime configuration. Use when the user says "deploy", "ship", "go live", "push to production", or asks to deploy a project.
```

The "when" part is what Hermes uses for auto-activation. Include the exact phrases users would say.

### Should I put examples in the skill?

**Always.** One concrete example is worth 10 abstract rules. Format them as "Good ✅" vs "Bad ❌":

```markdown
✅ Good commit messages:
```
feat: add user authentication with JWT
fix: prevent race condition in checkout flow
```

❌ Bad commit messages:
```
fixed stuff
updates
WIP
```
```

### How do I prevent my skill from activating when it shouldn't?

Add a "When NOT to Use" section in the skill body:

```markdown
## When NOT to Use
- Do NOT activate for simple "what does this do?" questions
- Do NOT activate when the user is just discussing ideas (not sharing actual code)
- Do NOT activate for pseudocode or whiteboard-style sketches
```

And tighten your description. If it's too broad, Hermes will activate it too often.

### Can a skill reference another skill?

Yes. Use the `related_skills` field in frontmatter:

```yaml
metadata:
  hermes:
    related_skills: [test-driven-dev, code-quality-guardian]
```

And in the body, tell Hermes to chain them:

```markdown
## Procedure
1. Complete the code changes
2. Then load `code-quality-guardian` to review before committing
3. Finally, use `cicd-orchestrator` to deploy
```

---

## Loading & Activation

### How do I load a skill?

**In-session (slash command):**
```
/skill my-skill-name
```

**At launch:**
```bash
hermes --skills my-skill-name
hermes --skills skill-a,skill-b
```

**Automatically:**
Just mention a task that matches the skill's description. Hermes loads it.

### Why isn't my skill showing up?

Common causes:

1. **Skill installed but session started before installation.** Run `/reload-skills` or start a new session.
2. **Wrong directory.** Skills must be in `~/.hermes/skills/<name>/SKILL.md`.
3. **Invalid frontmatter.** Check that your YAML parses correctly — a syntax error in frontmatter silently prevents loading.
4. **Platform mismatch.** If `platforms: [macos]` is set, the skill won't show on Windows or Linux.

### Why does my skill load when I don't want it to?

Your description is too broad. Add negative triggers in the body:

```markdown
## When NOT to Use
- Do NOT activate when the user is discussing git history (only for creating commits)
```

Or tighten the description to be more specific about what triggers it.

### How do I see what skills are available?

```bash
# In terminal
hermes skills list

# In-session slash command
/skills

# Browse the hub marketplace
hermes skills browse
```

### Can I disable a skill without uninstalling?

Skills are loaded on demand — if you never invoke it and it doesn't match your tasks, it stays idle. It costs ~100 tokens in metadata at startup (0.01% of a 1M context window).

To explicitly hide a skill:

```bash
hermes skills config    # Disable per platform
```

Or just delete it:

```bash
rm -rf ~/.hermes/skills/unwanted-skill/
/reload-skills
```

---

## Skill Lifecycle & Curator

### What is the Curator?

Curator is Hermes's built-in skill lifecycle manager. It runs in the background and:

- **Tracks** how often each skill is used
- **Flags** idle skills as "stale" after 30 days without use
- **Archives** stale skills after 60 more days (still restorable)
- **Never deletes** — maximum destructive action is archive
- **Backs up** skills before any automatic action

### Will Hermes delete my skills?

**No.** Hermes never deletes skills. The most it does is archive them — and you can restore archived skills anytime:

```bash
hermes curator restore <skill-name>
```

Pinned skills are completely exempt from automatic management:

```bash
hermes curator pin my-important-skill
```

### Can Hermes create skills on its own?

Yes. After completing a complex task (5+ tool calls, errors overcome, non-trivial workflow), Hermes may offer to save the approach as a new skill. You can accept or decline.

You can also ask explicitly:

```
Save this debugging workflow as a skill called "debug-flaky-tests"
```

### How do skills improve over time?

When Hermes uses a skill and encounters edge cases, discovers better approaches, or gets corrected by you, it can patch the skill automatically. The `/curator` system also periodically reviews skills and suggests improvements based on usage patterns.

---

## Comparison with Other Tools

### Hermes Skills vs Anthropic Agent Skills

Both use the same `SKILL.md` open standard. The key additions in Hermes:

| Feature | Anthropic | Hermes |
|---------|:---------:|:------:|
| SKILL.md format | ✅ | ✅ |
| Progressive disclosure | ✅ | ✅ |
| Agent creates skills from experience | — | ✅ |
| Automatic skill improvement | — | ✅ |
| Built-in lifecycle management (Curator) | — | ✅ |
| Persistent memory integration | — | ✅ |
| Conditional activation (requires/fallback toolsets) | — | ✅ |
| Platform-specific skills | — | ✅ |
| Portable to other agents | ✅ | ✅ (standard format) |

### Hermes Skills vs Cursor Rules

Cursor Rules (.mdc files) are **always-injected context** — they're project conventions, not procedures.

| Aspect | Cursor Rules | Hermes Skills |
|--------|:------------:|:-------------:|
| Purpose | Set coding standards | Execute specific workflows |
| Loading | Always loaded or glob-scoped | On demand (progressive disclosure) |
| Format | .mdc in .cursor/rules/ | SKILL.md in ~/.hermes/skills/ |
| Self-improving | No | Yes |
| Cross-agent portable | No (Cursor-specific) | Yes (open standard) |
| Lifecycle management | No | Yes (Curator) |

### Hermes Skills vs Claude Code Skills

Both follow the Agent Skills open standard. Differences are in platform integration:

| Feature | Claude Code | Hermes |
|---------|:-----------:|:------:|
| Format | SKILL.md | SKILL.md |
| Invocation | `/skill-name` | `/skill-name` |
| Subagent support | Via `--fork` | Via `delegate_task` |
| Dynamic context (`!` commands) | ✅ | — |
| Persistent memory | — | ✅ |
| Self-improvement | — | ✅ |
| Cron scheduling | — | ✅ (`cronjob`) |
| Multi-platform delivery | — | ✅ (Telegram, Discord, Slack, etc.) |

### Can I use the same skill across all these tools?

If your skill uses only the standard SKILL.md format (no tool-specific references), it works in any tool that supports the Agent Skills standard — Claude Code, Codex CLI, Cursor, Gemini CLI, and Hermes.

Hermes-specific features (`delegate_task`, `memory`, `session_search`, `cronjob`, `/curator`) are unique to Hermes and won't work elsewhere — but they don't break the skill either. A tool that doesn't support them will just skip those instructions.

---

## Troubleshooting

### "My skill is in the right place but hermes skills list doesn't show it"

```bash
# Check the exact path
ls -la ~/.hermes/skills/your-skill/

# Check SKILL.md frontmatter
head -20 ~/.hermes/skills/your-skill/SKILL.md

# Reload skills in session
/reload-skills
```

Common frontmatter issues:
- Missing `---` on line 1
- `name` field doesn't match the directory name (not required to match, but good practice)
- YAML syntax error (unbalanced quotes, bad indentation)

### "Hermes says 'skill not found' when I use /skill-name"

The slash command uses the `name` field from frontmatter, not the directory name. Verify:

```bash
grep "^name:" ~/.hermes/skills/your-skill/SKILL.md
```

Make sure you're using the exact name (case-sensitive, hyphens not underscores).

### "My edits to SKILL.md aren't working"

Skills are cached at session start. After editing:

```
/reload-skills
```

Or start a new session: `/new`

### "The skill loads but Hermes doesn't follow my instructions"

Diagnose step by step:

1. **Instructions too long?** Trim to under 500 lines. Move details to reference files.
2. **Instructions too vague?** Replace "write good code" with specific checklists.
3. **Instructions buried?** Put critical steps first and in numbered lists.
4. **Conflicting with system prompt?** Check if your instructions contradict Hermes's default behavior.

### "I'm getting YAML errors in my frontmatter"

```bash
# Validate your YAML
python -c "import yaml; yaml.safe_load(open('$HOME/.hermes/skills/your-skill/SKILL.md').read().split('---')[1])"
```

Common YAML issues:
- Tabs instead of spaces
- Unquoted strings with special characters (`:`, `#`, `{`, `}`)
- Multi-line strings without `|` or `>` indicator

---

## Advanced

### Can I use MCP tools in a skill?

Yes. If an MCP server is connected via `hermes mcp add`, its tools appear alongside built-in Hermes tools. Your skill can reference them by name, just like any other tool.

### Can a skill run on a schedule?

Use the `cronjob` tool with skills:

```bash
hermes cron create "0 9 * * *" \
  --prompt "Generate the daily standup report" \
  --skills standup-generator \
  --deliver telegram
```

### Can skills share data with each other?

Skills within the same Hermes session can use `memory` to share data. For cross-session or cross-skill data, use `session_search` or write to a shared file:

```markdown
## Procedure
1. Check `memory` for any previous analysis results from `data-analyzer` skill
2. Read shared state from `~/.hermes/skills/shared/state.json`
3. After completion, update the shared state
```

### Are skills version-controlled?

User-local skills (`~/.hermes/skills/`) are not git-tracked by default. The Curator creates backups before any automatic action:

```bash
hermes curator backup    # Manual backup
hermes curator rollback  # Restore from last backup
```

For skills you want to version-control, put them in a git repo and install via `hermes skills tap`:

```bash
hermes skills tap add your-username/your-skills-repo
```

---

## Still Stuck?

- Check the [official Hermes docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
- Load the `hermes-agent` skill in a session: `/skill hermes-agent`
- Search past conversations: `session_search` in any Hermes session
- [Open a GitHub issue](https://github.com/NousResearch/hermes-agent/issues)
- Join the [Nous Research Discord](https://discord.gg/NousResearch)
