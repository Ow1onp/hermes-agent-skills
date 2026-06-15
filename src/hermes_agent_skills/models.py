"""
Data models for the Skill Validator v1.

Defines structured types for validation issues, results, and configuration.
All types use Python 3.9-compatible syntax (no X | Y unions).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class IssueSeverity(Enum):
    """Severity level of a validation finding."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationDimension(Enum):
    """The six validation dimensions of Skill Validator v1."""
    FRONTMATTER = "frontmatter"
    METADATA = "metadata"
    TRIGGER = "trigger"
    VERSION = "version"
    STRUCTURE = "structure"
    BEST_PRACTICE = "best_practice"


@dataclass
class ValidationIssue:
    """A single structured validation finding.

    Attributes:
        dimension: Which validation dimension produced this issue.
        severity: ERROR (blocks validity), WARNING (advisory), or INFO (neutral).
        message: Human-readable description of the issue.
        field: Optional name of the offending frontmatter field.
        suggestion: Optional fix guidance.
    """
    dimension: ValidationDimension
    severity: IssueSeverity
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete result of validating a single SKILL.md file.

    Backward-compatible with v0.x: ``.errors`` and ``.warnings`` remain
    ``List[str]``, populated from ``.issues`` by ``add_issue()``.

    Attributes:
        path: Absolute or relative path to the validated file.
        valid: True when no ERROR-severity issues exist.
        issues: Full structured list of all findings.
        errors: Flat string list of error messages (backward compat).
        warnings: Flat string list of warning messages (backward compat).
        frontmatter: Parsed YAML frontmatter dict.
        body_length: Character length of the body (after frontmatter).
        total_chars: Total character count of the file.
        skill_name: Extracted from frontmatter ``name`` field.
        dir_name: Name of the parent directory (for name-vs-directory check).
    """
    path: str
    valid: bool = False
    issues: List[ValidationIssue] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    frontmatter: Dict = field(default_factory=dict)
    body_length: int = 0
    total_chars: int = 0
    skill_name: Optional[str] = None
    dir_name: Optional[str] = None

    # ── helpers ────────────────────────────────────────────────

    def add_issue(self, issue: ValidationIssue) -> None:
        """Append an issue and update string lists for backward compat."""
        self.issues.append(issue)
        if issue.severity == IssueSeverity.ERROR:
            self.errors.append(issue.message)
        elif issue.severity == IssueSeverity.WARNING:
            self.warnings.append(issue.message)

    def add_error(
        self,
        dimension: ValidationDimension,
        message: str,
        field: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Convenience: add an ERROR-severity issue."""
        self.add_issue(ValidationIssue(
            dimension=dimension,
            severity=IssueSeverity.ERROR,
            message=message,
            field=field,
            suggestion=suggestion,
        ))

    def add_warning(
        self,
        dimension: ValidationDimension,
        message: str,
        field: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Convenience: add a WARNING-severity issue."""
        self.add_issue(ValidationIssue(
            dimension=dimension,
            severity=IssueSeverity.WARNING,
            message=message,
            field=field,
            suggestion=suggestion,
        ))

    def add_info(
        self,
        dimension: ValidationDimension,
        message: str,
        field: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Convenience: add an INFO-severity issue."""
        self.add_issue(ValidationIssue(
            dimension=dimension,
            severity=IssueSeverity.INFO,
            message=message,
            field=field,
            suggestion=suggestion,
        ))

    def recompute_valid(self) -> None:
        """Recompute ``valid`` from current issues (use after batch modifications)."""
        self.valid = not any(
            i.severity == IssueSeverity.ERROR for i in self.issues
        )

    # ── output ─────────────────────────────────────────────────

    def summary(self) -> str:
        """One-line-per-issue human-readable summary."""
        status = "VALID" if self.valid else "INVALID"
        lines = [f"[{status}] {self.path}"]
        if self.skill_name:
            lines.append(f"  skill: {self.skill_name}")
        for issue in self.issues:
            prefix = issue.severity.value.upper()
            lines.append(
                f"  {prefix}: [{issue.dimension.value}] {issue.message}"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialize to a JSON-friendly dict."""
        return {
            "path": self.path,
            "valid": self.valid,
            "skill_name": self.skill_name,
            "dir_name": self.dir_name,
            "body_length": self.body_length,
            "total_chars": self.total_chars,
            "frontmatter": self.frontmatter,
            "issue_count": len(self.issues),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [
                {
                    "dimension": i.dimension.value,
                    "severity": i.severity.value,
                    "message": i.message,
                    "field": i.field,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ],
        }


@dataclass
class ValidatorConfig:
    """Per-run configuration for SkillValidator behavior.

    Each ``check_*`` flag enables/disables a validation dimension.
    ``strict`` promotes certain warnings to errors.
    ``require_*`` flags make optional fields mandatory.
    """
    strict: bool = False
    check_frontmatter: bool = True
    check_metadata: bool = True
    check_trigger: bool = True
    check_version: bool = True
    check_structure: bool = True
    check_best_practice: bool = True
    max_name_length: int = 64
    max_description_length: int = 1024
    max_skill_content_chars: int = 100_000
    max_body_lines: int = 500
    require_version: bool = False
    require_author: bool = False
    require_license: bool = False
    min_triggers: int = 3
    min_description_length: int = 20
    recognized_licenses: List[str] = field(default_factory=lambda: [
        "MIT", "Apache-2.0", "GPL-3.0", "GPL-2.0", "LGPL-3.0",
        "BSD-2-Clause", "BSD-3-Clause", "MPL-2.0", "CC0-1.0",
        "Unlicense", "Proprietary",
    ])

    @classmethod
    def strict_all(cls) -> "ValidatorConfig":
        """Return a configuration that requires all optional fields."""
        return cls(
            strict=True,
            require_version=True,
            require_author=True,
            require_license=True,
        )
