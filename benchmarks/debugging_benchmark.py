"""
Debugging Benchmark — measures the debugging toolchain end-to-end.

Metrics:
  - SkillValidator error detection speed
  - SoulReader parse + validate time
  - EvolutionEngine analyze time
  - CLI validate --strict error reporting latency
"""
import subprocess
import time
import sys
import json
import tempfile
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJ_ROOT / "src"


def time_fn(fn, *args, **kwargs) -> dict:
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - t0
    return {"result": result, "elapsed_s": round(elapsed, 4)}


def bench_validator_strict() -> dict:
    """Validate with --strict flag (catches more issues)."""
    import subprocess as sp
    t0 = time.perf_counter()
    r = sp.run(
        [sys.executable, "-m", "cli.main", "validate",
         str(PROJ_ROOT / "skills"), "--strict"],
        capture_output=True, text=True, cwd=str(SRC_DIR)
    )
    return round(time.perf_counter() - t0, 3)


def bench_soul_reader() -> dict:
    """Parse a real SOUL.md and measure time."""
    # Create a minimal SOUL.md inline
    soul_content = """# Test Persona
## Identity
- Name: TestBot
- Role: Debugger
## Code Style
- naming: snake_case
- comments: sparse
- architecture: functional
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(soul_content)
        tmp_path = f.name

    try:
        from hermes_agent_skills.soul_reader import SoulReader
        reader = SoulReader()
        t0 = time.perf_counter()
        profile = reader.read(tmp_path)
        elapsed = time.perf_counter() - t0
        from dataclasses import asdict
        return {
            "elapsed_s": round(elapsed, 4),
            "profile_name": profile.name,
            "traits": profile.traits,
        }
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def bench_evolution_analyze() -> dict:
    """Measure EvolutionEngine.analyze() time."""
    from hermes_agent_skills.evolution import EvolutionEngine, TaskExecutionRecord
    engine = EvolutionEngine()

    # Seed with 20 mock tasks
    for i in range(20):
        engine.record_task(TaskExecutionRecord(
            task_description=f"validate skill-{i%5}",
            skills_used=[f"test-skill-{i % 5}"],
            success=(i % 3 != 0),
            user_corrections=(i % 3),
            tool_calls_count=5,
        ))

    t0 = time.perf_counter()
    suggestions = engine.analyze()
    elapsed = time.perf_counter() - t0
    return {
        "elapsed_s": round(elapsed, 4),
        "suggestion_count": len(suggestions) if suggestions else 0,
    }


def bench_validate_corrupt_skill() -> dict:
    """Validate a deliberately malformed SKILL.md (error detection speed)."""
    corrupt = """---
name: BAD!!NAME
description: ""
version: not-semver
---
# This skill has multiple validation errors
No frontmatter structure at all.
"""
    with tempfile.TemporaryDirectory() as tmp:
        skill_dir = Path(tmp) / "bad-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(corrupt)

        import subprocess as sp
        t0 = time.perf_counter()
        r = sp.run(
            [sys.executable, "-m", "cli.main", "validate",
             str(skill_dir), "--strict", "--format", "json"],
            capture_output=True, text=True, cwd=str(SRC_DIR)
        )
        elapsed = time.perf_counter() - t0
        issues_found = 0
        try:
            data = json.loads(r.stdout)
            if isinstance(data, dict):
                issues_found = len(data.get("issues", []))
            elif isinstance(data, list):
                issues_found = sum(len(d.get("issues", [])) for d in data if isinstance(d, dict))
        except (json.JSONDecodeError, AttributeError):
            # Validator may return non-JSON error output for corrupt files
            issues_found = len(r.stderr.splitlines()) if r.stderr else 0
            if issues_found == 0 and r.stdout:
                issues_found = len([l for l in r.stdout.splitlines() if l.strip()])
        return {
            "elapsed_s": round(elapsed, 3),
            "exit_code": r.returncode,
            "issues_found": issues_found,
        }


def main():
    report = {
        "benchmark": "debugging",
        "python_version": sys.version.split()[0],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": {}
    }

    print("=" * 50)
    print(" Debugging Benchmark")
    print("=" * 50)

    print("\n[1/4] Validator strict mode (all skills)...")
    r = bench_validator_strict()
    report["results"]["validator_strict"] = {"elapsed_s": r}
    print(f"  elapsed: {r:.3f}s")

    print("\n[2/4] SoulReader parse + profile...")
    r = bench_soul_reader()
    report["results"]["soul_reader"] = r
    print(f"  elapsed: {r['elapsed_s']:.4f}s  name: {r['profile_name']}  traits: {r['traits']}")

    print("\n[3/4] EvolutionEngine analyze (20 tasks)...")
    r = bench_evolution_analyze()
    report["results"]["evolution_analyze"] = r
    print(f"  elapsed: {r['elapsed_s']:.4f}s  suggestions: {r['suggestion_count']}")

    print("\n[4/4] Corrupt skill detection speed...")
    r = bench_validate_corrupt_skill()
    report["results"]["corrupt_skill"] = r
    print(f"  elapsed: {r['elapsed_s']:.3f}s  issues found: {r['issues_found']}")

    # Thresholds
    report["results"]["threshold_pass"] = (
        report["results"]["validator_strict"]["elapsed_s"] < 3.0
        and report["results"]["evolution_analyze"]["elapsed_s"] < 1.0
        and report["results"]["corrupt_skill"]["issues_found"] >= 3
    )
    print(f"\n  Thresholds passed: {report['results']['threshold_pass']}")

    out_path = PROJ_ROOT / "benchmarks" / "results_debugging.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n✅ Report saved to {out_path}")
    return report


if __name__ == "__main__":
    main()
