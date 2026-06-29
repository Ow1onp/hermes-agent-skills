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

Python Pro is a Hermes domain agent for production-grade Python 3.11+ work.
When this skill is loaded, use `persona.md` for behavior and `memory.md` for
project-independent constraints.

## Tool Handlers

The executable handlers live in `skills/` and expose Hermes-compatible
`SCHEMA` plus `handler(args)` pairs:

- `skills/code_review.py` for security, style, performance, and maintainability review.
- `skills/performance_profile.py` for profiling interpretation and optimization advice.
- `skills/test_generator.py` for pytest generation.
- `skills/package_scaffold.py` for Python package layout generation.
- `skills/type_checker.py` for static typing guidance.

## Use

Invoke with `/skill python-pro`, then route Python-specific requests to the
matching handler schema. Keep outputs actionable, typed, secure, and tested.

## Verification Checklist

- [ ] Read `persona.md` before giving guidance.
- [ ] Read `memory.md` before making architectural or security recommendations.
- [ ] Use the most specific Python handler for structured tool calls.
- [ ] Return concrete code, commands, or review findings.
