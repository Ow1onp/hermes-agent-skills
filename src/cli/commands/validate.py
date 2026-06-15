"""
hermes-skill validate — validate SKILL.md files.

Validates one or more SKILL.md files against the Agent Skills
open standard, reporting errors, warnings, and compliance status.
"""

import sys
from pathlib import Path
from typing import Optional

import typer


def _load_validator():
    """Import and return SkillValidator. Exits with helpful message if not found."""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from hermes_agent_skills.validator import SkillValidator
        return SkillValidator
    except ImportError:
        typer.echo(
            "Error: hermes_agent_skills package not found. "
            "Install with: pip install hermes-agent-skills",
            err=True,
        )
        raise typer.Exit(code=1)


# ── Exported command function ──────────────────────────────

def validate_skills(
    path: str = ".",
    strict: bool = False,
    recursive: bool = True,
    quiet: bool = False,
) -> None:
    """Validate SKILL.md file(s) against the Agent Skills standard.

    Validates frontmatter (name, description format, YAML syntax),
    body content (non-empty, section headers, gate checklist), and
    file-level constraints (size, encoding, naming).

    Exit code 0 = all valid. Exit code 1 = one or more invalid.
    """
    SkillValidator = _load_validator()
    target = Path(path)

    if not target.exists():
        typer.echo(f"Error: Path not found: {target}", err=True)
        raise typer.Exit(code=1)

    validator = SkillValidator(strict=strict)

    # ── Collect results ───────────────────────────────────
    if target.is_file():
        results = [validator.validate_file(target)]
    elif target.is_dir():
        if recursive:
            results = validator.validate_directory(target)
        else:
            results = [validator.validate_file(target)]
    else:
        typer.echo(f"Error: Not a file or directory: {target}", err=True)
        raise typer.Exit(code=1)

    if not results:
        typer.echo(f"No SKILL.md files found in: {target}")
        raise typer.Exit(code=0)

    # ── Report ────────────────────────────────────────────
    total = len(results)
    valid_count = sum(1 for r in results if r.valid)
    invalid_count = total - valid_count
    warning_count = sum(len(r.warnings) for r in results)

    for result in results:
        if quiet and result.valid:
            continue
        typer.echo(result.summary())

    # Summary line
    status_icon = "✓" if invalid_count == 0 else "✗"
    parts = [f"{status_icon} {valid_count}/{total} valid"]
    if warning_count:
        parts.append(f"{warning_count} warning(s)")
    typer.echo(f"\n  {', '.join(parts)}")

    if strict:
        typer.echo("  (strict mode: recommended fields are required)")

    raise typer.Exit(code=1 if invalid_count > 0 else 0)
