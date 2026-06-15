"""
Skill template registry and generation for hermes-skill CLI.

Provides pre-built SKILL.md templates following the Agent Skills open standard,
along with a template engine that supports variable interpolation, category
selection, and metadata generation.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List


# ── Template data class ────────────────────────────────────

@dataclass
class SkillTemplate:
    """A reusable SKILL.md template with metadata."""
    name: str                          # template identifier: basic, advanced
    label: str                         # human-readable name
    description: str                   # when to use this template
    # Template body with {variable} placeholders
    template: str
    # Default frontmatter values (can be overridden)
    defaults: Dict[str, str] = field(default_factory=dict)
    # Category this template is best suited for
    recommended_category: str = "define"


# ── Template Engine ─────────────────────────────────────────

class TemplateEngine:
    """Simple template engine that subs {var} placeholders with values."""

    def render(
        self,
        template: str,
        variables: Dict[str, str],
        allow_missing: bool = False,
    ) -> str:
        """Render a template by substituting variables.

        Args:
            template: Template string with {var} placeholders.
            variables: Dict of variable_name → value.
            allow_missing: If True, leave unreplaced {var} as-is.
                          If False, raise KeyError on missing vars.

        Returns:
            Rendered string.

        Raises:
            KeyError: If allow_missing=False and a variable is missing.
        """
        result = template
        if allow_missing:
            for key, value in variables.items():
                result = result.replace("{" + key + "}", value)
        else:
            # Validate all keys exist before substitution
            missing = self._find_missing(template, variables)
            if missing:
                raise KeyError(
                    f"Missing template variables: {', '.join(sorted(missing))}"
                )
            for key, value in variables.items():
                result = result.replace("{" + key + "}", value)
        return result

    @staticmethod
    def _find_missing(template: str, variables: Dict[str, str]) -> set:
        """Find template variables that have no value."""
        import re
        used = set(re.findall(r"\{(\w+)\}", template))
        return used - set(variables.keys())

    @staticmethod
    def extract_variables(template: str) -> List[str]:
        """Return ordered list of variable names in a template."""
        import re
        seen = set()
        result = []
        for m in re.finditer(r"\{(\w+)\}", template):
            name = m.group(1)
            if name not in seen:
                seen.add(name)
                result.append(name)
        return result


# ── Template Registry ───────────────────────────────────────

class TemplateRegistry:
    """Registry of skill templates, searchable by name."""

    def __init__(self):
        self._templates: Dict[str, SkillTemplate] = {}
        self._register_all()

    def get(self, name: str) -> Optional[SkillTemplate]:
        """Get a template by name, or None if not found."""
        return self._templates.get(name)

    def list_names(self) -> List[str]:
        """Return sorted list of template names."""
        return sorted(self._templates.keys())

    def list_all(self) -> List[SkillTemplate]:
        """Return all templates."""
        return list(self._templates.values())

    def _register_all(self) -> None:
        """Register all built-in templates."""
        self._register(BASIC_TEMPLATE)
        self._register(ADVANCED_TEMPLATE)
        self._register(MINIMAL_TEMPLATE)

    def _register(self, t: SkillTemplate) -> None:
        self._templates[t.name] = t


# ── Built-in Templates ──────────────────────────────────────

BASIC_TEMPLATE = SkillTemplate(
    name="basic",
    label="Basic skill (recommended)",
    description="Standard skill with Overview, Flow, Pitfalls, and Checklist sections.",
    recommended_category="define",
    defaults={
        "version": "1.0.0",
        "author": "Hermes Agent",
        "license_name": "MIT",
    },
    template="""---
name: {skill_name}
description: Use when {trigger_when}. {skill_summary}.
triggers: [{trigger_keywords}]
version: {version}
author: {author}
license: {license_name}
metadata:
  hermes:
    tags: [{tags}]
    related_skills: [{related_skills}]
---

# {skill_title}

## Overview

{overview_paragraph}

## When to Use

- When {trigger_1}
- When {trigger_2}
- When {trigger_3}

Do NOT use for:

- {counter_trigger_1}
- {counter_trigger_2}

## Core Workflow

### 1. {step_1_title}

{step_1_description}

### 2. {step_2_title}

{step_2_description}

### 3. {step_3_title}

{step_3_description}

```bash
# Example usage
{example_command}
```

## Common Pitfalls

1. **{pitfall_1_title}** — {pitfall_1_fix}
2. **{pitfall_2_title}** — {pitfall_2_fix}
3. **{pitfall_3_title}** — {pitfall_3_fix}

## Verification Checklist

- [ ] {check_1}
- [ ] {check_2}
- [ ] {check_3}

## Reference

- [Agent Skills Standard](https://github.com/addyosmani/agent-skills)
- [Hermes Agent Docs](https://hermes-agent.nousresearch.com/docs/)
""",
)

ADVANCED_TEMPLATE = SkillTemplate(
    name="advanced",
    label="Advanced skill (multi-phase)",
    description="Full-featured skill with phases, metrics, Hermes integration, and excuses table.",
    recommended_category="build",
    defaults={
        "version": "1.0.0",
        "author": "Hermes Agent",
        "license_name": "MIT",
    },
    template="""---
name: {skill_name}
description: Use when {trigger_when}. {skill_summary}.
triggers: [{trigger_keywords}]
version: {version}
author: {author}
license: {license_name}
metadata:
  hermes:
    tags: [{tags}]
    related_skills: [{related_skills}]
---

# {skill_title}

## 1. Overview

{overview_paragraph}

### Hermes Agent Integration

| Capability | How This Skill Uses It |
|-----------|----------------------|
| `delegate_task` | {hermes_delegate_use} |
| `terminal` | {hermes_terminal_use} |
| `/curator` | {hermes_curator_use} |

## 2. When to Use

- When {trigger_1}
- When {trigger_2}
- When {trigger_3}

### Counter-Triggers (Do NOT use)

| Scenario | Reason | Alternative |
|----------|--------|-------------|
| {counter_trigger_1} | {counter_reason_1} | {counter_alt_1} |
| {counter_trigger_2} | {counter_reason_2} | {counter_alt_2} |

## 3. Core Workflow

```text
  PHASE 1           PHASE 2           PHASE 3
  {phase_1}  →  {phase_2}  →  {phase_3}
```

### Phase 1 — {phase_1}

{phase_1_description}

```bash
{phase_1_command}
```

### Phase 2 — {phase_2}

{phase_2_description}

```bash
{phase_2_command}
```

### Phase 3 — {phase_3}

{phase_3_description}

```bash
{phase_3_command}
```

## 4. Quality Gates

| Gate | Metric | Threshold | Action on Fail |
|------|--------|-----------|---------------|
| {gate_1_name} | {gate_1_metric} | {gate_1_threshold} | {gate_1_action} |
| {gate_2_name} | {gate_2_metric} | {gate_2_threshold} | {gate_2_action} |
| {gate_3_name} | {gate_3_metric} | {gate_3_threshold} | {gate_3_action} |

## 5. Common Pitfalls

1. **{pitfall_1_title}** — {pitfall_1_fix}
2. **{pitfall_2_title}** — {pitfall_2_fix}
3. **{pitfall_3_title}** — {pitfall_3_fix}

## 6. Verification Checklist

- [ ] {check_1}
- [ ] {check_2}
- [ ] {check_3}

## 7. Excuses & Rebuttals

| Excuse | Rebuttal |
|--------|----------|
| {excuse_1} | {rebuttal_1} |
| {excuse_2} | {rebuttal_2} |

## 8. Reference

- [Agent Skills Standard](https://github.com/addyosmani/agent-skills)
- [Hermes Agent Docs](https://hermes-agent.nousresearch.com/docs/)
""",
)

MINIMAL_TEMPLATE = SkillTemplate(
    name="minimal",
    label="Minimal (just the essentials)",
    description="Bare-bones skill with only required sections. Good for simple one-shot procedures.",
    recommended_category="define",
    defaults={
        "version": "1.0.0",
        "author": "Hermes Agent",
    },
    template="""---
name: {skill_name}
description: Use when {trigger_when}. {skill_summary}.
triggers: [{trigger_keywords}]
version: {version}
author: {author}
---

# {skill_title}

## Overview

{overview_paragraph}

## When to Use

- When {trigger_1}
- When {trigger_2}

## Core Steps

1. {step_1}
2. {step_2}
3. {step_3}

```bash
{example_command}
```

## Common Pitfalls

- {pitfall_1}
- {pitfall_2}

## Verification

- [ ] {check_1}
- [ ] {check_2}
""",
)


# ── Default fill values for new skills ──────────────────────

def get_default_variables(
    skill_name: str,
    category: str = "define",
) -> Dict[str, str]:
    """Return a dict of sensible default values for template variables.

    These are used as initial values when creating a new skill
    non-interactively, so the user gets a valid SKILL.md that
    they can edit further.
    """
    return {
        "skill_name": skill_name,
        "skill_title": skill_name.replace("-", " ").title(),
        "skill_summary": "Brief description of what this skill does.",
        "trigger_when": "doing <activity>",
        "trigger_keywords": f"{skill_name}, example, keyword",
        "tags": f"{skill_name}, {category}",
        "related_skills": "",
        "version": "1.0.0",
        "author": "Ow1onp",
        "license_name": "MIT",
        "overview_paragraph": (
            "Describe what this skill does, why it matters, "
            "and how it integrates with Hermes Agent."
        ),
        "trigger_1": "<specific trigger scenario 1>",
        "trigger_2": "<specific trigger scenario 2>",
        "trigger_3": "<specific trigger scenario 3>",
        "counter_trigger_1": "<scenario where this skill does NOT apply>",
        "counter_trigger_2": "<another scenario where this skill does NOT apply>",
        "counter_reason_1": "<why not>",
        "counter_reason_2": "<why not>",
        "counter_alt_1": "Use <other-skill> instead",
        "counter_alt_2": "Use <other-skill> instead",
        "step_1_title": "Step One",
        "step_1_description": "Description of step one.",
        "step_2_title": "Step Two",
        "step_2_description": "Description of step two.",
        "step_3_title": "Step Three",
        "step_3_description": "Description of step three.",
        "step_1": "First, do X.",
        "step_2": "Then, do Y.",
        "step_3": "Finally, do Z.",
        "example_command": "$ echo 'TODO: add real commands'",
        "pitfall_1_title": "Pitfall A",
        "pitfall_1_fix": "How to avoid or fix it.",
        "pitfall_2_title": "Pitfall B",
        "pitfall_2_fix": "How to avoid or fix it.",
        "pitfall_3_title": "Pitfall C",
        "pitfall_3_fix": "How to avoid or fix it.",
        "pitfall_1": "Watch out for X — do Y instead.",
        "pitfall_2": "Common mistake Z — check W first.",
        "check_1": "Verify step one completed successfully.",
        "check_2": "Verify step two completed successfully.",
        "check_3": "Verify step three completed successfully.",
        # Advanced template extras
        "hermes_delegate_use": "{description}",
        "hermes_terminal_use": "{description}",
        "hermes_curator_use": "{description}",
        "phase_1": "Prepare",
        "phase_2": "Execute",
        "phase_3": "Verify",
        "phase_1_description": "Preparation steps.",
        "phase_2_description": "Execution steps.",
        "phase_3_description": "Verification steps.",
        "phase_1_command": "$ echo 'TODO: phase 1 commands'",
        "phase_2_command": "$ echo 'TODO: phase 2 commands'",
        "phase_3_command": "$ echo 'TODO: phase 3 commands'",
        "gate_1_name": "Gate A",
        "gate_1_metric": "metric_name",
        "gate_1_threshold": "> 80%",
        "gate_1_action": "Block merge",
        "gate_2_name": "Gate B",
        "gate_2_metric": "metric_name",
        "gate_2_threshold": "< 3",
        "gate_2_action": "Flag for review",
        "gate_3_name": "Gate C",
        "gate_3_metric": "metric_name",
        "gate_3_threshold": "= 0",
        "gate_3_action": "Auto-fix via patch",
        "excuse_1": "\"This is just a quick script\"",
        "rebuttal_1": "Quick scripts become permanent — invest now.",
        "excuse_2": "\"We'll add quality gates later\"",
        "rebuttal_2": "Later never comes. Every merge is an opportunity.",
    }
