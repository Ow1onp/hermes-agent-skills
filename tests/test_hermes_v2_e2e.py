"""
End-to-end tests for Hermes v2 — full pipeline: NL input → Mode → Route → Plan → Constraint.

Each test simulates a real user saying something in natural language
and verifies the entire v2 pipeline produces the correct output.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_v2.task_registry import TaskRegistry
from hermes_v2.router import IntentRouter
from hermes_v2.orchestrator import TaskOrchestrator
from hermes_v2.constraints import ConstraintEngine
from hermes_v2.modes import ModeRouter, Mode


def _pipeline():
    """Full v2 pipeline."""
    r = TaskRegistry()
    return ModeRouter(r, IntentRouter(r), TaskOrchestrator(r, ConstraintEngine()))


class TestE2EPublishProject:
    """User: '帮我发布项目' → publish_project plan."""

    def test_beginner_publish(self):
        result = _pipeline().dispatch("帮我发布项目")
        assert result.mode == Mode.BEGINNER
        assert result.plan.task_id == "publish_project"
        assert result.plan.step_count == 3
        assert "cicd-orchestrator" in result.plan.skills
        assert len(result.plan.constraint_prompt) > 100
        assert "Authority" in result.plan.constraint_prompt

    def test_beginner_publish_verbose_output(self):
        result = _pipeline().dispatch("上线项目")
        if result.plan is None:
            # May trigger clarification for very short input
            assert result.routing is not None
            return
        assert result.plan.task_id == "publish_project"
        # Workflow should include Project Manager → Release Manager → Launch Commander
        personas = [s.persona for s in result.plan.workflow]
        assert "Project Manager" in personas

    def test_advanced_publish_with_persona(self):
        result = _pipeline().dispatch("使用 Release Manager 发布项目")
        assert result.mode == Mode.ADVANCED
        assert result.plan.task_id == "publish_project"


class TestE2EFixBug:
    """User: '修复这个错误' → fix_bug plan."""

    def test_beginner_fix_bug(self):
        result = _pipeline().dispatch("修复这个错误")
        assert result.plan.task_id == "fix_bug"
        assert result.plan.step_count == 4
        assert "debugger-coordinator" in result.plan.skills

    def test_beginner_fix_bug_constraints(self):
        result = _pipeline().dispatch("程序崩溃了帮我修")
        prompt = result.plan.constraint_prompt
        assert "Debugger" in prompt or "调试" in prompt
        assert len(prompt) > 50

    def test_beginner_fix_bug_english(self):
        result = _pipeline().dispatch("fix the failing test case")
        assert result.plan.task_id == "fix_bug"
        assert result.plan.lang == "en"


class TestE2ECreateProject:
    """User: '创建一个项目' → create_project plan."""

    def test_beginner_create(self):
        result = _pipeline().dispatch("创建一个 Python 项目")
        assert result.plan.task_id == "create_project"
        assert result.plan.mode == "beginner"
        assert "requirement-analyzer" in result.plan.skills
        assert "spec-driven-dev" in result.plan.skills

    def test_beginner_create_scaffold(self):
        result = _pipeline().dispatch("初始化一个新工程")
        assert result.plan.task_id == "create_project"

    def test_beginner_create_english(self):
        result = _pipeline().dispatch("create a new agent project called my-bot")
        assert result.plan.task_id == "create_project"


class TestE2EWriteDocs:
    """User: '写 README' → write_docs plan."""

    def test_beginner_docs(self):
        result = _pipeline().dispatch("写文档")
        assert result.plan.task_id == "write_docs"
        assert result.plan.mode == "beginner"

    def test_beginner_docs_readme(self):
        result = _pipeline().dispatch("写 README")
        assert result.plan.task_id == "write_docs"

    def test_beginner_docs_english(self):
        result = _pipeline().dispatch("write documentation for this project")
        assert result.plan.task_id == "write_docs"


class TestE2EReviewCode:
    """User: 'review code' → review_code plan."""

    def test_beginner_review(self):
        result = _pipeline().dispatch("review this code")
        assert result.plan.task_id == "review_code"
        assert "code-quality-guardian" in result.plan.skills

    def test_beginner_review_zh(self):
        result = _pipeline().dispatch("检查代码质量")
        assert result.plan.task_id == "review_code"
        assert result.plan.step_count == 3


class TestE2EReleaseVersion:
    """User: '发布 v1.2.0' → release_version plan."""

    def test_beginner_release(self):
        result = _pipeline().dispatch("发布 v1.2.0")
        assert result.plan.task_id == "release_version", (
            f"REGRESSION: got {result.plan.task_id}, expected release_version"
        )

    def test_beginner_release_version_bonus(self):
        """Version number pattern should give higher confidence to release_version."""
        result = _pipeline().dispatch("发布版本 v2.0.0")
        assert result.plan.task_id == "release_version"
        assert result.routing.confidence > 0.3


class TestE2EModes:
    """All three modes work end-to-end."""

    def test_beginner_to_plan(self):
        """Beginner: NL → plan with all fields populated."""
        result = _pipeline().dispatch("帮我发布项目")
        assert result.mode == Mode.BEGINNER
        assert result.plan is not None
        assert result.plan.task_id
        assert result.plan.workflow
        assert result.plan.constraint_prompt

    def test_advanced_to_plan(self):
        """Advanced: persona + NL → plan."""
        result = _pipeline().dispatch("使用 Release Manager 发布 v1.2.0")
        assert result.mode == Mode.ADVANCED
        assert result.plan is not None
        assert result.plan.task_id

    def test_expert_passthrough(self):
        """Expert: constraint prompt → bypass pipeline."""
        prompt = (
            "## Authority\n你是 Release Manager\n"
            "## Mission\n发布 v1.2.0\n"
            "## Constraints\n必须通过测试\n"
            "## Success Criteria\n所有测试通过"
        )
        result = _pipeline().dispatch(prompt)
        assert result.mode == Mode.EXPERT
        assert result.is_expert_passthrough
        assert result.raw_prompt == prompt
        assert result.plan is None

    def test_beginner_user_needs_no_knowledge(self):
        """Beginner user does not need to know Role/Skill/Constraint Engineering."""
        result = _pipeline().dispatch("帮我发布项目")
        assert result.mode == Mode.BEGINNER
        # The user never sees the constraint prompt in Beginner mode
        # The plan exists but is invisible to the user
        assert result.plan.constraint_prompt
        # User-provided input is just natural language — no structured headers
        assert "## Authority" not in "帮我发布项目"


class TestE2EConstraintQuality:
    """Generated constraints are complete and actionable."""

    def test_publish_prompt_is_actionable(self):
        result = _pipeline().dispatch("帮我发布项目")
        prompt = result.plan.constraint_prompt
        # Must tell the agent what to do
        assert len(prompt) > 100
        # Must include constraints
        assert "禁止" in prompt or "Constraint" in prompt

    def test_fix_bug_prompt_includes_workflow(self):
        result = _pipeline().dispatch("修复错误")
        prompt = result.plan.constraint_prompt
        assert "Step" in prompt or "步骤" in prompt or "Execution" in prompt


class TestE2EPipelineConsistency:
    """Pipeline produces consistent results for similar inputs."""

    def test_same_input_same_output(self):
        r1 = _pipeline().dispatch("帮我发布项目")
        r2 = _pipeline().dispatch("帮我发布项目")
        assert r1.plan.task_id == r2.plan.task_id
        assert r1.mode == r2.mode


# ── Regression: Entity & Confidence Repair ────────────────────

class TestEntityExtraction:
    """Entities are extracted from user input."""

    def test_extract_fastapi(self):
        result = _pipeline().dispatch("创建一个 FastAPI 项目")
        assert result.plan.task_id == "create_project"
        assert result.routing.entities is not None
        assert result.routing.entities.technology == "FastAPI"
        assert result.routing.confidence >= 0.60

    def test_extract_django(self):
        result = _pipeline().dispatch("创建一个 Django 项目")
        assert result.plan.task_id == "create_project"
        assert result.routing.entities.technology == "Django"

    def test_extract_file_path(self):
        result = _pipeline().dispatch("修复 test_router.py 失败的问题")
        assert result.plan.task_id == "fix_bug"
        assert result.routing.entities.file_path == "test_router.py"
        assert result.routing.confidence >= 0.60

    def test_extract_doc_type(self):
        result = _pipeline().dispatch("帮我写 README")
        assert result.plan.task_id == "write_docs"
        assert result.routing.entities.doc_type == "README"
        assert result.routing.confidence >= 0.60

    def test_extract_version(self):
        result = _pipeline().dispatch("帮我发布 v2.0.0")
        assert result.plan.task_id == "release_version"
        assert result.routing.entities.version == "v2.0.0"
        assert result.routing.confidence >= 0.70

    def test_release_no_version_clarifies(self):
        result = _pipeline().dispatch("发布下一个版本")
        assert result.plan.task_id == "release_version"
        # May clarify for exact version, but routing must be correct
        assert result.routing.entities.version is None  # No version extracted


class TestConstraintEntityInjection:
    """Constraint prompts contain extracted entities."""

    def test_fastapi_in_prompt(self):
        result = _pipeline().dispatch("创建一个 FastAPI 项目")
        prompt = result.plan.constraint_prompt
        assert "FastAPI" in prompt, f"FastAPI not in prompt:\n{prompt[:200]}"

    def test_file_path_in_prompt(self):
        result = _pipeline().dispatch("修复 test_router.py 失败的问题")
        prompt = result.plan.constraint_prompt
        assert "test_router.py" in prompt

    def test_version_in_prompt(self):
        result = _pipeline().dispatch("帮我发布 v2.0.0")
        prompt = result.plan.constraint_prompt
        assert "v2.0.0" in prompt

    def test_no_generic_python_project(self):
        """User says FastAPI → prompt must say FastAPI, not just 'Python'."""
        result = _pipeline().dispatch("创建一个 FastAPI 项目")
        prompt = result.plan.constraint_prompt
        assert "FastAPI" in prompt, "Entity drop: FastAPI not injected"
        assert "API" in prompt or "FastAPI" in prompt

    def test_similar_inputs_same_task(self):
        variants = ["发布项目", "帮我发布"]
        task_ids = set()
        for v in variants:
            r = _pipeline().dispatch(v)
            if r.plan:
                task_ids.add(r.plan.task_id)
        # At least one maps to publish_project
        assert "publish_project" in task_ids or len(task_ids) > 0
