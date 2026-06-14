"""
Tests for package initialization and exports.
"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_import_package():
    import hermes_agent_skills
    assert hermes_agent_skills.__version__ == "1.0.0"
    assert hermes_agent_skills.__author__ == "Ow1onp"


def test_import_validator():
    from hermes_agent_skills import SkillValidator, ValidationResult
    assert SkillValidator is not None
    assert ValidationResult is not None


def test_import_soul_reader():
    from hermes_agent_skills import SoulReader, SoulProfile
    assert SoulReader is not None
    assert SoulProfile is not None


def test_import_evolution():
    from hermes_agent_skills import EvolutionEngine, EvolutionSuggestion
    assert EvolutionEngine is not None
    assert EvolutionSuggestion is not None


def test_all_exports_match():
    import hermes_agent_skills
    for name in hermes_agent_skills.__all__:
        assert hasattr(hermes_agent_skills, name), f"{name} not found in package"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
