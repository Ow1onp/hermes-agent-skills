"""
hermes-agent-skills - Production-grade skills for Hermes Agent.

This package provides:
- validator: SKILL.md validation against the Agent Skills open standard
- evolution: Self-evolution engine that analyzes task execution and proposes improvements
- soul_reader: SOUL.md parser for persona-aware skill adaptation
"""

__version__ = "1.0.0"
__author__ = "Ow1onp"

from .validator import SkillValidator, ValidationResult
from .soul_reader import SoulReader, SoulProfile
from .evolution import EvolutionEngine, EvolutionSuggestion

__all__ = [
    "SkillValidator",
    "ValidationResult",
    "SoulReader",
    "SoulProfile",
    "EvolutionEngine",
    "EvolutionSuggestion",
]
