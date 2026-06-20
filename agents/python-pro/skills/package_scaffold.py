"""
Package Scaffold Skill — Generate modern Python project scaffolding with pyproject.toml.

Creates complete Python project structures including pyproject.toml, directory layout,
CI configuration, and development tooling setup. Follows modern Python packaging standards.

Part of the Python Pro agent in the HermesHub marketplace.
"""
import json
from typing import Any


# ============================================================
# JSON Schema — visible to the model for tool dispatch
# ============================================================
SCHEMA = {
    "name": "python_package_scaffold",
    "description": (
        "Generate a complete modern Python project scaffold. Creates pyproject.toml with "
        "dependencies and tool configs (ruff, pytest, mypy), directory structure (src layout "
        "or flat), and optional extras like Dockerfile, CI config, .gitignore, and Makefile. "
        "Use when: starting a new Python project, setting up packaging, or modernizing project structure."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "project_name": {
                "type": "string",
                "description": "Name of the Python project (lowercase, hyphens, e.g., 'my-fastapi-app')."
            },
            "project_type": {
                "type": "string",
                "enum": ["library", "cli", "web_api", "minimal"],
                "description": "Type of project to scaffold.",
                "default": "library"
            },
            "python_version": {
                "type": "string",
                "description": "Minimum Python version required (e.g., '3.11').",
                "default": "3.11"
            },
            "layout": {
                "type": "string",
                "enum": ["src", "flat"],
                "description": "Package layout: 'src' (src/package_name/) or 'flat' (package_name/ at root).",
                "default": "src"
            },
            "with_extras": {
                "type": "array",
                "items": {"type": "string", "enum": ["docker", "ci", "makefile", "pre_commit", "devcontainer"]},
                "description": "Optional extras to include in the scaffold.",
                "default": []
            },
            "dependencies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Additional production dependencies to add to pyproject.toml.",
                "default": []
            },
            "dev_dependencies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Additional dev dependencies to add.",
                "default": []
            }
        },
        "required": ["project_name"]
    }
}


# ============================================================
# Handler — executed by the system
# ============================================================
def handler(args: dict[str, Any]) -> str:
    """
    Generate project scaffold files.

    Args:
        args: Validated parameters matching SCHEMA.

    Returns:
        JSON string with all generated file contents and directory structure.
    """
    try:
        project_name = args.get("project_name", "")
        project_type = args.get("project_type", "library")
        python_version = args.get("python_version", "3.11")
        layout = args.get("layout", "src")
        with_extras_raw = args.get("with_extras", [])
        dependencies = args.get("dependencies", [])
        dev_dependencies = args.get("dev_dependencies", [])

        # Input validation
        if not project_name or not project_name.strip():
            return json.dumps({"error": "project_name is required and cannot be empty."})

        # Validate project name format
        import re
        if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', project_name):
            return json.dumps({
                "error": (
                    f"Invalid project name '{project_name}'. "
                    "Must be lowercase, use hyphens, start with a letter, and end with a letter or digit. "
                    "Example: 'my-fastapi-app'"
                )
            })

        if len(project_name) > 50:
            return json.dumps({
                "error": "Project name too long (max 50 characters)."
            })

        # Validate extras
        valid_extras = {"docker", "ci", "makefile", "pre_commit", "devcontainer"}
        with_extras = [e for e in with_extras_raw if e in valid_extras]

        # Generate all scaffold files
        files: dict[str, str] = {}

        # 1. pyproject.toml
        files["pyproject.toml"] = _generate_pyproject(
            project_name, project_type, python_version, layout,
            dependencies, dev_dependencies, with_extras
        )

        # 2. Source directory structure
        package_name = project_name.replace("-", "_")
        if layout == "src":
            init_path = f"src/{package_name}/__init__.py"
        else:
            init_path = f"{package_name}/__init__.py"
        files[init_path] = _generate_init(project_name, project_type)

        # 3. .gitignore
        files[".gitignore"] = _generate_gitignore(layout)

        # 4. README.md stub
        files["README.md"] = _generate_readme(project_name, project_type)

        # 5. Optional extras
        if "docker" in with_extras:
            files["Dockerfile"] = _generate_dockerfile(project_name, layout, project_type)
            files[".dockerignore"] = _generate_dockerignore()

        if "ci" in with_extras:
            files[".github/workflows/ci.yml"] = _generate_ci(project_name, python_version)

        if "makefile" in with_extras:
            files["Makefile"] = _generate_makefile(project_name)

        if "pre_commit" in with_extras:
            files[".pre-commit-config.yaml"] = _generate_precommit(python_version)

        if "devcontainer" in with_extras:
            files[".devcontainer/devcontainer.json"] = _generate_devcontainer(python_version)

        # Generate directory tree
        directories = _generate_directory_tree(project_name, layout, package_name, with_extras)

        return json.dumps({
            "success": True,
            "project_name": project_name,
            "package_name": package_name,
            "project_type": project_type,
            "python_version": python_version,
            "layout": layout,
            "extras": with_extras,
            "directories": directories,
            "files": files,
            "instructions": {
                "create": (
                    f"Create the project directory: mkdir {project_name} && cd {project_name}"
                ),
                "write": "Write each file from the 'files' map to the corresponding path.",
                "setup": (
                    "After creating files, run:\n"
                    "  python -m venv .venv\n"
                    "  source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows\n"
                    "  uv pip install -e '.[dev]'\n"
                    "  ruff check . && pytest"
                )
            }
        })

    except Exception as e:
        return json.dumps({
            "error": f"Scaffold generation failed: {str(e)}",
            "type": type(e).__name__
        })


# ============================================================
# File Generators
# ============================================================
def _generate_pyproject(
    name: str, ptype: str, py_ver: str, layout: str,
    deps: list[str], dev_deps: list[str], extras: list[str]
) -> str:
    """Generate a modern pyproject.toml file."""
    package_name = name.replace("-", "_")

    # Base dependencies by project type
    base_deps: dict[str, list[str]] = {
        "library": [],
        "cli": ["click>=8.0"],
        "web_api": ["fastapi>=0.110", "uvicorn>=0.29"],
        "minimal": [],
    }

    # Base dev dependencies
    base_dev = [
        "pytest>=8.0",
        "pytest-cov>=4.0",
        "ruff>=0.5",
        "mypy>=1.0",
    ]
    if "pre_commit" in extras:
        base_dev.append("pre-commit>=3.0")

    # Combine all dependencies
    all_deps = sorted(set(base_deps.get(ptype, []) + deps))
    all_dev = sorted(set((base_dev + dev_deps)))

    packages_path = f"src/{package_name}" if layout == "src" else package_name
    packages_config = f'\npackages = ["{packages_path}"]' if layout == "src" else ""

    # Build optional-dependencies section
    dev_deps_str = "\n".join(f'    "{d}",' for d in all_dev)
    optional_deps_section = f"""
[project.optional-dependencies]
dev = [
{dev_deps_str}
]"""

    deps_str = "\n".join(f'    "{d}",' for d in all_deps) if all_deps else "    # Add production dependencies here"

    return f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
description = "A Python project"
readme = "README.md"
requires-python = ">={py_ver}"
license = {{text = "MIT"}}
authors = [{{name = "Developer", email = "dev@example.com"}}]
dependencies = [
{deps_str}
]
{optional_deps_section}

[tool.hatch.build.targets.wheel]{packages_config}

[tool.ruff]
line-length = 88
target-version = "py{py_ver.replace('.', '')}"
lint.select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
lint.ignore = []

[tool.ruff.lint.isort]
known-first-party = ["{package_name}"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = ["-v", "--tb=short", "--strict-markers"]

[tool.mypy]
python_version = "{py_ver}"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false

[tool.coverage.run]
source = ["{package_name}"]
omit = ["tests/*", "*/migrations/*"]
'''


def _generate_init(name: str, ptype: str) -> str:
    """Generate __init__.py with appropriate content."""
    docstrings = {
        "library": '"""A Python library for data processing and utilities."""\n\n__version__ = "0.1.0"',
        "cli": '"""A command-line tool for task automation."""\n\n__version__ = "0.1.0"',
        "web_api": '"""A FastAPI web application."""\n\n__version__ = "0.1.0"',
        "minimal": '"""A Python module."""\n\n__version__ = "0.1.0"',
    }
    return docstrings.get(ptype, docstrings["minimal"])


def _generate_gitignore(layout: str) -> str:
    """Generate a comprehensive .gitignore for Python projects."""
    src_ignore = "/src/*.egg-info/" if layout == "src" else "/*.egg-info/"
    return f'''# Bytecode
__pycache__/
*.py[cod]
*.pyo

# Virtual environment
.venv/
venv/
env/

# Distribution
dist/
build/{src_ignore}
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Project-specific
.ruff_cache/
.mypy_cache/
*.log
'''


def _generate_readme(name: str, ptype: str) -> str:
    """Generate a README.md stub."""
    descriptions = {
        "library": "A Python library providing reusable components.",
        "cli": "A command-line tool for task automation.",
        "web_api": "A FastAPI web application with async support.",
        "minimal": "A Python project.",
    }
    desc = descriptions.get(ptype, descriptions["minimal"])
    return f'''# {name}

{desc}

## Installation

```bash
pip install {name}
```

For development:

```bash
git clone <repo-url>
cd {name}
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
uv pip install -e ".[dev]"
```

## Usage

```python
# Add usage examples here
```

## Development

- Run tests: `pytest`
- Run linter: `ruff check .`
- Run type checker: `mypy .`
- Format code: `ruff format .`
'''


def _generate_dockerfile(name: str, layout: str, ptype: str) -> str:
    """Generate a multi-stage Dockerfile."""
    package_name = name.replace("-", "_")
    entry_point = ""
    if ptype == "web_api":
        entry_point = 'CMD ["uvicorn", f"{package_name}.main:app", "--host", "0.0.0.0", "--port", "8000"]'
    elif ptype == "cli":
        entry_point = f'ENTRYPOINT ["{name}"]'

    copy_src = "COPY src/ src/" if layout == "src" else f"COPY {package_name}/ {package_name}/"

    return f'''# ---- Build Stage ----
FROM python:{_get_py_version_simple("3.11")}-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml README.md ./
{copy_src}
RUN uv pip install --system --no-cache .

# ---- Runtime Stage ----
FROM python:{_get_py_version_simple("3.11")}-slim AS runtime
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY --from=builder /usr/local/lib/python3.*/site-packages /usr/local/lib/python3.*/site-packages
COPY --from=builder /app/src ./src
COPY --from=builder /app/pyproject.toml ./
USER app
EXPOSE 8000
{entry_point or '# Add CMD or ENTRYPOINT'}
'''


def _get_py_version_simple(version: str) -> str:
    """Get a base Python version for Docker images."""
    return version  # Just use the given version


def _generate_dockerignore() -> str:
    """Generate .dockerignore."""
    return '''.venv
__pycache__
*.pyc
.git
.gitignore
.pytest_cache
.mypy_cache
.ruff_cache
dist
build
*.egg-info
.env
.vscode
.idea
'''


def _generate_ci(name: str, py_ver: str) -> str:
    """Generate GitHub Actions CI workflow."""
    return f'''name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["{py_ver}", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{{{ matrix.python-version }}}}
        uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv pip install --system -e ".[dev]"

      - name: Lint with ruff
        run: ruff check .

      - name: Type check with mypy
        run: mypy .

      - name: Test with pytest
        run: pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
'''


def _generate_makefile(name: str) -> str:
    """Generate a Makefile with common targets."""
    return f'''# {name} Makefile
.PHONY: help install test lint format type-check clean build

help:
\t@echo "Available targets:"
\t@echo "  install     Install project and dev dependencies"
\t@echo "  test        Run tests with coverage"
\t@echo "  lint        Run ruff linter"
\t@echo "  format      Format code with ruff"
\t@echo "  type-check  Run mypy type checker"
\t@echo "  clean       Remove build artifacts"
\t@echo "  build       Build distribution packages"
\t@echo "  all         Run format + lint + type-check + test"

install:
\tuv pip install -e ".[dev]"

test:
\tpytest --cov --cov-report=term-missing

lint:
\truff check .

format:
\truff format .

type-check:
\tmypy .

clean:
\tfind . -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true
\tfind . -type f -name "*.pyc" -delete
\trm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info

build:
\tpython -m build

all: format lint type-check test
'''


def _generate_precommit(py_ver: str) -> str:
    """Generate .pre-commit-config.yaml."""
    return f'''repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--python-version={py_ver}]
'''


def _generate_devcontainer(py_ver: str) -> str:
    """Generate devcontainer.json for VS Code."""
    return f'''{{
    "name": "Python {py_ver}",
    "image": "mcr.microsoft.com/devcontainers/python:{py_ver}",
    "features": {{
        "ghcr.io/devcontainers/features/git:1": {{}}
    }},
    "customizations": {{
        "vscode": {{
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "charliermarsh.ruff",
                "ms-python.mypy-type-checker"
            ],
            "settings": {{
                "python.defaultInterpreterPath": ".venv/bin/python",
                "python.testing.pytestEnabled": true,
                "editor.formatOnSave": true,
                "editor.codeActionsOnSave": {{
                    "source.organizeImports": "explicit"
                }}
            }}
        }}
    }},
    "postCreateCommand": "pip install uv && uv pip install -e '.[dev]'"
}}
'''


def _generate_directory_tree(
    name: str, layout: str, package_name: str, extras: list[str]
) -> list[str]:
    """Generate the expected directory tree for the project."""
    dirs = [name]

    if layout == "src":
        dirs.append(f"{name}/src")
        dirs.append(f"{name}/src/{package_name}")
    else:
        dirs.append(f"{name}/{package_name}")

    dirs.append(f"{name}/tests")

    if "ci" in extras:
        dirs.append(f"{name}/.github/workflows")
    if "devcontainer" in extras:
        dirs.append(f"{name}/.devcontainer")

    return dirs
