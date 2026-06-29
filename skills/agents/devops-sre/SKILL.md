---
name: devops-sre
description: Use when the user needs DevOps or SRE help including CI/CD pipelines, Docker optimization, Kubernetes manifests, infrastructure safety, or production log analysis.
triggers: [devops, sre, ci/cd, docker, kubernetes, k8s, logs, deployment]
version: 1.0.0
author: Ow1onp
license: MIT
metadata:
  hermes:
    tags: [devops, sre, cicd, docker, kubernetes]
---

# DevOps SRE

## Overview

DevOps SRE is a Hermes domain agent packaged as an installable skill. It is
available through the repository tap with `hermes skills install devops-sre`
and can be loaded with `/skill devops-sre`.

Use `references/persona.md` for behavior and `references/memory.md` for
operational constraints.

## Tool Handlers

The executable handlers live in `scripts/` and expose Hermes-compatible
`SCHEMA` plus `handler(args)` pairs:

- `scripts/ci_cd_generator.py` for GitHub Actions and GitLab CI generation.
- `scripts/docker_optimizer.py` for Dockerfile review and optimization.
- `scripts/k8s_deployer.py` for Kubernetes manifests.
- `scripts/log_analyzer.py` for production log triage.

## Use

Invoke with `/skill devops-sre`, then route infrastructure requests to the
matching handler schema. Always state rollout risk, rollback path, and
validation commands before destructive or production-affecting changes.

## Verification Checklist

- [ ] Read `references/persona.md` before giving guidance.
- [ ] Read `references/memory.md` before producing infrastructure changes.
- [ ] Use the most specific DevOps handler for structured tool calls.
- [ ] Include validation and rollback guidance for operational changes.
