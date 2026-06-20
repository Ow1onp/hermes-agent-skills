"""
Tests for SOUL.md reader and SoulProfile.
"""

import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_agent_skills.soul_reader import (
    SoulReader, SoulProfile
)


# ── Helpers ────────────────────────────────────────────────


def make_soul_file(content: str) -> Path:
    tmpdir = Path(tempfile.mkdtemp())
    path = tmpdir / "SOUL.md"
    path.write_text(content, encoding="utf-8")
    return path


# ── Tests ──────────────────────────────────────────────────


def test_default_profile_when_no_file():
    reader = SoulReader(search_paths=["/nonexistent/SOUL.md"])
    profile = reader.read()
    assert profile.is_default
    assert profile.name == "Default Agent"
    assert profile.naming_convention == "snake_case"


def test_read_yaml_frontmatter():
    content = """---
name: "严谨架构师"
traits:
  - 类型安全
  - 显式优于隐式
coding_style:
  naming: camelCase
  prefer:
    - type_hints
    - immutability
comment_style: "代码即文档"
test_style: "BDD"
architecture_preference: "六边形架构"
commit_style: "angular"
tone: "formal"
---

# SOUL.md for testing
"""
    path = make_soul_file(content)
    reader = SoulReader()
    profile = reader.read(path)

    assert profile.name == "严谨架构师"
    assert "类型安全" in profile.traits
    assert profile.naming_convention == "camelCase"
    assert profile.prefers_type_hints is True
    assert profile.comment_style == "代码即文档"
    assert profile.test_style == "BDD"
    assert profile.architecture_preference == "六边形架构"
    assert profile.tone == "formal"


def test_read_plain_yaml():
    content = """
name: "敏捷实干家"
traits:
  - 快速迭代
  - 实用主义
coding_style:
  naming: snake_case
  prefer: [type_hints_on_public_api]
comment_style: "必要时解释"
test_style: "pytest"
architecture_preference: "模块化单体"
tone: "casual"
"""
    path = make_soul_file(content)
    reader = SoulReader()
    profile = reader.read(path)

    assert profile.name == "敏捷实干家"
    assert not profile.is_default
    assert profile.naming_convention == "snake_case"


def test_get_code_prompt_hint():
    reader = SoulReader()
    profile = reader.read()  # default

    hint = profile.get_code_prompt_hint()
    assert "snake_case" in hint
    assert "type hints" in hint.lower()


def test_comment_density_sparse():
    profile = SoulProfile(
        name="test",
        comment_style="代码即文档，无需额外注释",
    )
    assert profile.comment_density == "sparse"


def test_comment_density_detailed():
    profile = SoulProfile(
        name="test",
        comment_style="详细注释，每个函数都要解释设计决策",
    )
    assert profile.comment_density == "detailed"


def test_comment_density_moderate():
    profile = SoulProfile(
        name="test",
        comment_style="必要时解释为什么",
    )
    assert profile.comment_density == "moderate"


def test_generate_soul_template_balanced():
    reader = SoulReader()
    template = reader.generate_soul_template("balanced")
    assert "name:" in template
    assert "务实工程师" in template
    assert "snake_case" in template


def test_generate_soul_template_architect():
    reader = SoulReader()
    template = reader.generate_soul_template("architect")
    assert "严谨架构师" in template
    assert "六边形架构" in template


def test_generate_soul_template_pragmatist():
    reader = SoulReader()
    template = reader.generate_soul_template("pragmatist")
    assert "敏捷实干家" in template
    assert "模块化单体" in template


def test_generate_soul_template_unknown():
    reader = SoulReader()
    template = reader.generate_soul_template("nonexistent")
    assert "务实工程师" in template  # defaults to balanced


def test_find_soul_file_none():
    reader = SoulReader(search_paths=["/nonexistent/SOUL.md"])
    path = reader.find_soul_file()
    assert path is None


def test_find_soul_file_exists():
    tmp_path = make_soul_file("name: Test")
    reader = SoulReader(search_paths=[str(tmp_path)])
    found = reader.find_soul_file()
    assert found is not None
    assert found.name == "SOUL.md"


def test_read_invalid_yaml_fallback():
    content = """
This is not valid: YAML: :
But has key: value pairs
name: FallbackAgent
"""
    path = make_soul_file(content)
    reader = SoulReader()
    profile = reader.read(path)
    # Should fall back to line parser
    assert profile.name == "FallbackAgent"


def test_profile_is_default_flag():
    reader = SoulReader()
    profile = reader.read()  # default
    assert profile.is_default is True

    content = "name: CustomAgent"
    path = make_soul_file(content)
    profile = reader.read(path)
    assert profile.is_default is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
