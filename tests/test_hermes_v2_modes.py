"""
Tests for Hermes v2 Mode Router — Beginner/Advanced/Expert detection + dispatch.

Covers:
  - Mode auto-detection
  - Mode-specific behavior
  - Expert passthrough
  - Advanced persona detection
  - Beginner default
  - Clarification flow
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_v2.task_registry import TaskRegistry
from hermes_v2.router import IntentRouter
from hermes_v2.orchestrator import TaskOrchestrator
from hermes_v2.constraints import ConstraintEngine
from hermes_v2.modes import ModeRouter, Mode


def _mode_router():
    r = TaskRegistry()
    return ModeRouter(r, IntentRouter(r), TaskOrchestrator(r, ConstraintEngine()))


class TestModeDetection:
    """Auto-detection of user mode from input text."""

    def test_beginner_simple(self):
        result = _mode_router().dispatch("帮我发布项目")
        assert result.mode == Mode.BEGINNER

    def test_beginner_create(self):
        result = _mode_router().dispatch("创建一个项目")
        assert result.mode == Mode.BEGINNER

    def test_beginner_docs(self):
        result = _mode_router().dispatch("写文档")
        assert result.mode == Mode.BEGINNER

    def test_advanced_persona_zh(self):
        result = _mode_router().dispatch("用 Release Manager 发布")
        assert result.mode == Mode.ADVANCED

    def test_advanced_persona_en(self):
        result = _mode_router().dispatch("use the Debugger to fix this")
        assert result.mode == Mode.ADVANCED

    def test_advanced_persona_zh_use(self):
        result = _mode_router().dispatch("使用 Project Manager 创建项目")
        assert result.mode == Mode.ADVANCED

    def test_expert_constraint_headers(self):
        result = _mode_router().dispatch(
            "## Authority\n你是 BOSS\n## Mission\n做事情\n## Constraints\n不可以"
        )
        assert result.mode == Mode.EXPERT

    def test_expert_single_header(self):
        result = _mode_router().dispatch("## Authority\n你是 Release Manager")
        assert result.mode == Mode.EXPERT

    def test_expert_success_criteria(self):
        result = _mode_router().dispatch(
            "## Mission\n发布\n## Success Criteria\n所有测试通过"
        )
        assert result.mode == Mode.EXPERT


class TestModeBehavior:
    """Each mode produces appropriate dispatch results."""

    def test_beginner_generates_plan(self):
        result = _mode_router().dispatch("帮我发布项目")
        assert result.plan is not None
        assert result.plan.task_id == "publish_project"
        assert not result.is_expert_passthrough

    def test_advanced_generates_plan(self):
        result = _mode_router().dispatch("用 Release Manager 发布 v1.2.0")
        assert result.plan is not None
        assert result.mode == Mode.ADVANCED

    def test_expert_passthrough(self):
        result = _mode_router().dispatch(
            "## Authority\n你是 Release Manager\n## Mission\n发布 v1.2.0"
        )
        assert result.is_expert_passthrough
        assert result.raw_prompt is not None
        assert result.plan is None  # Expert bypasses plan generation

    def test_expert_raw_prompt_preserved(self):
        prompt = "## Authority\n你是 BOSS\n## Mission\n做事情"
        result = _mode_router().dispatch(prompt)
        assert result.raw_prompt == prompt


class TestClarification:
    """Low-confidence routes trigger clarification."""

    def test_vague_input_clarifies(self):
        result = _mode_router().dispatch("帮我")
        assert result.routing is not None
        assert result.routing.confidence < 0.5  # too vague

    def test_clarification_has_message(self):
        result = _mode_router().dispatch("做点什么")
        if result.routing and result.routing.clarification_needed:
            assert result.message  # not empty

    def test_clear_input_no_clarification(self):
        result = _mode_router().dispatch("帮我发布项目 v1.2.0")
        assert result.routing is not None
        assert not result.routing.clarification_needed


class TestDispatchMessage:
    """Dispatch result messages are user-friendly."""

    def test_beginner_has_message(self):
        result = _mode_router().dispatch("创建项目")
        assert result.message
        assert "创建" in result.message or "自动" in result.message or "Beginner" in result.message

    def test_expert_has_message(self):
        result = _mode_router().dispatch(
            "## Authority\n你是 BOSS\n## Mission\n做事"
        )
        assert result.message
        assert "Expert" in result.message or "专家" in result.message or "raw" in result.message.lower()
