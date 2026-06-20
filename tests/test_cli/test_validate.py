"""
Tests for hermes-skill validate command.
"""

from pathlib import Path


# ── Helpers ────────────────────────────────────────────────

def _make_skill(tmpdir: Path, name: str, content: str) -> Path:
    """Write a SKILL.md and return its path."""
    skill_dir = tmpdir / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


VALID_SKILL = """---
name: test-skill
description: Use when testing validation.
version: 1.0.0
author: Tester
triggers: [test]
---

# Test Skill

## Overview
This is a test.

## When to Use
- When running tests.

## Verification Checklist
- [ ] Pass
"""

INVALID_SKILL_NO_NAME = """---
description: Use when testing.
---

# Body
"""

INVALID_SKILL_YAML = """---
name: test
description: [bad yaml
---
# Body
"""


# ── Tests ──────────────────────────────────────────────────

def test_validate_valid_file(app, runner, tmp_skills_dir):
    """Valid SKILL.md should pass with exit code 0."""
    skill_path = _make_skill(tmp_skills_dir, "valid", VALID_SKILL)
    result = runner.invoke(app, ["validate", str(skill_path)])
    assert result.exit_code == 0, f"Expected 0, got {result.exit_code}: {result.output}"
    assert "VALID" in result.output
    assert "1/1 valid" in result.output


def test_validate_invalid_file_no_name(app, runner, tmp_skills_dir):
    """SKILL.md missing 'name' should fail."""
    skill_path = _make_skill(tmp_skills_dir, "no-name", INVALID_SKILL_NO_NAME)
    result = runner.invoke(app, ["validate", str(skill_path)])
    assert result.exit_code == 1
    assert "INVALID" in result.output


def test_validate_missing_file(app, runner, tmp_skills_dir):
    """Non-existent path should fail."""
    result = runner.invoke(app, ["validate", str(tmp_skills_dir / "nonexistent" / "SKILL.md")])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_validate_directory_recursive(app, runner, tmp_skills_dir):
    """Scanning a directory should find all SKILL.md files."""
    _make_skill(tmp_skills_dir, "a", VALID_SKILL)
    _make_skill(tmp_skills_dir, "b", VALID_SKILL)
    result = runner.invoke(app, ["validate", str(tmp_skills_dir / "skills")])
    assert result.exit_code == 0
    assert "2/2 valid" in result.output


def test_validate_directory_mixed(app, runner, tmp_skills_dir):
    """Valid + invalid skills should report correctly."""
    _make_skill(tmp_skills_dir, "ok", VALID_SKILL)
    _make_skill(tmp_skills_dir, "bad", INVALID_SKILL_NO_NAME)
    result = runner.invoke(app, ["validate", str(tmp_skills_dir / "skills")])
    assert result.exit_code == 1
    assert "1/2 valid" in result.output


def test_validate_quiet_mode(app, runner, tmp_skills_dir):
    """--quiet should only show failures."""
    _make_skill(tmp_skills_dir, "ok", VALID_SKILL)
    _make_skill(tmp_skills_dir, "bad", INVALID_SKILL_NO_NAME)
    result = runner.invoke(app, ["validate", str(tmp_skills_dir / "skills"), "--quiet"])
    assert result.exit_code == 1
    # Should mention the invalid one but not the valid one
    assert "INVALID" in result.output
    # The word VALID appears inside INVALID; check that the status
    # prefix "[VALID]" does NOT appear (the valid file is silenced).
    assert "[VALID]" not in result.output


def test_validate_strict_mode(app, runner, tmp_skills_dir):
    """Strict mode should fail on missing recommended fields."""
    minimal = """---
name: strict-test
description: Use when testing strict mode.
---

# Body
"""
    skill_path = _make_skill(tmp_skills_dir, "strict", minimal)
    # Without strict, it should pass
    result = runner.invoke(app, ["validate", str(skill_path)])
    assert result.exit_code == 0

    # With strict, it should fail
    result = runner.invoke(app, ["validate", str(skill_path), "--strict"])
    assert result.exit_code == 1
    assert "INVALID" in result.output
