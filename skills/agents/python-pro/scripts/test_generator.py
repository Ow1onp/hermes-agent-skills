"""
Test Generator Skill — Generate pytest test cases from Python function signatures and docstrings.

Analyzes function signatures, type hints, and docstrings to generate comprehensive
pytest test cases covering normal operation, edge cases, and error conditions.

Part of the Python Pro agent in the HermesHub marketplace.
"""
import json
import re
from typing import Any, Optional


# ============================================================
# JSON Schema — visible to the model for tool dispatch
# ============================================================
SCHEMA = {
    "name": "python_test_generator",
    "description": (
        "Generate pytest test cases from Python function code. Analyzes function signatures, "
        "type hints, and docstrings to create comprehensive tests covering: normal inputs, "
        "edge cases (empty strings, None, zero, negative), error conditions, and boundary values. "
        "Returns ready-to-run pytest test functions. "
        "Use when: user needs tests for a function, wants test coverage improvement, "
        "or asks for unit tests."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python function(s) to generate tests for. Can include multiple functions."
            },
            "test_style": {
                "type": "string",
                "enum": ["comprehensive", "minimal", "property_based"],
                "description": "Style of tests to generate. 'comprehensive': normal+edge+error cases. 'minimal': happy path only. 'property_based': adds Hypothesis strategies.",
                "default": "comprehensive"
            },
            "include_imports": {
                "type": "boolean",
                "description": "Whether to include import statements and conftest setup in output.",
                "default": True
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
    Generate pytest test cases from Python function code.

    Args:
        args: Validated parameters matching SCHEMA.

    Returns:
        JSON string with generated test code and metadata.
    """
    try:
        code = args.get("code", "")
        test_style = args.get("test_style", "comprehensive")
        include_imports = args.get("include_imports", True)

        # Input validation
        if not code or not code.strip():
            return json.dumps({
                "error": "No code provided. Please provide the Python function(s) to generate tests for."
            })

        if len(code) > 30000:
            return json.dumps({
                "error": "Code too long for test generation. Limit to 30,000 characters.",
                "code_length": len(code),
                "max_allowed": 30000
            })

        # Parse functions from code
        functions = _parse_functions(code)
        if not functions:
            return json.dumps({
                "error": "No function definitions found in the provided code. Ensure the code contains at least one 'def' statement."
            })

        # Generate tests for each function
        all_tests: list[str] = []
        imports_needed: set[str] = {"pytest"}
        test_count = 0

        for func in functions:
            tests = _generate_tests_for_function(func, test_style)
            all_tests.extend(tests["test_functions"])
            imports_needed.update(tests.get("imports", []))
            test_count += tests["count"]

        # Build complete test file
        test_code = _build_test_file(all_tests, imports_needed, include_imports, test_style)

        return json.dumps({
            "success": True,
            "summary": {
                "functions_analyzed": len(functions),
                "tests_generated": test_count,
                "test_style": test_style,
                "function_names": [f["name"] for f in functions]
            },
            "test_code": test_code,
            "instructions": (
                "Save the test_code to a file (e.g., test_module.py) and run with: "
                "pytest test_module.py -v"
            )
        })

    except Exception as e:
        return json.dumps({
            "error": f"Test generation failed: {str(e)}",
            "type": type(e).__name__
        })


# ============================================================
# Function Parser
# ============================================================
def _parse_functions(code: str) -> list[dict]:
    """Extract function definitions with their signatures and docstrings."""
    functions: list[dict] = []

    pattern = r'''
        def\s+(\w+)\s*          # function name
        \((.*?)\)\s*            # parameters
        (?::\s*(\S+))?\s*       # optional return type
        :\s*\n                  # colon + newline
        ((?:\s+["'][^"']*["']\s*\n)?)  # optional docstring
    '''
    for match in re.finditer(pattern, code, re.VERBOSE | re.DOTALL):
        func_name = match.group(1)
        params_str = match.group(2)
        return_type = match.group(3)
        docstring = match.group(4).strip()

        # Parse parameters
        params = _parse_params(params_str)
        required_params = [p for p in params if p.get("default") is None and p["name"] != "self" and p["name"] != "cls"]

        functions.append({
            "name": func_name,
            "params": params,
            "required_params": required_params,
            "return_type": return_type,
            "docstring": docstring.strip("'\"") if docstring else "",
            "is_async": "async def" in code[match.start():match.start()+match.end()-match.start()+20],
            "has_self": any(p["name"] == "self" for p in params),
            "has_cls": any(p["name"] == "cls" for p in params),
        })

    return functions


def _parse_params(params_str: str) -> list[dict]:
    """Parse function parameters into structured form."""
    if not params_str.strip():
        return []

    params = []
    for part in _split_params(params_str):
        part = part.strip()
        if ":" in part and "=" in part:
            # name: type = default
            name_type, default = part.split("=", 1)
            name, ptype = name_type.split(":", 1)
            params.append({"name": name.strip(), "type": ptype.strip(), "default": default.strip()})
        elif ":" in part:
            name, ptype = part.split(":", 1)
            params.append({"name": name.strip(), "type": ptype.strip(), "default": None})
        elif "=" in part:
            name, default = part.split("=", 1)
            params.append({"name": name.strip(), "type": None, "default": default.strip()})
        else:
            name = part.strip()
            if name in ("*", "**", "/", ""):
                continue
            if name.startswith("**"):
                params.append({"name": name[2:], "type": "dict", "default": None, "is_kwargs": True})
            elif name.startswith("*"):
                params.append({"name": name[1:], "type": "tuple", "default": None, "is_args": True})
            else:
                params.append({"name": name, "type": None, "default": None})

    return params


def _split_params(params_str: str) -> list[str]:
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
# Test Generation Engine
# ============================================================
def _generate_tests_for_function(func: dict, style: str) -> dict:
    """Generate test functions for a single parsed function."""
    tests: list[str] = []
    imports_needed: set[str] = set()

    func_name = func["name"]
    required = func["required_params"]
    is_async = func["is_async"]
    func["has_self"]

    # Determine test prefix
    await_prefix = "await " if is_async else ""
    decorator = "@pytest.mark.asyncio\n    " if is_async else ""

    # Test 1: Happy path — valid inputs
    if required:
        happy_args = _generate_happy_args(required)
        tests.append(f'''
def test_{func_name}_happy_path():
    """Test {func_name} with valid inputs."""
    {decorator}result = {await_prefix}{func_name}({happy_args})
    assert result is not None
''')
        if func.get("return_type") and func["return_type"] != "None":
            tests.append(f'''
def test_{func_name}_returns_correct_type():
    """Test {func_name} returns expected type."""
    {decorator}result = {await_prefix}{func_name}({happy_args})
    assert isinstance(result, _infer_type("{func['return_type']}"))
''')
            imports_needed.add("typing")

    # Test 2: Edge cases
    if style in ("comprehensive", "property_based") and required:
        for param in required:
            pname = param["name"]
            ptype = param.get("type", "")
            ptype_lower = (ptype or "").lower()
            if "str" in ptype_lower:
                # Empty string edge case
                empty_args = _generate_happy_args(required, override={pname: '""'})
                tests.append(f'''
def test_{func_name}_empty_string_{pname}():
    """Test {func_name} with empty string for {pname}."""
    {decorator}result = {await_prefix}{func_name}({empty_args})
    assert result is not None  # Should handle empty strings gracefully
''')
            if "int" in ptype_lower or "float" in ptype_lower or ptype is None:
                # Zero edge case
                zero_args = _generate_happy_args(required, override={pname: "0"})
                tests.append(f'''
def test_{func_name}_zero_{pname}():
    """Test {func_name} with zero value for {pname}."""
    {decorator}result = {await_prefix}{func_name}({zero_args})
    assert result is not None
''')
                # Negative edge case
                neg_args = _generate_happy_args(required, override={pname: "-1"})
                tests.append(f'''
def test_{func_name}_negative_{pname}():
    """Test {func_name} with negative value for {pname}."""
    {decorator}result = {await_prefix}{func_name}({neg_args})
    assert result is not None
''')

    # Test 3: Error condition — missing required params
    if style in ("comprehensive", "property_based") and required:
        first_required = required[0]["name"]
        tests.append(f'''
def test_{func_name}_raises_on_missing_{first_required}():
    """Test {func_name} raises TypeError when required parameter is missing."""
    with pytest.raises(TypeError):
        {await_prefix}{func_name}()  # Missing required arguments
''')

    # Test 4: Property-based (Hypothesis)
    if style == "property_based" and required:
        imports_needed.add("hypothesis")
        strat_lines = ", ".join(
            f"{p['name']}=st.text()" if p.get("type") and "str" in str(p.get("type", "")).lower()
            else f"{p['name']}=st.integers()" if p.get("type") and ("int" in str(p.get("type", "")).lower())
            else f"{p['name']}=st.none() | st.integers()"
            for p in required
        )
        tests.append(f'''
@given({strat_lines})
def test_{func_name}_property_based({", ".join(p["name"] for p in required)}):
    """Property-based test for {func_name}."""
    {decorator}result = {await_prefix}{func_name}({", ".join(p["name"] for p in required)})
    # Add domain-specific invariants here
    assert result is not None
''')

    return {
        "test_functions": tests,
        "count": len(tests),
        "imports": imports_needed
    }


def _generate_happy_args(required_params: list[dict], override: Optional[dict] = None) -> str:
    """Generate reasonable test arguments for required parameters."""
    override = override or {}
    args = []
    for p in required_params:
        pname = p["name"]
        if pname in override:
            args.append(f"{pname}={override[pname]}")
            continue
        ptype_str = str(p.get("type", "")).lower()
        if "str" in ptype_str:
            args.append(f'{pname}="test_{pname}"')
        elif "int" in ptype_str:
            args.append(f"{pname}=42")
        elif "float" in ptype_str:
            args.append(f"{pname}=3.14")
        elif "bool" in ptype_str:
            args.append(f"{pname}=True")
        elif "list" in ptype_str or "dict" in ptype_str:
            args.append(f"{pname}={{\"key\": \"value\"}}" if "dict" in ptype_str else f"{pname}=[1, 2, 3]")
        else:
            args.append(f'{pname}="test_{pname}"')
    return ", ".join(args)


def _infer_type(type_str: str):
    """Convert type annotation string to a Python type for isinstance check."""
    mapping = {
        "str": "str", "int": "int", "float": "float", "bool": "bool",
        "list": "list", "dict": "dict", "tuple": "tuple", "set": "set",
        "bytes": "bytes", "None": "type(None)",
    }
    for key, val in mapping.items():
        if key in type_str:
            return val
    return "object"


# ============================================================
# Test File Builder
# ============================================================
def _build_test_file(tests: list[str], imports_needed: set[str], include_imports: bool, style: str) -> str:
    """Assemble complete test file from generated test functions."""
    lines: list[str] = []

    if include_imports:
        lines.append('"""Auto-generated pytest test cases."""')
        lines.append("import pytest")
        if "typing" in imports_needed:
            lines.append("from typing import Any, Optional")
        if "hypothesis" in imports_needed:
            lines.append("from hypothesis import given, strategies as st")
        lines.append("")
        lines.append("# Import the module under test")
        lines.append("# from your_module import function_name")
        lines.append("")

    for test in tests:
        lines.append(test.strip())

    return "\n\n".join(lines) + "\n"
