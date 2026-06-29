"""
Performance Profiling Skill — Runtime performance analysis and optimization for Python code.

Analyzes performance characteristics of Python code, identifies bottlenecks,
and recommends optimization strategies covering CPU, memory, I/O, and async patterns.

Part of the Python Pro agent in the HermesHub marketplace.
"""
import json
import re
from typing import Any


# ============================================================
# JSON Schema — visible to the model for tool dispatch
# ============================================================
SCHEMA = {
    "name": "python_performance_profile",
    "description": (
        "Analyze Python code for performance characteristics and optimization opportunities. "
        "Covers CPU bottlenecks (O(n) complexity, hot loops), memory issues (object creation, "
        "leaks), I/O patterns (blocking calls, missing caching), and async efficiency. "
        "Use when: user wants performance analysis, optimization advice, or profiling interpretation."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python source code to analyze for performance."
            },
            "analysis_type": {
                "type": "string",
                "enum": ["comprehensive", "cpu", "memory", "io", "async"],
                "description": "Type of performance analysis to run.",
                "default": "comprehensive"
            },
            "context": {
                "type": "string",
                "description": "Optional context about the code: expected input sizes, runtime constraints, deployment environment.",
                "default": ""
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
    Execute performance profiling with validated arguments.

    Args:
        args: Validated parameters matching SCHEMA.

    Returns:
        JSON string with profiling results and optimization recommendations.
    """
    try:
        code = args.get("code", "")
        analysis_type = args.get("analysis_type", "comprehensive")
        context = args.get("context", "")

        # Input validation
        if not code or not code.strip():
            return json.dumps({
                "error": "No code provided for analysis. The 'code' parameter is required."
            })

        if len(code) > 50000:
            return json.dumps({
                "error": "Code exceeds analysis limit. Split into smaller segments.",
                "code_length": len(code),
                "max_allowed": 50000
            })

        # Run selected analyses
        findings: list[dict] = []

        if analysis_type in ("comprehensive", "cpu"):
            findings.extend(_cpu_analysis(code, context))
        if analysis_type in ("comprehensive", "memory"):
            findings.extend(_memory_analysis(code, context))
        if analysis_type in ("comprehensive", "io"):
            findings.extend(_io_analysis(code, context))
        if analysis_type in ("comprehensive", "async"):
            findings.extend(_async_analysis(code, context))

        # Sort by impact (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        findings.sort(key=lambda f: severity_order.get(f.get("impact", "low"), 3))

        # Generate optimization recommendations by category
        by_category: dict[str, list[dict]] = {}
        for f in findings:
            cat = f.get("category", "other")
            by_category.setdefault(cat, []).append(f)

        recommendations = _generate_recommendations(by_category, context)

        return json.dumps({
            "success": True,
            "summary": {
                "total_findings": len(findings),
                "by_impact": {
                    impact: sum(1 for f in findings if f.get("impact") == impact)
                    for impact in ["critical", "high", "medium", "low"]
                },
                "by_category": {cat: len(items) for cat, items in by_category.items()},
                "analysis_type": analysis_type
            },
            "findings": findings,
            "recommendations": recommendations,
            "profiling_tools": _suggest_tools(findings, analysis_type)
        })

    except Exception as e:
        return json.dumps({
            "error": f"Performance profiling failed: {str(e)}",
            "type": type(e).__name__
        })


# ============================================================
# CPU Analysis
# ============================================================
def _cpu_analysis(code: str, context: str) -> list[dict]:
    """Analyze CPU-related performance patterns."""
    findings: list[dict] = []

    # Look for loops that process collections — check for O(n^2) patterns
    lines = code.split("\n")
    loops = []
    for i, line in enumerate(lines, 1):
        if re.match(r'\s*for\s+\w+\s+in\s+', line):
            loops.append(i)

    # Check for list/dict comprehensions that could be generators
    for match in re.finditer(r'\[[^]]*for\s+\w+\s+in\s+[^\]]+\]', code):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "impact": "medium",
            "category": "cpu",
            "pattern": "eager_list_comprehension",
            "description": "List comprehension builds full list in memory. If only iterated once, use a generator expression (parentheses).",
            "snippet": match.group(0)[:100],
            "fix": "Replace [...] with (...) or return a generator. If the result must support indexing, keep the list."
        })

    # Check for repeated function calls in loop conditions
    for match in re.finditer(r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', code):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "impact": "low",
            "category": "cpu",
            "pattern": "range_len_anti_pattern",
            "description": "Using 'range(len(...))' is less Pythonic. Use 'enumerate()' if you need the index, or iterate directly.",
            "snippet": match.group(0),
            "fix": "Use 'for i, item in enumerate(collection):' or 'for item in collection:' directly."
        })

    # Check for function definitions that look like hot-path candidates
    for match in re.finditer(r'def\s+(\w+)\s*\(', code):
        func_name = match.group(1)
        if any(kw in func_name.lower() for kw in ['process', 'handle', 'compute', 'transform', 'convert', 'loop']):
            line_num = code[:match.start()].count("\n") + 1
            findings.append({
                "line": line_num,
                "impact": "low",
                "category": "cpu",
                "pattern": "potential_hot_path",
                "description": f"Function '{func_name}' may be a hot path. Consider profiling with cProfile to confirm.",
                "snippet": match.group(0),
                "fix": "Add @profile decorator (from memory_profiler) or use cProfile: python -m cProfile -s cumulative script.py"
            })

    return findings


# ============================================================
# Memory Analysis
# ============================================================
def _memory_analysis(code: str, context: str) -> list[dict]:
    """Analyze memory-related patterns."""
    findings: list[dict] = []

    # Loading entire file into memory
    for match in re.finditer(r'\.read\s*\(\s*\)', code):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "impact": "high",
            "category": "memory",
            "pattern": "full_file_read",
            "description": "Reading entire file into memory with .read(). For large files, use chunked reading or iterate line by line.",
            "snippet": match.group(0),
            "fix": "Large files: 'for line in file:' (line-by-line). Binary: 'while chunk := f.read(8192):' for chunked reading."
        })

    # Large list creation without generator
    for match in re.finditer(r'(\w+)\s*=\s*\[\s*[^]]*\s+for\s+\w+\s+in\s+', code):
        var_name = match.group(1)
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "impact": "medium",
            "category": "memory",
            "pattern": "large_list_comprehension",
            "description": f"Variable '{var_name}' is a list comprehension that could consume significant memory. Consider a generator if the full list isn't needed at once.",
            "snippet": match.group(0)[:100],
            "fix": "Use () for generator expression, or iterate directly without storing if possible."
        })

    # Object creation in loops (potential GC pressure)
    for match in re.finditer(r'(\w+)\s*=\s*\w+\(\)', code):
        line_num = code[:match.start()].count("\n") + 1
        var_name = match.group(1)
        # Check if inside a loop context (simple heuristic)
        context_start = max(0, line_num - 5)
        surrounding = "\n".join(code.split("\n")[context_start:line_num])
        if re.search(r'\s*for\s+\w+\s+in\s+', surrounding):
            findings.append({
                "line": line_num,
                "impact": "medium",
                "category": "memory",
                "pattern": "object_in_loop",
                "description": f"Variable '{var_name}' created inside a loop. Frequent object creation causes GC pressure. Consider reusing objects or moving allocation outside the loop.",
                "snippet": match.group(0),
                "fix": "Move object creation outside the loop, or use an object pool/flyweight pattern for hot paths."
            })
            break  # One example is sufficient

    return findings


# ============================================================
# I/O Analysis
# ============================================================
def _io_analysis(code: str, context: str) -> list[dict]:
    """Analyze I/O patterns."""
    findings: list[dict] = []

    # File open without context manager
    for match in re.finditer(r'(\w+)\s*=\s*open\s*\(', code):
        line_num = code[:match.start()].count("\n") + 1
        match.group(1)
        # Check if 'with' is used
        before = code[:match.start()].split("\n")[-1]
        if "with " not in before:
            findings.append({
                "line": line_num,
                "impact": "high",
                "category": "io",
                "pattern": "open_without_context_manager",
                "description": "File opened without 'with' statement. File may not close properly on exceptions, leaking file descriptors.",
                "snippet": match.group(0),
                "fix": "Use 'with open(path) as f:' for automatic cleanup."
            })

    # Multiple single-row DB queries (N+1 pattern)
    n_plus_one = re.findall(r'\.execute\s*\(', code)
    if len(n_plus_one) > 2:
        # Check if they're inside a loop
        loop_queries = 0
        for match in re.finditer(r'\.execute\s*\(', code):
            before = code[:match.start()].split("\n")
            # Check last 10 lines for a for-loop
            recent = "\n".join(before[-10:])
            if re.search(r'\s*for\s+\w+\s+in\s+', recent):
                loop_queries += 1
        if loop_queries > 0:
            findings.append({
                "line": 1,
                "impact": "critical",
                "category": "io",
                "pattern": "possible_n_plus_one",
                "description": f"Database queries ({loop_queries}) detected inside loops. This may indicate an N+1 query pattern causing excessive I/O.",
                "snippet": "Multiple .execute() calls in loop context",
                "fix": "Use JOIN queries, batch fetching (WHERE id IN (...)), or an ORM with eager loading (selectinload, joinedload)."
            })

    # HTTP requests without connection pooling
    for match in re.finditer(r'(?:requests|urllib)\.(?:get|post|put|delete)\s*\(', code):
        line_num = code[:match.start()].count("\n") + 1
        findings.append({
            "line": line_num,
            "impact": "medium",
            "category": "io",
            "pattern": "no_connection_pool",
            "description": "HTTP request without connection pooling. Each request creates a new TCP connection.",
            "snippet": match.group(0),
            "fix": "Use requests.Session() for connection reuse, or httpx.AsyncClient() for async. Set pool_connections and pool_maxsize."
        })

    # Missing caching for expensive operations
    if re.search(r'(?:\.get\(|fetch|query|compute|calculate)', code) and not re.search(r'(?:lru_cache|cache|cached|memoize)', code):
        findings.append({
            "line": 1,
            "impact": "medium",
            "category": "io",
            "pattern": "missing_caching",
            "description": "Expensive operations (fetch/compute) detected without caching. Consider adding caching for repeated calls.",
            "snippet": "No @lru_cache or caching pattern found in code with expensive operations.",
            "fix": "Use @functools.lru_cache(maxsize=128) for pure functions, or @cache for unlimited cache. For external data, consider Redis or in-memory TTL cache."
        })

    return findings


# ============================================================
# Async Analysis
# ============================================================
def _async_analysis(code: str, context: str) -> list[dict]:
    """Analyze async/await patterns."""
    findings: list[dict] = []

    # Blocking calls in async functions
    if "async def" in code:
        blocking_patterns = [
            (r'time\.sleep\s*\(', "time.sleep() in async function. Use 'await asyncio.sleep()'."),
            (r'requests\.(?:get|post|put|delete)\s*\(', "Blocking requests.get() in async function. Use 'await httpx.AsyncClient().get()'."),
            (r'open\s*\(', "Blocking open() in async function. Use 'aiofiles.open()' for async file I/O."),
        ]
        for pattern, msg in blocking_patterns:
            if re.search(pattern, code):
                line_num = code[:re.search(pattern, code).start()].count("\n") + 1
                findings.append({
                    "line": line_num,
                    "impact": "high",
                    "category": "async",
                    "pattern": "blocking_in_async",
                    "description": msg,
                    "snippet": re.search(pattern, code).group(0),
                    "fix": "Use async equivalents: asyncio.sleep(), httpx.AsyncClient, aiofiles."
                })

    # asyncio.gather() opportunity
    if "await " in code and "asyncio.gather" not in code:
        # Check for sequential awaits that could be parallelized
        awaits = list(re.finditer(r'await\s+(\w+)\s*\(', code))
        if len(awaits) >= 2:
            findings.append({
                "line": code[:awaits[1].start()].count("\n") + 1,
                "impact": "medium",
                "category": "async",
                "pattern": "sequential_await",
                "description": "Multiple independent awaits detected. Consider using asyncio.gather() for concurrent execution.",
                "snippet": f"Sequential awaits: {', '.join(m.group(1) for m in awaits[:3])}",
                "fix": "tasks = [coro1(), coro2()]; results = await asyncio.gather(*tasks)"
            })

    # asyncio.create_task() not used for fire-and-forget
    if "asyncio.gather" in code and "create_task" not in code:
        findings.append({
            "line": 1,
            "impact": "low",
            "category": "async",
            "pattern": "missing_create_task",
            "description": "Consider asyncio.create_task() for fire-and-forget coroutines that don't need immediate results.",
            "snippet": "asyncio.gather() used without create_task",
            "fix": "task = asyncio.create_task(coroutine()); # runs in background; await when needed"
        })

    return findings


# ============================================================
# Recommendations & Tool Suggestions
# ============================================================
def _generate_recommendations(by_category: dict[str, list[dict]], context: str) -> list[dict]:
    """Generate prioritized optimization recommendations."""
    recs: list[dict] = []

    priority_order = ["io", "async", "memory", "cpu"]
    for category in priority_order:
        items = by_category.get(category, [])
        if not items:
            continue

        critical = [i for i in items if i.get("impact") == "critical"]
        high = [i for i in items if i.get("impact") == "high"]

        if critical or high:
            recs.append({
                "priority": "immediate",
                "category": category,
                "action": f"Fix {len(critical + high)} {category.upper()} issues first",
                "details": [i["description"] for i in critical + high][:3]
            })

    # Add a general recommendations section
    recs.append({
        "priority": "general",
        "category": "all",
        "action": "Run profiling tools to validate findings",
        "details": [
            "1. CPU: cProfile + snakeviz for call-graph visualization",
            "2. Memory: memory_profiler for line-by-line memory usage",
            "3. I/O: py-spy for production profiling without code changes",
            "4. Async: pytest-asyncio with --log-cli-level=DEBUG"
        ]
    })

    return recs


def _suggest_tools(findings: list[dict], analysis_type: str) -> list[str]:
    """Suggest profiling tools based on findings."""
    tools: set[str] = set()

    categories = {f.get("category") for f in findings}
    {f.get("impact") for f in findings}

    if "cpu" in categories:
        tools.update(["cProfile", "snakeviz", "py-spy", "scalene"])
    if "memory" in categories:
        tools.update(["memory_profiler", "objgraph", "tracemalloc"])
    if "io" in categories:
        tools.update(["py-spy", "strace (Linux)", "httpx logging"])
    if "async" in categories:
        tools.update(["asyncio debug mode", "pytest-asyncio"])

    if not tools:
        tools.add("cProfile")  # Default recommendation

    return sorted(tools)
