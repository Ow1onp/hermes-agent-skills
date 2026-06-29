"""
Task Orchestrator — converts task_id into an executable plan.

Layer 3 of Hermes v2.

v2.1: Passes ExtractedEntities through to Constraint Engine.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from .task_registry import TaskRegistry, WorkflowStep
from .router import RoutingResult
from .entities import ExtractedEntities
from .constraints import ConstraintEngine


@dataclass
class ExecutionPlan:
    task_id: str
    label: str
    mode: str
    workflow: List[WorkflowStep] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    constraint_prompt: str = ""
    success_criteria: List[str] = field(default_factory=list)
    lang: str = "zh"
    entities: Optional[ExtractedEntities] = None

    @property
    def step_count(self) -> int:
        return len(self.workflow)

    def summary(self) -> str:
        lines = [
            f"Task: {self.label} ({self.task_id})",
            f"Mode: {self.mode}",
            f"Steps: {self.step_count}",
            f"Skills: {', '.join(self.skills) if self.skills else '(none)'}",
        ]
        if self.entities and self.entities.has_any:
            lines.append(f"Entities: {self.entities.to_dict()}")
        return "\n".join(lines)


class TaskOrchestrator:

    def __init__(self, registry=None, constraint_engine=None):
        self.registry = registry or TaskRegistry()
        self.constraints = constraint_engine or ConstraintEngine()

    def plan(self, routing: RoutingResult, user_input: str) -> ExecutionPlan:
        task = self.registry.get(routing.task_id)
        if task is None:
            task = self.registry.get("general")
        if task is None:
            return self._fallback_plan(routing)

        lang = routing.lang
        entities = routing.entities

        constraint_prompt = self.constraints.generate(
            task=task,
            user_input=user_input,
            lang=lang,
            entities=entities,
        )

        return ExecutionPlan(
            task_id=task.task_id,
            label=task.label.get(lang, task.task_id),
            mode=task.default_mode,
            workflow=task.workflow,
            skills=task.required_skills,
            constraint_prompt=constraint_prompt,
            success_criteria=task.success_criteria,
            lang=lang,
            entities=entities,
        )

    def _fallback_plan(self, routing: RoutingResult) -> ExecutionPlan:
        return ExecutionPlan(
            task_id="general",
            label="通用任务" if routing.lang == "zh" else "General Task",
            mode="beginner",
            workflow=[],
            skills=[],
            constraint_prompt="",
            success_criteria=["用户目标已达成"],
            lang=routing.lang,
        )
