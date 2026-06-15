"""
Skill Validator v1 — validates SKILL.md files against the Agent Skills Open Standard.

Six validation dimensions:
  1. Frontmatter — YAML structure, required fields, name format
  2. Metadata   — optional field constraints (license, compatibility, metadata, allowed-tools)
  3. Trigger    — project-specific trigger list quality
  4. Version    — semantic versioning check
  5. Structure  — directory layout, SKILL.md file naming
  6. Best Practice — description quality, body guidelines, progressive disclosure
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml

from .models import (
    IssueSeverity,
    ValidationDimension,
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
)

# Re-export for backward compatibility (existing code imports from .validator)
__all__ = [
    "SkillValidator",
    "ValidationResult",
    "ValidatorConfig",
    "ValidationIssue",
    "IssueSeverity",
    "ValidationDimension",
]

# ── constants ──────────────────────────────────────────────────

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_CONTENT_CHARS = 100_000
MAX_COMPATIBILITY_LENGTH = 500
MAX_BODY_LINES = 500
MIN_DESCRIPTION_LENGTH = 20
MIN_TRIGGERS = 3

REQUIRED_FRONTMATTER_FIELDS = {"name", "description"}
RECOMMENDED_FIELDS = {"version", "author", "license"}

# Agent Skills Open Standard: lowercase alphanumeric + hyphens only,
# no leading/trailing hyphens, no consecutive hyphens.
_VALID_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9]*(?:-[a-z0-9]+)*$")
# Semantic version: MAJOR.MINOR.PATCH with optional pre-release/build
_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)

_ALLOWED_DIRS = {"scripts", "references", "assets"}
_RESERVED_NAMES = {"claude", "anthropic", "skill", "skills"}

# ── public API ─────────────────────────────────────────────────


class SkillValidator:
    """Validates SKILL.md files against the Agent Skills Open Standard.

    Usage::

        v = SkillValidator()
        result = v.validate_file("skills/my-skill/SKILL.md")
        print(result.summary())

        # Batch / directory:
        for r in v.validate_directory("skills/"):
            print(r.summary())
    """

    def __init__(self, config: Optional[ValidatorConfig] = None, strict: bool = False):
        """
        Args:
            config: Full ValidatorConfig; overrides ``strict`` if provided.
            strict: If True and no ``config`` given, uses ``ValidatorConfig(strict=True)``.
        """
        if config is not None:
            self.config = config
        elif strict:
            self.config = ValidatorConfig(strict=True)
        else:
            self.config = ValidatorConfig()

    # ── main entry points ──────────────────────────────────────

    def validate_file(self, path: Union[str, Path]) -> ValidationResult:
        """Validate a single SKILL.md file at *path*."""
        path = Path(path)
        result = ValidationResult(path=str(path))

        # Existence
        if not path.exists():
            result.add_error(
                ValidationDimension.STRUCTURE,
                f"File not found: {path}",
            )
            result.valid = False
            return result

        # Directory info for structure checks
        result.dir_name = path.parent.name

        # Read
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:
            result.add_error(
                ValidationDimension.STRUCTURE,
                f"Cannot read file: {exc}",
            )
            result.valid = False
            return result

        result.total_chars = len(content)

        # ── 1. Frontmatter ─────────────────────────────────────
        if self.config.check_frontmatter:
            self._check_frontmatter(path, content, result)

        # Stop early if frontmatter is broken — remaining checks
        # depend on a valid frontmatter dict.
        if not result.frontmatter:
            result.recompute_valid()
            return result

        # ── 2. Metadata ────────────────────────────────────────
        if self.config.check_metadata:
            self._check_metadata(result)

        # ── 3. Trigger ─────────────────────────────────────────
        if self.config.check_trigger:
            self._check_trigger(result)

        # ── 4. Version ─────────────────────────────────────────
        if self.config.check_version:
            self._check_version(result)

        # ── 5. Structure ───────────────────────────────────────
        if self.config.check_structure:
            self._check_structure(path, result)

        # ── 6. Best Practice ───────────────────────────────────
        if self.config.check_best_practice:
            self._check_best_practice(content, result)

        result.recompute_valid()
        return result

    def validate_directory(
        self, dir_path: Union[str, Path]
    ) -> List[ValidationResult]:
        """Recursively validate all SKILL.md files under *dir_path*."""
        dir_path = Path(dir_path)
        results: List[ValidationResult] = []
        for skill_file in sorted(dir_path.rglob("SKILL.md")):
            results.append(self.validate_file(skill_file))
        return results

    def batch_validate(
        self, paths: List[Union[str, Path]]
    ) -> List[ValidationResult]:
        """Validate an explicit list of skill file paths."""
        return [self.validate_file(p) for p in paths]

    # ── 1. Frontmatter ─────────────────────────────────────────

    def _check_frontmatter(
        self, path: Path, content: str, result: ValidationResult
    ) -> None:
        """Validate YAML frontmatter: structure, required fields, name format."""
        fm = self._parse_frontmatter(content, result)
        if fm is None:
            return

        result.frontmatter = fm

        # Size cap
        if result.total_chars > self.config.max_skill_content_chars:
            result.add_error(
                ValidationDimension.STRUCTURE,
                f"File too large: {result.total_chars} chars "
                f"(max: {self.config.max_skill_content_chars})",
            )

        # Required fields
        missing = REQUIRED_FRONTMATTER_FIELDS - set(fm.keys())
        if missing:
            result.add_error(
                ValidationDimension.FRONTMATTER,
                f"Missing required field(s): {', '.join(sorted(missing))}",
                field=sorted(missing)[0],
            )

        # Name validation (Agent Skills Open Standard)
        name = fm.get("name", "")
        result.skill_name = name

        self._validate_name(name, path, result)

        # Description validation
        desc = fm.get("description", "")
        self._validate_description(desc, result)

        # Body emptiness
        body_text = self._extract_body(content)
        result.body_length = len(body_text.strip())
        if result.body_length == 0:
            result.add_error(
                ValidationDimension.FRONTMATTER,
                "Body is empty after frontmatter",
            )

    # ── 2. Metadata ────────────────────────────────────────────

    def _check_metadata(self, result: ValidationResult) -> None:
        """Validate optional metadata fields."""
        fm = result.frontmatter

        # license
        lic = fm.get("license", "")
        if lic:
            if not isinstance(lic, str):
                result.add_error(
                    ValidationDimension.METADATA,
                    f"'license' must be a string, got {type(lic).__name__}",
                    field="license",
                )
            elif lic not in self.config.recognized_licenses:
                result.add_warning(
                    ValidationDimension.METADATA,
                    f"Unrecognized license '{lic}'. "
                    f"Recognized: {', '.join(self.config.recognized_licenses)}",
                    field="license",
                    suggestion="Use a standard SPDX identifier or 'Proprietary'",
                )

        # compatibility
        compat = fm.get("compatibility", "")
        if compat and isinstance(compat, str) and len(compat) > MAX_COMPATIBILITY_LENGTH:
            result.add_error(
                ValidationDimension.METADATA,
                f"'compatibility' is {len(compat)} chars (max: {MAX_COMPATIBILITY_LENGTH})",
                field="compatibility",
            )

        # metadata field must be a dict
        meta = fm.get("metadata")
        if meta is not None:
            if not isinstance(meta, dict):
                result.add_error(
                    ValidationDimension.METADATA,
                    f"'metadata' must be a YAML mapping (dict), got {type(meta).__name__}",
                    field="metadata",
                )
            else:
                # Check for non-string values in metadata
                for k, v in meta.items():
                    if not isinstance(v, (str, int, float, bool, list, dict)):
                        result.add_warning(
                            ValidationDimension.METADATA,
                            f"metadata.{k} has complex type {type(v).__name__}; "
                            f"prefer strings for portability",
                            field=f"metadata.{k}",
                        )

        # allowed-tools
        atools = fm.get("allowed-tools", "")
        if atools:
            if not isinstance(atools, str):
                result.add_error(
                    ValidationDimension.METADATA,
                    f"'allowed-tools' must be a space-separated string, got {type(atools).__name__}",
                    field="allowed-tools",
                )
            elif len(atools.split()) == 0:
                result.add_warning(
                    ValidationDimension.METADATA,
                    "'allowed-tools' is present but empty",
                    field="allowed-tools",
                )

        # author
        author = fm.get("author", "")
        if self.config.require_author and not author:
            result.add_error(
                ValidationDimension.METADATA,
                "Missing required field: 'author'",
                field="author",
            )

    # ── 3. Trigger ─────────────────────────────────────────────

    def _check_trigger(self, result: ValidationResult) -> None:
        """Validate the project-specific 'triggers' field."""
        fm = result.frontmatter
        triggers = fm.get("triggers")

        if triggers is None:
            # Triggers are optional but recommended
            result.add_info(
                ValidationDimension.TRIGGER,
                "No 'triggers' field. Adding triggers helps agents activate this skill.",
                field="triggers",
                suggestion="Add a list of trigger keywords, e.g. triggers: [review, 审查, code review]",
            )
            return

        if not isinstance(triggers, list):
            result.add_error(
                ValidationDimension.TRIGGER,
                f"'triggers' must be a list, got {type(triggers).__name__}",
                field="triggers",
            )
            return

        # Empty list
        if len(triggers) == 0:
            result.add_warning(
                ValidationDimension.TRIGGER,
                "'triggers' list is empty",
                field="triggers",
            )
            return

        # Non-string items
        for i, t in enumerate(triggers):
            if not isinstance(t, str):
                result.add_error(
                    ValidationDimension.TRIGGER,
                    f"triggers[{i}] must be a string, got {type(t).__name__}",
                    field="triggers",
                )
            elif t.strip() == "":
                result.add_error(
                    ValidationDimension.TRIGGER,
                    f"triggers[{i}] is an empty string",
                    field="triggers",
                )

        # Duplicate detection (case-insensitive)
        seen: Dict[str, int] = {}
        for i, t in enumerate(triggers):
            if isinstance(t, str) and t.strip():
                key = t.strip().lower()
                if key in seen:
                    result.add_warning(
                        ValidationDimension.TRIGGER,
                        f"Duplicate trigger: '{t}' (also at index {seen[key]})",
                        field="triggers",
                    )
                else:
                    seen[key] = i

        # Minimum count
        valid_count = sum(1 for t in triggers if isinstance(t, str) and t.strip())
        if 0 < valid_count < self.config.min_triggers:
            result.add_warning(
                ValidationDimension.TRIGGER,
                f"Only {valid_count} trigger(s); "
                f"recommend at least {self.config.min_triggers} for reliable skill activation",
                field="triggers",
            )

    # ── 4. Version ─────────────────────────────────────────────

    def _check_version(self, result: ValidationResult) -> None:
        """Validate the 'version' field as semantic versioning."""
        fm = result.frontmatter
        version = fm.get("version", "")

        if not version:
            if self.config.require_version:
                result.add_error(
                    ValidationDimension.VERSION,
                    "Missing required field: 'version'",
                    field="version",
                )
            else:
                result.add_info(
                    ValidationDimension.VERSION,
                    "No 'version' field. Consider adding semantic versioning (e.g., '1.0.0').",
                    field="version",
                )
            return

        if not isinstance(version, str):
            result.add_error(
                ValidationDimension.VERSION,
                f"'version' must be a string, got {type(version).__name__}",
                field="version",
            )
            return

        # Strip quotes that YAML might have added
        version_str = str(version).strip().strip("'\"")

        if version_str.startswith("v"):
            result.add_warning(
                ValidationDimension.VERSION,
                f"Version '{version_str}' has a 'v' prefix. "
                f"Use bare semver (e.g., '1.0.0' not 'v1.0.0').",
                field="version",
            )

        if not _SEMVER_RE.match(version_str.lstrip("v")):
            result.add_error(
                ValidationDimension.VERSION,
                f"Version '{version}' is not valid semantic versioning. "
                f"Expected format: MAJOR.MINOR.PATCH (e.g., '1.0.0').",
                field="version",
            )

    # ── 5. Structure ───────────────────────────────────────────

    def _check_structure(self, path: Path, result: ValidationResult) -> None:
        """Validate directory layout and file naming."""
        # File name check
        parent = path.parent

        if path.name != "SKILL.md":
            result.add_warning(
                ValidationDimension.STRUCTURE,
                f"Skill file should be named 'SKILL.md', not '{path.name}'",
                suggestion="Rename to SKILL.md",
            )

        # Name-vs-directory check (from frontmatter)
        name = result.frontmatter.get("name", "")
        if name and parent.name != name:
            result.add_warning(
                ValidationDimension.STRUCTURE,
                f"Name '{name}' does not match parent directory '{parent.name}'. "
                f"The Agent Skills Standard requires the name to match the directory.",
                field="name",
                suggestion=f"Either rename the directory to '{name}' "
                           f"or change 'name' to '{parent.name}'",
            )

        # Reserved name check
        if name:
            name_lower = name.lower()
            for reserved in _RESERVED_NAMES:
                if reserved in name_lower:
                    result.add_warning(
                        ValidationDimension.STRUCTURE,
                        f"Name '{name}' contains reserved word '{reserved}'. "
                        f"Avoid using agent/brand names in skill names.",
                        field="name",
                    )

        # Directory structure — check for unexpected top-level entries
        if parent.exists():
            try:
                entries = [e.name for e in parent.iterdir()]
                unexpected = [
                    e for e in entries
                    if e not in _ALLOWED_DIRS
                    and e != "SKILL.md"
                    and not e.startswith(".")
                ]
                if unexpected:
                    result.add_info(
                        ValidationDimension.STRUCTURE,
                        f"Unexpected files/dirs in skill directory: {', '.join(sorted(unexpected))}. "
                        f"Standard directories: {', '.join(sorted(_ALLOWED_DIRS))}",
                        suggestion="Move supporting files into references/, scripts/, or assets/",
                    )
            except PermissionError:
                pass

    # ── 6. Best Practice ───────────────────────────────────────

    def _check_best_practice(
        self, content: str, result: ValidationResult
    ) -> None:
        """Quality heuristics for description, body, and progressive disclosure."""
        # Extract body
        body_text = self._extract_body(content)
        body_lines = body_text.split("\n")

        # Description quality
        desc = result.frontmatter.get("description", "")
        self._check_description_best_practice(desc, result)

        # Body section headers
        has_h2 = "## " in body_text
        if not has_h2:
            result.add_warning(
                ValidationDimension.BEST_PRACTICE,
                "Body should include '## ' section headers for structure",
                suggestion="Add sections like ## Overview, ## When to Use, ## Common Pitfalls",
            )

        # Gate/Checklist section
        has_gate = (
            "Gate" in body_text
            or "Checklist" in body_text
            or "门禁" in body_text
            or "gate" in body_text.lower()
            or "checklist" in body_text.lower()
        )
        if not has_gate:
            result.add_warning(
                ValidationDimension.BEST_PRACTICE,
                "Body should include a gate-checklist section for verification",
                suggestion="Add '## Gate Checklist' or '## 门禁清单' section",
            )

        # Progressive disclosure: body line count
        non_empty_lines = [l for l in body_lines if l.strip()]
        if len(non_empty_lines) > self.config.max_body_lines:
            result.add_warning(
                ValidationDimension.BEST_PRACTICE,
                f"Body has {len(non_empty_lines)} non-empty lines "
                f"(recommend ≤ {self.config.max_body_lines}). "
                f"Consider moving detailed reference material to references/*.md.",
                suggestion="Move lengthy reference content to references/ directory",
            )

        # Recommended fields
        self._check_recommended_fields(result)

        # Absolute path detection
        if re.search(r"(?:(?:[A-Za-z]:[/\\])|(?:^|\s)/[a-z])", body_text):
            result.add_info(
                ValidationDimension.BEST_PRACTICE,
                "Body may contain absolute file paths. "
                "Use relative paths for portability across systems.",
            )

    # ── helpers ─────────────────────────────────────────────────

    @staticmethod
    def _parse_frontmatter(
        content: str, result: ValidationResult
    ) -> Optional[Dict]:
        """Parse YAML frontmatter; return dict or None (errors attached to result)."""
        if not content.startswith("---"):
            result.add_error(
                ValidationDimension.FRONTMATTER,
                "Frontmatter must start with '---' at byte 0",
                suggestion="Add YAML frontmatter delimited by --- at the top of the file",
            )
            return None

        # Find closing ---
        closing = content.find("\n---", 3)
        if closing == -1:
            result.add_error(
                ValidationDimension.FRONTMATTER,
                "Frontmatter closing '---' not found",
                suggestion="Add a closing '---' on its own line after the YAML block",
            )
            return None

        fm_text = content[3:closing].strip()

        try:
            fm = yaml.safe_load(fm_text)
        except yaml.YAMLError as exc:
            result.add_error(
                ValidationDimension.FRONTMATTER,
                f"Invalid YAML frontmatter: {exc}",
            )
            return None

        if not isinstance(fm, dict):
            result.add_error(
                ValidationDimension.FRONTMATTER,
                f"Frontmatter must be a YAML mapping, got {type(fm).__name__}",
            )
            return None

        return fm

    @staticmethod
    def _extract_body(content: str) -> str:
        """Return the body text after the frontmatter closing delimiter."""
        closing = content.find("\n---", 3)
        if closing == -1:
            return ""
        return content[closing + 4:].lstrip("\n")

    def _validate_name(
        self, name: str, path: Path, result: ValidationResult
    ) -> None:
        """Validate the 'name' field against the Agent Skills Open Standard."""
        if not name:
            return

        # Length
        if len(name) > self.config.max_name_length:
            result.add_error(
                ValidationDimension.FRONTMATTER,
                f"Name '{name}' is {len(name)} chars (max: {self.config.max_name_length})",
                field="name",
            )

        # Pattern: lowercase, digits, hyphens; no leading/trailing/consecutive hyphens
        if not _VALID_NAME_RE.match(name):
            # Provide a specific error message based on what's wrong
            if name != name.lower():
                result.add_error(
                    ValidationDimension.FRONTMATTER,
                    f"Name '{name}' contains uppercase characters. "
                    f"Use lowercase only.",
                    field="name",
                    suggestion=f"Change to '{name.lower()}'",
                )
            elif name.startswith("-") or name.endswith("-"):
                result.add_error(
                    ValidationDimension.FRONTMATTER,
                    f"Name '{name}' starts or ends with a hyphen.",
                    field="name",
                    suggestion="Remove leading/trailing hyphens",
                )
            elif "--" in name:
                result.add_error(
                    ValidationDimension.FRONTMATTER,
                    f"Name '{name}' contains consecutive hyphens '--'.",
                    field="name",
                    suggestion="Use single hyphens between words",
                )
            elif "_" in name:
                result.add_error(
                    ValidationDimension.FRONTMATTER,
                    f"Name '{name}' contains underscores. "
                    f"The Agent Skills Standard only allows hyphens.",
                    field="name",
                    suggestion=f"Change underscores to hyphens: '{name.replace('_', '-')}'",
                )
            else:
                result.add_error(
                    ValidationDimension.FRONTMATTER,
                    f"Name '{name}' contains invalid characters. "
                    f"Only lowercase letters, digits, and hyphens are allowed.",
                    field="name",
                )

    def _validate_description(
        self, desc: str, result: ValidationResult
    ) -> None:
        """Validate the 'description' field."""
        if not desc:
            return

        # Length
        if len(desc) > self.config.max_description_length:
            result.add_error(
                ValidationDimension.FRONTMATTER,
                f"Description is {len(desc)} chars (max: {self.config.max_description_length})",
                field="description",
            )

        # "Use when" prefix (best practice, not spec-required)
        if not desc.lower().startswith("use when"):
            result.add_warning(
                ValidationDimension.BEST_PRACTICE,
                "Description should start with 'Use when ...' for reliable agent activation",
                field="description",
                suggestion="Start with 'Use when <trigger condition>.'",
            )

    def _check_description_best_practice(
        self, desc: str, result: ValidationResult
    ) -> None:
        """Additional description quality checks beyond basic validation."""
        if not desc:
            return

        # Too short
        if len(desc) < self.config.min_description_length:
            result.add_warning(
                ValidationDimension.BEST_PRACTICE,
                f"Description is only {len(desc)} chars. "
                f"Aim for at least {self.config.min_description_length} chars "
                f"with specific trigger keywords.",
                field="description",
                suggestion="Add specific keywords and trigger conditions",
            )

        # Vague patterns
        vague_patterns = [
            (r"^[Hh]elps? (with|you)", "Too vague: 'Helps with/you ...'"),
            (r"^[Aa] (useful|helpful) ", "Too vague: 'A useful/helpful ...'"),
            (r"^[Tt]his skill ", "Redundant: 'This skill ...' — describe what it does directly"),
        ]
        for pattern, msg in vague_patterns:
            if re.search(pattern, desc):
                result.add_info(
                    ValidationDimension.BEST_PRACTICE,
                    f"Description quality: {msg}",
                    field="description",
                )

    def _check_recommended_fields(self, result: ValidationResult) -> None:
        """Check for recommended but optional frontmatter fields."""
        fm = result.frontmatter
        for field in sorted(RECOMMENDED_FIELDS - set(fm.keys())):
            msg = f"Missing recommended field: '{field}'"
            if field == "version" and self.config.require_version:
                continue  # Already reported as error in _check_version
            if field == "license" and self.config.require_license:
                result.add_error(
                    ValidationDimension.METADATA,
                    f"Missing required field: 'license'",
                    field="license",
                )
            elif self.config.strict:
                result.add_error(
                    ValidationDimension.BEST_PRACTICE,
                    msg,
                    field=field,
                )
            else:
                result.add_warning(
                    ValidationDimension.BEST_PRACTICE,
                    msg,
                    field=field,
                )
