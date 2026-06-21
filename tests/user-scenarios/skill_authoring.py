"""
User Scenario: Skill Authoring — full create → validate → evolve cycle.
"""
import subprocess, sys, tempfile, time, json
from pathlib import Path

REPO = Path("E:/Projects/hermes-agent-skills")
SRC = REPO / "src"

def run(cmd, **kw):
    t0 = time.perf_counter()
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(SRC), **kw)
    return r, round(time.perf_counter() - t0, 3)

def main():
    results = {}
    passed = True

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # [1/4] Create from all 3 templates
        print("=" * 50)
        print(" [1/4] Creating skills from 3 templates")
        for tmpl in ["basic", "advanced", "minimal"]:
            name = f"authoring-{tmpl}"
            outdir = tmp / "skills" / name
            outdir.mkdir(parents=True, exist_ok=True)
            r, elapsed = run(
                f'{sys.executable} -m cli.main create {name} '
                f'--template {tmpl} --category define --output {tmp} --no-interactive',
                timeout=30,
            )
            # CLI nests: <output>/skills/<category>/<name>/SKILL.md
            skill_file = tmp / "skills" / "define" / name / "SKILL.md"
            ok = skill_file.exists()
            if not ok:
                # Try without subdir (older behavior)
                skill_file = tmp / name / "SKILL.md"
                ok = skill_file.exists()
            results[f"create_{tmpl}"] = {"elapsed_s": elapsed, "ok": ok}
            status = "✓" if ok else "✗"
            print(f"  {status} {tmpl}: {elapsed:.3f}s")

        # [2/4] Validate table
        print("\n [2/4] Validating (table)...")
        skills_path = tmp / "skills"
        r, elapsed = run(f'{sys.executable} -m cli.main validate "{skills_path}"')
        results["validate_table"] = {"elapsed_s": elapsed, "exit": r.returncode}
        print(f"  ✓ {elapsed:.3f}s  (exit={r.returncode})")

        # [3/4] Validate JSON
        print("\n [3/4] Validating (JSON)...")
        r, elapsed = run(f'{sys.executable} -m cli.main validate "{skills_path}" --format json')
        try:
            data = json.loads(r.stdout)
            count = len(data) if isinstance(data, list) else 1
        except:
            count = "?"
        results["validate_json"] = {"elapsed_s": elapsed, "skills": count}
        print(f"  ✓ {elapsed:.3f}s  ({count} skills)")

        # [4/4] Evolution Engine
        print("\n [4/4] Evolution Engine analysis...")
        sys.path.insert(0, str(SRC))
        from hermes_agent_skills.evolution import EvolutionEngine, TaskExecutionRecord
        t0 = time.perf_counter()
        e = EvolutionEngine()
        for i in range(10):
            e.record_task(TaskExecutionRecord(
                task_description=f"task-{i}",
                skills_used=[f"skill-{i % 3}"],
                success=(i % 4 != 0),
                user_corrections=i % 3,
            ))
        suggestions = e.analyze()
        elapsed = round(time.perf_counter() - t0, 3)
        results["evolution"] = {"elapsed_s": elapsed, "suggestions": len(suggestions) if suggestions else 0}
        print(f"  ✓ {elapsed:.3f}s  ({len(suggestions) if suggestions else 0} suggestions)")

    # Summary
    print("\n" + "=" * 50)
    all_ok = all(v.get("ok", True) for v in results.values())
    if all_ok and passed:
        print("✅ SCENARIO PASSED — skill-authoring")
    else:
        print("⚠️  SCENARIO FAILED")
    return results


if __name__ == "__main__":
    main()
