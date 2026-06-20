"""
Tests for the self-evolution engine.
"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hermes_agent_skills.evolution import (
    EvolutionEngine, EvolutionSuggestion,
    SkillMetrics, TaskExecutionRecord,
)


# ── Fixtures ────────────────────────────────────────────────


def make_record(
    desc="test task",
    skills=None,
    retries=0,
    corrections=0,
    success=True,
    duration=60,
    mistakes=None,
):
    return TaskExecutionRecord(
        task_description=desc,
        skills_used=skills or [],
        tool_calls_count=10,
        retries=retries,
        user_corrections=corrections,
        success=success,
        duration_seconds=duration,
        mistakes=mistakes or [],
    )


# ── SkillMetrics tests ──────────────────────────────────────


def test_skill_metrics_health_healthy():
    m = SkillMetrics(
        skill_name="test-skill",
        use_count_30d=10,
        success_rate=1.0,
        user_corrections=0,
        days_since_last_update=5,
    )
    assert m.status == "healthy"
    assert m.health_score >= 0.8


def test_skill_metrics_health_stale():
    m = SkillMetrics(
        skill_name="old-skill",
        use_count_30d=1,
        success_rate=0.5,
        user_corrections=3,
        days_since_last_update=120,
    )
    assert m.status in ("stale", "needs_review", "candidate_for_archive")
    assert m.health_score < 0.5


def test_skill_metrics_health_archive_candidate():
    m = SkillMetrics(
        skill_name="dead-skill",
        use_count_30d=0,
        success_rate=0.3,
        user_corrections=5,
        days_since_last_update=200,
    )
    assert m.status == "candidate_for_archive"
    assert m.health_score < 0.3


# ── EvolutionEngine tests ────────────────────────────────────


def test_engine_empty_returns_no_suggestions():
    engine = EvolutionEngine()
    suggestions = engine.analyze()
    assert suggestions == []


def test_engine_too_few_tasks_returns_no_suggestions():
    engine = EvolutionEngine(min_tasks_for_analysis=5)
    engine.record_task(make_record())
    engine.record_task(make_record())
    suggestions = engine.analyze()
    assert suggestions == []


def test_record_task_updates_metrics():
    engine = EvolutionEngine()
    engine.record_task(make_record(
        skills=["test-skill"],
        success=True,
    ))
    engine.record_task(make_record(
        skills=["test-skill"],
        success=False,
        corrections=1,
    ))

    assert "test-skill" in engine._skill_metrics
    m = engine._skill_metrics["test-skill"]
    assert m.use_count_30d == 2
    assert m.success_rate == 0.5
    assert m.user_corrections == 1


def test_detect_recurring_mistakes():
    engine = EvolutionEngine()
    for i in range(4):
        engine.record_task(make_record(
            skills=["build-skill"],
            mistakes=["forgot to update lockfile"],
        ))
    engine.record_task(make_record(
        skills=["build-skill"],
        mistakes=["forgot to update lockfile"],
    ))
    engine.record_task(make_record(
        skills=["build-skill"],
        mistakes=["forgot to update lockfile"],
    ))

    suggestions = engine.analyze()
    # The recurring mistake should trigger a suggestion
    mistake_suggestions = [
        s for s in suggestions
        if "forgot to update lockfile" in s.reason
    ]
    assert len(mistake_suggestions) > 0
    assert mistake_suggestions[0].priority == "high"


def test_identify_workflow_gaps():
    engine = EvolutionEngine()
    engine.record_task(make_record(
        desc="complex deployment with many steps",
        skills=[],  # no skills used
        retries=4,
        success=True,
        duration=600,  # 10 minutes
    ))
    engine.record_task(make_record(skills=["some-skill"]))
    engine.record_task(make_record(skills=["some-skill"]))

    suggestions = engine.analyze()
    # Should suggest creating a new skill for the gap
    create_suggestions = [s for s in suggestions if s.action == "create"]
    assert len(create_suggestions) > 0


def test_stale_skill_triggers_suggestion():
    engine = EvolutionEngine()

    # Manually insert a stale metric
    engine._skill_metrics["old-skill"] = SkillMetrics(
        skill_name="old-skill",
        use_count_30d=1,
        success_rate=0.4,
        user_corrections=3,
        days_since_last_update=150,
    )

    # Add minimal tasks to satisfy min_tasks
    for _ in range(3):
        engine.record_task(make_record(skills=["old-skill"]))

    suggestions = engine.analyze()
    old_skill_suggestions = [
        s for s in suggestions if s.skill_name == "old-skill"
    ]
    assert len(old_skill_suggestions) > 0


def test_export_task_history():
    engine = EvolutionEngine()
    engine.record_task(make_record(desc="task a"))
    engine.record_task(make_record(desc="task b"))

    history = engine.export_task_history()
    assert len(history) == 2
    assert history[0]["task"] == "task a"
    assert history[1]["task"] == "task b"


def test_get_metrics_summary():
    engine = EvolutionEngine()
    engine.record_task(make_record(skills=["skill-a"]))
    engine.record_task(make_record(skills=["skill-a", "skill-b"]))

    summary = engine.get_metrics_summary()
    assert summary["total_tasks_analyzed"] == 2
    assert summary["skills_tracked"] == 2
    assert "skill-a" in summary["skills"]
    assert "skill-b" in summary["skills"]


def test_evolution_suggestion_to_dict():
    s = EvolutionSuggestion(
        skill_name="test",
        action="patch",
        reason="needs update",
        old_string="old",
        new_string="new",
        priority="high",
        estimated_time_saved_minutes=30,
    )
    d = s.to_dict()
    assert d["skill_name"] == "test"
    assert d["action"] == "patch"
    assert d["reason"] == "needs update"
    assert d["priority"] == "high"


def test_priority_sorting():
    """High priority suggestions should come before low priority."""
    engine = EvolutionEngine()

    # Create a scenario with mixed priorities
    engine._skill_metrics["high-prio"] = SkillMetrics(
        skill_name="high-prio",
        use_count_30d=2,
        success_rate=0.5,
        user_corrections=4,
        days_since_last_update=10,
    )
    engine._skill_metrics["low-prio"] = SkillMetrics(
        skill_name="low-prio",
        use_count_30d=0,
        success_rate=0.2,
        user_corrections=0,
        days_since_last_update=200,
    )

    for _ in range(3):
        engine.record_task(make_record(skills=["high-prio", "low-prio"]))

    suggestions = engine.analyze()
    if len(suggestions) >= 2:
        priorities = [s.priority for s in suggestions]
        # high should appear before low
        first_high = next(
            (i for i, p in enumerate(priorities) if p == "high"), None
        )
        first_low = next(
            (i for i, p in enumerate(priorities) if p == "low"), None
        )
        if first_high is not None and first_low is not None:
            assert first_high < first_low, (
                f"High priority ({first_high}) should come before "
                f"low priority ({first_low})"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
