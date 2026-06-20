"""
hermes-skill CLI — command-line interface for managing Hermes Agent skills.

Entry point for the hermes-skill command. Mounts subcommands for
creating, validating, listing, and managing SKILL.md files following
the Agent Skills open standard.

Usage:
    hermes-skill create <name>       Create a new SKILL.md from a template
    hermes-skill validate <path>     Validate SKILL.md files
    hermes-skill list [path]         List discovered skills
    hermes-skill soul generate       Generate a SOUL.md persona file
    hermes-skill soul read           Read/parse a SOUL.md file
"""

import sys
from pathlib import Path
from typing import Optional

import typer

# Ensure the src/ package is on sys.path so commands can import
# hermes_agent_skills without requiring pip install
_SRC_DIR = Path(__file__).parent.parent
if _SRC_DIR.exists():
    sys.path.insert(0, str(_SRC_DIR))

from . import __version__  # noqa: E402 — sys.path must be set before import


# ── Main Typer app ─────────────────────────────────────────

app = typer.Typer(
    name="hermes-skill",
    help="Manage Hermes Agent skills — create, validate, and list SKILL.md files.",
    add_completion=True,
    no_args_is_help=True,
)


# ── create command ─────────────────────────────────────────

@app.command()
def create(
    name: str = typer.Argument(
        ...,
        help="Skill name (lowercase, hyphens, ≤64 chars). E.g. 'my-analysis-tool'.",
    ),
    category: str = typer.Option(
        "define",
        "--category", "-c",
        help="Phase category: define, build, verify, ship, evolve.",
    ),
    template: str = typer.Option(
        "basic",
        "--template", "-t",
        help="Template: basic, advanced, minimal.",
    ),
    output: str = typer.Option(
        ".",
        "--output", "-o",
        help="Root directory for the skills/ tree.",
        show_default=True,
    ),
    soul: bool = typer.Option(
        False,
        "--soul",
        help="Also generate a SOUL.md persona file.",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="Prompt for each template variable (default: interactive).",
    ),
    soul_type: str = typer.Option(
        "balanced",
        "--soul-type",
        help="SOUL.md persona type: balanced, architect, pragmatist.",
        hidden=True,
    ),
):
    """Create a new SKILL.md skill file from a template.

    Generates a well-structured SKILL.md following the Agent Skills
    open standard, ready for editing. Supports interactive and
    non-interactive modes, plus optional SOUL.md generation.

    \b
    Examples:
        hermes-skill create my-debug-workflow
        hermes-skill create my-debug-workflow -c verify -t advanced
        hermes-skill create my-debug-workflow --no-interactive
        hermes-skill create my-debug-workflow --soul
    """
    from .commands.create import create_skill
    create_skill(
        name=name,
        category=category,
        template=template,
        output=output,
        soul=soul,
        interactive=interactive,
        soul_type=soul_type,
    )


# ── validate command ───────────────────────────────────────

@app.command()
def validate(
    path: str = typer.Argument(
        ".",
        help="Path to a SKILL.md file or a directory containing them.",
        show_default=True,
    ),
    strict: bool = typer.Option(
        False,
        "--strict/--no-strict",
        help="Require recommended fields (version, author, triggers).",
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        "-r",
        help="Scan directories recursively for SKILL.md files.",
        show_default=True,
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Only show files with validation errors.",
    ),
):
    """Validate SKILL.md file(s) against the Agent Skills standard.

    Validates frontmatter (name, description format, YAML syntax),
    body content (non-empty, section headers, gate checklist), and
    file-level constraints (size, encoding, naming).

    Exit code 0 = all valid. Exit code 1 = one or more invalid.

    \b
    Examples:
        hermes-skill validate ./SKILL.md
        hermes-skill validate skills/ --recursive
        hermes-skill validate skills/ --strict
        hermes-skill validate skills/ --quiet
    """
    from .commands.validate import validate_skills
    validate_skills(
        path=path,
        strict=strict,
        recursive=recursive,
        quiet=quiet,
    )


# ── list command ───────────────────────────────────────────

@app.command(name="list")
def list_cmd(
    path: str = typer.Argument(
        ".",
        help="Path to a skills directory.",
        show_default=True,
    ),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive", "-r",
        help="Scan directories recursively.",
        show_default=True,
    ),
    fmt: str = typer.Option(
        "table", "--format", "-f",
        help="Output format: table, json.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show additional details.",
    ),
    filter_status: Optional[str] = typer.Option(
        None, "--filter",
        help="Filter by validation status: valid, invalid.",
    ),
):
    """List discovered SKILL.md files with metadata."""
    from .commands.list import list_skills
    list_skills(
        path=path,
        recursive=recursive,
        fmt=fmt,
        verbose=verbose,
        filter_status=filter_status,
    )


# ── soul command group ─────────────────────────────────────

soul_app = typer.Typer(
    help="Manage SOUL.md persona files.",
    no_args_is_help=True,
)


@soul_app.command("generate")
def soul_generate_cmd(
    persona_type: str = typer.Argument(
        "balanced",
        help="Persona type: balanced, architect, pragmatist.",
    ),
    output: str = typer.Option(
        ".",
        "--output", "-o",
        help="Output directory.",
    ),
):
    """Generate a SOUL.md persona template file."""
    try:
        from hermes_agent_skills.soul_reader import SoulReader
    except ImportError:
        typer.echo(
            "Error: hermes_agent_skills package not found. "
            "Install with: pip install hermes-agent-skills",
            err=True,
        )
        raise typer.Exit(code=1)

    reader = SoulReader()
    valid_types = ["balanced", "architect", "pragmatist"]
    if persona_type not in valid_types:
        typer.echo(
            f"Error: Unknown persona type '{persona_type}'. "
            f"Choose from: {', '.join(valid_types)}",
            err=True,
        )
        raise typer.Exit(code=1)

    content = reader.generate_soul_template(persona_type)
    out_path = Path(output) / "SOUL.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    typer.echo(f"  ✓  Created {out_path}")
    typer.echo(f"  Persona: {persona_type}")
    raise typer.Exit(code=0)


@soul_app.command("read")
def soul_read_cmd(
    path: Optional[str] = typer.Argument(
        None,
        help="Path to SOUL.md. Auto-discovers if not provided.",
    ),
):
    """Read and parse a SOUL.md persona file."""
    try:
        from hermes_agent_skills.soul_reader import SoulReader
    except ImportError:
        typer.echo(
            "Error: hermes_agent_skills package not found. "
            "Install with: pip install hermes-agent-skills",
            err=True,
        )
        raise typer.Exit(code=1)

    reader = SoulReader()
    profile = reader.read(path)

    typer.echo(f"\n  Name:       {profile.name}")
    typer.echo(f"  Tone:       {profile.tone}")
    typer.echo(f"  Naming:     {profile.naming_convention}")
    typer.echo(f"  Comments:   {profile.comment_style}")
    typer.echo(f"  Tests:      {profile.test_style}")
    typer.echo(f"  Architecture: {profile.architecture_preference}")
    typer.echo(f"  Commits:    {profile.commit_style}")
    typer.echo(f"  Traits:     {', '.join(profile.traits)}")
    if profile.prefers_type_hints:
        typer.echo("  Type hints: yes")
    typer.echo("")

    raise typer.Exit(code=0)


app.add_typer(soul_app, name="soul")


# ── Version callback ───────────────────────────────────────

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"hermes-skill {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        False,
        "--version", "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Hermes Agent Skills CLI — manage SKILL.md files.

    Create, validate, and list Agent Skills Standard skill files.
    Built on Typer with template generation and interactive wizards.
    """
    pass


# ── CLI runner (used by console_scripts entry point) ───────

def run() -> None:
    """Entry point for the hermes-skill console script."""
    app()


if __name__ == "__main__":
    run()
