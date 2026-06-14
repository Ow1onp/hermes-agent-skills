"""
SKILL.md validator - validates skill files against the Agent Skills open standard.
"""

import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Union

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_CONTENT_CHARS = 100_000
REQUIRED_FRONTMATTER_FIELDS = {"name", "description"}
RECOMMENDED_FRONTMATTER_FIELDS = {"version", "author", "triggers"}
VALID_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@dataclass
class ValidationResult:
    """Result of validating a single SKILL.md file."""
    path: str
    valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    frontmatter: Dict = field(default_factory=dict)
    body_length: int = 0
    total_chars: int = 0

    def summary(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        lines = [f"[{status}] {self.path}"]
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        for w in self.warnings:
            lines.append(f"  WARN:  {w}")
        return "\n".join(lines)


class SkillValidator:
    """Validates SKILL.md files against the Agent Skills standard."""

    def __init__(self, strict: bool = False):
        self.strict = strict

    def validate_file(self, path: Union[str, Path]) -> ValidationResult:
        """Validate a single SKILL.md file at the given path."""
        path = Path(path)
        result = ValidationResult(path=str(path))

        if not path.exists():
            result.errors.append(f"File not found: {path}")
            result.valid = False
            return result

        if path.name != "SKILL.md":
            result.warnings.append(
                f"Skill file should be named 'SKILL.md', not '{path.name}'"
            )

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            result.errors.append(f"Cannot read file: {e}")
            result.valid = False
            return result

        result.total_chars = len(content)

        if result.total_chars > MAX_SKILL_CONTENT_CHARS:
            result.errors.append(
                f"File too large: {result.total_chars} chars "
                f"(max: {MAX_SKILL_CONTENT_CHARS})"
            )

        if not content.startswith("---"):
            result.errors.append(
                "Frontmatter must start with '---' at byte 0"
            )
            result.valid = False
            return result

        body_start = content.find("\n---", 3)
        if body_start == -1:
            result.errors.append("Frontmatter closing '---' not found")
            result.valid = False
            return result

        fm_text = content[3:body_start].strip()
        body_text = content[body_start + 4:].lstrip("\n")

        try:
            fm = yaml.safe_load(fm_text)
        except yaml.YAMLError as e:
            result.errors.append(f"Invalid YAML frontmatter: {e}")
            result.valid = False
            return result

        if not isinstance(fm, dict):
            result.errors.append("Frontmatter must be a YAML mapping")
            result.valid = False
            return result

        result.frontmatter = fm

        missing = REQUIRED_FRONTMATTER_FIELDS - set(fm.keys())
        if missing:
            result.errors.append(
                f"Missing required field(s): {', '.join(sorted(missing))}"
            )

        name = fm.get("name", "")
        if name:
            if len(name) > MAX_NAME_LENGTH:
                result.errors.append(
                    f"Name '{name}' is {len(name)} chars (max: {MAX_NAME_LENGTH})"
                )
            if not VALID_NAME_PATTERN.match(name):
                result.errors.append(
                    f"Name '{name}' must match: lowercase, digits, hyphens, underscores"
                )

        desc = fm.get("description", "")
        if desc:
            if len(desc) > MAX_DESCRIPTION_LENGTH:
                result.errors.append(
                    f"Description is {len(desc)} chars (max: {MAX_DESCRIPTION_LENGTH})"
                )
            if not desc.startswith("Use when"):
                result.warnings.append(
                    "Description should start with 'Use when ...'"
                )

        result.body_length = len(body_text.strip())
        if result.body_length == 0:
            result.errors.append("Body is empty after frontmatter")

        missing_rec = RECOMMENDED_FRONTMATTER_FIELDS - set(fm.keys())
        for field in sorted(missing_rec):
            msg = f"Missing recommended field: '{field}'"
            if self.strict:
                result.errors.append(msg)
            else:
                result.warnings.append(msg)

        has_overview = "## " in body_text
        has_gates = (
            "Gate" in body_text
            or "Checklist" in body_text
            or "门禁" in body_text
        )
        if not has_overview:
            result.warnings.append("Body should include '## ' section headers")
        if not has_gates:
            result.warnings.append("Body should include a gate/checklist section")

        result.valid = len(result.errors) == 0
        return result

    def validate_directory(
        self, dir_path: Union[str, Path]
    ) -> List[ValidationResult]:
        """Recursively validate all SKILL.md files in a directory."""
        dir_path = Path(dir_path)
        results = []
        for skill_file in sorted(dir_path.rglob("SKILL.md")):
            results.append(self.validate_file(skill_file))
        return results

    def batch_validate(
        self, paths: List[Union[str, Path]]
    ) -> List[ValidationResult]:
        """Validate multiple skill file paths."""
        return [self.validate_file(p) for p in paths]
