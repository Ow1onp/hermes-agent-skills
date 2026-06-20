# HermesHub Architecture Design Document

## Overview

HermesHub is a professional domain Agent marketplace built natively for Hermes Agent, inspired by the architectural principles of [wshobson/agents](https://github.com/wshobson/agents). This document explains the design decisions, architecture patterns, and development conventions.

## Design Principles

### 1. Plugin-Like Isolation (from wshobson/agents)
Each domain Agent is a self-contained directory with its own persona, memory, and skills. No cross-agent dependencies — you install only what you need.

### 2. Progressive Context Loading (Hermes-native)
Skills are not pre-loaded into the conversation context. They are discovered and dispatched by Hermes' tool system only when the user's intent matches a skill's JSON Schema description. This keeps token consumption low (typically <300 tokens for skill schemas).

### 3. Declarative Agent Identity
Agent identity is split into two Markdown files:
- **persona.md**: "Who you are" — behavioral rules, style, tool constraints, domain scope
- **memory.md**: "What you know" — hard constraints, ecosystem facts, anti-patterns, format rules

This separation follows the CAP (Context-Action-Personality) framework: persona handles behavioral layer, memory handles constraint layer.

### 4. JSON Schema + Python Handler Pattern
Each Skill is a single `.py` file containing:
- `SCHEMA` dict: The JSON Schema interface that Hermes uses for tool dispatch
- `handler(args) -> str`: The Python function that executes when the tool is called
- Supporting functions for the actual logic

This pattern is directly compatible with Hermes Agent's `registry.register()` tool mechanism.

## Architecture Comparison

| Aspect | wshobson/agents | HermesHub |
|--------|----------------|-----------|
| Agent Definition | Single `.md` file with YAML frontmatter | Split persona.md + memory.md |
| Skill Format | `.md` with progressive disclosure | `.py` with JSON Schema + Python code |
| Tool Execution | Native Claude Code tool calling | Hermes registry.register() pattern |
| Model Selection | Tiered (Opus/Sonnet/Haiku) | Hermes provider config |
| Multi-harness | 5 harnesses (Claude, Codex, Cursor, etc.) | Hermes-native only |
| Plugin System | 84 plugins, 192 agents | N agents (started with 2) |

## Skill Development Pattern

### Standard Skill Template

```python
SCHEMA = {
    "name": "skill_name",
    "description": "Use when: <trigger conditions>. <behavior>.",
    "parameters": {
        "type": "object",
        "properties": { ... },
        "required": [ ... ]
    }
}

def handler(args: dict[str, Any]) -> str:
    try:
        # Validate inputs
        # Execute logic
        # Return JSON result
        return json.dumps({"success": True, "data": result})
    except Exception as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})
```

### Key Conventions

1. **Schema description starts with "Use when:"** — This helps Hermes determine when to dispatch the tool
2. **All handlers return JSON strings** — Compatible with Hermes' tool output format
3. **Input validation before processing** — Prevents injection and invalid state
4. **Structured error returns** — Never return raw tracebacks; always wrap in `{"error": ..., "type": ...}`
5. **No side effects without approval** — Skills should be pure analysis/generation unless explicitly designed for mutation

## Security Design

### Defense in Depth

1. **Input validation** — Every handler validates all parameters before processing
2. **Size limits** — Prevents DoS via oversized inputs (30K-50K char limits per skill)
3. **No credential storage** — Skills reference environment variables, never hardcode secrets
4. **Structured output** — JSON output prevents injection into shell contexts
5. **Error isolation** — Every handler is wrapped in try/except; failures don't propagate

### Audit Trail

Each skill that performs analysis includes:
- Timestamp of analysis (via output structure)
- Input summary (what was analyzed)
- Findings with severity and line numbers
- Recommendations for remediation

## Adding a New Agent

### Directory Structure

```
agents/<agent-name>/
├── persona.md       # Identity, behavioral rules, style, domain scope
├── memory.md        # Hard constraints, ecosystem facts, security rules
└── skills/
    ├── skill_one.py
    ├── skill_two.py
    └── skill_three.py
```

### Persona Requirements

- Must define: Core Identity, Behavioral Rules (numbered), Style & Tone, Tool Usage Constraints, Domain Scope (handles + does NOT handle)
- Keep under 3KB to minimize token overhead

### Memory Requirements

- Must include: Hard Constraints, Security Rules, Format & Style Rules, Ecosystem Knowledge, Anti-Patterns
- Keep under 4KB

### Skill Requirements

- Each skill must have: `SCHEMA` dict + `handler()` function
- Minimum 3 test cases per skill
- Input validation + error handling
- Clear docstring explaining purpose

## Future Roadmap

### Phase 2 (Planned)
- **Web Dev Expert**: React/Vue specialist with component generation, accessibility audit, performance profiling
- **Rust Pro**: Memory safety analysis, Cargo optimization, unsafe code audit

### Phase 3 (Planned)
- **Cloud Architect**: AWS/Azure/GCP infrastructure design, Terraform generation, cost optimization
- **Security Auditor**: OWASP compliance, dependency vulnerability scanning, secret detection

### Cross-Agent Orchestration (Phase 4)
- Multi-agent workflows using Hermes' `delegate_task` and Kanban system
- Agent-to-agent handoff protocols
- Combined code review (Python Pro + Security Auditor)

## References

- [wshobson/agents](https://github.com/wshobson/agents) — Reference architecture
- [Hermes Agent Docs](https://hermes-agent.nousresearch.com/docs/) — Hermes internals
- [Hermes Agent Skills](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) — Skill system documentation
