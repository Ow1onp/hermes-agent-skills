"""
hermes-skill create — scaffold a new SKILL.md file.

Generates SKILL.md and optional SOUL.md files from templates,
validates the output, and provides next-step guidance.
"""

import sys
from pathlib import Path
from typing import Optional

import typer

from ..templates.skill_templates import (
    TemplateEngine,
    TemplateRegistry,
    get_default_variables,
)


# Valid categories (matching existing skill tree)
VALID_CATEGORIES = ["define", "build", "verify", "ship", "evolve"]

# Default output root — relative to CWD
DEFAULT_OUTPUT_ROOT = "."


def _ensure_output_dir(
    name: str,
    category: str,
    output_root: str,
) -> Path:
    """Create and return the skill output directory.

    Layout: <output_root>/skills/<category>/<name>/
    """
    skill_dir = Path(output_root) / "skills" / category / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    return skill_dir


def _prompt_variable(
    key: str,
    default: str,
    interactive: bool,
) -> str:
    """Prompt user for a template variable value, or return default."""
    if not interactive:
        return default

    prompt = f"  {key} [{default}]: "
    try:
        raw = input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return raw.strip() if raw.strip() else default


def _interactive_fill(
    engine: TemplateEngine,
    template_str: str,
    defaults: dict,
) -> dict:
    """Walk every variable in the template, prompt for value, return filled dict."""
    variables = {}
    var_names = engine.extract_variables(template_str)

    print("\n  (Press Enter to accept defaults, Ctrl+C to cancel)\n")

    for var in var_names:
        default = defaults.get(var, "")
        if len(default) > 80:
            display_default = default[:77] + "..."
        else:
            display_default = default

        value = _prompt_variable(var, display_default, interactive=True)
        if value == display_default and len(default) > 80:
            value = default
        variables[var] = value

    return variables


def _generate_soul_file(
    output_dir: Path,
    persona_type: str,
) -> Optional[Path]:
    """Generate a SOUL.md using SoulReader's template generator."""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from hermes_agent_skills.soul_reader import SoulReader
    except ImportError:
        typer.echo("  ⚠  SOUL.md generation skipped: hermes_agent_skills not found")
        return None

    reader = SoulReader()
    content = reader.generate_soul_template(persona_type)
    soul_path = output_dir / "SOUL.md"
    soul_path.write_text(content, encoding="utf-8")
    return soul_path


# ── Exported command function ──────────────────────────────

def create_skill(
    name: str,
    category: str = "define",
    template: str = "basic",
    output: str = DEFAULT_OUTPUT_ROOT,
    soul: bool = False,
    interactive: bool = True,
    soul_type: str = "balanced",
) -> None:
    """Create a new SKILL.md skill file from a template.

    Generates a well-structured SKILL.md following the Agent Skills
    open standard, ready for editing. Supports interactive and
    non-interactive modes, plus optional SOUL.md generation.
    """
    # ── Validate inputs ──────────────────────────────────
    if category not in VALID_CATEGORIES:
        typer.echo(
            f"Error: Invalid category '{category}'. "
            f"Choose from: {', '.join(VALID_CATEGORIES)}",
            err=True,
        )
        raise typer.Exit(code=1)

    registry = TemplateRegistry()
    skill_template_obj = registry.get(template)
    if skill_template_obj is None:
        typer.echo(
            f"Error: Unknown template '{template}'. "
            f"Available: {', '.join(registry.list_names())}",
            err=True,
        )
        raise typer.Exit(code=1)

    # ── Prepare variables ─────────────────────────────────
    engine = TemplateEngine()
    defaults = {
        **get_default_variables(name, category),
        **skill_template_obj.defaults,
    }

    if interactive:
        typer.echo(f"\n  Creating skill: {name}")
        typer.echo(f"  Template:       {skill_template_obj.label}")
        typer.echo(f"  Category:       {category}")
        typer.echo(f"  Output:         {output}\n")
        variables = _interactive_fill(engine, skill_template_obj.template, defaults)
    else:
        variables = defaults

    # ── Render and write ──────────────────────────────────
    try:
        rendered = engine.render(skill_template_obj.template, variables)
    except KeyError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    skill_dir = _ensure_output_dir(name, category, output)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(rendered, encoding="utf-8")

    typer.echo(f"\n  ✓  Created {skill_path}")

    # ── Optional SOUL.md ──────────────────────────────────
    if soul:
        soul_path = _generate_soul_file(skill_dir, soul_type)
        if soul_path:
            typer.echo(f"  ✓  Created {soul_path}")

    # ── Validate the result ───────────────────────────────
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from hermes_agent_skills.validator import SkillValidator
        validator = SkillValidator(strict=False)
        result = validator.validate_file(skill_path)
        if result.valid:
            typer.echo("  ✓  Validation passed")
        else:
            typer.echo("  ⚠  Validation warnings/errors:", err=True)
            for e in result.errors:
                typer.echo(f"     ERROR: {e}", err=True)
            for w in result.warnings:
                typer.echo(f"     WARN:  {w}", err=True)
    except ImportError:
        pass

    # ── Next steps ────────────────────────────────────────
    typer.echo(f"""
  Next steps:
    Edit      {skill_path}
    Validate  hermes-skill validate {skill_path}
    List all  hermes-skill list {output}/skills/
""")

    raise typer.Exit(code=0)
