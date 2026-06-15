"""
Tests for hermes-skill list command.
"""

import json
from pathlib import Path


# ── Helpers ────────────────────────────────────────────────

def _make_skill(tmpdir: Path, name: str, content: str) -> Path:
    """Write a SKILL.md and return its path."""
    skill_dir = tmpdir / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


VALID_SKILL_A = """---
name: skill-alpha
description: Use when alpha testing.
version: 1.0.0
author: Tester
triggers: [alpha]
---

# Alpha

## Overview
Alpha skill.

## Verification Checklist
- [ ] Done
"""

VALID_SKILL_B = """---
name: skill-beta
description: Use when beta testing.
version: 1.0.0
author: Tester
triggers: [beta]
---

# Beta

## Overview
Beta skill.

## Verification Checklist
- [ ] Done
"""

# ⚠  REVIEW: set strict=False below to keep test_validate_directory_mixed working.
# Strict=True also flags missing recommended fields (version/author/triggers)
# as ERRORS rather than warnings, so be careful when changing this.


# ── Tests ──────────────────────────────────────────────────

def test_list_table_format(app, runner, tmp_skills_dir):
    """Default table output shows skill names and status."""
    _make_skill(tmp_skills_dir, "alpha", VALID_SKILL_A)
    _make_skill(tmp_skills_dir, "beta", VALID_SKILL_B)

    result = runner.invoke(app, ["list", str(tmp_skills_dir / "skills")])
    assert result.exit_code == 0
    assert "skill-alpha" in result.output
    assert "skill-beta" in result.output
    assert "valid" in result.output.lower()
    assert "2 skill(s) total" in result.output


def test_list_json_format(app, runner, tmp_skills_dir):
    """JSON output should be valid parseable JSON."""
    _make_skill(tmp_skills_dir, "alpha", VALID_SKILL_A)

    result = runner.invoke(app, ["list", str(tmp_skills_dir / "skills"), "-f", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["skill"] == "skill-alpha"
    assert data[0]["valid"] is True
    assert "errors" in data[0]
    assert "warnings" in data[0]


def test_list_empty_directory(app, runner, tmp_skills_dir):
    """Empty directory should produce clean output."""
    result = runner.invoke(app, ["list", str(tmp_skills_dir)])
    assert result.exit_code == 0
    assert "No SKILL.md files found" in result.output


def test_list_filter_valid(app, runner, tmp_skills_dir):
    """--filter valid shows only valid skills."""
    _make_skill(tmp_skills_dir, "ok", VALID_SKILL_A)
    _make_skill(tmp_skills_dir, "bad", """---
description: Use when testing.
---

# No name
""")

    result = runner.invoke(app, ["list", str(tmp_skills_dir / "skills"), "--filter", "valid"])
    assert result.exit_code == 0
    assert "skill-alpha" in result.output
    assert "1 skill(s) total" in result.output


def test_list_filter_invalid(app, runner, tmp_skills_dir):
    """--filter invalid shows only invalid skills."""
    _make_skill(tmp_skills_dir, "ok", VALID_SKILL_A)
    _make_skill(tmp_skills_dir, "bad", """---
description: Use when testing.
---

# No name
""")

    result = runner.invoke(app, ["list", str(tmp_skills_dir / "skills"), "--filter", "invalid"])
    assert result.exit_code == 0
    assert "INVALID" in result.output
    assert "1 skill(s) total" in result.output


def test_list_missing_path(app, runner, tmp_skills_dir):
    """Non-existent path should fail."""
    result = runner.invoke(app, ["list", str(tmp_skills_dir / "nope")])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()
