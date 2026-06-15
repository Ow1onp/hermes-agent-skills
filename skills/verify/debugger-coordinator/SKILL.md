---
name: debugger-coordinator
description: Use when debugging complex issues involving multiple modalities (frontend + backend, API + UI, terminal + browser). Coordinates Hermes Agent's built-in debugger, browser, terminal, and vision tools for systematic root-cause analysis.
triggers: [debug, 调试, 报错, error, crash, 崩溃, "500", bug, not working, 不工作, traceback, stack trace]
version: 1.0.0
author: Ow1onp
---

# 调试协调器 (Debugger Coordinator)

## 1. 概述

现代软件调试往往涉及多个层面：前端 UI 异常、后端 API 错误、数据库状态不一致、网络超时……传统的单工具调试思路已不足以应对。本技能协调 Hermes Agent 的多模态工具矩阵（`browser` + `terminal` + `vision` + `web_extract`），进行系统性的根因分析。

核心理念：**不要修你还没理解的 bug**。先理解，再修复，最后加固。

## 2. 核心流程

### 2.1 五步调试法

```
第一步：复现 (Reproduce)
  ├─ 记录精确的复现步骤
  ├─ terminal: 查看日志、重启服务
  ├─ browser: 在真实浏览器中复现 UI bug
  └─ vision: 截图确认异常状态

第二步：定位 (Localize)
  ├─ terminal: 二分法缩小代码范围 (git bisect / 日志 grep)
  ├─ browser_console: 检查前端 JS 错误和网络请求
  └─ browser_vision: 可视化检查 UI 渲染状态

第三步：隔离 (Isolate)
  ├─ 写最小复现用例
  ├─ terminal: 单元测试隔离可疑函数
  └─ 排除外部依赖（mock 网络、DB 等）

第四步：修复 (Fix)
  ├─ 最小化修改（只改必要的代码）
  ├─ test-driven-dev 技能验证修复
  └─ 回归测试确认无副作用

第五步：加固 (Guard)
  ├─ 添加回归测试
  ├─ 增加日志/监控
  └─ 文档化根因和修复方案
```

### 2.2 多模态工具协调矩阵

| 调试场景 | 工具组合 | 说明 |
|---------|---------|------|
| 后端 API 异常 | `terminal` + `web_extract` | 查看服务器日志 + 抓取 API 文档 |
| 前端 UI Bug | `browser` + `vision` + `browser_console` | 截图对比 + JS 控制台错误 |
| 全栈问题 | `browser` + `terminal` + `browser_console` | 前端网络请求 + 后端日志联合分析 |
| 性能问题 | `terminal` (profiler) + `browser_console` | 后端 profiler + 前端 Performance API |
| 第三方集成故障 | `terminal` (curl) + `web_search` | 模拟请求 + 搜索已知 Issue |

### 2.3 Hermes 命令体系集成

```bash
# 在 Hermes 会话中直接加载
/skill debugger-coordinator

# 打开浏览器调试
/browser  # 启动 CDP 浏览器连接

# 利用 Hermes 的 terminal 执行调试命令
terminal(command="tail -100 /var/log/app.log | grep ERROR")
terminal(command="pytest tests/ -k 'test_failing_case' -v --pdb")

# 使用 vision 进行视觉验证
vision_analyze(image_url="screenshot.png", question="页面上的错误信息是什么？")
```

### 2.4 自进化机制

1. **Bug 模式库**：自动识别和分类常见 Bug 模式（如"空指针"、"竞态条件"、"类型错误"）
2. **调试效率追踪**：记录从 Bug 发现到修复的时间，识别瓶颈步骤
3. **预防建议**：对高频 Bug 类型，建议在 `code-quality-guardian` 中添加对应的检查规则
4. **调试命令模板**：积累项目特定的调试快捷命令

### 2.5 身份感知

- 读取 `SOUL.md` 中定义的技术栈偏好
- 调试命令自动适配技术栈（如 Node.js 项目用 `node --inspect`，Python 用 `pdb`）
- 日志分析风格适配（简洁型 vs 详细型）

## 3. 门禁标准

- [ ] Bug 已成功复现并记录精确步骤
- [ ] 根因已定位到具体的代码行或配置项
- [ ] 修复已通过 Prove-It 测试（见 test-driven-dev）
- [ ] 回归测试确认无新问题引入
- [ ] 如果适用，添加了日志/监控以防复发
- [ ] 调试过程中的关键发现已记录（可在项目文档或 Hermes 记忆中）

## 4. 常见逃避借口与反驳

| 借口 | 反驳 |
|------|------|
| "重启一下就好了" | 重启不是修复，是逃避。今天重启能解决，明天同样的 Bug 还会回来。 |
| "我没法复现，可能是用户的网络问题" | 先穷尽所有本地复现手段（日志、数据快照、流量回放），再归因于外部因素。 |
| "这个报错信息很清楚，我知道怎么修" | 报错信息告诉你症状，不告诉你根因。不理解根因的修复是创可贴，不是手术。 |
| "多试几次看看是不是偶发的" | 偶发 Bug 是最危险的 Bug——它们通常暗示竞态条件或资源泄漏，需要最高优先级的根因分析。 |
| "这 Bug 影响很小，不用管" | 今天的"小 Bug"是明天的"大故障"。每一个 Bug 都是系统在向你发出信号——倾听它。 |
