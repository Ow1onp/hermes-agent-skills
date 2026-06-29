"""
Hermes Agent integration checks for repository-provided skills.
"""

import importlib.util
import json
from pathlib import Path

from hermes_agent_skills.validator import SkillValidator


ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_workflow_skills_are_discoverable_by_hermes_layout():
    skills = sorted(
        path
        for path in (ROOT / "skills").rglob("SKILL.md")
        if "agents" not in path.relative_to(ROOT / "skills").parts
    )

    assert len(skills) == 8
    assert {path.parent.name for path in skills} >= {
        "requirement-analyzer",
        "test-driven-dev",
        "code-quality-guardian",
        "cicd-orchestrator",
    }


def test_domain_agents_have_installable_skill_wrappers():
    validator = SkillValidator(strict=False)
    results = validator.validate_directory(ROOT / "skills" / "agents")

    names = {result.frontmatter.get("name") for result in results}
    assert {"python-pro", "devops-sre"} <= names
    assert all(result.valid for result in results)

    for name in ("python-pro", "devops-sre"):
        wrapper = ROOT / "skills" / "agents" / name
        assert (wrapper / "SKILL.md").is_file()
        assert (wrapper / "references" / "persona.md").is_file()
        assert (wrapper / "references" / "memory.md").is_file()
        assert any((wrapper / "scripts").glob("*.py"))


def test_domain_agent_python_handler_can_be_called():
    module = _load_module(ROOT / "skills" / "agents" / "python-pro" / "scripts" / "code_review.py")

    assert module.SCHEMA["name"] == "python_code_review"
    result = json.loads(
        module.handler(
            {
                "code": "password = 'supersecret'\nprint(password)\n",
                "focus": "security",
            }
        )
    )

    assert result["success"] is True
    assert result["summary"]["total_issues"] >= 1


def test_devops_agent_handler_can_be_called():
    module = _load_module(ROOT / "skills" / "agents" / "devops-sre" / "scripts" / "ci_cd_generator.py")

    assert module.SCHEMA["name"] == "devops_ci_cd_generator"
    result = json.loads(
        module.handler(
            {
                "platform": "github_actions",
                "project_type": "python",
                "project_name": "demo",
            }
        )
    )

    assert result["success"] is True
    assert result["filename"] == ".github/workflows/ci.yml"
    assert "name:" in result["config"]
