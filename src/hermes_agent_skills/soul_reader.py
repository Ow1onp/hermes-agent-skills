"""
SOUL.md reader - parses Hermes Agent's persona definition file.
"""

import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict

DEFAULT_SOUL = {
    "name": "Default Agent",
    "traits": ["neutral", "professional", "helpful"],
    "coding_style": {
        "naming": "snake_case",
        "max_line_length": 100,
        "prefer": ["type_hints", "docstrings"],
        "avoid": ["magic_numbers", "global_state"],
    },
    "comment_style": "explain why, not what",
    "test_style": "pytest standard",
    "architecture_preference": "layered architecture",
    "commit_style": "conventional commits",
    "tone": "professional",
}


@dataclass
class SoulProfile:
    """Structured representation of an Agent's persona."""
    name: str = "Default Agent"
    traits: List[str] = field(default_factory=list)
    coding_style: Dict = field(default_factory=dict)
    comment_style: str = ""
    test_style: str = ""
    architecture_preference: str = ""
    commit_style: str = ""
    tone: str = "professional"
    raw: Dict = field(default_factory=dict)

    @property
    def is_default(self) -> bool:
        return self.name == "Default Agent" and not self.raw

    @property
    def naming_convention(self) -> str:
        return self.coding_style.get("naming", "snake_case")

    @property
    def prefers_type_hints(self) -> bool:
        return "type_hints" in self.coding_style.get("prefer", [])

    @property
    def comment_density(self) -> str:
        style = self.comment_style.lower()
        if any(w in style for w in ["sparse", "minimal", "none", "稀疏", "无需", "代码即文档"]):
            return "sparse"
        if any(w in style for w in ["detailed", "verbose", "tutorial", "详细", "每个函数"]):
            return "detailed"
        return "moderate"

    def get_code_prompt_hint(self) -> str:
        hints = []
        hints.append(f"Use {self.naming_convention} naming convention.")
        if self.prefers_type_hints:
            hints.append("Always include type hints.")
        hints.append(f"Comment style: {self.comment_style}.")
        hints.append(f"Architecture: {self.architecture_preference}.")
        return " ".join(hints)


class SoulReader:
    """Reads and parses SOUL.md files into SoulProfile objects."""

    DEFAULT_SEARCH_PATHS = [
        "~/.hermes/SOUL.md",
        "./SOUL.md",
        "./.hermes/SOUL.md",
    ]

    def __init__(self, search_paths: Optional[List[str]] = None):
        self.search_paths = search_paths or self.DEFAULT_SEARCH_PATHS

    def find_soul_file(self) -> Optional[Path]:
        for raw_path in self.search_paths:
            path = Path(os.path.expanduser(raw_path)).resolve()
            if path.exists() and path.is_file():
                return path
        return None

    def read(self, path: Optional[str] = None) -> SoulProfile:
        if path is None:
            path = self.find_soul_file()
        else:
            path = Path(path)

        if path is None or not path.exists():
            return self._default_profile()

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return self._default_profile()

        return self._parse(content)

    def _parse(self, content: str) -> SoulProfile:
        profile_data = {}

        if content.startswith("---"):
            body_start = content.find("\n---", 3)
            if body_start != -1:
                try:
                    fm = yaml.safe_load(content[3:body_start])
                    if isinstance(fm, dict):
                        profile_data.update(fm)
                except yaml.YAMLError:
                    pass

        if not profile_data:
            try:
                parsed = yaml.safe_load(content)
                if isinstance(parsed, dict):
                    profile_data = parsed
            except yaml.YAMLError:
                profile_data = self._parse_line_format(content)

        merged = {**DEFAULT_SOUL, **profile_data}

        return SoulProfile(
            name=merged.get("name", "Default Agent"),
            traits=merged.get("traits", []),
            coding_style=merged.get("coding_style", {}),
            comment_style=merged.get("comment_style", ""),
            test_style=merged.get("test_style", ""),
            architecture_preference=merged.get("architecture_preference", ""),
            commit_style=merged.get("commit_style", ""),
            tone=merged.get("tone", "professional"),
            raw=profile_data,
        )

    @staticmethod
    def _parse_line_format(content: str) -> dict:
        result = {}
        for line in content.strip().split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip()
        return result

    def _default_profile(self) -> SoulProfile:
        return SoulProfile(
            name="Default Agent",
            traits=["neutral", "professional", "helpful"],
            coding_style={"naming": "snake_case", "max_line_length": 100, "prefer": ["type_hints"]},
            comment_style="explain why, not what",
            test_style="pytest standard",
            architecture_preference="layered architecture",
            commit_style="conventional commits",
            tone="professional",
        )

    def generate_soul_template(self, persona_type: str = "balanced") -> str:
        templates = {
            "balanced": """---
name: "务实工程师"
traits:
  - pragmatic
  - readable-code-first
  - test-driven
coding_style:
  naming: snake_case
  max_line_length: 100
  prefer:
    - type_hints
    - dataclasses
    - dependency_injection
  avoid:
    - magic_numbers
    - global_state
    - premature_optimization
comment_style: "explain design decisions, not obvious code"
test_style: "pytest with describe/it style"
architecture_preference: "layered (Controller -> Service -> Repository)"
commit_style: "conventional commits (feat/fix/docs/refactor)"
tone: "professional"
---
""",
            "architect": """---
name: "严谨架构师"
traits:
  - type-safety-first
  - explicit-over-implicit
  - defensive-programming
coding_style:
  naming: snake_case
  prefer:
    - exhaustive_type_hints
    - custom_exceptions
    - immutable_data
  avoid:
    - any_type
    - bare_except
    - mutable_global_state
comment_style: "code is documentation; add design notes only when necessary"
test_style: "Given-When-Then BDD style"
architecture_preference: "六边形架构 + CQRS"
commit_style: "conventional commits with detailed body"
tone: "formal"
---
""",
            "pragmatist": """---
name: "敏捷实干家"
traits:
  - fast-iteration
  - good-enough
  - pragmatic
coding_style:
  naming: snake_case
  prefer:
    - type_hints_on_public_api
    - simple_functions
  avoid:
    - over_engineering
    - unnecessary_abstraction
comment_style: "explain why when necessary"
test_style: "pytest concise, cover critical paths"
architecture_preference: "模块化单体 → 按需拆分微服务"
commit_style: "conventional commits, concise"
tone: "casual_professional"
---
""",
        }
        return templates.get(persona_type, templates["balanced"])
