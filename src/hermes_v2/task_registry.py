"""
Task Registry — loads and manages task definitions from YAML.

Each task defines:
  - intent keywords (CN + EN)
  - workflow (ordered personas)
  - required_skills
  - constraints (auto-generated)
  - success_criteria
"""
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

TASKS_DIR = Path(__file__).parent.parent.parent / "tasks"


@dataclass
class WorkflowStep:
    persona: str
    step: str
    description: str


@dataclass
class TaskDefinition:
    task_id: str
    label: Dict[str, str]          # {"zh": "...", "en": "..."}
    description: Dict[str, str]
    keywords_zh: List[str] = field(default_factory=list)
    keywords_en: List[str] = field(default_factory=list)
    workflow: List[WorkflowStep] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    default_mode: str = "beginner"  # beginner | advanced | expert

    @property
    def all_keywords(self) -> List[str]:
        return self.keywords_zh + self.keywords_en


class TaskRegistry:
    """Loads and queries task definitions."""

    def __init__(self, tasks_dir: Optional[Path] = None):
        self._dir = tasks_dir or TASKS_DIR
        self._tasks: Dict[str, TaskDefinition] = {}
        self._load_all()

    def _load_all(self) -> None:
        if not self._dir.exists():
            return
        for yaml_file in sorted(self._dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                td = TaskDefinition(
                    task_id=data["task_id"],
                    label=data.get("label", {}),
                    description=data.get("description", {}),
                    keywords_zh=data.get("intent", {}).get("keywords_zh", []),
                    keywords_en=data.get("intent", {}).get("keywords_en", []),
                    workflow=[
                        WorkflowStep(**ws) for ws in data.get("workflow", [])
                    ],
                    required_skills=data.get("required_skills", []),
                    constraints=data.get("constraints", []),
                    success_criteria=data.get("success_criteria", []),
                    default_mode=data.get("default_mode", "beginner"),
                )
                self._tasks[td.task_id] = td
            except Exception as e:
                print(f"[TaskRegistry] Skipping {yaml_file.name}: {e}")

    def get(self, task_id: str) -> Optional[TaskDefinition]:
        return self._tasks.get(task_id)

    def list_all(self) -> List[TaskDefinition]:
        return list(self._tasks.values())

    def __len__(self) -> int:
        return len(self._tasks)

    def __contains__(self, task_id: str) -> bool:
        return task_id in self._tasks
