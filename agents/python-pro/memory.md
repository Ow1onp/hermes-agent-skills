# Python Pro — Domain Memory

## Hard Constraints
- **Python version:** 3.11+ for this runtime. Use `Union[X, Y]` and `Optional[X]` from `typing`, NOT `X | Y` syntax (breaks on Python 3.9 which Hermes may run on in some environments).
- **Linter/Formatter:** `ruff` — replaces black, isort, flake8, pyupgrade. Run `ruff check . && ruff format .` for linting.
- **Package manager:** `uv` (preferred, fast) or `pip`. `uv pip install`, `uv lock`, `uv run`.
- **Build system:** `pyproject.toml` with setuptools or hatchling backend.
- **Virtual environment:** `.venv/` at project root, gitignored.
- **Line ending:** LF (`\n`), not CRLF. Set `.gitattributes` to normalize.

## Security Rules (ALWAYS ENFORCED)
1. **NO hardcoded secrets.** Use `os.getenv("VAR")` or `python-dotenv` for API keys, tokens, passwords.
2. **Input validation everywhere.** Validate and sanitize ALL external input before processing.
3. **SQL injection prevention.** Use parameterized queries (SQLAlchemy bind params, psycopg2 `%s` placeholders). NEVER string-format user input into SQL.
4. **Command injection prevention.** Use `subprocess.run([cmd, arg1, arg2])` with list form, NEVER `os.system()` or string-shell interpolation with user data.
5. **Deserialization safety.** Never use `pickle.loads()` on untrusted data. Use `json.loads()` or `yaml.safe_load()`.
6. **Path traversal prevention.** Use `pathlib.Path.resolve()` and validate paths are within expected directories.
7. **Dependency auditing.** Run `pip-audit` or `uv pip audit` to check for known vulnerabilities.

## Format & Style Rules
- **Docstrings:** Google-style for all public functions/classes. Include Args, Returns, Raises sections.
- **Type hints:** All function signatures. Use `from __future__ import annotations` for forward references.
- **Imports order:** stdlib → third-party → local, each group separated by blank line. `isort` profile: black.
- **Error messages:** Human-readable, actionable. Include what went wrong AND what to do about it.
- **No bare except:** Use `except Exception` or specific exception types. Add logging on catch.

## Ecosystem Knowledge (Current Best Practices)

### Web Frameworks
- **FastAPI** — first choice for new REST APIs. Async-native, auto-docs, Pydantic v2 integration.
- **Django 5.x** — for full-featured apps with ORM, admin, auth. Use async views where beneficial.
- **Flask** — for minimal services, but prefer FastAPI for new projects.

### Data Validation
- **Pydantic v2** — THE standard. `model_validate()`, `model_dump()`, field validators.
- **dataclasses** — for internal DTOs without validation needs.

### ORM & Database
- **SQLAlchemy 2.0+** — async session support, declarative mapping style.
- **Alembic** — migration management.

### Async
- **asyncio** — standard library. `asyncio.gather()`, `asyncio.create_task()`.
- **httpx** — async HTTP client. Replaces requests for async code.
- **anyio** — trio-like structured concurrency on asyncio.

### Testing
- **pytest** — test runner. Fixtures, parametrize, markers.
- **pytest-cov** — coverage reporting. Target >80%.
- **pytest-asyncio** — for async test functions.
- **hypothesis** — property-based testing for complex logic.

### Profiling
- **cProfile + snakeviz** — CPU profiling.
- **memory_profiler** — memory usage.
- **py-spy** — production profiling without code changes.
- **scalene** — combined CPU+memory+GPU profiler.

### Packaging & Publishing
- **pyproject.toml** — single source of truth for build config, dependencies, tool settings.
- **`uv build`** — build wheels and sdists.
- **`uv publish`** — publish to PyPI.

## Anti-Patterns (NEVER RECOMMEND)
- `from module import *` — pollutes namespace.
- Mutable default arguments: `def f(x=[])` — use `None` and initialize inside.
- Catching `Exception` and silently passing.
- `time.sleep()` in async code — use `await asyncio.sleep()`.
- String concatenation in loops — use `"".join()` or `io.StringIO`.
- `os.system()` or `shell=True` with user input.
- Global mutable state in modules.
- Circular imports — restructure or use lazy imports.
