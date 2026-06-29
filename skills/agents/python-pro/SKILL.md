---
name: python-pro
description: Use when the user needs expert Python engineering help including code review, performance profiling, pytest generation, package scaffolding, or static type guidance.
triggers: [python, code review, pytest, performance, type checking, package, scaffold]
version: 1.0.0
author: Ow1onp
license: MIT
metadata:
  hermes:
    tags: [python, engineering, code-review, testing]
---

# Python Pro

## Overview

Python Pro is a Hermes domain agent packaged as an installable skill. It is
available through the repository tap with
`hermes skills install Ow1onp/hermes-agent-skills/skills/agents/python-pro` and
can be loaded with `/skill python-pro`.

Use `references/persona.md` for behavior and `references/memory.md` for
project-independent constraints.

## Tool Handlers

The executable handlers live in `scripts/` and expose Hermes-compatible
`SCHEMA` plus `handler(args)` pairs:

- `scripts/code_review.py` for security, style, performance, and maintainability review.
- `scripts/performance_profile.py` for profiling interpretation and optimization advice.
- `scripts/test_generator.py` for pytest generation.
- `scripts/package_scaffold.py` for Python package layout generation.
- `scripts/type_checker.py` for static typing guidance.

## Use

Invoke with `/skill python-pro`, then route Python-specific requests to the
matching handler schema. Keep outputs actionable, typed, secure, and tested.

## Verification Checklist

- [ ] Read `references/persona.md` before giving guidance.
- [ ] Read `references/memory.md` before making architectural or security recommendations.
- [ ] Use the most specific Python handler for structured tool calls.
- [ ] Return concrete code, commands, or review findings.
