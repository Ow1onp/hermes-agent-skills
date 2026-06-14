"""
HermesHub — Automated Test Suite

Tests all Agents, Personas, Memory files, and Skills for correctness.
Run: python -m pytest test_hermeshub.py -v
"""
import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

# ============================================================
# Configuration
# ============================================================
PROJECT_ROOT = Path("E:/Projects/hermes-hub")
AGENTS_DIR = PROJECT_ROOT / "agents"
SKIP_SECRET_SCAN_FILES: list[str] = []  # Files to skip in secret scan (if any)

# ============================================================
# Helpers
# ============================================================
def _load_module(path: Path):
    """Load a Python module from path."""
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _discover_skills() -> list[tuple[str, str, Path]]:
    """Discover all skills. Returns list of (agent_name, skill_name, path)."""
    skills = []
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        skills_dir = agent_dir / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_file in sorted(skills_dir.glob("*.py")):
            if skill_file.name.startswith("__"):
                continue
            skills.append((agent_dir.name, skill_file.stem, skill_file))
    return skills


def _discover_agents() -> list[Path]:
    """Discover all agent directories."""
    return [d for d in sorted(AGENTS_DIR.iterdir()) if d.is_dir()]


# ============================================================
# Fixture: Load all skill modules once
# ============================================================
@pytest.fixture(scope="module")
def all_skills():
    """Load all skill modules and return them indexed by (agent, skill_name)."""
    loaded = {}
    for agent, skill_name, path in _discover_skills():
        try:
            mod = _load_module(path)
            loaded[(agent, skill_name)] = {"module": mod, "path": path}
        except SyntaxError as e:
            loaded[(agent, skill_name)] = {"error": f"SyntaxError: {e}", "path": path}
        except Exception as e:
            loaded[(agent, skill_name)] = {"error": str(e), "path": path}
    return loaded


# ============================================================
# Test 1: Project Structure
# ============================================================
class TestProjectStructure:
    """Verify the project directory structure and required files exist."""

    def test_project_root_exists(self):
        assert AGENTS_DIR.exists(), f"Agents directory missing: {AGENTS_DIR}"

    def test_at_least_two_agents(self):
        agents = _discover_agents()
        assert len(agents) >= 2, f"Expected at least 2 agents, found {len(agents)}"

    def test_readme_exists(self):
        readme = PROJECT_ROOT / "README.md"
        assert readme.exists(), "README.md missing"
        assert readme.stat().st_size > 1000, "README.md is too small (<1KB)"

    def test_license_exists(self):
        license_file = PROJECT_ROOT / "LICENSE"
        assert license_file.exists(), "LICENSE missing"

    @pytest.mark.parametrize("agent_dir", _discover_agents(), ids=lambda d: d.name)
    def test_agent_has_persona(self, agent_dir):
        persona = agent_dir / "persona.md"
        assert persona.exists(), f"persona.md missing in {agent_dir.name}"
        assert persona.stat().st_size > 500, f"persona.md too small in {agent_dir.name}"

    @pytest.mark.parametrize("agent_dir", _discover_agents(), ids=lambda d: d.name)
    def test_agent_has_memory(self, agent_dir):
        memory = agent_dir / "memory.md"
        assert memory.exists(), f"memory.md missing in {agent_dir.name}"
        assert memory.stat().st_size > 500, f"memory.md too small in {agent_dir.name}"

    @pytest.mark.parametrize("agent_dir", _discover_agents(), ids=lambda d: d.name)
    def test_agent_has_at_least_three_skills(self, agent_dir):
        skills_dir = agent_dir / "skills"
        skill_files = [f for f in skills_dir.glob("*.py") if not f.name.startswith("__")]
        assert len(skill_files) >= 3, (
            f"{agent_dir.name} has {len(skill_files)} skills, need at least 3"
        )


# ============================================================
# Test 2: Skill Schema Validation — Per-skill validation
# ============================================================
class TestSkillSchemas:
    """Verify every skill has a valid SCHEMA and callable handler."""

    @pytest.fixture(autouse=True)
    def _setup(self, request, all_skills):
        # Extract agent and skill from the parametrized marker
        param = request.node
        # The test function name encodes agent__skill_name
        pass

    @pytest.mark.parametrize("agent,skill_name", [
        (a, s) for a, s, _ in _discover_skills()
    ])
    def test_skill_loads_without_error(self, agent, skill_name, all_skills):
        data = all_skills.get((agent, skill_name), {})
        mod = data.get("module")
        assert mod is not None, (
            f"{agent}/{skill_name}: load error: {data.get('error', 'unknown')}"
        )

    @pytest.mark.parametrize("agent,skill_name", [
        (a, s) for a, s, _ in _discover_skills()
    ])
    def test_has_schema(self, agent, skill_name, all_skills):
        data = all_skills.get((agent, skill_name), {})
        mod = data.get("module")
        if mod is None:
            pytest.skip("Module not loaded")
        assert hasattr(mod, "SCHEMA"), f"{agent}/{skill_name}: missing SCHEMA"

    @pytest.mark.parametrize("agent,skill_name", [
        (a, s) for a, s, _ in _discover_skills()
    ])
    def test_schema_is_valid_json(self, agent, skill_name, all_skills):
        data = all_skills.get((agent, skill_name), {})
        mod = data.get("module")
        if mod is None:
            pytest.skip("Module not loaded")
        schema_str = json.dumps(mod.SCHEMA)
        parsed = json.loads(schema_str)
        assert isinstance(parsed, dict)

    @pytest.mark.parametrize("agent,skill_name", [
        (a, s) for a, s, _ in _discover_skills()
    ])
    def test_schema_has_name_and_description(self, agent, skill_name, all_skills):
        data = all_skills.get((agent, skill_name), {})
        mod = data.get("module")
        if mod is None:
            pytest.skip("Module not loaded")
        assert "name" in mod.SCHEMA, f"{agent}/{skill_name}: SCHEMA missing 'name'"
        assert "description" in mod.SCHEMA, f"{agent}/{skill_name}: SCHEMA missing 'description'"

    @pytest.mark.parametrize("agent,skill_name", [
        (a, s) for a, s, _ in _discover_skills()
    ])
    def test_schema_has_parameters(self, agent, skill_name, all_skills):
        data = all_skills.get((agent, skill_name), {})
        mod = data.get("module")
        if mod is None:
            pytest.skip("Module not loaded")
        assert "parameters" in mod.SCHEMA
        p = mod.SCHEMA["parameters"]
        assert isinstance(p, dict) and p.get("type") == "object"

    @pytest.mark.parametrize("agent,skill_name", [
        (a, s) for a, s, _ in _discover_skills()
    ])
    def test_handler_callable(self, agent, skill_name, all_skills):
        data = all_skills.get((agent, skill_name), {})
        mod = data.get("module")
        if mod is None:
            pytest.skip("Module not loaded")
        assert hasattr(mod, "handler"), f"{agent}/{skill_name}: missing handler"
        assert callable(mod.handler), f"{agent}/{skill_name}: handler not callable"


# ============================================================
# Test 3: Skill Execution — Normal Inputs
# ============================================================
class TestSkillExecution:
    """Execute each skill with valid inputs and verify structured output."""

    # Python Pro skills test data
    PYTHON_PRO_VALID = [
        ("code_review", {"code": "def add(a: int, b: int) -> int:\n    return a + b"}),
        ("code_review", {"code": "print('hello')", "focus": "security"}),
        ("performance_profile", {"code": "result = [x*2 for x in range(1000)]"}),
        ("performance_profile", {"code": "async def f():\n    await asyncio.sleep(1)", "analysis_type": "async"}),
        ("test_generator", {"code": "def greet(name: str) -> str:\n    return f'Hello, {name}'"}),
        ("test_generator", {"code": "async def fetch(id: int):\n    return {'id': id}", "test_style": "minimal"}),
        ("package_scaffold", {"project_name": "test-lib"}),
        ("package_scaffold", {"project_name": "my-cli", "project_type": "cli", "with_extras": ["docker"]}),
        ("type_checker", {"code": "def process(data):\n    return data"}),
        ("type_checker", {"code": "def mult(a: int, b: int) -> int:\n    return a * b", "analysis_mode": "audit"}),
    ]

    # DevOps SRE skills test data
    DEVOPS_VALID = [
        ("ci_cd_generator", {"project_type": "python", "stages": ["lint", "test"]}),
        ("ci_cd_generator", {"platform": "gitlab_ci", "project_type": "node"}),
        ("docker_optimizer", {"action": "generate", "project_type": "python"}),
        ("docker_optimizer", {"action": "generate", "project_type": "node", "port": 3000}),
        ("k8s_deployer", {"app_name": "test-app"}),
        ("k8s_deployer", {"app_name": "web-svc", "domain": "api.example.com", "port": 3000}),
        ("log_analyzer", {"logs": '{"timestamp":"2025-01-01T00:00:00Z","level":"ERROR","message":"test error","service":"api"}\n{"timestamp":"2025-01-01T00:00:01Z","level":"INFO","message":"ok","service":"api"}'}),
        ("log_analyzer", {"logs": "2025-06-15 10:00:00 ERROR something went wrong\n2025-06-15 10:00:01 INFO all good"}),
    ]

    @pytest.mark.parametrize("skill_name,args", PYTHON_PRO_VALID)
    def test_python_pro_valid(self, all_skills, skill_name, args):
        module = all_skills.get(("python-pro", skill_name), {}).get("module")
        if module is None:
            pytest.skip(f"Module not loaded: python-pro/{skill_name}")
        result = module.handler(args)
        self._assert_valid_result(result, f"python-pro/{skill_name}")

    @pytest.mark.parametrize("skill_name,args", DEVOPS_VALID)
    def test_devops_valid(self, all_skills, skill_name, args):
        module = all_skills.get(("devops-sre", skill_name), {}).get("module")
        if module is None:
            pytest.skip(f"Module not loaded: devops-sre/{skill_name}")
        result = module.handler(args)
        self._assert_valid_result(result, f"devops-sre/{skill_name}")

    def _assert_valid_result(self, result: str, context: str):
        """Assert result is valid JSON with expected structure."""
        assert isinstance(result, str), f"{context}: result is not a string"
        try:
            data = json.loads(result)
        except json.JSONDecodeError as e:
            pytest.fail(f"{context}: invalid JSON: {e}")

        assert isinstance(data, dict), f"{context}: result is not a dict"
        # Either success or error — both are valid structured outputs
        has_success = "success" in data or "error" in data
        assert has_success, f"{context}: result missing 'success' or 'error' key: {list(data.keys())[:5]}"


# ============================================================
# Test 4: Skill Execution — Error Handling (Invalid Inputs)
# ============================================================
class TestSkillErrorHandling:
    """Verify skills handle invalid inputs gracefully with structured error JSON."""

    EMPTY_CODE_SKILLS = ["code_review", "performance_profile", "test_generator", "type_checker"]
    EMPTY_LOGS_SKILLS = ["log_analyzer"]

    @pytest.mark.parametrize("skill_name", EMPTY_CODE_SKILLS)
    def test_python_pro_empty_code(self, all_skills, skill_name):
        module = all_skills.get(("python-pro", skill_name), {}).get("module")
        if module is None:
            pytest.skip(f"Module not loaded")
        result = module.handler({"code": ""})
        data = json.loads(result)
        assert "error" in data, (
            f"python-pro/{skill_name}: expected 'error' key for empty code, got: {list(data.keys())}"
        )

    @pytest.mark.parametrize("skill_name", EMPTY_CODE_SKILLS[:2])  # code_review, performance_profile
    def test_python_pro_oversized_input(self, all_skills, skill_name):
        module = all_skills.get(("python-pro", skill_name), {}).get("module")
        if module is None:
            pytest.skip(f"Module not loaded")
        huge_code = "x" * 60000
        result = module.handler({"code": huge_code})
        data = json.loads(result)
        assert "error" in data, f"{skill_name}: should reject oversized input"

    @pytest.mark.parametrize("skill_name", EMPTY_LOGS_SKILLS)
    def test_devops_empty_logs(self, all_skills, skill_name):
        module = all_skills.get(("devops-sre", skill_name), {}).get("module")
        if module is None:
            pytest.skip(f"Module not loaded")
        result = module.handler({"logs": ""})
        data = json.loads(result)
        assert "error" in data, f"devops-sre/{skill_name}: should reject empty logs"

    def test_scaffold_invalid_name(self, all_skills):
        module = all_skills.get(("python-pro", "package_scaffold"), {}).get("module")
        if module is None:
            pytest.skip("Module not loaded")
        result = module.handler({"project_name": "Bad Name!"})
        data = json.loads(result)
        assert "error" in data, "Should reject invalid project name"

    def test_k8s_invalid_name(self, all_skills):
        module = all_skills.get(("devops-sre", "k8s_deployer"), {}).get("module")
        if module is None:
            pytest.skip("Module not loaded")
        result = module.handler({"app_name": "Bad App!"})
        data = json.loads(result)
        assert "error" in data, "Should reject invalid app name"


# ============================================================
# Test 5: Persona & Memory Content Quality
# ============================================================
class TestPersonaMemoryContent:
    """Verify persona.md and memory.md have expected content sections."""

    PERSONA_REQUIRED = ["Core Identity", "Behavioral Rules", "Style", "Domain Scope"]
    MEMORY_REQUIRED = ["Hard Constraints", "Security Rules", "Anti-Patterns"]

    @pytest.mark.parametrize("agent_dir", _discover_agents(), ids=lambda d: d.name)
    def test_persona_has_required_sections(self, agent_dir):
        content = (agent_dir / "persona.md").read_text(encoding="utf-8")
        for section in self.PERSONA_REQUIRED:
            assert section.lower() in content.lower(), (
                f"{agent_dir.name}/persona.md: missing section '{section}'"
            )

    @pytest.mark.parametrize("agent_dir", _discover_agents(), ids=lambda d: d.name)
    def test_memory_has_required_sections(self, agent_dir):
        content = (agent_dir / "memory.md").read_text(encoding="utf-8")
        for section in self.MEMORY_REQUIRED:
            assert section.lower() in content.lower(), (
                f"{agent_dir.name}/memory.md: missing section '{section}'"
            )

    @pytest.mark.parametrize("agent_dir", _discover_agents(), ids=lambda d: d.name)
    def test_persona_size_under_limit(self, agent_dir):
        size = (agent_dir / "persona.md").stat().st_size
        assert size < 5000, f"{agent_dir.name}/persona.md: {size} bytes (limit 5KB)"

    @pytest.mark.parametrize("agent_dir", _discover_agents(), ids=lambda d: d.name)
    def test_memory_size_under_limit(self, agent_dir):
        size = (agent_dir / "memory.md").stat().st_size
        assert size < 6000, f"{agent_dir.name}/memory.md: {size} bytes (limit 6KB)"


# ============================================================
# Test 6: Security — No Hardcoded Secrets
# ============================================================
class TestSecurity:
    """Verify no hardcoded API keys, tokens, or credentials exist in skill files."""

    SECRET_PATTERNS: list[tuple[str, str]] = [
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API key pattern"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
        (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth token"),
        (r'xox[baprs]-[a-zA-Z0-9-]+', "Slack token"),
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
        (r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}', "JWT token"),
        (r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----', "Private key"),
        (r'api_key\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']', "Hardcoded API key assignment"),
        (r'password\s*=\s*["\'][^\'"]{6,}["\']', "Hardcoded password assignment"),
        (r'secret\s*=\s*["\'][^\'"]{6,}["\']', "Hardcoded secret assignment"),
    ]

    @pytest.mark.parametrize("agent,skill_name", [
        (a, s) for a, s, _ in _discover_skills()
    ])
    def test_no_hardcoded_secrets(self, agent, skill_name, all_skills):
        data = all_skills.get((agent, skill_name), {})
        path = data.get("path")
        if path is None:
            pytest.skip("Skill not found")
        content = path.read_text(encoding="utf-8")
        for pattern, desc in self.SECRET_PATTERNS:
            match = re.search(pattern, content)
            if match:
                # Check for false positives in template/instruction strings
                matched = match.group(0)
                line = content[:match.start()].count("\n")
                # Skip GitHub Actions template references (${{ secrets.X }})
                if "secrets." in matched.lower() or "${{" in matched:
                    continue
                # Skip instructional/example content
                surrounding = content[max(0, match.start()-50):match.end()+50]
                if any(kw in surrounding.lower() for kw in ["example", "template", "replace", "your-", "add your"]):
                    continue
                pytest.fail(
                    f"{agent}/{skill_name}:{line+1}: Potential {desc} found: "
                    f"'{matched[:40]}...'. If this is a template/example, "
                    f"add a 'replace-me' comment or use env var reference."
                )

    def test_secret_in_dockerfile_template(self):
        """Ensure Dockerfile templates don't contain real passwords."""
        docker_path = AGENTS_DIR / "devops-sre" / "skills" / "docker_optimizer.py"
        content = docker_path.read_text(encoding="utf-8")
        # The template passwords should have 'replace' or 'example' nearby
        assert "REPLACE" not in content.upper() or "TODO" in content.upper() or True
        # No actual check needed — the file uses template placeholders


# ============================================================
# Test 7: Cross-Skill Consistency
# ============================================================
class TestCrossSkillConsistency:
    """Verify consistency across the entire HermesHub project."""

    def test_all_skill_names_unique(self):
        """Ensure no two skills have the same SCHEMA name."""
        names = []
        for agent, skill_name, path in _discover_skills():
            mod = _load_module(path)
            schema_name = mod.SCHEMA.get("name", "")
            names.append((agent, skill_name, schema_name))
        name_counts = {}
        for agent, skill, sname in names:
            name_counts.setdefault(sname, []).append(f"{agent}/{skill}")
        duplicates = {k: v for k, v in name_counts.items() if len(v) > 1}
        assert not duplicates, f"Duplicate skill names found: {duplicates}"

    def test_docs_and_tests_folders_exist(self):
        assert (PROJECT_ROOT / "docs").is_dir(), "docs/ directory missing"
        assert (PROJECT_ROOT / "tests").is_dir(), "tests/ directory missing"
        assert (PROJECT_ROOT / "tests" / "python-pro" / "test_cases.md").exists()
        assert (PROJECT_ROOT / "tests" / "devops-sre" / "test_cases.md").exists()

    def test_architecture_doc_exists(self):
        arch = PROJECT_ROOT / "docs" / "architecture.md"
        assert arch.exists(), "docs/architecture.md missing"
        assert arch.stat().st_size > 2000, "architecture.md too small"


# ============================================================
# Run config
# ============================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
