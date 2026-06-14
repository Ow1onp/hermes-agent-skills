# 🎯 hermes-agent-skills

> **深度适配 Hermes Agent 的开箱即用技能集 — 自进化 · 身份感知 · 命令体系原生集成**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-8A2BE2.svg)](https://github.com/NousResearch/hermes-agent)
[![Agent Skills Standard](https://img.shields.io/badge/Agent_Skills-Open_Standard-orange.svg)](https://github.com/addyosmani/agent-skills)

为 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 量身定制的生产级技能集合。每个技能都是经过实战验证的工作流，融入了 Hermes Agent 的三大核心优势：

| 特性 | 说明 |
|------|------|
| 🔗 **命令体系集成** | 与 Hermes 的 `/skills`、`/curator`、`/skill` 等斜杠命令深度结合 |
| 🧬 **自进化机制** | 技能内置学习循环，可被 Hermes 的 curator 系统自动优化 |
| 🎭 **身份感知** | 读取 `SOUL.md` 文件，根据 Agent 人设动态调整代码风格和语气 |

---

## 📦 技能矩阵（8 大技能）

```
  DEFINE           BUILD          VERIFY           SHIP           EVOLVE
 ┌────────┐     ┌────────┐     ┌─────────┐     ┌────────┐     ┌──────────┐
 │需求分析 │ ──▶ │TDD 开发│ ──▶ │多模态调试│ ──▶ │CI/CD   │ ──▶ │自进化策展 │
 │规格驱动 │     │        │     │代码门禁  │     │编排    │     │身份感知  │
 └────────┘     └────────┘     └─────────┘     └────────┘     └──────────┘
```

| 阶段 | 技能 | 一句话描述 | Hermes 独有特性 |
|------|------|-----------|----------------|
| 🎯 定义 | `requirement-analyzer` | 五轮结构化对话，澄清模糊需求至 95% 清晰度 | 持久记忆跨会话保持上下文 |
| 📐 规格 | `spec-driven-dev` | 七要素 PRD/Spec 文档，代码先行 | `/skills` 串联形成流水线 |
| 🔨 构建 | `test-driven-dev` | RED-GREEN-REFACTOR + 测试金字塔 | `delegate_task` 并行测试执行 |
| 🔍 验证 | `debugger-coordinator` | 五步调试法 + 多模态工具矩阵 | `browser` + `terminal` + `vision` 联动 |
| 🛡️ 评审 | `code-quality-guardian` | 六轴质量门禁（安全/复杂度/风格/覆盖/文档/依赖） | `patch` 自动修复 + `/curator` 质量追踪 |
| 🚀 交付 | `cicd-orchestrator` | GitHub Actions 流水线生成与优化 | `cronjob` 定时流水线 + `webhook` 触发 |
| 🧬 进化 | `skill-curator` | 四阶段策展流程，技能自我优化 | 直接对接 Hermes 的 curator 自学习循环 |
| 🎭 身份 | `persona-aware-coding` | SOUL.md 驱动全流程代码风格适配 | 原生身份系统，代码 "像这个人写的" |

---

## 🚀 快速安装

### 方式一：通过 Hermes skills 命令（推荐）

```bash
# 添加本仓库为技能源
hermes skills tap add Ow1onp/hermes-agent-skills

# 浏览并安装技能
hermes skills browse
hermes skills install requirement-analyzer
```

### 方式二：本地克隆

```bash
git clone https://github.com/Ow1onp/hermes-agent-skills.git
cd hermes-agent-skills

# 将所有技能复制到 Hermes 技能目录
cp -r skills/* ~/.hermes/skills/

# 或安装 Python 工具链
pip install -e ".[dev]"
```

### 方式三：直接加载单个技能

```bash
# 在 Hermes 会话中直接加载
/skill requirement-analyzer
/skill test-driven-dev
/skill code-quality-guardian
```

---

## 📖 使用示例

### 从需求到部署的完整流水线

```bash
# Step 1: 澄清需求
/skill requirement-analyzer
# → Hermes 进行 5 轮结构化对话，明确需求边界

# Step 2: 撰写规格
/skill spec-driven-dev
# → 生成包含 API 契约、数据模型、测试策略的 Spec 文档

# Step 3: TDD 开发
/skill test-driven-dev
# → RED → GREEN → REFACTOR 循环，测试先行

# Step 4: 质量门禁
/skill code-quality-guardian
# → 六轴审查，拦截低质量代码

# Step 5: CI/CD 部署
/skill cicd-orchestrator
# → 生成 GitHub Actions workflow，自动化部署

# Step 6: 自我进化
/skill skill-curator
# → 分析执行记录，提出技能优化建议
```

---

## 🧬 自进化机制详解

hermes-agent-skills 不仅仅是一组静态的技能文件——它们被设计为 **可自我优化的活文档**：

```
执行任务 → 记录指标 → curator 分析 → 发现改进点 → 更新技能 → 下次更好
    ↑                                                            │
    └──────────────── 正反馈循环 ─────────────────────────────────┘
```

1. **使用追踪**：每次技能被调用，记录成功率、用户纠正次数、耗时
2. **健康评分**：五维度评估（使用频率/成功率/纠正数/时效性/命令有效性）
3. **自动建议**：识别过时技能、建议合并重复、发现工作流盲区
4. **持续改进**：通过 Hermes 的 `/curator` 系统自动应用低风险更新

---

## 🎭 身份感知（SOUL.md）

定义你的 Agent 人设，所有技能自动适配风格：

```yaml
# ~/.hermes/SOUL.md
name: "严谨架构师"
traits:
  - 类型安全至上
  - 显式优于隐式
coding_style:
  naming: snake_case
  prefer: [type_hints, custom_exceptions, immutability]
comment_style: "代码即文档"
architecture_preference: "六边形架构"
```

加载 `persona-aware-coding` 后，所有代码、注释、文档都会自动适配这个人设风格。

---

## 🧪 测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行全部测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_validator.py -v
pytest tests/test_soul_reader.py -v
pytest tests/test_evolution.py -v

# 验证所有 SKILL.md 合法性
pytest tests/test_validator.py::test_validate_directory -v
```

---

## 🐍 Python API

```python
from hermes_agent_skills import (
    SkillValidator,      # SKILL.md 验证器
    SoulReader,          # SOUL.md 解析器
    EvolutionEngine,     # 自进化引擎
)

# 验证技能文件
validator = SkillValidator(strict=False)
result = validator.validate_file("skills/build/test-driven-dev/SKILL.md")
print(result.summary())

# 读取 Agent 人设
reader = SoulReader()
profile = reader.read("~/.hermes/SOUL.md")
print(f"命名风格: {profile.naming_convention}")
print(f"注释密度: {profile.comment_density}")

# 自进化分析
engine = EvolutionEngine()
engine.record_task(TaskExecutionRecord(
    task_description="修复登录 bug",
    skills_used=["test-driven-dev", "debugger-coordinator"],
    retries=2,
    success=True,
    duration_seconds=300,
))
suggestions = engine.analyze()
for s in suggestions:
    print(f"[{s.priority}] {s.action}: {s.reason}")
```

---

## 📁 项目结构

```
hermes-agent-skills/
├── skills/                       # 技能文件（Agent Skills 开放标准）
│   ├── define/                   # 定义阶段
│   │   ├── requirement-analyzer/SKILL.md
│   │   └── spec-driven-dev/SKILL.md
│   ├── build/                    # 构建阶段
│   │   └── test-driven-dev/SKILL.md
│   ├── verify/                   # 验证阶段
│   │   ├── debugger-coordinator/SKILL.md
│   │   └── code-quality-guardian/SKILL.md
│   ├── ship/                     # 交付阶段
│   │   └── cicd-orchestrator/SKILL.md
│   └── evolve/                   # 进化阶段
│       ├── skill-curator/SKILL.md
│       └── persona-aware-coding/SKILL.md
├── src/hermes_agent_skills/      # Python 核心库
│   ├── __init__.py
│   ├── validator.py              # SKILL.md 验证器
│   ├── evolution.py              # 自进化引擎
│   └── soul_reader.py            # SOUL.md 解析器
├── tests/                        # 单元测试
├── scripts/                      # 安装 & 工具脚本
├── .github/workflows/            # CI/CD
├── pyproject.toml                # Python 项目配置
└── README.md                     # 你在这 👋
```

---

## 🤝 贡献

欢迎贡献！请遵循 [Agent Skills 开放标准](https://github.com/addyosmani/agent-skills)。

```bash
# 1. Fork 本仓库
# 2. 创建你的特性分支
git checkout -b feat/my-awesome-skill

# 3. 创建技能文件
mkdir -p skills/<phase>/<skill-name>/
# 编写 SKILL.md（参考已有技能格式）

# 4. 验证技能合法性
pytest tests/test_validator.py -v

# 5. 提交 PR
git commit -m "feat: add <skill-name> skill"
```

### 社区承诺

- 🕐 **Issues 响应**：24 小时内回复
- 📝 **PR 审查**：48 小时内完成 Code Review
- 📢 **社区讨论**：[GitHub Discussions](https://github.com/Ow1onp/hermes-agent-skills/discussions)

---

## 📄 许可证

MIT © 2026 [Ow1onp](https://github.com/Ow1onp)

---

## 🔗 参考

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — Nous Research 的开源 AI Agent 框架
- [Agent Skills](https://github.com/addyosmani/agent-skills) — Addy Osmani 的 Agent Skills 开放标准
- [Hermes Agent 文档](https://hermes-agent.nousresearch.com/docs/)
