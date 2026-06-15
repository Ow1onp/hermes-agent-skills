"""
Tests for Skill Validator v1 — 6 dimension validation.

Covers: Frontmatter, Metadata, Trigger, Version, Structure, Best Practice.
"""

import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_agent_skills.validator import (
    SkillValidator,
    ValidationResult,
    ValidatorConfig,
)
from hermes_agent_skills.models import (
    IssueSeverity,
    ValidationDimension,
    ValidationIssue,
)


# ── helpers ────────────────────────────────────────────────────

def make_skill_file(content: str, dirname: str = "test-skill") -> Path:
    """Create a temporary SKILL.md inside a named directory, return its path."""
    tmpdir = Path(tempfile.mkdtemp())
    skill_dir = tmpdir / dirname
    skill_dir.mkdir()
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


def make_skill_file_flat(content: str) -> Path:
    """Create a SKILL.md directly in a temp dir (no subdir)."""
    tmpdir = Path(tempfile.mkdtemp())
    skill_path = tmpdir / "SKILL.md"
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


# ── 1. Frontmatter Tests ───────────────────────────────────────

class TestFrontmatter:
    """Frontmatter parsing and name/description validation."""

    def test_missing_file(self):
        v = SkillValidator()
        result = v.validate_file("/nonexistent/SKILL.md")
        assert not result.valid
        assert any("not found" in e.lower() for e in result.errors)

    def test_empty_body(self):
        content = """---
name: test-skill
description: Use when testing.
---

"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_missing_frontmatter(self):
        content = """# Just a heading
No frontmatter here.
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("start with '---'" in e for e in result.errors)

    def test_missing_closing_frontmatter(self):
        content = """---
name: test-skill
description: Use when testing.
No closing ---
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("closing" in e.lower() for e in result.errors)

    def test_missing_required_fields(self):
        content = """---
triggers: [test]
---

# Body content here.
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any(
            "missing required field" in e.lower() for e in result.errors
        )

    def test_valid_skill(self):
        content = """---
name: test-skill
description: Use when testing the validator.
triggers: [test, validate]
version: 1.0.0
author: Test Author
---

# Test Skill

## Overview
This is a test skill.

## Gate Checklist
- [ ] Test passes
- [ ] No errors
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid, f"Errors: {result.errors}"
        assert result.frontmatter["name"] == "test-skill"
        assert result.frontmatter["description"] == "Use when testing the validator."
        assert result.body_length > 0

    def test_name_too_long(self):
        name65 = "a" * 65
        content = f"""---
name: {name65}
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("chars" in e for e in result.errors)

    def test_name_uppercase(self):
        content = """---
name: Test-Skill-Name
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("uppercase" in e.lower() for e in result.errors)

    def test_name_underscores(self):
        content = """---
name: test_skill_name
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("underscore" in e.lower() for e in result.errors)

    def test_name_leading_hyphen(self):
        content = """---
name: -test-skill
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid

    def test_name_trailing_hyphen(self):
        content = """---
name: test-skill-
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid

    def test_name_consecutive_hyphens(self):
        content = """---
name: test--skill
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("consecutive" in e.lower() for e in result.errors)

    def test_description_too_long(self):
        desc = "Use when " + "x" * 1024
        content = f"""---
name: test-skill
description: {desc}
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("chars" in e for e in result.errors)

    def test_description_warning_no_use_when(self):
        content = """---
name: test-skill
description: This does not start with Use when.
version: 1.0.0
author: Tester
---

# Body text here.
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid  # valid, just a warning
        assert any("Use when" in w for w in result.warnings)

    def test_name_matches_directory(self):
        """Name == directory name should produce no structure warning."""
        content = """---
name: my-awesome-skill
description: Use when doing awesome things.
---

# Body
"""
        path = make_skill_file(content, dirname="my-awesome-skill")
        result = SkillValidator().validate_file(path)
        assert result.valid
        # No structure warning about name/dir mismatch
        structure_warnings = [
            w for w in result.warnings
            if "does not match" in w.lower()
        ]
        assert len(structure_warnings) == 0

    def test_name_mismatch_directory(self):
        """Name != directory name should produce a structure warning."""
        content = """---
name: skill-foo
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content, dirname="skill-bar")
        result = SkillValidator().validate_file(path)
        assert any(
            "does not match parent directory" in w.lower()
            for w in result.warnings
        )


# ── 2. Metadata Tests ──────────────────────────────────────────

class TestMetadata:
    """Optional metadata field validation."""

    def test_unrecognized_license(self):
        content = """---
name: test-skill
description: Use when testing.
license: WeirdLicense-v7.2-custom
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any("unrecognized" in w.lower() for w in result.warnings)

    def test_recognized_license(self):
        content = """---
name: test-skill
description: Use when testing.
license: MIT
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid

    def test_compatibility_too_long(self):
        compat = "x" * 501
        content = f"""---
name: test-skill
description: Use when testing.
compatibility: {compat}
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("chars" in e for e in result.errors)

    def test_metadata_not_dict(self):
        content = """---
name: test-skill
description: Use when testing.
metadata: "just a string"
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("must be a yaml mapping" in e.lower() for e in result.errors)

    def test_metadata_valid_dict(self):
        content = """---
name: test-skill
description: Use when testing.
metadata:
  author: test-org
  version: "1.0"
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid

    def test_allowed_tools_valid(self):
        content = """---
name: test-skill
description: Use when testing.
allowed-tools: "Bash(git:*) Bash(jq:*) Read"
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid

    def test_require_license_error(self):
        content = """---
name: test-skill
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        cfg = ValidatorConfig(require_license=True)
        result = SkillValidator(config=cfg).validate_file(path)
        assert not result.valid
        assert any("license" in e.lower() for e in result.errors)

    def test_require_author_error(self):
        content = """---
name: test-skill
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        cfg = ValidatorConfig(require_author=True)
        result = SkillValidator(config=cfg).validate_file(path)
        assert not result.valid
        assert any("author" in e.lower() for e in result.errors)


# ── 3. Trigger Tests ───────────────────────────────────────────

class TestTrigger:
    """Trigger field validation."""

    def test_triggers_not_list(self):
        content = """---
name: test-skill
description: Use when testing.
triggers: "not a list"
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("must be a list" in e.lower() for e in result.errors)

    def test_triggers_empty_list(self):
        content = """---
name: test-skill
description: Use when testing.
triggers: []
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid  # empty list is a warning, not an error
        assert any("empty" in w.lower() for w in result.warnings)

    def test_trigger_non_string(self):
        content = """---
name: test-skill
description: Use when testing.
triggers: [test, 42, validate]
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("must be a string" in e.lower() for e in result.errors)

    def test_trigger_empty_string(self):
        content = """---
name: test-skill
description: Use when testing.
triggers: [test, "", validate]
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("empty string" in e.lower() for e in result.errors)

    def test_duplicate_triggers(self):
        content = """---
name: test-skill
description: Use when testing.
triggers: [test, validate, test]
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid  # duplicates are warnings, not errors
        assert any("duplicate" in w.lower() for w in result.warnings)

    def test_too_few_triggers(self):
        content = """---
name: test-skill
description: Use when testing.
triggers: [test]
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any("recommend at least" in w.lower() for w in result.warnings)

    def test_no_triggers_info(self):
        """Missing triggers field gets an INFO, not a warning or error."""
        content = """---
name: test-skill
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid
        assert any(
            "no 'triggers' field" in w.lower()
            or "no 'triggers' field" in str(result.issues).lower()
            for w in result.warnings
        ) or any(
            "triggers" in str(i.message).lower()
            and i.severity == IssueSeverity.INFO
            for i in result.issues
        )


# ── 4. Version Tests ───────────────────────────────────────────

class TestVersion:
    """Semantic versioning validation."""

    def test_valid_semver(self):
        content = """---
name: test-skill
description: Use when testing.
version: 1.2.3
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid

    def test_semver_with_prerelease(self):
        content = """---
name: test-skill
description: Use when testing.
version: 2.0.0-beta.1
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert result.valid

    def test_invalid_semver(self):
        content = """---
name: test-skill
description: Use when testing.
version: "one-point-oh"
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("not valid semantic" in e.lower() for e in result.errors)

    def test_v_prefix_warning(self):
        content = """---
name: test-skill
description: Use when testing.
version: v1.0.0
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any("v' prefix" in w for w in result.warnings)

    def test_require_version_error(self):
        content = """---
name: test-skill
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        cfg = ValidatorConfig(require_version=True)
        result = SkillValidator(config=cfg).validate_file(path)
        assert not result.valid
        assert any("version" in e.lower() for e in result.errors)


# ── 5. Structure Tests ─────────────────────────────────────────

class TestStructure:
    """Directory layout and file placement."""

    def test_filename_not_skill_md(self):
        tmpdir = Path(tempfile.mkdtemp())
        skill_dir = tmpdir / "test-skill"
        skill_dir.mkdir()
        bad_path = skill_dir / "README.md"
        bad_path.write_text("""---
name: test-skill
description: Use when testing.
---

# Body
""", encoding="utf-8")
        result = SkillValidator().validate_file(bad_path)
        assert any("should be named" in w.lower() for w in result.warnings)

    def test_reserved_name_claude(self):
        content = """---
name: claude-skill
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any("reserved" in w.lower() for w in result.warnings)

    def test_reserved_name_anthropic(self):
        content = """---
name: anthropic-tool
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any("reserved" in w.lower() for w in result.warnings)


# ── 6. Best Practice Tests ─────────────────────────────────────

class TestBestPractice:
    """Quality heuristics and progressive disclosure."""

    def test_missing_section_headers(self):
        content = """---
name: test-skill
description: Use when testing.
version: 1.0.0
author: Tester
---

# Title

Just a paragraph with no subsections at all.
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any(
            "section headers" in w.lower() for w in result.warnings
        )

    def test_missing_gate_checklist(self):
        content = """---
name: test-skill
description: Use when testing.
version: 1.0.0
author: Tester
---

# Title

## Overview
This skill has no verification section.
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any(
            "gate" in w.lower() or "checklist" in w.lower()
            for w in result.warnings
        )

    def test_description_too_short(self):
        content = """---
name: test-skill
description: Use when.
version: 1.0.0
author: Tester
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any(
            "only" in w.lower() and "char" in w.lower()
            for w in result.warnings
        )

    def test_vague_description(self):
        content = """---
name: test-skill
description: Helps with things.
version: 1.0.0
author: Tester
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert any(
            "vague" in str(i.message).lower()
            for i in result.issues
            if i.severity == IssueSeverity.INFO
        )

    def test_file_too_large(self):
        desc = "Use when testing. "
        body = "# Body\n\n" + ("x" * 100_000) + "\n"
        content = f"""---
name: test-skill
description: {desc}
---

{body}"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        assert not result.valid
        assert any("too large" in e.lower() for e in result.errors)


# ── 7. Config / Batch / Directory Tests ────────────────────────

class TestConfigAndBatch:
    """ValidatorConfig, strict mode, batch, directory validation."""

    def test_strict_mode_missing_recommended(self):
        content = """---
name: test-skill
description: Use when testing strict mode.
---

# Body
"""
        path = make_skill_file(content)
        result = SkillValidator(strict=True).validate_file(path)
        assert not result.valid
        assert any(
            "version" in e.lower() or "author" in e.lower() or "license" in e.lower()
            for e in result.errors
        )

    def test_config_strict_all(self):
        content = """---
name: test-skill
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        cfg = ValidatorConfig.strict_all()
        result = SkillValidator(config=cfg).validate_file(path)
        assert not result.valid
        # Should require version, author, AND license
        found = {e.lower() for e in result.errors}
        assert any("version" in e for e in found)
        assert any("author" in e for e in found)
        assert any("license" in e for e in found)

    def test_batch_validate_empty(self):
        result = SkillValidator().batch_validate([])
        assert result == []

    def test_batch_validate_multiple(self):
        content = """---
name: skill-a
description: Use when testing A.
---

# Body A
"""
        path_a = make_skill_file(content, dirname="skill-a")
        content_b = """---
name: skill-b
description: Use when testing B.
---

# Body B
"""
        path_b = make_skill_file(content_b, dirname="skill-b")
        results = SkillValidator().batch_validate([path_a, path_b])
        assert len(results) == 2
        assert all(r.valid for r in results)

    def test_validate_all_project_skills(self):
        """Validate all SKILL.md files in the project skills/ directory."""
        import os
        skills_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "skills"
        )
        if not os.path.isdir(skills_dir):
            pytest.skip("skills/ directory not found (running outside repo?)")

        v = SkillValidator()
        results = v.validate_directory(skills_dir)

        assert len(results) > 0, "No SKILL.md files found in skills/ directory"

        failures = [r for r in results if not r.valid]
        for r in failures:
            print(f"\n{r.summary()}")

        assert len(failures) == 0, (
            f"{len(failures)} skill(s) failed validation:\n"
            + "\n".join(r.summary() for r in failures)
        )

    def test_validation_result_to_dict(self):
        content = """---
name: test-skill
description: Use when testing serialization.
triggers: [test, serialize]
version: 1.0.0
author: Tester
license: MIT
---

# Test Skill

## Overview
Testing to_dict.

## Gate Checklist
- [ ] Works
"""
        path = make_skill_file(content)
        result = SkillValidator().validate_file(path)
        d = result.to_dict()
        assert d["valid"] is True
        assert d["skill_name"] == "test-skill"
        assert "issues" in d
        assert isinstance(d["issues"], list)

    def test_dimension_disable(self):
        """Disabling a dimension should skip its checks."""
        content = """---
name: test_skill_name
description: Use when testing.
---

# Body
"""
        path = make_skill_file(content)
        cfg = ValidatorConfig(check_frontmatter=False)
        result = SkillValidator(config=cfg).validate_file(path)
        # Without frontmatter check, underscores in name won't be caught
        # But structure check still runs
        assert result.skill_name is None or result.skill_name == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
