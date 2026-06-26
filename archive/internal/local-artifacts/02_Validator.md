# 02 — Skill Validator

## Overview

`SkillValidator` is the quality gate for SKILL.md files. It checks conformance against the Agent Skills Open Standard across 6 dimensions, producing structured `ValidationResult` output with severity-graded issues.

- **File:** `src/hermes_agent_skills/validator.py` (~29KB)
- **Data models:** `src/hermes_agent_skills/models.py` (~8KB)
- **Tests:** `tests/test_validator.py` — 52 tests
- **CLI entry:** `hermes-skill validate` (Typer) + `python -m hermes_agent_skills.validator` (argparse)

## Data Model

### ValidationIssue
```python
@dataclass
class ValidationIssue:
    dimension: ValidationDimension  # Which check failed
    severity: IssueSeverity         # ERROR | WARNING | INFO
    message: str                    # Human-readable description
    location: str                   # File path or YAML key
    suggestion: Optional[str]       # How to fix
```

### ValidationResult
```python
@dataclass
class ValidationResult:
    valid: bool = False
    file_path: str = ""
    issues: list[ValidationIssue]
    errors: int = 0      # Count of ERROR severity
    warnings: int = 0    # Count of WARNING severity
    info: int = 0        # Count of INFO severity
    dimensions_passed: int = 0
    dimensions_total: int = 6
```

### ValidatorConfig
```python
@dataclass
class ValidatorConfig:
    strict: bool = False           # ERROR on WARNING-level items
    require_author: bool = False
    require_license: bool = False
    require_version: bool = False
    max_description_length: int = 500
    allowed_licenses: list[str]    # SPDX identifiers
    reserved_names: list[str]      # claude, anthropic, etc.
```

## Six Validation Dimensions

### 1. Frontmatter
- YAML parse validity
- Required fields: `name`, `description`
- Naming rules: lowercase + digits + hyphens only, no leading/trailing hyphens, no consecutive hyphens, no underscores
- Name must match parent directory name

### 2. Metadata
- `license` must be recognized SPDX identifier or "Proprietary"
- `compatibility` max 500 characters
- `metadata` must be a dict if present
- `allowed-tools` format validation if present

### 3. Triggers
- Must be a list of non-empty strings
- Case-insensitive duplicate detection
- Minimum 3 triggers recommended (INFO if fewer)

### 4. Version
- Must match SemVer `X.Y.Z` (+ optional prerelease suffix)
- `v` prefix generates WARNING
- `require_version` strict mode errors on missing version

### 5. Structure
- File must be named `SKILL.md`
- Reserved name detection (claude, anthropic, cursor, etc.)
- Directory layout: `scripts/`, `references/`, `assets/` are recognized
- Extra files generate INFO (not errors)

### 6. Best Practice
- Description should start with "Use when" or similar
- Minimum description length: 20 characters
- Fuzzy/vague description detection
- Section headers should use `##` format
- Gate/checklist section should exist
- Progressive disclosure: file should be ≤500 lines
- No absolute paths in references

## Usage

```bash
# Validate single file
hermes-skill validate skills/build/test-driven-dev/SKILL.md

# Recursive directory scan
hermes-skill validate skills/ --recursive

# Strict mode (all WARNINGs become ERRORs)
hermes-skill validate skills/ --strict

# JSON output for machine consumption
hermes-skill validate skills/ --format json

# Quiet mode (only show failures)
hermes-skill validate skills/ --quiet
```

## Test Coverage

52 tests cover:
- Frontmatter parsing edge cases (missing fields, bad YAML, invalid names)
- SemVer parsing (valid, invalid, prerelease, v-prefix)
- Trigger validation (duplicates, empty strings, minimum count)
- Metadata checks (license SPDX, compatibility length)
- Structure checks (reserved names, directory layout)
- Strict mode behavior
- Recursive scanning
- JSON output format
