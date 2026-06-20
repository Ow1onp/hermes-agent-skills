"""
Tests for hermes-skill create command.
"""



def test_create_non_interactive_basic(app, runner, tmp_skills_dir):
    """Create a skill in non-interactive mode with default template."""
    result = runner.invoke(
        app,
        [
            "create", "my-test-skill",
            "--no-interactive",
            "-o", str(tmp_skills_dir),
        ],
    )
    assert result.exit_code == 0, f"CLI failed: {result.output}"

    # Verify the file was created
    skill_path = tmp_skills_dir / "skills" / "define" / "my-test-skill" / "SKILL.md"
    assert skill_path.exists(), f"Expected {skill_path} to exist"
    content = skill_path.read_text(encoding="utf-8")
    assert content.startswith("---"), "Frontmatter must start with ---"
    assert "name: my-test-skill" in content
    assert "description: Use when" in content
    assert "## Overview" in content


def test_create_with_category(app, runner, tmp_skills_dir):
    """Create a skill in a specific category."""
    result = runner.invoke(
        app,
        [
            "create", "build-tool",
            "--no-interactive",
            "-c", "build",
            "-o", str(tmp_skills_dir),
        ],
    )
    assert result.exit_code == 0
    skill_path = tmp_skills_dir / "skills" / "build" / "build-tool" / "SKILL.md"
    assert skill_path.exists()


def test_create_advanced_template(app, runner, tmp_skills_dir):
    """Create a skill with the advanced template."""
    result = runner.invoke(
        app,
        [
            "create", "advanced-skill",
            "--no-interactive",
            "-t", "advanced",
            "-o", str(tmp_skills_dir),
        ],
    )
    assert result.exit_code == 0
    skill_path = tmp_skills_dir / "skills" / "define" / "advanced-skill" / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "Quality Gates" in content
    assert "Excuses & Rebuttals" in content


def test_create_minimal_template(app, runner, tmp_skills_dir):
    """Create a skill with the minimal template."""
    result = runner.invoke(
        app,
        [
            "create", "minimal-skill",
            "--no-interactive",
            "-t", "minimal",
            "-o", str(tmp_skills_dir),
        ],
    )
    assert result.exit_code == 0
    skill_path = tmp_skills_dir / "skills" / "define" / "minimal-skill" / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "## Core Steps" in content
    # Minimal template should NOT have quality gates
    assert "Quality Gates" not in content


def test_create_invalid_category(app, runner, tmp_skills_dir):
    """Creating with an invalid category should fail."""
    result = runner.invoke(
        app,
        [
            "create", "bad-skill",
            "--no-interactive",
            "-c", "nonexistent",
            "-o", str(tmp_skills_dir),
        ],
    )
    assert result.exit_code != 0
    assert "Invalid category" in result.output


def test_create_invalid_template(app, runner, tmp_skills_dir):
    """Creating with an invalid template should fail."""
    result = runner.invoke(
        app,
        [
            "create", "bad-skill",
            "--no-interactive",
            "-t", "nonexistent",
            "-o", str(tmp_skills_dir),
        ],
    )
    assert result.exit_code != 0
    assert "Unknown template" in result.output


def test_create_output_is_valid_skill(app, runner, tmp_skills_dir):
    """The generated SKILL.md should pass the validator."""
    result = runner.invoke(
        app,
        [
            "create", "valid-skill",
            "--no-interactive",
            "-o", str(tmp_skills_dir),
        ],
    )
    assert result.exit_code == 0
    assert "Validation passed" in result.output
