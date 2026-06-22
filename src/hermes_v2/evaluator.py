"""
Result Evaluator — validates execution plans before handing off to Execution Layer.

Layer 8 of Hermes v2.

Checks:
  1. Plan completeness (task_id, workflow, skills, constraint_prompt)
  2. Confidence threshold (must be >= clarification threshold)
  3. Entity preservation (user entities in constraint prompt)
  4. Constraint safety (no dangerous/missing constraints)
  5. Beginner mode guard (no role/skill/constraint engineering exposed to user)
"""
from dataclasses import dataclass, field
from typing import List, Optional

from .orchestrator import ExecutionPlan


@dataclass
class EvaluationResult:
    passed: bool
    score: int                # 0–100
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendation: str = ""

    @property
    def is_ready(self) -> bool:
        return self.passed and self.score >= 60


class ResultEvaluator:
    """Validates execution plans before execution."""

    CLARIFY_THRESHOLD = 0.40
    MIN_PROMPT_LENGTH = 50

    def evaluate(self, plan: ExecutionPlan, user_input: str,
                 confidence: float, clarification_needed: bool) -> EvaluationResult:
        issues = []
        warnings = []
        score = 100

        # 1. Plan completeness
        if not plan.task_id or plan.task_id == "?":
            issues.append("No task identified")
            score -= 40
        if not plan.workflow:
            warnings.append("No workflow steps defined")
            score -= 10
        if not plan.constraint_prompt or len(plan.constraint_prompt) < self.MIN_PROMPT_LENGTH:
            issues.append("Constraint prompt too short or missing")
            score -= 30

        # 2. Confidence threshold
        if clarification_needed:
            issues.append(f"Confidence {confidence:.0%} below clarify threshold {self.CLARIFY_THRESHOLD:.0%}")
            score -= 30

        # 3. Entity preservation
        if plan.entities and plan.entities.has_any:
            ents = plan.entities.to_dict()
            for key, value in ents.items():
                if value and str(value) not in plan.constraint_prompt:
                    warnings.append(f"Entity '{key}={value}' not in constraint prompt")
                    score -= 5

        # 4. Safety check
        dangerous = ["rm -rf", "DROP TABLE", "DELETE FROM", "format c:", "del /f"]
        for d in dangerous:
            if d.lower() in plan.constraint_prompt.lower():
                issues.append(f"Dangerous command in prompt: {d}")
                score -= 50

        # 5. Beginner mode guard
        if plan.mode == "beginner":
            expose_words = ["constraint engineering", "约束工程", "write the Authority section"]
            for w in expose_words:
                if w.lower() in plan.constraint_prompt.lower():
                    warnings.append(f"Beginner mode exposes '{w}'")
                    score -= 5

        passed = len(issues) == 0
        recommendation = "READY" if passed and score >= 60 else "NEEDS REVIEW"

        return EvaluationResult(
            passed=passed,
            score=max(score, 0),
            issues=issues,
            warnings=warnings,
            recommendation=recommendation,
        )
