"""
CLI entry point for the Skill Validator.

Usage::

    python -m hermes_agent_skills.validator <path> [options]
    hermes-skills-validator <path> [options]          # after pip install
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .validator import SkillValidator
from .models import ValidatorConfig


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hermes-skills-validator",
        description="Validate SKILL.md files against the Agent Skills Open Standard.",
    )
    p.add_argument(
        "path",
        help="Path to a SKILL.md file or a skills/ directory",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Promote recommended-field warnings to errors",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--dimensions",
        default="",
        help="Comma-separated dimensions to enable "
             "(frontmatter,metadata,trigger,version,structure,best_practice). "
             "Default: all",
    )
    p.add_argument(
        "--skip",
        default="",
        help="Comma-separated dimensions to skip",
    )
    p.add_argument(
        "--require-version",
        action="store_true",
        help="Require the 'version' field",
    )
    p.add_argument(
        "--require-author",
        action="store_true",
        help="Require the 'author' field",
    )
    p.add_argument(
        "--require-license",
        action="store_true",
        help="Require the 'license' field",
    )
    p.add_argument(
        "--max-body-lines",
        type=int,
        default=500,
        help="Maximum recommended body lines (default: 500)",
    )
    return p


def _parse_dimension_list(raw: str) -> Optional[List[str]]:
    """Parse a comma-separated dimension list; return None for empty."""
    if not raw.strip():
        return None
    return [d.strip().lower() for d in raw.split(",") if d.strip()]


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target = Path(args.path)

    # Build config
    enable = _parse_dimension_list(args.dimensions)
    skip = _parse_dimension_list(args.skip)

    config = ValidatorConfig(
        strict=args.strict,
        require_version=args.require_version,
        require_author=args.require_author,
        require_license=args.require_license,
        max_body_lines=args.max_body_lines,
    )

    if enable:
        all_dims = {"frontmatter", "metadata", "trigger", "version", "structure", "best_practice"}
        disabled = all_dims - set(enable)
        for d in disabled:
            setattr(config, f"check_{d}", False)

    if skip:
        for d in skip:
            if hasattr(config, f"check_{d}"):
                setattr(config, f"check_{d}", False)

    v = SkillValidator(config=config)

    # Validate
    if target.is_dir():
        results = v.validate_directory(target)
    elif target.is_file() or not target.exists():
        results = [v.validate_file(target)]
    else:
        print(f"Error: '{target}' is not a valid file or directory.", file=sys.stderr)
        return 1

    # Output
    if args.format == "json":
        output = [r.to_dict() for r in results]
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        for r in results:
            print(r.summary())
            if r != results[-1]:
                print()

    # Exit code
    has_failures = any(not r.valid for r in results)
    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
