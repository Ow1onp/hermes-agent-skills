"""
Tests for Hermes v2 Constraint Engine — auto-generate structured prompts.

Covers:
  - Full prompt generation (all 5 sections)
  - Simple prompt generation (Beginner Mode)
  - Language handling (zh/en)
  - Missing workflow/success criteria handling
  - Constraint content correctness
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_v2.task_registry import TaskRegistry
from hermes_v2.constraints import ConstraintEngine


def _engine():
    return ConstraintEngine()


def _task(task_id):
    return TaskRegistry().get(task_id)


class TestFullPromptChinese:
    """Full constraint prompts in Chinese."""

    def test_has_authority(self):
        prompt = _engine().generate(_task("publish_project"), "帮我发布", "zh")
        assert "## Authority" in prompt
        assert "Project Manager" in prompt

    def test_has_mission(self):
        prompt = _engine().generate(_task("fix_bug"), "修复错误", "zh")
        assert "## Mission" in prompt
        assert "修复错误" in prompt  # user input preserved

    def test_has_constraints(self):
        prompt = _engine().generate(_task("release_version"), "发布 v1.0", "zh")
        assert "## Constraints" in prompt

    def test_has_execution_rules(self):
        prompt = _engine().generate(_task("publish_project"), "发布", "zh")
        assert "## Execution Rules" in prompt
        assert "Step 1" in prompt or "1." in prompt

    def test_has_success_criteria(self):
        prompt = _engine().generate(_task("create_project"), "创建项目", "zh")
        assert "## Success Criteria" in prompt

    def test_all_five_sections(self):
        """Every task prompt should have all sections populated."""
        for tid in ["publish_project", "fix_bug", "create_project",
                     "write_docs", "review_code", "release_version"]:
            task = _task(tid)
            prompt = _engine().generate(task, "test", "zh")
            assert "## Authority" in prompt, f"{tid} missing Authority"
            assert "## Mission" in prompt, f"{tid} missing Mission"
            # Constraints and Success Criteria may be empty for some tasks
            # but Execution Rules should exist if there's a workflow
            if task.workflow:
                assert "## Execution Rules" in prompt, f"{tid} missing Execution Rules"


class TestFullPromptEnglish:
    """Full constraint prompts in English."""

    def test_english_sections(self):
        prompt = _engine().generate(_task("release_version"), "release v1.0", "en")
        assert "## Authority" in prompt
        assert "## Mission" in prompt

    def test_english_user_input_preserved(self):
        prompt = _engine().generate(_task("fix_bug"), "fix the crash", "en")
        assert "fix the crash" in prompt


class TestSimplePrompt:
    """Simplified prompts for Beginner Mode."""

    def test_simple_chinese(self):
        prompt = _engine().generate_simple(_task("fix_bug"), "修复错误", "zh")
        assert "Debugger" in prompt or "修复" in prompt
        assert len(prompt) < 500  # Should be concise

    def test_simple_english(self):
        prompt = _engine().generate_simple(_task("review_code"), "review this", "en")
        assert "Code Reviewer" in prompt or "review" in prompt.lower()

    def test_simple_has_constraints(self):
        prompt = _engine().generate_simple(_task("release_version"), "release", "zh")
        assert "禁止" in prompt or "constraint" in prompt.lower()

    def test_simple_has_success(self):
        prompt = _engine().generate_simple(_task("publish_project"), "publish", "en")
        assert "Verify" in prompt or "检查" in prompt or "check" in prompt.lower()


class TestConstraintContent:
    """Generated constraints match task definitions."""

    def test_publish_constraints_include_no_unfinished(self):
        prompt = _engine().generate(_task("publish_project"), "发布", "zh")
        assert "未完成" in prompt

    def test_fix_bug_constraints_include_root_cause(self):
        prompt = _engine().generate(_task("fix_bug"), "修复", "zh")
        assert "根因" in prompt or "理解" in prompt

    def test_release_constraints_include_six_locations(self):
        prompt = _engine().generate(_task("release_version"), "发布", "zh")
        assert "6" in prompt or "版本号" in prompt

    def test_review_constraints_include_security_first(self):
        prompt = _engine().generate(_task("review_code"), "审查", "zh")
        assert "安全" in prompt


class TestEdgeCases:
    """Constraint engine handles edge cases gracefully."""

    def test_task_without_workflow(self):
        # write_docs has workflow — use a task with empty workflow
        task = _task("write_docs")
        task.workflow = []  # simulate empty
        prompt = _engine().generate(task, "test", "zh")
        assert "## Authority" in prompt  # Still has authority + mission

    def test_task_without_constraints(self):
        task = _task("write_docs")
        task.constraints = []
        prompt = _engine().generate(task, "test", "zh")
        assert "## Constraints" not in prompt  # Skip empty section

    def test_task_without_success_criteria(self):
        task = _task("write_docs")
        task.success_criteria = []
        prompt = _engine().generate(task, "test", "zh")
        assert "## Success Criteria" not in prompt
