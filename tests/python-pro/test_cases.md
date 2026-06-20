# Python Pro Agent — Test Cases

> Each skill has 3+ test cases covering normal operation, edge cases, and error handling.

---

## Skill 1: code_review.py

### Test Case 1.1: Normal — Review secure, well-written Python code
**User Intent:** "Review this Python function for issues"
**Input:**
```python
def calculate_average(numbers: list[int]) -> float:
    """Calculate the average of a list of integers."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)
```
**Expected Behavior:**
- Returns `success: true`
- `quality_score` >= 90
- `rating`: "Excellent" or "Good"
- Minimal findings (≤ 2)

**Verification:** No false positives on clean code.

---

### Test Case 1.2: Edge — Code with SQL injection vulnerability
**User Intent:** "Check this code for security issues"
**Input:**
```python
def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()
```
**Expected Behavior:**
- `summary.errors` >= 1
- Finding with `category: "security"` and `severity: "error"`
- `message` mentions "SQL injection" or "parameterized queries"
- `fix` contains actionable guidance

**Verification:** SQL injection detected and flagged as error.

---

### Test Case 1.3: Edge — Empty code input
**User Intent:** "Review this code" (empty input)
**Input:** `""`
**Expected Behavior:**
- Returns error JSON: `{"error": "No code provided for review..."}`

**Verification:** Graceful handling of empty input.

---

### Test Case 1.4: Normal — Focused security-only review
**User Intent:** "Security audit this code"
**Input:**
```python
import pickle
import os

def load_data(filename):
    data = open(filename).read()
    result = pickle.loads(data)
    os.system(f"process {result}")
    return result
```
**Parameters:** `focus: "security"`
**Expected Behavior:**
- Only security-category findings (no style/performance)
- Findings for: pickle.loads, os.system, open without context manager, no input validation
- At least 3 security findings

**Verification:** Security focus mode returns only security issues.

---

### Test Case 1.5: Edge — Long code exceeding limit
**User Intent:** "Review this 60KB Python file"
**Input:** 51,000+ characters of Python code
**Expected Behavior:**
- Returns error: `{"error": "Code exceeds the 50,000 character review limit..."}`

**Verification:** Size limit enforced.

---

## Skill 2: performance_profile.py

### Test Case 2.1: Normal — Analyze function with performance anti-patterns
**Input:**
```python
def process_items(data):
    """Process a list of items."""
    result = ""
    for item in data:
        result += str(item)  # String concatenation in loop
    return result

def fetch_all(ids):
    results = []
    for id in ids:
        results.append(db.execute(f"SELECT * FROM t WHERE id={id}"))  # N+1 queries
    return results
```
**Expected Behavior:**
- String concatenation in loop detected: `pattern: "no_connection_pool"` or related I/O issue
- Multiple `await` or loop query concern flagged
- At least 2 findings

**Verification:** Performance anti-patterns identified.

---

### Test Case 2.2: Normal — CPU analysis detects list comprehension opportunity
**Input:**
```python
result = [x * 2 for x in range(1000000)]  # eager list, could be generator
```
**Expected Behavior:**
- Finding with `pattern: "eager_list_comprehension"`
- Impact >= "medium"
- Suggestion mentions generator expression

**Verification:** Memory optimization suggested.

---

### Test Case 2.3: Edge — Async function with blocking call
**Input:**
```python
import time

async def fetch_data():
    time.sleep(5)  # BLOCKING in async!
    return await some_async_call()
```
**Expected Behavior:**
- Finding with `category: "async"`, `pattern: "blocking_in_async"`
- Impact: "high"
- Message mentions time.sleep() in async function

**Verification:** Async blocking call detected.

---

### Test Case 2.4: Edge — Empty input
**Input:** `""`
**Expected Behavior:**
- Error: `{"error": "No code provided for analysis..."}`

**Verification:** Empty input handled.

---

## Skill 3: test_generator.py

### Test Case 3.1: Normal — Generate tests for a simple function
**Input:**
```python
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b
```
**Expected Behavior:**
- `tests_generated` >= 2
- Test code contains `def test_add_`
- Includes happy path test with `result = add(42, ...)`
- Includes error test with `pytest.raises(TypeError)`

**Verification:** Comprehensive test generation for simple function.

---

### Test Case 3.2: Edge — Function with multiple parameter types
**Input:**
```python
def format_name(first: str, last: str, title: str = "") -> str:
    """Format a full name."""
    return f"{title} {first} {last}".strip()
```
**Expected Behavior:**
- Tests for normal inputs
- Edge case test for empty title (default value)
- Edge case test for empty string first/last

**Verification:** Parameter-aware test generation.

---

### Test Case 3.3: Edge — Async function test generation
**Input:**
```python
async def fetch_user(user_id: int) -> dict:
    """Fetch user by ID."""
    return {"id": user_id}
```
**Expected Behavior:**
- Generated tests use `@pytest.mark.asyncio` decorator
- Uses `await fetch_user(...)` in test
- At least 2 test functions generated

**Verification:** Async test generation correct.

---

### Test Case 3.4: Edge — No function found
**Input:** `x = 1 + 2`
**Expected Behavior:**
- Error: `{"error": "No function definitions found..."}`

**Verification:** Non-function input handled.

---

## Skill 4: package_scaffold.py

### Test Case 4.1: Normal — Generate a Python library scaffold
**Parameters:** `project_name: "my-utils"`, `project_type: "library"`
**Expected Behavior:**
- `success: true`
- `files` contains: `pyproject.toml`, `src/my_utils/__init__.py`, `.gitignore`, `README.md`
- `pyproject.toml` includes `[build-system]`, `[project]`, `[tool.ruff]`, `[tool.pytest.ini_options]`

**Verification:** Complete library scaffold generated.

---

### Test Case 4.2: Normal — CLI project with Docker + CI extras
**Parameters:** `project_name: "my-cli"`, `project_type: "cli"`, `with_extras: ["docker", "ci"]`
**Expected Behavior:**
- `files` contains `Dockerfile`, `.github/workflows/ci.yml`
- `pyproject.toml` has `click>=8.0` dependency
- Dockerfile has multi-stage build and `ENTRYPOINT`

**Verification:** Extras correctly included.

---

### Test Case 4.3: Edge — Invalid project name
**Parameters:** `project_name: "My Project!"`
**Expected Behavior:**
- Error with message about invalid name format
- Suggests correct format

**Verification:** Name validation works.

---

### Test Case 4.4: Edge — Web API with all extras
**Parameters:** `project_name: "my-api"`, `project_type: "web_api"`, `with_extras: ["docker", "ci", "makefile", "pre_commit", "devcontainer"]`
**Expected Behavior:**
- `files` contains all 10+ files
- `pyproject.toml` has `fastapi>=0.110` and `uvicorn>=0.29`
- Makefile has install/test/lint/format/type-check targets
- `.pre-commit-config.yaml` includes ruff, mypy, pre-commit-hooks

**Verification:** Full web API scaffold with all extras.

---

## Skill 5: type_checker.py

### Test Case 5.1: Normal — Audit untyped function
**Input:**
```python
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")
```
**Parameters:** `analysis_mode: "audit"`, `strictness: "strict"`
**Expected Behavior:**
- `summary.untyped` >= 1 or `audit` section has issues
- Finding with `category: "missing_return_type"` or `"missing_param_type"`
- `severity: "warning"` for missing type on `user_id`

**Verification:** Missing type annotations detected with severity.

---

### Test Case 5.2: Normal — Generate annotations for untyped code
**Input:**
```python
def process(data, flag=False):
    if flag:
        return data.upper()
    return data
```
**Parameters:** `analysis_mode: "generate"`, `strictness: "strict"`
**Expected Behavior:**
- `generated.annotations` has at least one suggested annotation
- `annotated_signature` includes type hints for `data` and `flag`

**Verification:** Annotation suggestions generated.

---

### Test Case 5.3: Edge — Pedantic mode flags `Any` usage
**Input:**
```python
from typing import Any

def handle(value: Any) -> Any:
    return value
```
**Parameters:** `analysis_mode: "audit"`, `strictness: "pedantic"`
**Expected Behavior:**
- Findings for `overly_broad_type` on parameter and return type
- Suggests more specific types

**Verification:** Overly broad types flagged in pedantic mode.

---

### Test Case 5.4: Edge — Fully typed code returns minimal issues
**Input:**
```python
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b
```
**Parameters:** `analysis_mode: "audit"`
**Expected Behavior:**
- `summary.fully_typed` >= 1 or `typed_percentage` = 100
- Zero or minimal issues

**Verification:** Clean code passes audit without false positives.

---

### Test Case 5.5: Edge — Invalid code input
**Input:** `""`
**Expected Behavior:**
- Error: `{"error": "No code provided..."}`

**Verification:** Empty input handled gracefully.
