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

DevOps SRE is a Hermes domain agent for reliable infrastructure automation.
When this skill is loaded, use `persona.md` for behavior and `memory.md` for
operational constraints.

## Tool Handlers

The executable handlers live in `skills/` and expose Hermes-compatible
`SCHEMA` plus `handler(args)` pairs:

- `skills/ci_cd_generator.py` for GitHub Actions and GitLab CI generation.
- `skills/docker_optimizer.py` for Dockerfile review and optimization.
- `skills/k8s_deployer.py` for Kubernetes manifests.
- `skills/log_analyzer.py` for production log triage.

## Use

Invoke with `/skill devops-sre`, then route infrastructure requests to the
matching handler schema. Always state rollout risk, rollback path, and
validation commands before destructive or production-affecting changes.

## Verification Checklist

- [ ] Read `persona.md` before giving guidance.
- [ ] Read `memory.md` before producing infrastructure changes.
- [ ] Use the most specific DevOps handler for structured tool calls.
- [ ] Include validation and rollback guidance for operational changes.
