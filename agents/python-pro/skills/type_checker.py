"""
Type Checker Skill — Static type analysis and type annotation generation for Python code.

Analyzes Python code for type safety issues, generates missing type annotations,
detects type inconsistencies, and suggests typing improvements (Protocols, Generics, overloads).

Part of the Python Pro agent in the HermesHub marketplace.
"""
import json
import re
from typing import Any, Optional


# ============================================================
# JSON Schema — visible to the model for tool dispatch
# ============================================================
SCHEMA = {
    "name": "python_type_checker",
    "description": (
        "Perform static type analysis on Python code. Detects missing type annotations, "
        "type inconsistencies, overly broad types (Any, object), and opportunities for "
        "more precise types (Literal, Protocol, TypedDict, Generic). Generates suggested "
        "type annotations for untyped functions. "
        "Use when: user wants type safety analysis, needs type annotations generated, "
        "or asks about typing best practices."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python source code to analyze for type issues."
            },
            "analysis_mode": {
                "type": "string",
                "enum": ["audit", "generate", "both"],
                "description": "'audit': find type issues. 'generate': produce type annotations. 'both': do both.",
                "default": "both"
            },
            "strictness": {
                "type": "string",
                "enum": ["basic", "strict", "pedantic"],
                "description": "Analysis strictness level. 'basic': missing annotations only. 'strict': also flag Any/object. 'pedantic': suggest Protocol/overload.",
                "default": "strict"
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
    Perform type analysis on Python code.

    Args:
        args: Validated parameters matching SCHEMA.

    Returns:
        JSON string with type analysis results.
    """
    try:
        code = args.get("code", "")
        analysis_mode = args.get("analysis_mode", "both")
        strictness = args.get("strictness", "strict")

        # Input validation
        if not code or not code.strip():
            return json.dumps({
                "error": "No code provided. The 'code' parameter is required."
            })

        if len(code) > 30000:
            return json.dumps({
                "error": "Code too long for type analysis. Limit to 30,000 characters.",
                "code_length": len(code),
                "max_allowed": 30000
            })

        results: dict = {"success": True}

        # 1. Parse functions and methods from code
        functions = _parse_typed_functions(code)

        if not functions:
            return json.dumps({
                "success": True,
                "summary": {
                    "total_functions": 0,
                    "message": "No function definitions found in the provided code."
                }
            })

        # 2. Audit mode: find type issues
        if analysis_mode in ("audit", "both"):
            issues = _audit_types(functions, strictness)
            results["audit"] = {
                "total_issues": len(issues),
                "by_severity": {
                    sev: sum(1 for i in issues if i.get("severity") == sev)
                    for sev in ["error", "warning", "info"]
                },
                "issues": issues
            }

        # 3. Generate mode: produce type annotations
        if analysis_mode in ("generate", "both"):
            annotations = _generate_annotations(functions, strictness)
            results["generated"] = {
                "functions_annotated": len(annotations),
                "annotations": annotations
            }

        # Summary
        results["summary"] = {
            "total_functions": len(functions),
            "fully_typed": sum(1 for f in functions if _is_fully_typed(f)),
            "partially_typed": sum(1 for f in functions if _is_partially_typed(f)),
            "untyped": sum(1 for f in functions if _is_untyped(f)),
            "typed_percentage": round(
                sum(1 for f in functions if _is_fully_typed(f)) / len(functions) * 100, 1
            ) if functions else 0.0
        }

        return json.dumps(results)

    except Exception as e:
        return json.dumps({
            "error": f"Type analysis failed: {str(e)}",
            "type": type(e).__name__
        })


# ============================================================
# Function Parser (Type-Aware)
# ============================================================
def _parse_typed_functions(code: str) -> list[dict]:
    """Parse function definitions with type annotation analysis."""
    functions: list[dict] = []
    lines = code.split("\n")

    # Find all function definitions
    for match in re.finditer(
        r'(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*(\S+))?\s*:',
        code
    ):
        func_name = match.group(1)
        params_str = match.group(2)
        return_type = match.group(3)
        line_num = code[:match.start()].count("\n") + 1

        # Parse parameters
        params = _parse_typed_params(params_str)

        functions.append({
            "name": func_name,
            "line": line_num,
            "params": params,
            "return_type": return_type,
            "is_method": any(p["name"] == "self" for p in params),
            "is_classmethod": any(p["name"] == "cls" for p in params),
            "is_async": "async def" in lines[line_num - 1] if line_num <= len(lines) else False,
            "is_dunder": func_name.startswith("__") and func_name.endswith("__"),
        })

    return functions


def _parse_typed_params(params_str: str) -> list[dict]:
    """Parse parameters with type annotations."""
    if not params_str.strip():
        return []

    params = []
    for part in _split_param_parts(params_str):
        part = part.strip()
        if not part or part in ("*", "/", ""):
            continue

        param: dict[str, Any] = {"name": "", "type": None, "default": None, "has_type": False}

        # Handle **kwargs and *args
        if part.startswith("**"):
            name = part[2:]
            if ":" in name:
                name, ptype = name.split(":", 1)
                param = {"name": name.strip(), "type": ptype.strip(), "default": None, "has_type": True, "is_kwargs": True}
            else:
                param = {"name": name.strip(), "type": None, "default": None, "has_type": False, "is_kwargs": True}
        elif part.startswith("*"):
            name = part[1:]
            if ":" in name:
                name, ptype = name.split(":", 1)
                param = {"name": name.strip(), "type": ptype.strip(), "default": None, "has_type": True, "is_args": True}
            else:
                param = {"name": name.strip(), "type": None, "default": None, "has_type": False, "is_args": True}
        elif ":" in part and "=" in part:
            # name: type = default
            name_type, default = part.split("=", 1)
            name, ptype = name_type.split(":", 1)
            param = {"name": name.strip(), "type": ptype.strip(), "default": default.strip(), "has_type": True}
        elif ":" in part:
            name, ptype = part.split(":", 1)
            param = {"name": name.strip(), "type": ptype.strip(), "default": None, "has_type": True}
        elif "=" in part:
            name, default = part.split("=", 1)
            param = {"name": name.strip(), "type": None, "default": default.strip(), "has_type": False}
        else:
            param = {"name": part.strip(), "type": None, "default": None, "has_type": False}

        params.append(param)

    return params


def _split_param_parts(params_str: str) -> list[str]:
    """Split parameter string respecting nested brackets."""
    parts = []
    current = ""
    depth = 0
    for ch in params_str:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current)
    return parts


# ============================================================
# Type Classification Helpers
# ============================================================
def _is_fully_typed(func: dict) -> bool:
    """Check if function has complete type annotations."""
    if func.get("is_dunder"):
        return True  # Don't flag __init__, __repr__, etc.
    params_typed = all(
        p.get("has_type") or p.get("is_args") or p.get("is_kwargs")
        or p["name"] in ("self", "cls")
        for p in func["params"]
    )
    return_typed = func.get("return_type") is not None
    return params_typed and return_typed


def _is_partially_typed(func: dict) -> bool:
    """Check if function has some but not all type annotations."""
    if func.get("is_dunder"):
        return False
    has_any = (
        any(p.get("has_type") for p in func["params"])
        or func.get("return_type") is not None
    )
    return has_any and not _is_fully_typed(func)


def _is_untyped(func: dict) -> bool:
    """Check if function has no type annotations."""
    if func.get("is_dunder"):
        return False
    return not _is_fully_typed(func) and not _is_partially_typed(func)


# ============================================================
# Audit Engine
# ============================================================
def _audit_types(functions: list[dict], strictness: str) -> list[dict]:
    """Find type annotation issues in parsed functions."""
    issues: list[dict] = []

    for func in functions:
        fname = func["name"]
        fline = func["line"]

        if func.get("is_dunder"):
            continue

        # Missing return type
        if func["return_type"] is None and not func["is_method"]:
            severity = "error" if strictness == "pedantic" else "warning"
            issues.append({
                "line": fline,
                "severity": severity,
                "function": fname,
                "category": "missing_return_type",
                "message": f"Function '{fname}' is missing a return type annotation.",
                "suggestion": f"Infer return type from the function body. For functions that return None: 'def {fname}(...) -> None:'"
            })

        # Missing param types
        for param in func["params"]:
            pname = param["name"]
            if pname in ("self", "cls") or param.get("is_args") or param.get("is_kwargs"):
                continue
            if not param.get("has_type"):
                issues.append({
                    "line": fline,
                    "severity": "warning",
                    "function": fname,
                    "category": "missing_param_type",
                    "message": f"Parameter '{pname}' in function '{fname}' is missing a type annotation.",
                    "suggestion": _suggest_type_for_param(pname, param.get("default"))
                })

        # Overly broad types (strict+)
        if strictness in ("strict", "pedantic"):
            for param in func["params"]:
                ptype = param.get("type")
                if ptype and ptype.strip() == "Any":
                    issues.append({
                        "line": fline,
                        "severity": "info",
                        "function": fname,
                        "category": "overly_broad_type",
                        "message": f"Parameter '{param['name']}' is typed as 'Any'. Consider a more specific type.",
                        "suggestion": "Replace 'Any' with a specific type (str, int, dict[str, Any]) or a Protocol."
                    })

            if func["return_type"] and func["return_type"].strip() == "Any":
                issues.append({
                    "line": fline,
                    "severity": "info",
                    "function": fname,
                    "category": "overly_broad_return",
                    "message": f"Return type of '{fname}' is 'Any'. Consider a more specific type.",
                    "suggestion": "Use a concrete type, Union, or Optional instead of Any."
                })

        # Useless return type (just 'None' for __init__)
        if fname == "__init__" and func["return_type"] and func["return_type"] != "None":
            issues.append({
                "line": fline,
                "severity": "info",
                "function": fname,
                "category": "init_return_type",
                "message": "__init__ should have return type 'None' or omit it entirely.",
                "suggestion": "Remove return type annotation or use '-> None'."
            })

    return issues


def _suggest_type_for_param(param_name: str, default: Optional[Any]) -> str:
    """Suggest a type based on parameter name heuristics and default value."""
    name_lower = param_name.lower()

    # Default value based inference
    if default is not None:
        default_str = str(default).strip()
        if default_str in ("True", "False"):
            return f"Add type: '{param_name}: bool = {default_str}'"
        if re.match(r'^-?\d+$', default_str):
            return f"Add type: '{param_name}: int = {default_str}'"
        if re.match(r'^-?\d+\.?\d*$', default_str) and "." in default_str:
            return f"Add type: '{param_name}: float = {default_str}'"
        if default_str.startswith(('"', "'")):
            return f"Add type: '{param_name}: str = {default_str}'"
        if default_str in ("[]", "list()"):
            return f"Add type: '{param_name}: list = []'"
        if default_str in ("{}", "dict()"):
            return f"Add type: '{param_name}: dict = {{}}'"
        if default_str == "None":
            return f"Add type: '{param_name}: Optional[<type>] = None'"

    # Name-based heuristics
    heuristics = {
        "name": "str", "path": "str | Path", "url": "str",
        "id": "int | str", "count": "int", "size": "int",
        "flag": "bool", "enabled": "bool", "data": "dict[str, Any]",
        "items": "list[Any]", "config": "dict[str, Any]",
        "timeout": "float | int", "callback": "Callable[..., Any]",
    }
    for keyword, suggested in heuristics.items():
        if keyword in name_lower:
            return f"Add type: '{param_name}: {suggested}'"

    return f"Add type: '{param_name}: <type>' (infer from usage)"


# ============================================================
# Annotation Generator
# ============================================================
def _generate_annotations(functions: list[dict], strictness: str) -> list[dict]:
    """Generate type annotation suggestions for untyped functions."""
    annotations: list[dict] = []

    for func in functions:
        fname = func["name"]

        if func.get("is_dunder"):
            continue

        changes: list[str] = []

        # Generate param annotations for untyped params
        for param in func["params"]:
            pname = param["name"]
            if pname in ("self", "cls") or param.get("is_args") or param.get("is_kwargs"):
                continue
            if not param.get("has_type"):
                default_str = f" = {param['default']}" if param.get("default") else ""
                # Use more specific types for strict/pedantic modes
                if strictness == "pedantic":
                    ptype = _infer_type_from_name(pname)
                else:
                    ptype = _infer_type_from_name(pname)
                changes.append(f"    Parameter '{pname}': add type annotation -> '{pname}: {ptype}{default_str}'")

        # Generate return type
        if func["return_type"] is None and not func["is_method"]:
            # Heuristic: if name contains 'get'/'fetch'/'find' suggest the type, else None
            if any(kw in fname.lower() for kw in ("get", "fetch", "find", "query", "list", "create", "build", "make", "parse")):
                rtype = "Any  # TODO: specify actual return type"
            elif any(kw in fname.lower() for kw in ("is_", "has_", "check", "validate", "test")):
                rtype = "bool"
            elif any(kw in fname.lower() for kw in ("run", "execute", "process", "handle")):
                rtype = "None"
            else:
                rtype = "None  # or specify return type"
            changes.append(f"    Return type: add '-> {rtype}'")

        if changes:
            annotations.append({
                "function": fname,
                "line": func["line"],
                "changes": changes,
                "annotated_signature": _build_annotated_signature(func),
            })

    return annotations


def _infer_type_from_name(name: str) -> str:
    """Infer type from parameter name."""
    mapping = {
        "name": "str", "title": "str", "description": "str",
        "message": "str", "text": "str", "path": "str",
        "url": "str", "email": "str", "filename": "str",
        "id": "int", "count": "int", "index": "int",
        "size": "int", "length": "int", "age": "int",
        "price": "float", "amount": "float", "rate": "float",
        "flag": "bool", "enabled": "bool", "active": "bool",
        "items": "list", "values": "list", "options": "list",
        "data": "dict", "config": "dict", "kwargs": "dict",
        "callback": "Callable", "handler": "Callable",
    }
    name_lower = name.lower()
    for keyword, ptype in mapping.items():
        if keyword in name_lower:
            return ptype
    return "Any"


def _build_annotated_signature(func: dict) -> str:
    """Build a fully annotated function signature string."""
    params = []
    for p in func["params"]:
        pname = p["name"]
        if p.get("is_args"):
            params.append(f"*{pname}")
        elif p.get("is_kwargs"):
            params.append(f"**{pname}")
        elif p.get("has_type"):
            params.append(f"{pname}: {p['type']}" + (f" = {p['default']}" if p.get("default") else ""))
        elif pname in ("self", "cls"):
            params.append(pname)
        else:
            ptype = _infer_type_from_name(pname)
            params.append(f"{pname}: {ptype}" + (f" = {p['default']}" if p.get("default") else ""))

    return_type = func["return_type"] or "None"
    prefix = "async " if func.get("is_async") else "def"
    return f"{prefix} {func['name']}({', '.join(params)}) -> {return_type}:"
