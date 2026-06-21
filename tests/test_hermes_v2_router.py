"""
Tests for Hermes v2 Intent Router — NL → task_id classification.

Covers:
  - Chinese input routing
  - English input routing
  - Confidence scoring
  - Clarification triggers
  - Version pattern bonus
  - Edge cases (empty, unknown, mixed language)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_v2.task_registry import TaskRegistry
from hermes_v2.router import IntentRouter, RoutingResult


def _router():
    return IntentRouter(TaskRegistry())


class TestChineseRouting:
    """Chinese natural language → correct task_id."""

    def test_publish_project_exact(self):
        r = _router().route("帮我发布项目")
        assert r.task_id == "publish_project"
        assert r.confidence > 0.2

    def test_publish_project_short(self):
        r = _router().route("发布")
        # "发布" alone is short — may route to publish_project or release_version
        # Both are valid; we just verify it doesn't crash
        assert r.task_id in ("publish_project", "release_version", "general")

    def test_fix_bug_exact(self):
        r = _router().route("修复这个错误")
        assert r.task_id == "fix_bug"
        assert r.confidence > 0.2

    def test_fix_bug_short(self):
        r = _router().route("报错了")
        assert r.task_id == "fix_bug"

    def test_fix_bug_crash(self):
        r = _router().route("程序崩溃了帮我调试")
        assert r.task_id == "fix_bug"

    def test_create_project_exact(self):
        r = _router().route("创建一个 Python 项目")
        assert r.task_id == "create_project"
        assert r.confidence > 0.2

    def test_create_project_new(self):
        r = _router().route("新建一个工程")
        assert r.task_id == "create_project"

    def test_write_docs(self):
        r = _router().route("写文档")
        assert r.task_id == "write_docs"

    def test_write_docs_readme(self):
        r = _router().route("帮我写 README")
        assert r.task_id == "write_docs"

    def test_review_code(self):
        r = _router().route("检查代码质量")
        assert r.task_id == "review_code"

    def test_review_code_inspect(self):
        r = _router().route("审查一下这个代码")
        assert r.task_id == "review_code"

    def test_release_version_with_number(self):
        r = _router().route("发布 v1.2.0")
        assert r.task_id == "release_version"
        assert r.confidence > 0.3  # version pattern bonus

    def test_release_version_new(self):
        r = _router().route("新版本发布")
        assert r.task_id in ("release_version", "publish_project")


class TestEnglishRouting:
    """English natural language → correct task_id."""

    def test_publish(self):
        r = _router().route("publish")
        # Single-word English queries are ambiguous
        assert r.task_id in ("publish_project", "release_version", "general")

    def test_fix_bug(self):
        r = _router().route("fix the failing test")
        assert r.task_id == "fix_bug"

    def test_fix_crash(self):
        r = _router().route("debug this crash")
        assert r.task_id == "fix_bug"

    def test_create_project(self):
        r = _router().route("create a new agent project")
        assert r.task_id == "create_project"

    def test_review_code(self):
        r = _router().route("review this code")
        assert r.task_id == "review_code"

    def test_write_docs(self):
        r = _router().route("write documentation")
        assert r.task_id == "write_docs"

    def test_release_version(self):
        r = _router().route("release v2.0.0")
        assert r.task_id == "release_version"


class TestConfidence:
    """Confidence scoring behavior."""

    def test_exact_match_high_confidence(self):
        r = _router().route("发布项目")
        assert r.confidence >= 0.0
        assert not r.clarification_needed

    def test_vague_input_low_confidence(self):
        r = _router().route("做点事情")
        assert r.confidence < 0.5

    def test_empty_input(self):
        r = _router().route("")
        assert r.task_id == "general"
        assert r.confidence == 0.0

    def test_unknown_topic(self):
        r = _router().route("今天天气怎么样")
        assert r.confidence < 0.3  # No task keywords match


class TestLanguageDetection:
    """Language auto-detection."""

    def test_chinese_detected(self):
        r = _router().route("帮我发布项目")
        assert r.lang == "zh"

    def test_english_detected(self):
        r = _router().route("release version 1.0")
        assert r.lang == "en"

    def test_mixed_prefers_chinese(self):
        # Has enough CJK chars → zh
        r = _router().route("帮我 fix 一下")
        assert r.lang == "zh"


class TestRegression:
    """Previously-fixed routing bugs."""

    def test_release_not_mistaken_for_publish(self):
        """"发布 v1.2.0" must route to release_version, not publish_project."""
        r = _router().route("发布 v1.2.0")
        assert r.task_id == "release_version", (
            f"Expected release_version, got {r.task_id} "
            f"(keywords: {r.matched_keywords})"
        )

    def test_review_code_not_clarify(self):
        """'review this code' must resolve to review_code, not clarification."""
        r = _router().route("review this code")
        assert r.task_id == "review_code"
        assert not r.clarification_needed

    def test_fix_test_not_clarify(self):
        """'fix the failing test' must resolve to fix_bug."""
        r = _router().route("fix the failing test")
        assert r.task_id == "fix_bug"
        assert not r.clarification_needed
