# 🔍 Hermes Agent Skills — 用户反馈系统设计

> v1.2.0 反馈采集框架 · 面向开源社区的产品反馈闭环

---

## 目录

1. [GitHub Issues 模板](#1-github-issues-模板)
2. [GitHub Discussion 分类](#2-github-discussion-分类)
3. [用户问卷](#3-用户问卷)
4. [首批用户访谈提纲](#4-首批用户访谈提纲)
5. [v1.2.0 反馈采集框架](#5-v120-反馈采集框架)

---

## 1. GitHub Issues 模板

### 1.1 Bug Report（Bug 报告）

**文件路径：** `.github/ISSUE_TEMPLATE/bug_report.yml`

```yaml
name: "🐛 Bug Report"
description: "Report a bug in hermes-agent-skills"
title: "[Bug]: "
labels: ["bug", "triage"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to report a bug! Please fill out the form below.

  - type: input
    id: version
    attributes:
      label: "hermes-agent-skills 版本"
      description: "`hermes-skill --version` 或 `pip show hermes-agent-skills`"
      placeholder: "1.1.0"
    validations:
      required: true

  - type: input
    id: hermes-version
    attributes:
      label: "Hermes Agent 版本"
      description: "Hermes Agent 的版本号"
      placeholder: "v0.8.0"
    validations:
      required: false

  - type: dropdown
    id: affected-skill
    attributes:
      label: "受影响的技能 / 组件"
      description: "Bug 出现在哪个技能或组件？"
      multiple: true
      options:
        - "requirement-analyzer"
        - "spec-driven-dev"
        - "test-driven-dev"
        - "debugger-coordinator"
        - "code-quality-guardian"
        - "cicd-orchestrator"
        - "skill-curator"
        - "persona-aware-coding"
        - "CLI (hermes-skill)"
        - "Validator"
        - "EvolutionEngine"
        - "SoulReader"
        - "文档"
        - "其他"

  - type: textarea
    id: description
    attributes:
      label: "Bug 描述"
      description: "发生了什么？期望行为是什么？"
      placeholder: |
        1. 加载 `test-driven-dev` 技能
        2. 执行 `/skill test-driven-dev`
        3. 发现...
        期望：...
        实际：...
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: "复现步骤"
      description: "逐步说明如何复现此 Bug"
      placeholder: |
        1. 安装 `pip install hermes-agent-skills==1.1.0`
        2. 在 Hermes 会话中执行 `...`
        3. 打开文件 `...`
        4. 运行命令 `...`
        5. 看到错误
    validations:
      required: true

  - type: textarea
    id: error-log
    attributes:
      label: "错误日志 / 截图"
      description: "粘贴终端输出、错误 traceback，或拖入截图"
      render: shell

  - type: dropdown
    id: os
    attributes:
      label: "操作系统"
      options:
        - "Windows 10"
        - "Windows 11"
        - "macOS (Intel)"
        - "macOS (Apple Silicon)"
        - "Ubuntu / Debian"
        - "其他 Linux"
    validations:
      required: true

  - type: input
    id: python-version
    attributes:
      label: "Python 版本"
      description: "`python --version`"
      placeholder: "3.11.0"
    validations:
      required: true

  - type: checkboxes
    id: checks
    attributes:
      label: "提交前确认"
      options:
        - label: "我已搜索现有 Issues，未发现重复报告"
          required: true
        - label: "我已查看 [FAQ](https://github.com/Ow1onp/hermes-agent-skills/blob/main/docs/FAQ.md)"
          required: false
```

---

### 1.2 Feature Request（功能请求）

**文件路径：** `.github/ISSUE_TEMPLATE/feature_request.yml`

```yaml
name: "💡 Feature Request"
description: "Suggest a new feature or improvement"
title: "[Feature]: "
labels: ["enhancement", "triage"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thanks for the feature idea! Describe what you want and why it matters.

  - type: textarea
    id: problem
    attributes:
      label: "要解决的问题"
      description: "这个功能解决了什么痛点？你现在是怎么绕过的？"
      placeholder: |
        当我需要跨多个技能做批量验证时，目前只能逐个运行 `hermes-skill validate`...
        如果有批量模式，可以一次检查全部技能...
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: "期望的解决方案"
      description: "你期望这个功能怎么做？有参考实现或类似产品吗？"
      placeholder: |
        `hermes-skill validate skills/ --batch --format json` 一次性输出所有技能的状态...
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: "考虑过的替代方案"
      description: "有哪些其他方式可以达到同样目的？为什么不够好？"
      placeholder: "我试过写 shell 脚本遍历目录，但无法利用 Validator 的内部校验逻辑..."

  - type: dropdown
    id: scope
    attributes:
      label: "影响范围"
      options:
        - "单技能改进"
        - "CLI 工具"
        - "核心库 (validator / evolution / soul_reader)"
        - "文档 / 示例"
        - "CI/CD"
        - "多技能联动"
        - "Skill Marketplace 方向"
        - "Skill Analytics 方向"

  - type: dropdown
    id: priority-feel
    attributes:
      label: "对你有多重要？"
      options:
        - "Nice to have — 有更好，没有也能用"
        - "Important — 每周因为这个痛点浪费时间"
        - "Critical — 不用这个功能没法继续用"
    validations:
      required: true

  - type: checkboxes
    id: checks
    attributes:
      label: "提交前确认"
      options:
        - label: "我已搜索现有 Issues 和 Discussions，未发现重复请求"
          required: true
        - label: "我已阅读项目 [Roadmap](https://github.com/Ow1onp/hermes-agent-skills#-特点) 中的远期方向"
          required: false
```

---

### 1.3 Skill Request（技能请求）

**文件路径：** `.github/ISSUE_TEMPLATE/skill_request.yml`

```yaml
name: "🧬 Skill Request"
description: "Request a new skill for the collection"
title: "[Skill Request]: "
labels: ["skill-request", "triage"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thanks for suggesting a new skill! Good skills are reusable workflows that solve a specific, recurring problem.

  - type: input
    id: skill-name
    attributes:
      label: "建议的技能名称"
      description: "lowercase + hyphens, e.g. `api-doc-generator`"
      placeholder: "my-skill-idea"
    validations:
      required: true

  - type: dropdown
    id: phase
    attributes:
      label: "所属阶段"
      description: "这个技能在开发生命周期的哪个阶段？"
      options:
        - "DEFINE (需求分析)"
        - "BUILD (构建开发)"
        - "VERIFY (验证测试)"
        - "SHIP (交付部署)"
        - "EVOLVE (进化维护)"
    validations:
      required: true

  - type: textarea
    id: use-case
    attributes:
      label: "使用场景"
      description: "用户在什么情况下需要这个技能？描述一个具体的场景。"
      placeholder: |
        当用户需要在 CI 中生成 API 文档时，当前需要手动拼接 OpenAPI spec + Markdown...
        期望有一个技能：读取 FastAPI app → 生成 OpenAPI spec → 转 Markdown → 提交到 docs/...
    validations:
      required: true

  - type: textarea
    id: workflow
    attributes:
      label: "工作流草案"
      description: "这个技能应该包含哪些步骤？（不需要完整 SKILL.md，思路即可）"
      placeholder: |
        1. 检测项目中的 FastAPI 路由
        2. 提取路径、参数、响应 schema
        3. 生成 OpenAPI 3.0 spec
        4. 用模板渲染 Markdown
        5. 写入 docs/api.md

  - type: textarea
    id: hermes-features
    attributes:
      label: "期望利用的 Hermes 专有能力"
      description: "这个技能能不能用到 Hermes 特有的工具？"
      placeholder: |
        - `delegate_task` 并行提取多个路由
        - `cronjob` 定时更新文档
        - 持久记忆缓存已解析的 schema

  - type: checkboxes
    id: skill-checks
    attributes:
      label: "提交前确认"
      options:
        - label: "我已确认 `skills/` 目录下不存在类似技能"
          required: true
        - label: "我同意此技能遵循 Agent Skills 开放标准"
          required: true
        - label: "我愿意参与技能的设计讨论（非必须）"
          required: false
```

---

### 1.4 Documentation Issue（文档问题）

**文件路径：** `.github/ISSUE_TEMPLATE/documentation.yml`

```yaml
name: "📖 Documentation Issue"
description: "Report unclear, missing, or incorrect documentation"
title: "[Docs]: "
labels: ["documentation", "triage"]
assignees: []
body:
  - type: dropdown
    id: doc-type
    attributes:
      label: "文档类型"
      options:
        - "README.md"
        - "README.en.md"
        - "QUICKSTART.md"
        - "TUTORIAL.md"
        - "FAQ.md"
        - "CONTRIBUTING.md"
        - "CHANGELOG.md"
        - "SKILL.md (技能内文档)"
        - "代码注释 / docstring"
        - "Error messages"

  - type: dropdown
    id: issue-type
    attributes:
      label: "问题类型"
      options:
        - "缺失（Missing）—— 某主题完全没有文档"
        - "不清晰（Unclear）—— 现有文档难以理解"
        - "过时（Outdated）—— 文档与当前版本行为不一致"
        - "错误（Wrong）—— 文档中存在事实错误"
        - "翻译（Translation）—— 中英文不一致或缺失翻译"
        - "示例不足（Examples needed）—— 缺少足够的代码示例"

  - type: textarea
    id: location
    attributes:
      label: "涉及的文档位置"
      description: "链接或文件路径 + 行号（如有）"
      placeholder: |
        https://github.com/Ow1onp/hermes-agent-skills/blob/main/docs/QUICKSTART.md#L45
        或者 `skills/build/test-driven-dev/SKILL.md` 中的安装步骤

  - type: textarea
    id: problem-desc
    attributes:
      label: "问题描述"
      description: "具体哪里不清楚/不对/缺失？你期望看到什么内容？"

  - type: textarea
    id: suggestion
    attributes:
      label: "建议的修改（可选）"
      description: "如果你有具体的改写建议或示例，请贴在这里"
      render: markdown

  - type: checkboxes
    id: doc-checks
    attributes:
      label: "提交前确认"
      options:
        - label: "我已确认问题存在于最新版本"
          required: true
```

---

### 1.5 配置文件

**文件路径：** `.github/ISSUE_TEMPLATE/config.yml`

```yaml
blank_issues_enabled: false
contact_links:
  - name: "💬 GitHub Discussions"
    url: https://github.com/Ow1onp/hermes-agent-skills/discussions
    about: "Ask questions, share ideas, or showcase your custom skills here."
  - name: "📖 项目文档"
    url: https://github.com/Ow1onp/hermes-agent-skills/tree/main/docs
    about: "Read QUICKSTART, TUTORIAL, FAQ, and CONTRIBUTING before opening an issue."
  - name: "🔗 Agent Skills 开放标准"
    url: https://github.com/addyosmani/agent-skills
    about: "The upstream standard that SKILL.md files follow."
  - name: "🤖 Hermes Agent 项目"
    url: https://github.com/NousResearch/hermes-agent
    about: "Upstream Hermes Agent project by Nous Research."
```

---

## 2. GitHub Discussion 分类

在 GitHub Discussions 中启用以下分类：

```yaml
# .github/DISCUSSION_TEMPLATE/categories.yml — 配置参考

discussions:
  - name: "📣 Announcements"
    emoji: "📣"
    description: "版本发布、重大更新、社区活动公告（仅维护者）"
    format: "Announcement"

  - name: "💡 Ideas"
    emoji: "💡"
    description: "头脑风暴：新技能创意、架构设想、长期愿景讨论"
    format: "Discussion"

  - name: "🔧 Q&A"
    emoji: "🔧"
    description: "使用问题、配置求助、故障排查。回答后可标记为 Answered"
    format: "Q&A"

  - name: "🎨 Show & Tell"
    emoji: "🎨"
    description: "展示你自己写的技能、工作流配置、SOUL.md 创作"
    format: "Discussion"

  - name: "🧪 Feedback"
    emoji: "🧪"
    description: "使用体验反馈、技能效果评价、改进建议"
    format: "Discussion"

  - name: "🌐 Community"
    emoji: "🌐"
    description: "中文社区交流、本地化讨论、Hermes 生态闲聊"
    format: "Discussion"
```

**分类设计逻辑：**

| 分类 | 目标 | 典型帖子 |
|------|------|---------|
| `📣 Announcements` | 官方信息发布 | v1.2.0 发布公告 |
| `💡 Ideas` | 收集远期方向输入 | "如果有个 Skill Marketplace 会怎样？" |
| `🔧 Q&A` | 降低使用门槛 | "Windows 下 `hermes-skill` 报 49 退出码怎么修？" |
| `🎨 Show & Tell` | 激励贡献者、展示生态 | "我写了个 `k8s-deploy` 技能，用了 delegate_task 并行部署" |
| `🧪 Feedback` | 产品决策依据 | "EvolutionEngine 的 health score 阈值太高，建议从 0.5 降到 0.3" |
| `🌐 Community` | 留存、归属感 | "有没有国内用户群？时区对齐一下" |

---

## 3. 用户问卷

### 3.1 问卷设计目标

- **投放渠道：** GitHub Discussion pinned post + README 链接
- **语言：** 中英双语
- **长度：** 10 题以内，完成时间 < 5 分钟
- **工具：** Google Forms / Tally / 直接 Markdown 回复 Discussion
- **激励：** 在 CHANGELOG 中致谢前 30 位回应者

---

### 3.2 问卷正文

```markdown
# 🧪 Hermes Agent Skills — User Survey (v1.2.0 前)

> 填写时间：~3 分钟 · 帮助我们决定下一步做什么

---

## Part 1: 你是谁？

### Q1. 你使用 Hermes Agent 多久了？
- [ ] 刚接触（< 1 周）
- [ ] 初级用户（1 周 - 1 个月）
- [ ] 中级用户（1-3 个月）
- [ ] 老用户（3 个月以上）

### Q2. 你的主要角色？
- [ ] 独立开发者 / Solo Developer
- [ ] 开源项目维护者
- [ ] 企业 / 团队开发者
- [ ] AI / Agent 技术研究者
- [ ] 学生 / 学习用途
- [ ] 其他：_______

---

## Part 2: 使用情况

### Q3. 你安装 hermes-agent-skills 多久了？
- [ ] 还没装，在观望
- [ ] < 1 周
- [ ] 1-4 周
- [ ] 1 个月以上

### Q4. 你最常用的 3 个技能是？（选 3 个）
- [ ] requirement-analyzer
- [ ] spec-driven-dev
- [ ] test-driven-dev
- [ ] debugger-coordinator
- [ ] code-quality-guardian
- [ ] cicd-orchestrator
- [ ] skill-curator
- [ ] persona-aware-coding
- [ ] 没用过，只用了 CLI

### Q5. 你用 `hermes-skill` CLI 吗？
- [ ] 天天用
- [ ] 偶尔用（创建/验证技能时）
- [ ] 装了就忘，只用 `/skill` 斜杠命令
- [ ] 不知道有 CLI

---

## Part 3: 满意度

### Q6. 整体满意度（1-5 分）
- [ ] 5 — 超出预期，主动推荐给别人
- [ ] 4 — 不错，有继续用的动力
- [ ] 3 — 能用，但没感觉特别
- [ ] 2 — 有较大痛点，犹豫是否继续
- [ ] 1 — 打算放弃

### Q7. 最大的痛点是什么？（选最重要的 1-2 个）
- [ ] 技能数量太少，缺少我需要的工作流
- [ ] 现有技能在我的场景下不 work
- [ ] 文档不够（看不懂、找不到）
- [ ] 安装/配置太复杂
- [ ] CLI 不好用 / 报错
- [ ] 不知道技能能做什么（缺乏演示）
- [ ] 性能问题（运行太慢 / 消耗 token 太多）
- [ ] 其他：_______

### Q8. 你最希望 v1.2.0 增加什么？（选 1 个）
- [ ] 更多技能（请注明：_______）
- [ ] Skill Marketplace（分享/发现社区技能）
- [ ] Skill Analytics（使用数据、健康仪表盘）
- [ ] 更好的 CLI（自动补全、更多子命令）
- [ ] 更好的文档（视频教程、交互式演示）
- [ ] Evolution Engine 升级（自动建议更智能）
- [ ] 多语言支持（日文、韩文等）
- [ ] 其他：_______

---

## Part 4: 开放反馈

### Q9. 如果你可以改一件事，你会改什么？
（开放文本）

### Q10. （可选）留下联系方式
如果你愿意参与后续深度访谈：
- GitHub: _______
- Email: _______
- Discord: _______
```
```

---

### 3.3 问卷数据分析维度

| 分析维度 | 数据来源 | 决策用途 |
|---------|---------|---------|
| 用户画像 | Q1, Q2 | 确定核心用户群，指导内容策略 |
| 技能热度 | Q4, Q5 | 决定哪些技能优先维护、哪些可归档 |
| 满意度基线 | Q6 | v1.2.0 发布前后对比 |
| 痛点排行 | Q7 | v1.2.0 路线图优先级排序 |
| 需求投票 | Q8 | 大方向决策（Marketplace vs Analytics vs 更多技能） |
| 定性洞察 | Q9 | 发现问卷没覆盖的隐藏需求 |

---

## 4. 首批用户访谈提纲

### 4.1 访谈目标

- **人数：** 5-8 人
- **时长：** 30-45 分钟/人
- **形式：** Discord 语音 / 飞书会议 / 异步（GitHub Discussion 深度回复）
- **目标对象：**
  - 已安装并使用 ≥ 2 周（重度用户 × 3）
  - 安装后未深入使用 / 遇到障碍（流失用户 × 2）
  - 自己写过 Skill 的贡献者（贡献者 × 2）

---

### 4.2 访谈问题

```markdown
# 🎙 Hermes Agent Skills — First User Interview Guide

> 30-45 min · 半结构化 · 先建立 rapport，再深入

---

## 阶段 1: 破冰 (5 min)

1. 简单自我介绍，怎么知道 Hermes Agent 和 hermes-agent-skills 的？
2. 平时用 AI Agent 做什么类型的任务？

---

## 阶段 2: 首次体验回顾 (10 min)

3. **你是怎么第一次安装/使用的？**
   - 还记得安装过程吗？有没有卡住的地方？
   - 安装后第一个加载的技能是哪个？为什么选它？

4. **10 分钟内的第一印象？**
   - 有没有 "wow" 时刻？
   - 有没有 "这啥？" 的困惑时刻？

5. **如果你给朋友推荐，你会怎么说？**
   - 一句话推荐语是什么？
   - 你会提醒朋友注意什么坑？

---

## 阶段 3: 深度使用行为 (15 min)

6. **你现在的使用频率和场景是什么？**
   - 每天用？每周用？按需用？
   - 你的 "典型会话" 长什么样？（描述一次具体使用）

7. **哪些技能你不再用了？为什么？**
   - 是场景不匹配？还是技能本身不好用？
   - 有没有你手动 override 技能的行为？（比如技能说做 A，你自己做了 B）

8. **CLI 工具使用体验？**
   - `hermes-skill create` 好用吗？
   - `hermes-skill validate` 对你有价值吗？
   - 有没有自己写脚本绕过 CLI 的情况？

9. **SOUL.md 功能你用了吗？**
   - 如果用了：效果符合预期吗？哪里需要改进？
   - 如果没用：为什么？不知道？不需要？不知道怎么配？

---

## 阶段 4: 需求探索 (10 min)

10. **如果让 Skill Marketplace 上线，你愿意付费吗？**
    - 付费买什么？单个 Skill？打包？订阅？
    - 什么价位你觉得合理？

11. **你目前有没有自己写的 "非正式技能"？**
    - （给用户看概念）比如你在 Hermes 里反复粘贴同一段 prompt?
    - 你会愿意把它发布到社区吗？有什么顾虑？

12. **除了写代码，你希望 AI Agent 在哪些场景帮你？**
    - 文档写作？项目管理？设计评审？
    - 有没有 "我试过让 Agent 做但效果很差" 的经历？

---

## 阶段 5: 展望 (5 min)

13. **一年后，你理想中的 hermes-agent-skills 是什么样？**
    - 不设限，随便说。

14. **还有什么我没问到但你想说的？**

---

## 访谈后 checklist

- [ ] 记录用户 profile（角色、使用时长、技能偏好）
- [ ] 标记 "wow" 时刻和 "frustration" 时刻
- [ ] 提取 1-2 条可用于 CHANGELOG 的用户引言
- [ ] 标记是否愿意参与后续 Beta 测试
```
```

---

### 4.3 访谈数据整理模板

```markdown
## 用户访谈记录 · [编号 U001]

| 字段 | 内容 |
|------|------|
| 日期 | |
| 用户类型 | □ 重度 □ 流失 □ 贡献者 |
| 使用时长 | |
| 主要技能 | |
| 主要痛点 | |
| Wow 时刻 | |
| 一句话推荐 | |
| 期望改进 | |
| 付费意愿 | □ 有 □ 无 □ 不确定 |
| 是否愿继续参与 | □ 是 □ 否 |
```

---

## 5. v1.2.0 反馈采集框架

### 5.1 框架总览

```
                        ┌──────────────────────────────────┐
                        │      v1.2.0 反馈采集闭环          │
                        └──────────────────────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
           ▼                          ▼                          ▼
   ┌───────────────┐        ┌───────────────┐        ┌───────────────┐
   │  被动采集      │        │  主动采集      │        │  数据采集      │
   │  (Always On)  │        │  (Sprint)     │        │  (Auto)       │
   └───────────────┘        └───────────────┘        └───────────────┘
           │                          │                          │
           ▼                          ▼                          ▼
   · GitHub Issues          · 用户问卷              · GitHub Stars
   · GitHub Discussions     · 深度访谈              · PyPI 下载量
   · PR Review 反馈         · 社区帖子互动           · 技能 Usage 统计
```

---

### 5.2 时间线：6 周反馈窗口

```
Week 1-2 │ Week 3-4 │ Week 5 │ Week 6
─────────┼──────────┼────────┼─────────
  发布    │  问卷    │  访谈  │  决策
v1.1.0   │ 投放    │  执行  │  汇总
稳定期   │ + 被动   │       │  输出
         │  采集    │       │ v1.2.0
         │          │       │ Roadmap
```

| 阶段 | 周次 | 活动 | 产出 |
|------|------|------|------|
| 观察期 | Week 1-2 | Issue 模板上线 · Discussion 分类激活 · 被动收集所有 Issue/Discussion | 原始信号清单 |
| 主动采集 | Week 3-4 | 发布问卷 · 定向邀请 5-8 人访谈 · 在 Reddit/Discord 推广 | 问卷数据 + 访谈记录 |
| 汇总分析 | Week 5 | 合并三路数据 · 提取 Top 3 痛点 · 提取 Top 3 需求 · 计算 NPS 分 | 分析报告 |
| 决策 | Week 6 | 发布 v1.2.0 Roadmap · 关闭 "won't do" 的 Issue · 标记 accepted 的 Feature Request | Roadmap + Label 更新 |

---

### 5.3 信号分类与优先级

每条反馈被收集后，按以下分类标记 Label：

| Label | 含义 | 示例 |
|-------|------|------|
| `P0-blocker` | 阻塞性 Bug / 无法安装使用 | pip install 在 Python 3.9 上崩溃 |
| `P1-v1.2` | 高优先级，力争 v1.2.0 解决 | CLI 在 Windows MSYS 下报错 |
| `P2-backlog` | 重要但不急，进入 Backlog | 希望 CLI 支持自动补全 |
| `P3-icebox` | 好想法，但当前不排期 | Skill Marketplace 完整实现 |
| `wontfix` | 不予处理 | 与项目方向不一致的请求 |
| `needs-discussion` | 需要社区讨论 | 某技能的默认行为争议 |

**优先级判断矩阵：**

| | 影响人数多 | 影响人数少 |
|---|---|---|
| **严重程度高** | P0 | P1 |
| **严重程度低** | P1 | P2/P3 |

---

### 5.4 关键指标（用于 v1.2.0 决策）

| 指标 | 数据来源 | 目标 | 获取方式 |
|------|---------|------|---------|
| **NPS** | Q6 满意度 | 了解当前净推荐值基线 | 问卷 |
| **技能使用分布** | Q4 + 被动统计 | 前 3 技能 > 50% 用户使用 | 问卷 + Issue 提及频率 |
| **安装成功率** | Issues 标签 `P0-blocker` | ≤ 2 个 v1.1.0 遗留 Blocker | Issue 计数 |
| **CLI 认知率** | Q5 | > 60% 用户知道 CLI 存在 | 问卷 |
| **Top 3 痛点** | Q7 + 访谈高频词 | 明确 3 个最痛的点 | 定性聚合 |
| **Top 3 功能需求** | Q8 + 访谈 | 明确 3 个最想要的功能 | 定性聚合 |
| **贡献者留存** | Show & Tell Discussion 数 | ≥ 2 个社区贡献技能 | Discussion 计数 |
| **文档满意度** | Documentation Issue 数 + Q7 | ≤ 5 个 "文档不够" 反馈 | Issue 计数 + 问卷 |

---

### 5.5 v1.2.0 输出模板

反馈采集完成后，输出以下文档：

```markdown
# 📊 v1.2.0 反馈分析报告

> 采集周期：2026-06-16 — 2026-07-28
> 数据来源：GitHub Issues（N 个）· Discussions（N 个）· 问卷（N 份）· 访谈（N 人）

---

## 关键数字

| 指标 | 数值 | 趋势 |
|------|------|------|
| NPS | xx | — |
| 安装用户（估计） | xxx PyPI downloads | — |
| 社区贡献技能 | x 个 | — |
| Open Issues | xx | — |
| 满意度 ≥ 4 分 | xx% | — |

---

## Top 3 痛点

1. **痛点 A** — 提及 N 次，代表用户引言："..."
2. **痛点 B** — 提及 N 次
3. **痛点 C** — 提及 N 次

## Top 3 功能需求

1. **需求 A** — Q8 投票第 1，提及 N 次
2. **需求 B** — Q8 投票第 2
3. **需求 C** — Q8 投票第 3

## 建议的 v1.2.0 路线图

| 优先级 | 项目 | 来源 |
|--------|------|------|
| P0 | Fix ... | Issue #xxx |
| P0 | Fix ... | Issue #xxx |
| P1 | Feature ... | 需求 A |
| P1 | Feature ... | 需求 B |
| P2 | ... | ... |

## 长尾信号（未来版本）

- 信号 1 — Skill Marketplace 方向讨论 3 帖
- 信号 2 — 用户提到 "想给技能打分"
- 信号 3 — 有人发了自己改的 Evolution Engine

## 用户引言精选

> "..." — U001, 重度用户
> "..." — U003, 贡献者
```

---

### 5.6 未来扩展留白

以下功能不在 v1.2.0 范围内，但反馈系统设计时已预留入口：

| 未来功能 | 反馈入口 | 观察信号 |
|---------|---------|---------|
| **Skill Marketplace** | Skill Request 模板 · `💡 Ideas` Discussion · Q8 投票 · 访谈 Q10 | "我想买/卖技能" 的提及次数 |
| **Skill Analytics** | Feature Request 模板 · `🧪 Feedback` Discussion · Q8 投票 | "想看技能数据" 的提及次数 |
| **Evolution Engine** | Skill Request (evolve 阶段) · Q8 | "技能自动优化不够智能" 的提及次数 |

---

## 附录 A: Labels 完整清单

建议在 GitHub 仓库中创建以下 Labels：

```
# 类型
bug           # 🐛 Bug 报告
enhancement   # 💡 功能改进
skill-request # 🧬 新技能请求
documentation # 📖 文档问题

# 优先级
P0-blocker       # 🔴 阻塞
P1-v1.2          # 🟠 高优先
P2-backlog       # 🟡 积压
P3-icebox        # ⚪ 待定

# 状态
triage           # 待分类
accepted         # 已接受
in-progress      # 进行中
needs-discussion # 需讨论
good-first-issue # 新手友好
help-wanted      # 求助

# 组件
area:cli         # hermes-skill CLI
area:validator   # SkillValidator
area:evolution   # EvolutionEngine
area:soul        # SoulReader / SOUL.md
area:docs        # 文档
area:ci          # CI/CD
```

---

## 附录 B: 文件清单

完成本设计后，需要在仓库中创建/更新的文件：

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml          ← 新建
│   ├── feature_request.yml     ← 新建
│   ├── skill_request.yml       ← 新建
│   ├── documentation.yml       ← 新建
│   └── config.yml              ← 新建
├── DISCUSSION_TEMPLATE/
│   └── categories.yml          ← 新建（参考配置）
docs/
├── user-feedback-system.md     ← 本文件
└── user-survey.md              ← 新建（可独立发布的问卷）
---
```

---

*本反馈系统设计于 v1.1.0 → v1.2.0 过渡期 · 设计原则：最小可行采集，最大信息密度 · 未来可扩展至 Skill Marketplace / Skill Analytics / Evolution Engine 反馈通道*
