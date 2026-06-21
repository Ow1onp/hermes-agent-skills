"""
User Modes — detects and dispatches between Beginner, Advanced, and Expert.

Layer entry-point for mode-based routing.

Beginner:  User says "帮我发布" → full-auto
Advanced: User says "用 Release Manager 发布" → partial-auto
Expert:   User writes constraint prompt → passthrough (pure v1)
"""
import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional

from .task_registry import TaskRegistry
from .router import IntentRouter, RoutingResult
from .orchestrator import TaskOrchestrator, ExecutionPlan
from .constraints import ConstraintEngine


class Mode(Enum):
    BEGINNER = "beginner"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class DispatchResult:
    mode: Mode
    plan: Optional[ExecutionPlan] = None
    routing: Optional[RoutingResult] = None
    raw_prompt: Optional[str] = None  # Expert Mode: raw constraint prompt
    message: str = ""                  # User-facing message

    @property
    def is_expert_passthrough(self) -> bool:
        return self.mode == Mode.EXPERT


# Patterns for mode detection
_EXPERT_HEADERS = re.compile(
    r'##\s*(Authority|Mission|Constraints|Success\s*Criteria|Execution\s*Rules)',
    re.IGNORECASE
)

_ADVANCED_PERSONA = re.compile(
    r'(使用|用|as|use|act as|扮演)\b.*'
    r'(Release\s*Manager|Project\s*Manager|Debugger|Code\s*Reviewer|'
    r'Documentation\s*Writer|Launch\s*Commander|Feedback\s*Analyst|'
    r'发布|项目经理|调试|代码审查|文档|发布管理)',
    re.IGNORECASE
)


class ModeRouter:
    """Detects user mode and dispatches to the appropriate pipeline."""

    def __init__(
        self,
        registry: Optional[TaskRegistry] = None,
        router: Optional[IntentRouter] = None,
        orchestrator: Optional[TaskOrchestrator] = None,
    ):
        self.registry = registry or TaskRegistry()
        self.router = router or IntentRouter(self.registry)
        self.orchestrator = orchestrator or TaskOrchestrator(
            self.registry, ConstraintEngine()
        )

    def dispatch(self, user_input: str) -> DispatchResult:
        """Detect mode + route + plan — all in one call."""
        mode = self._detect_mode(user_input)

        if mode == Mode.EXPERT:
            return DispatchResult(
                mode=Mode.EXPERT,
                raw_prompt=user_input,
                message="Expert Mode — executing raw constraint prompt.",
            )

        # Beginner + Advanced: run NL pipeline
        routing = self.router.route(user_input)

        if routing.clarification_needed:
            return DispatchResult(
                mode=mode,
                routing=routing,
                message=routing.clarification_question,
            )

        plan = self.orchestrator.plan(routing, user_input)

        # For Advanced Mode with explicit persona, override the plan's persona
        if mode == Mode.ADVANCED:
            persona_match = _ADVANCED_PERSONA.search(user_input)
            if persona_match and plan.workflow:
                # User specified a persona — respect it
                pass  # The orchestrator already picked the right one

        msg = self._mode_message(mode, plan, routing)
        return DispatchResult(mode=mode, plan=plan, routing=routing, message=msg)

    def _detect_mode(self, text: str) -> Mode:
        """Detect which mode the user is in."""
        if _EXPERT_HEADERS.search(text):
            return Mode.EXPERT
        if _ADVANCED_PERSONA.search(text):
            return Mode.ADVANCED
        return Mode.BEGINNER

    def _mode_message(
        self, mode: Mode, plan: ExecutionPlan, routing: RoutingResult
    ) -> str:
        lang = routing.lang if routing else "zh"
        if lang == "zh":
            labels = {
                Mode.BEGINNER: "🎯 自动模式",
                Mode.ADVANCED: "⚡ 高级模式",
                Mode.EXPERT: "🔧 专家模式",
            }
            return (
                f"{labels.get(mode, '')} — {plan.label}\n"
                f"步骤：{plan.step_count} | 技能：{len(plan.skills)} | "
                f"置信度：{routing.confidence:.0%}"
            )
        return (
            f"{mode.value.title()} Mode — {plan.label}\n"
            f"Steps: {plan.step_count} | Skills: {len(plan.skills)} | "
            f"Confidence: {routing.confidence:.0%}"
        )
