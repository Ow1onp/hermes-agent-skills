"""
Tests for SKILL.md validator.
"""

import pytest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_agent_skills.validator import SkillValidator, ValidationResult


# ── Helpers ────────────────────────────────────────────────


def make_skill_file(content: str) -> Path:
    """Create a temporary SKILL.md file and return its path."""
    tmpdir = Path(tempfile.mkdtemp())
    skill_path = tmpdir / "SKILL.md"
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


# ── Tests: File-level ──────────────────────────────────────


def test_missing_file():
    v = SkillValidator()
    result = v.validate_file("/nonexistent/SKILL.md")
    assert not result.valid
    assert "not found" in str(result.errors).lower()


def test_empty_body():
    content = """---
name: test-skill
description: Use when testing.
---

"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert not result.valid
    assert any("empty" in e.lower() for e in result.errors)


# ── Tests: Frontmatter ─────────────────────────────────────


def test_missing_frontmatter():
    content = """# Just a heading
No frontmatter here.
"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert not result.valid
    assert any("start with '---'" in e for e in result.errors)


def test_missing_closing_frontmatter():
    content = """---
name: test-skill
description: Use when testing.
No closing ---
"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert not result.valid
    assert any("closing" in e.lower() for e in result.errors)


def test_missing_required_fields():
    content = """---
triggers: [test]
---

# Body content here.
"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert not result.valid
    assert any("name" in e.lower() or "description" in e.lower() for e in result.errors)


def test_valid_skill():
    content = """---
name: test-skill
description: Use when testing the validator.
triggers: [test, validate]
version: 1.0.0
author: Test Author
---

# Test Skill

## 1. Overview
This is a test skill.

## 2. Core Flow
1. Step one
2. Step two

## 3. Gate Checklist
- [ ] Test passes
- [ ] No errors

## 4. Excuses
| Excuse | Rebuttal |
|--------|----------|
| Skip | Don't |
"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert result.valid, f"Errors: {result.errors}"
    assert result.frontmatter["name"] == "test-skill"
    assert result.frontmatter["description"] == "Use when testing the validator."
    assert result.body_length > 0


def test_name_too_long():
    content = f"""---
name: {'a' * 65}-skill
description: Use when testing.
---

# Body
"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert not result.valid
    assert any("chars" in e for e in result.errors)


def test_name_invalid_chars():
    content = """---
name: Test Skill With Spaces
description: Use when testing.
---

# Body
"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert not result.valid
    assert any("must match" in e.lower() for e in result.errors)


def test_description_too_long():
    content = f"""---
name: test-skill
description: {'Use when ' + 'x' * 1024}
---

# Body
"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert not result.valid
    assert any("chars" in e for e in result.errors)


def test_description_warning_no_use_when():
    content = """---
name: test-skill
description: This does not start with Use when.
version: 1.0.0
author: Tester
---

# Body text here.
"""
    path = make_skill_file(content)
    v = SkillValidator()
    result = v.validate_file(path)
    assert result.valid  # valid, just a warning
    assert any("Use when" in w for w in result.warnings)


def test_strict_mode_missing_recommended():
    content = """---
name: test-skill
description: Use when testing strict mode.
---

# Body
"""
    path = make_skill_file(content)
    v = SkillValidator(strict=True)
    result = v.validate_file(path)
    assert not result.valid
    assert any("version" in e.lower() or "author" in e.lower() for e in result.errors)


# ── Tests: Directory validation ─────────────────────────────


def test_validate_directory():
    """Validate all actual SKILL.md files in the skills/ directory."""
    import os
    skills_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "skills"
    )
    if not os.path.isdir(skills_dir):
        pytest.skip("skills/ directory not found (running outside repo?)")

    v = SkillValidator(strict=False)
    results = v.validate_directory(skills_dir)

    assert len(results) > 0, "No SKILL.md files found in skills/ directory"

    failures = [r for r in results if not r.valid]
    for r in failures:
        print(f"\n{r.summary()}")

    assert len(failures) == 0, (
        f"{len(failures)} skill(s) failed validation:\n"
        + "\n".join(r.summary() for r in failures)
    )


def test_batch_validate_empty():
    v = SkillValidator()
    results = v.batch_validate([])
    assert results == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
