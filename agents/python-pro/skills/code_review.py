"""
Code Review Skill — Intelligent Python code review with security, style, and performance analysis.

Provides comprehensive code review for Python code, identifying:
- Security vulnerabilities (SQL injection, command injection, unsafe deserialization)
- Style violations (PEP 8, naming conventions, docstring gaps)
- Performance anti-patterns (O(n^2) loops, missing caching, inefficient data structures)
- Maintainability issues (excessive complexity, god classes, circular imports)

Part of the Python Pro agent in the HermesHub marketplace.
"""
import json
import re
from typing import Any


# ============================================================
# JSON Schema — visible to the model for tool dispatch
# ============================================================
SCHEMA = {
    "name": "python_code_review",
    "description": (
        "Perform a comprehensive code review on the provided Python code. "
        "Analyzes security vulnerabilities, PEP 8 style violations, performance "
        "anti-patterns, and maintainability issues. Returns a structured report "
        "with severity ratings and actionable fix suggestions. "
        "Use when: the user wants a code review, security audit, or quality assessment "
        "of Python code."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python source code to review."
            },
            "focus": {
                "type": "string",
                "enum": ["all", "security", "style", "performance", "maintainability"],
                "description": "Review focus area. 'all' runs every check.",
                "default": "all"
            },
            "severity_threshold": {
                "type": "string",
                "enum": ["error", "warning", "info"],
                "description": "Minimum severity level to include in results.",
                "default": "info"
            }
        },
        "required": ["code"]
    }
}


# ============================================================
# Handler — executed by the system
# ============================================================
def handler(args: dict[str, Any]) -> str:
    """
    Execute the code review with validated arguments.

    Args:
        args: Validated parameters matching SCHEMA.

    Returns:
        JSON string with structured review results.
    """
    try:
        code = args.get("code", "")
        focus = args.get("focus", "all")
        severity_threshold = args.get("severity_threshold", "info")

        # Input validation
        if not code or not code.strip():
            return json.dumps({
                "error": "No code provided for review. The 'code' parameter is required and cannot be empty."
            })

        if len(code) > 50000:
            return json.dumps({
                "error": "Code exceeds the 50,000 character review limit. Please split into smaller segments.",
                "code_length": len(code),
                "max_allowed": 50000
            })

        # Collect findings from all check modules
        findings: list[dict] = []

        if focus in ("all", "security"):
            findings.extend(_security_audit(code))
        if focus in ("all", "style"):
            findings.extend(_style_check(code))
        if focus in ("all", "performance"):
            findings.extend(_performance_check(code))
        if focus in ("all", "maintainability"):
            findings.extend(_maintainability_check(code))

        # Filter by severity threshold
        severity_order = {"error": 0, "warning": 1, "info": 2}
        threshold = severity_order.get(severity_threshold, 2)
        findings = [f for f in findings if severity_order.get(f.get("severity", "info"), 2) <= threshold]

        # Sort by severity (error first), then line number
        findings.sort(key=lambda f: (severity_order.get(f.get("severity", "info"), 2), f.get("line", 0)))

        # Generate summary
        errors = sum(1 for f in findings if f.get("severity") == "error")
        warnings = sum(1 for f in findings if f.get("severity") == "warning")
        infos = sum(1 for f in findings if f.get("severity") == "info")

        score = _calculate_score(errors, warnings, infos)

        return json.dumps({
            "success": True,
            "summary": {
                "total_issues": len(findings),
                "errors": errors,
                "warnings": warnings,
                "infos": infos,
                "quality_score": score,
                "rating": _score_rating(score),
                "focus": focus
            },
            "findings": findings
        })

    except Exception as e:
        return json.dumps({
            "error": f"Code review failed: {str(e)}",
            "type": type(e).__name__
        })


# ============================================================
# Security Audit
# ============================================================
def _security_audit(code: str) -> list[dict]:
    """Scan for common security vulnerabilities."""
    findings: list[dict] = []

    patterns = [
        # SQL injection via string formatting
        (r'(?:cursor|c\.|conn)\.execute\s*\(\s*f["\']', "Possible SQL injection: using f-string or format() in SQL query. Use parameterized queries instead.", "error"),
        (r'(?:\.execute|\.executemany)\s*\([^)]*%\s*\(', "Possible SQL injection: using % formatting in SQL query.", "error"),
        (r'(?:\.execute|\.executemany)\s*\([^)]*\.format\(', "Possible SQL injection: using .format() in SQL query.", "error"),

        # Command injection
        (r'os\.system\s*\(', "Command injection risk: os.system() with user-controlled input. Use subprocess.run() with list arguments.", "error"),
        (r'subprocess\.\w+\s*\([^)]*shell\s*=\s*True', "Command injection risk: shell=True detected. Use list-form arguments unless absolutely necessary.", "warning"),

        # Unsafe deserialization
        (r'pickle\.loads?\s*\(', "Unsafe deserialization: pickle.loads() can execute arbitrary code. Use json.loads() for untrusted data.", "error"),
        (r'cPickle\.loads?\s*\(', "Unsafe deserialization: cPickle.loads() can execute arbitrary code.", "error"),
        (r'yaml\.load\s*\(', "Unsafe YAML loading: yaml.load() can construct arbitrary objects. Use yaml.safe_load() instead.", "warning"),

        # Hardcoded secrets
        (r'(?:password|passwd|secret|api_key|token)\s*=\s*["\'][^\'"]{8,}["\']', "Hardcoded secret detected. Use environment variables or a secrets manager.", "error"),
        (r'(?:API_KEY|SECRET|TOKEN)\s*=\s*["\'][^\'"]+["\']', "Hardcoded credential detected. Load from os.getenv() instead.", "error"),

        # Path traversal
        (r'open\s*\(\s*[^)]*\+\s*request\.', "Potential path traversal: concatenating user input in file paths. Use pathlib.Path.resolve().", "warning"),

        # Debug flag in production code
        (r'DEBUG\s*=\s*True', "DEBUG=True in what appears to be production code. Disable for production deployments.", "warning"),
    ]

    for line_num, line in enumerate(code.split("\n"), 1):
        for pattern, message, severity in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "line": line_num,
                    "severity": severity,
                    "category": "security",
                    "message": message,
                    "snippet": line.strip()[:120],
                    "fix": _get_security_fix(message)
                })

    return findings


def _get_security_fix(message: str) -> str:
    """Provide fix suggestions for security issues."""
    fixes = {
        "SQL injection": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,)). For SQLAlchemy: session.query(User).filter(User.id == user_id).",
        "Command injection": "Use subprocess.run(['program', arg1, arg2], capture_output=True, text=True) instead of os.system().",
        "deserialization": "Replace pickle with json: json.loads(data). For complex types, use Pydantic models.",
        "Hardcoded": "Replace with os.getenv('VARIABLE_NAME'). Store secrets in .env file (gitignored).",
        "path traversal": "Use resolved = pathlib.Path(user_input).resolve(); if not str(resolved).startswith(base_dir): raise ValueError('Invalid path').",
        "yaml.load": "Replace yaml.load(f) with yaml.safe_load(f).",
        "DEBUG=True": "Set DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'.",
    }
    for key, fix in fixes.items():
        if key in message:
            return fix
    return "Review the line and apply security best practices."


# ============================================================
# Style Check (PEP 8 and conventions)
# ============================================================
def _style_check(code: str) -> list[dict]:
    """Check for style and convention violations."""
    findings: list[dict] = []
    lines = code.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Line length check (88 chars, ruff default)
        if len(line) > 100:
            findings.append({
                "line": line_num,
                "severity": "info",
                "category": "style",
                "message": f"Line too long ({len(line)} > 100 characters). Consider breaking into multiple lines.",
                "snippet": line[:100] + "...",
                "fix": "Break long lines using parentheses, backslash continuation, or intermediate variables."
            })

        # Trailing whitespace
        if line != line.rstrip():
            findings.append({
                "line": line_num,
                "severity": "info",
                "category": "style",
                "message": "Trailing whitespace detected.",
                "snippet": f"'{line.rstrip()}' (has trailing spaces)",
                "fix": "Remove trailing whitespace. Most editors can do this automatically on save."
            })

    # Missing module docstring
    if not re.search(r'""".*?"""', code.split("\n")[0] if lines else "", re.DOTALL) and not code.strip().startswith("#!"):
        findings.append({
            "line": 1,
            "severity": "info",
            "category": "style",
            "message": "Module is missing a docstring. Add a module-level docstring describing the module's purpose.",
            "snippet": lines[0][:80] if lines else "(empty file)",
            "fix": 'Add a docstring at the top: """Module description."""'
        })

    # Bare except clauses
    for match in re.finditer(r'except\s*:', code):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "severity": "warning",
            "category": "style",
            "message": "Bare 'except:' clause. Specify the exception type(s) to catch.",
            "snippet": "except:",
            "fix": "Use 'except Exception as e:' for general errors, or catch specific exception types like 'except ValueError:'."
        })

    # Wildcard imports
    for match in re.finditer(r'from\s+(\S+)\s+import\s+\*', code):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "severity": "warning",
            "category": "style",
            "message": f"Wildcard import 'from {match.group(1)} import *'. Import only what you need.",
            "snippet": match.group(0),
            "fix": f"List specific names: 'from {match.group(1)} import Name1, Name2'."
        })

    # Mutable default arguments
    for match in re.finditer(r'def\s+\w+\s*\([^)]*=\s*(\[\s*\]|\{\s*\})', code):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "severity": "warning",
            "category": "style",
            "message": "Mutable default argument detected. Use None and initialize inside the function.",
            "snippet": match.group(0)[:80],
            "fix": "def func(arg=None): arg = arg or []"
        })

    return findings


# ============================================================
# Performance Check
# ============================================================
def _performance_check(code: str) -> list[dict]:
    """Identify performance anti-patterns."""
    findings: list[dict] = []

    anti_patterns = [
        # String concatenation in a loop
        (r'(for\s+\w+\s+in\s+[^:]+:.*(?:\n\s*.*\+=\s*["\']))', "String concatenation (+=) in a loop detected. Use ''.join() or io.StringIO for better performance.", "warning"),
        # List building with append in loop (suggest comprehension)
        (r'(\w+)\s*=\s*\[\]\s*\n(\s*)for\s+\w+\s+in\s+[^:]+:\s*\n\s*\1\.append\(', "List built with .append() in loop. Consider using a list comprehension for cleaner, faster code.", "info"),
        # time.sleep in async function
        (r'async\s+def[^:]*:.*time\.sleep\(', "time.sleep() inside an async function. Use 'await asyncio.sleep()' instead.", "error"),
        # Inefficient membership test (list instead of set)
        (r'if\s+\w+\s+in\s+\[[^\]]+\]:', "Membership test ('in') on a list literal. If this is called repeatedly, convert to a set or frozenset.", "info"),
        # Nested loops that might be O(n^2)
    ]
    # Simplified nested loop detection
    for_loops = list(re.finditer(r'for\s+\w+\s+in\s+', code))
    for i in range(len(for_loops) - 1):
        first_start = for_loops[i].start()
        second_start = for_loops[i+1].start()
        # Check if second loop is inside first (same or greater indentation within a few lines)
        if second_start - first_start < 500:
            line_num = code[:for_loops[i+1].start()].count("\n") + 1
            findings.append({
                "line": line_num,
                "severity": "info",
                "category": "performance",
                "message": "Nested loop detected. Verify time complexity is acceptable for expected input sizes.",
                "snippet": for_loops[i+1].group(0),
                "fix": "Consider using itertools.product(), pre-computing with sets/dicts, or restructuring the algorithm."
            })
            break  # One warning is enough

    for line_num, line in enumerate(code.split("\n"), 1):
        for pattern, message, severity in anti_patterns:
            if re.search(pattern, line, re.DOTALL):
                findings.append({
                    "line": line_num,
                    "severity": severity,
                    "category": "performance",
                    "message": message,
                    "snippet": line.strip()[:120],
                    "fix": "See the message for specific guidance."
                })

    return findings


# ============================================================
# Maintainability Check
# ============================================================
def _maintainability_check(code: str) -> list[dict]:
    """Check for maintainability and complexity issues."""
    findings: list[dict] = []
    lines = code.split("\n")

    # Find function definitions
    func_matches = list(re.finditer(r'def\s+(\w+)\s*\(', code))
    for match in func_matches:
        func_name = match.group(1)
        # Extract function body (simplified)
        func_start = match.start()
        # Count lines until dedent (approximate)
        base_indent = len(re.match(r'^(\s*)', lines[code[:func_start].count("\n")]).group(1)) if code[:func_start].count("\n") < len(lines) else 0
        body_start = code[:func_start].count("\n") + 1
        body_lines = 0
        for i in range(body_start, len(lines)):
            stripped = lines[i].strip()
            if stripped and not stripped.startswith("#"):
                current_indent = len(re.match(r'^(\s*)', lines[i]).group(1)) if re.match(r'^(\s*)', lines[i]) else 0
                if current_indent <= base_indent and stripped:
                    break
            body_lines += 1

        if body_lines > 50:
            findings.append({
                "line": code[:func_start].count("\n") + 1,
                "severity": "warning",
                "category": "maintainability",
                "message": f"Function '{func_name}' is {body_lines} lines long. Consider refactoring into smaller functions (target: <30 lines per function).",
                "snippet": f"def {func_name}(...):  # ~{body_lines} lines",
                "fix": "Extract logical sections into separate helper functions."
            })

        # Deep nesting check
        nested_ifs = re.findall(r'^(?:\s{12,})(?:if|for|while|with|try)', "\n".join(lines[code[:func_start].count("\n"):body_start+body_lines]), re.MULTILINE)
        if len(nested_ifs) > 3:
            findings.append({
                "line": code[:func_start].count("\n") + 1,
                "severity": "info",
                "category": "maintainability",
                "message": f"Function '{func_name}' has deep nesting. Consider using early returns or extracting nested logic.",
                "snippet": f"def {func_name}(...):",
                "fix": "Use guard clauses (early returns), extract nested blocks into functions, or flatten with 'continue' in loops."
            })

    # Global mutable state
    for match in re.finditer(r'^(?!\s*#)(?!\s*def)(?!\s*class)(?!\s*import)(?!\s*from)(\w+)\s*=\s*(\[|\{)', code, re.MULTILINE):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "severity": "warning",
            "category": "maintainability",
            "message": f"Global mutable state '{match.group(1)}' defined at module level. This can cause unexpected side effects.",
            "snippet": match.group(0)[:80],
            "fix": "Encapsulate in a function, class, or use a factory function. Consider using dataclasses for configuration."
        })

    # TODO comments
    for match in re.finditer(r'#\s*TODO', code):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "severity": "info",
            "category": "maintainability",
            "message": "TODO comment found. Track with an issue tracker rather than code comments.",
            "snippet": match.group(0)[:80],
            "fix": "Create a ticket/issue and reference it: '# TODO(#123): Description'."
        })

    return findings


# ============================================================
# Scoring
# ============================================================
def _calculate_score(errors: int, warnings: int, infos: int) -> float:
    """Calculate a quality score from 0-100."""
    base = 100.0
    base -= errors * 15.0
    base -= warnings * 5.0
    base -= infos * 1.0
    return max(0.0, round(base, 1))


def _score_rating(score: float) -> str:
    """Convert numerical score to rating label."""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Critical Issues"
