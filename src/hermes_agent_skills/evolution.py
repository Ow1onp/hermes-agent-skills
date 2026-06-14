"""
Self-evolution engine - analyzes task execution and proposes skill improvements.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class SkillMetrics:
    """Metrics for a single skill's usage and effectiveness."""
    skill_name: str
    use_count_30d: int = 0
    success_rate: float = 1.0
    user_corrections: int = 0
    days_since_last_update: int = 0
    commands_valid: bool = True
    last_used_at: Optional[datetime] = None

    @property
    def health_score(self) -> float:
        scores = []
        usage = min(self.use_count_30d / 10.0, 1.0)
        scores.append(usage * 0.25)
        scores.append(self.success_rate * 0.30)
        correction_score = max(1.0 - self.user_corrections / 5.0, 0.0)
        scores.append(correction_score * 0.25)
        freshness = max(1.0 - self.days_since_last_update / 180.0, 0.0)
        scores.append(freshness * 0.20)
        return sum(scores)

    @property
    def status(self) -> str:
        score = self.health_score
        if score >= 0.8:
            return "healthy"
        elif score >= 0.5:
            return "needs_review"
        elif score >= 0.3:
            return "stale"
        else:
            return "candidate_for_archive"


@dataclass
class EvolutionSuggestion:
    """A concrete suggestion for skill improvement."""
    skill_name: str
    action: str
    reason: str
    old_string: Optional[str] = None
    new_string: Optional[str] = None
    priority: str = "medium"
    estimated_time_saved_minutes: int = 0

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "action": self.action,
            "reason": self.reason,
            "old_string": self.old_string,
            "new_string": self.new_string,
            "priority": self.priority,
            "estimated_time_saved_minutes": self.estimated_time_saved_minutes,
        }


@dataclass
class TaskExecutionRecord:
    """Record of a completed task for analysis."""
    task_description: str
    skills_used: List[str] = field(default_factory=list)
    tool_calls_count: int = 0
    retries: int = 0
    user_corrections: int = 0
    success: bool = True
    duration_seconds: int = 0
    mistakes: List[str] = field(default_factory=list)
    timestamp: Optional[datetime] = None


class EvolutionEngine:
    """Analyzes task execution and proposes skill improvements."""

    def __init__(self, min_tasks_for_analysis: int = 3):
        self.min_tasks = min_tasks_for_analysis
        self._task_history: List[TaskExecutionRecord] = []
        self._skill_metrics: Dict[str, SkillMetrics] = {}

    def record_task(self, record: TaskExecutionRecord) -> None:
        record.timestamp = record.timestamp or datetime.now()
        self._task_history.append(record)

        for skill in record.skills_used:
            if skill not in self._skill_metrics:
                self._skill_metrics[skill] = SkillMetrics(skill_name=skill)
            metrics = self._skill_metrics[skill]
            metrics.use_count_30d += 1
            metrics.last_used_at = record.timestamp
            if not record.success:
                n = metrics.use_count_30d
                metrics.success_rate = (
                    metrics.success_rate * (n - 1) + 0.0
                ) / n
            metrics.user_corrections += record.user_corrections

    def analyze(self) -> List[EvolutionSuggestion]:
        suggestions = []

        if len(self._task_history) < self.min_tasks:
            return suggestions

        suggestions.extend(self._analyze_skill_health())
        suggestions.extend(self._detect_recurring_mistakes())
        suggestions.extend(self._identify_workflow_gaps())

        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 2))
        return suggestions

    def _analyze_skill_health(self) -> List[EvolutionSuggestion]:
        suggestions = []
        for skill_name, metrics in self._skill_metrics.items():
            status = metrics.status
            if status == "candidate_for_archive":
                suggestions.append(EvolutionSuggestion(
                    skill_name=skill_name,
                    action="archive",
                    reason=(
                        f"Skill '{skill_name}' has health {metrics.health_score:.2f}. "
                        f"Used {metrics.use_count_30d}x in 30d, "
                        f"success rate {metrics.success_rate:.0%}."
                    ),
                    priority="low",
                ))
            elif status == "stale":
                suggestions.append(EvolutionSuggestion(
                    skill_name=skill_name,
                    action="patch",
                    reason=f"Skill '{skill_name}' is stale (health: {metrics.health_score:.2f}).",
                    priority="medium",
                ))
            elif status == "needs_review" and metrics.user_corrections > 0:
                suggestions.append(EvolutionSuggestion(
                    skill_name=skill_name,
                    action="patch",
                    reason=(
                        f"Skill '{skill_name}' has {metrics.user_corrections} "
                        f"user corrections. Review for missing steps."
                    ),
                    priority="high",
                ))
        return suggestions

    def _detect_recurring_mistakes(self) -> List[EvolutionSuggestion]:
        suggestions = []
        mistake_counts: Dict[str, int] = {}
        for record in self._task_history:
            for mistake in record.mistakes:
                mistake_counts[mistake] = mistake_counts.get(mistake, 0) + 1

        for mistake, count in mistake_counts.items():
            if count >= 3:
                suggestions.append(EvolutionSuggestion(
                    skill_name="generic",
                    action="create",
                    reason=(
                        f"Mistake '{mistake}' occurred {count} times. "
                        f"Create a skill or pitfall entry to prevent recurrence."
                    ),
                    priority="high",
                    estimated_time_saved_minutes=count * 10,
                ))
        return suggestions

    def _identify_workflow_gaps(self) -> List[EvolutionSuggestion]:
        suggestions = []
        for record in self._task_history:
            if (
                record.retries >= 3
                and len(record.skills_used) == 0
                and record.success
            ):
                suggestions.append(EvolutionSuggestion(
                    skill_name="new_skill",
                    action="create",
                    reason=(
                        f"Task '{record.task_description[:80]}...' "
                        f"needed {record.retries} retries with no skills. "
                        f"Creating a skill could prevent future retries."
                    ),
                    priority="medium",
                    estimated_time_saved_minutes=record.duration_seconds // 60,
                ))
        return suggestions

    def get_metrics_summary(self) -> dict:
        return {
            "total_tasks_analyzed": len(self._task_history),
            "skills_tracked": len(self._skill_metrics),
            "skills": {
                name: {
                    "health_score": round(m.health_score, 2),
                    "status": m.status,
                    "use_count_30d": m.use_count_30d,
                    "success_rate": round(m.success_rate, 2),
                    "user_corrections": m.user_corrections,
                }
                for name, m in self._skill_metrics.items()
            },
        }

    def export_task_history(self) -> List[dict]:
        return [
            {
                "task": r.task_description,
                "skills_used": r.skills_used,
                "tool_calls": r.tool_calls_count,
                "retries": r.retries,
                "corrections": r.user_corrections,
                "success": r.success,
                "duration_s": r.duration_seconds,
                "mistakes": r.mistakes,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in self._task_history
        ]
