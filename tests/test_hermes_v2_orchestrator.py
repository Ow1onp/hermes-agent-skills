"""
Tests for Hermes v2 Task Orchestrator — task_id → ExecutionPlan.

Covers:
  - Plan generation for all 6 tasks
  - Skill assignment
  - Workflow step count
  - Fallback plan
  - Language handling (zh/en)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_v2.task_registry import TaskRegistry
from hermes_v2.router import RoutingResult
from hermes_v2.orchestrator import TaskOrchestrator
from hermes_v2.constraints import ConstraintEngine


def _orch():
    return TaskOrchestrator(TaskRegistry(), ConstraintEngine())


def _route(task_id, lang="zh"):
    """Fake a routing result for testing."""
    return RoutingResult(task_id=task_id, confidence=0.8, lang=lang)


class TestPlanGeneration:
    """Plan structure for each task."""

    def test_publish_project_plan(self):
        plan = _orch().plan(_route("publish_project"), "帮我发布项目")
        assert plan.task_id == "publish_project"
        assert plan.step_count == 3
        assert "cicd-orchestrator" in plan.skills
        assert "code-quality-guardian" in plan.skills
        assert len(plan.success_criteria) == 4

    def test_fix_bug_plan(self):
        plan = _orch().plan(_route("fix_bug"), "修复错误")
        assert plan.task_id == "fix_bug"
        assert plan.step_count == 4
        assert "debugger-coordinator" in plan.skills
        assert len(plan.constraint_prompt) > 50

    def test_create_project_plan(self):
        plan = _orch().plan(_route("create_project"), "创建项目")
        assert plan.task_id == "create_project"
        assert plan.step_count == 3
        assert "requirement-analyzer" in plan.skills
        assert "test-driven-dev" in plan.skills

    def test_write_docs_plan(self):
        plan = _orch().plan(_route("write_docs"), "写文档")
        assert plan.task_id == "write_docs"
        assert plan.step_count == 3
        # write_docs has no required skills — auto-detect
        assert plan.skills == []

    def test_review_code_plan(self):
        plan = _orch().plan(_route("review_code"), "审查代码")
        assert plan.task_id == "review_code"
        assert plan.step_count == 3
        assert "code-quality-guardian" in plan.skills

    def test_release_version_plan(self):
        plan = _orch().plan(_route("release_version"), "发布 v1.2.0")
        assert plan.task_id == "release_version"
        assert plan.step_count == 4
        assert "cicd-orchestrator" in plan.skills


class TestPlanStructure:
    """ExecutionPlan invariants."""

    def test_plan_has_label(self):
        plan = _orch().plan(_route("fix_bug"), "修 bug")
        assert plan.label  # not empty

    def test_plan_has_mode(self):
        plan = _orch().plan(_route("create_project"), "创建项目")
        assert plan.mode in ("beginner", "advanced", "expert")

    def test_plan_summary(self):
        plan = _orch().plan(_route("publish_project"), "发布")
        summary = plan.summary()
        assert "publish_project" in summary
        assert "3" in summary  # step count

    def test_beginner_tasks_default_to_beginner_mode(self):
        for tid in ("create_project", "write_docs"):
            plan = _orch().plan(_route(tid), "test")
            assert plan.mode == "beginner", f"{tid} should be beginner mode"

    def test_advanced_tasks_default_to_advanced_mode(self):
        for tid in ("release_version", "fix_bug", "review_code", "publish_project"):
            plan = _orch().plan(_route(tid), "test")
            assert plan.mode == "advanced", f"{tid} should be advanced mode"


class TestEnglishPlan:
    """English-language plans."""

    def test_english_label(self):
        plan = _orch().plan(_route("fix_bug", "en"), "fix the bug")
        assert "Fix Bug" in plan.label or "fix" in plan.label.lower()

    def test_english_prompt(self):
        plan = _orch().plan(_route("release_version", "en"), "release v1.0")
        assert "Authority" in plan.constraint_prompt or "Mission" in plan.constraint_prompt


class TestFallback:
    """Fallback handling for unknown tasks."""

    def test_unknown_task_fallback(self):
        plan = _orch().plan(_route("nonexistent_task"), "do something")
        assert plan.task_id == "general"
        assert plan.step_count == 0

    def test_fallback_has_label(self):
        plan = _orch().plan(_route("???"), "???")
        assert plan.label
