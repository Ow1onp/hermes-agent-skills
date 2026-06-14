---
name: cicd-orchestrator
description: Use when setting up or optimizing CI/CD pipelines. Generates GitHub Actions workflow configurations following best practices — matrix builds, caching, artifact management, and deployment gates.
triggers: [ci, cd, cicd, pipeline, 流水线, deploy, 部署, github actions, workflow, CI/CD, automation, 自动化]
version: 1.0.0
author: Ow1onp
---

# CI/CD 编排器 (CI/CD Orchestrator)

## 1. 概述

CI/CD 流水线是现代软件工程的脊柱。一个设计良好的流水线在 5 分钟内给出反馈，差的流水线让开发者等 30 分钟却只得到一个无关紧要的 lint 警告。本技能基于 `.github/workflows/` 规范，生成经过实战验证的 CI/CD 配置。

融入 Hermes Agent 的优势：利用 `terminal` 验证 workflow 语法，利用 `cronjob` 设置定时流水线，利用 `webhook` 触发外部构建系统。

## 2. 核心流程

### 2.1 流水线设计原则

```
快速反馈原则：
  Lint (30s) → Unit Test (2min) → Integration Test (5min) → Deploy Preview (8min)
   └─ 快速失败 — 如果 lint 不过，不跑测试
  
并行原则：
  ┌─ Lint ──────────────┐
  ├─ Unit Test (py3.10) ─┤
  ├─ Unit Test (py3.11) ─┼─→ Integration Test → Deploy
  ├─ Unit Test (py3.12) ─┤
  └─ Security Scan ─────┘

幂等原则：
  同样的 commit 跑 100 次，结果不变
```

### 2.2 GitHub Actions 模板生成

本技能自动生成以下标准 workflow：

**1. CI (Continuous Integration)**
```yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [checkout, setup-python, ruff check]
  
  test:
    needs: lint
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps: [checkout, setup-python, pytest --cov]
  
  security:
    needs: lint
    steps: [checkout, pip-audit, bandit]
```

**2. CD (Continuous Deployment)**
```yaml
name: CD
on:
  push:
    tags: ["v*"]
jobs:
  build:
    steps: [checkout, build-package]
  publish:
    needs: build
    steps: [publish-to-pypi / docker-push]
  deploy:
    needs: publish
    steps: [deploy-to-production]
```

**3. Scheduled Tasks (Cron)**
```yaml
name: Nightly
on:
  schedule: [{cron: "0 3 * * *"}]
jobs:
  full-suite: [runs full test suite]
  dependency-audit: [pip-audit, npm audit]
```

### 2.3 Hermes 工具链集成

```bash
# 验证 workflow 语法
terminal(command="act --dryrun -W .github/workflows/ci.yml")

# 使用 Hermes cronjob 设置定时质量检查
cronjob(
    action="create",
    schedule="0 9 * * *",
    prompt="Run full test suite and report coverage",
    skills=["test-driven-dev"],
    name="Daily Test Suite"
)

# 利用 Hermes webhook 触发部署
# 配置 webhook 接收 GitHub release 事件
webhook(
    action="subscribe",
    name="release-webhook"
)
```

### 2.4 自进化机制

1. **构建时间优化**：追踪每次 CI 运行时间，自动建议缓存优化和并行化机会
2. **失败模式学习**：分析 CI 失败日志，识别常见失败原因并建议预防措施
3. **流水线模板升级**：根据 GitHub Actions 的最新特性和最佳实践，自动建议 workflow 升级
4. **资源利用率优化**：分析 matrix build 的实际需求，建议减少不必要的组合

### 2.5 身份感知

- 读取 `SOUL.md` 中的部署偏好（如 "偏好蓝绿部署" 或 "偏好滚动更新"）
- CD 策略自动适配偏好
- 通知方式适配（Slack / Discord / Email）

## 3. 门禁标准

- [ ] CI workflow 包含 lint + test + security 三个基础 job
- [ ] 测试矩阵覆盖项目支持的所有主要版本
- [ ] 有明确的缓存策略（pip cache, node_modules cache）
- [ ] CD workflow 有明确的回滚方案（或回滚文档链接）
- [ ] 敏感信息（API Key, Token）通过 GitHub Secrets 管理，不硬编码
- [ ] Workflow 语法已验证通过

## 4. 常见逃避借口与反驳

| 借口 | 反驳 |
|------|------|
| "先手动部署，CI/CD 以后再加" | 第一次手动部署的 10 分钟 = 第 100 次的 1000 分钟。自动化投资回报是指数级的。 |
| "我们的项目太小，不需要 CI" | 小项目今天不需要，但明天就会长大。CI 配起来只需要 30 分钟，却能用 3 年。 |
| "GitHub Actions 免费额度够吗" | 公开仓库无限免费。私人仓库每月 2000 分钟，对于 90% 的项目绰绰有余。 |
| "CI 跑得太慢了" | 慢说明你的流水线设计有问题，而不是 CI 本身的问题。优化它，别放弃它。 |
| "我只是一个人开发，不需要 CD" | 一个人开发更需要自动化——你没有队友帮你 catch 部署失误。 |
