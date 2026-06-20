"""
hermes-skill list — discover and list SKILL.md files.

Scans directories for SKILL.md files and displays their metadata
in table or JSON format, with optional filtering.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(
    name="list",
    help="List discovered SKILL.md files with metadata.",
)


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


@app.command()
def list_skills(
    path: str = typer.Argument(
        ".",
        help="Path to a skills directory.",
        show_default=True,
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        "-r",
        help="Scan directories recursively.",
        show_default=True,
    ),
    fmt: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: table, json.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show additional details (body length, total chars).",
    ),
    filter_status: Optional[str] = typer.Option(
        None,
        "--filter",
        help="Filter by validation status: valid, invalid.",
    ),
):
    """List discovered SKILL.md files and their key metadata.

    Scans the given directory (recursively by default) for SKILL.md
    files, parses frontmatter, and displays a summary table or JSON.

    Examples:
        hermes-skill list ./skills/
        hermes-skill list ./skills/ -f json
        hermes-skill list ./skills/ --filter valid
        hermes-skill list ./skills/ -v
    """
    SkillValidator = _load_validator()
    target = Path(path)

    if not target.exists():
        typer.echo(f"Error: Path not found: {target}", err=True)
        raise typer.Exit(code=1)

    if not target.is_dir():
        typer.echo(f"Error: Expected a directory, got a file: {target}", err=True)
        raise typer.Exit(code=1)

    validator = SkillValidator(strict=False)
    if recursive:
        results = validator.validate_directory(target)
    else:
        results = [validator.validate_file(p) for p in target.glob("SKILL.md")]

    if not results:
        typer.echo(f"No SKILL.md files found in: {target}")
        raise typer.Exit(code=0)

    # ── Filter ────────────────────────────────────────────
    if filter_status:
        if filter_status == "valid":
            results = [r for r in results if r.valid]
        elif filter_status == "invalid":
            results = [r for r in results if not r.valid]
        else:
            typer.echo(
                f"Error: Invalid filter '{filter_status}'. "
                f"Use 'valid' or 'invalid'.",
                err=True,
            )
            raise typer.Exit(code=1)

    # ── Output ────────────────────────────────────────────
    if fmt == "json":
        _output_json(results, verbose)
    else:
        _output_table(results, verbose)

    raise typer.Exit(code=0)


def _output_table(results, verbose: bool) -> None:
    """Print a formatted table of skill metadata."""
    # Column widths
    name_w = max(len(_rel_path(r)) for r in results)
    name_w = max(name_w, len("Skill"))
    status_w = 8
    desc_w = 60

    # Header
    header = f"  {'Skill':<{name_w}}  {'Status':<{status_w}}  {'Description'}"
    if verbose:
        header += f"  {'Body':>8}  {'Total':>8}"
    typer.echo(header)
    typer.echo(f"  {'-' * name_w}  {'-' * status_w}  {'-' * desc_w}")

    for r in results:
        status = "✓ valid" if r.valid else "✗ INVALID"
        name = r.frontmatter.get("name", _rel_path(r))
        desc = r.frontmatter.get("description", "(no description)")
        if len(desc) > desc_w:
            desc = desc[:desc_w - 3] + "..."

        line = f"  {name:<{name_w}}  {status:<{status_w}}  {desc}"
        if verbose:
            line += f"  {r.body_length:>8}  {r.total_chars:>8}"
        typer.echo(line)

    typer.echo(f"\n  {len(results)} skill(s) total")


def _output_json(results, verbose: bool) -> None:
    """Print skill metadata as JSON."""
    data = []
    for r in results:
        entry = {
            "skill": r.frontmatter.get("name", _rel_path(r)),
            "path": r.path,
            "valid": r.valid,
            "description": r.frontmatter.get("description", ""),
            "errors": r.errors,
            "warnings": r.warnings,
        }
        if verbose:
            entry["body_length"] = r.body_length
            entry["total_chars"] = r.total_chars
            entry["frontmatter"] = r.frontmatter
        data.append(entry)
    typer.echo(json.dumps(data, indent=2, ensure_ascii=False))


def _rel_path(result) -> str:
    """Return a relative display path for a ValidationResult."""
    try:
        return str(Path(result.path).relative_to(Path.cwd()))
    except ValueError:
        return result.path
