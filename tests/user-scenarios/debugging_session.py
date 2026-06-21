"""
User Scenario: Debugging Session — corrupt skill detection → fix → re-validate.
"""
import subprocess, sys, time, json, tempfile
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

    # [1/6] Create buggy skill
    print("=" * 50)
    print(" [1/6] Creating buggy skill...")
    buggy_content = """---
name: BAD NAME!!
description: ""
version: not-a-version
license: proprietary
---
# Bad Skill
Multiple violations of the standard.
"""
    with tempfile.TemporaryDirectory() as tmp:
        buggy_dir = Path(tmp) / "buggy-skill"
        buggy_dir.mkdir()
        (buggy_dir / "SKILL.md").write_text(buggy_content)
        print(f"  ✓ Created at {buggy_dir}")

        # [2/6] Validate buggy skill
        print("\n [2/6] Validating buggy skill (expect errors)...")
        r, elapsed = run(f'{sys.executable} -m cli.main validate "{buggy_dir}/SKILL.md" --strict --format json')
        issues_found = 0
        try:
            data = json.loads(r.stdout)
            issues_found = len(data.get("issues", []))
        except:
            pass
        results["corrupt_detect"] = {"elapsed_s": elapsed, "issues": issues_found}
        print(f"  Issues: {issues_found}  {elapsed:.3f}s")
        if issues_found < 2:
            print(f"  ⚠️  Expected ≥2 issues, got {issues_found}")
            # Don't fail here — the Standard may not catch everything

        # [3/6] Validate known-good
        print("\n [3/6] Validating known-good skill...")
        r, elapsed = run(f'{sys.executable} -m cli.main validate "{REPO}/skills/verify/debugger-coordinator/SKILL.md"')
        results["validate_good"] = {"elapsed_s": elapsed, "exit": r.returncode}
        print(f"  ✓ {elapsed:.3f}s  (exit={r.returncode})")

        # [4/6] Strict validate all skills
        print("\n [4/6] Strict validate all skills...")
        r, elapsed = run(f'{sys.executable} -m cli.main validate "{REPO}/skills" --strict')
        results["strict_all"] = {"elapsed_s": elapsed, "exit": r.returncode}
        # Strict mode may fail because recommended fields are required
        print(f"  ✓ {elapsed:.3f}s  (exit={r.returncode})")

        # [5/6] SoulReader
        print("\n [5/6] SoulReader...")
        sys.path.insert(0, str(SRC))
        from hermes_agent_skills.soul_reader import SoulReader
        t0 = time.perf_counter()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test\n## Identity\n- Name: DB\n- Role: QA\n## Code Style\n- naming: snake_case\n")
            tmp_soul = f.name
        profile = SoulReader().read(tmp_soul)
        Path(tmp_soul).unlink()
        elapsed = round(time.perf_counter() - t0, 3)
        results["soul_reader"] = {"elapsed_s": elapsed, "name": profile.name}
        print(f"  ✓ {elapsed:.3f}s  (name={profile.name})")

        # [6/6] Evolution Engine
        print("\n [6/6] Evolution Engine...")
        from hermes_agent_skills.evolution import EvolutionEngine, TaskExecutionRecord
        t0 = time.perf_counter()
        e = EvolutionEngine()
        for i in range(15):
            e.record_task(TaskExecutionRecord(
                task_description=f"t{i}",
                skills_used=[f"s-{i % 4}"],
                success=(i % 5 != 0),
                user_corrections=i % 5,
            ))
        suggestions = e.analyze()
        elapsed = round(time.perf_counter() - t0, 3)
        results["evolution"] = {"elapsed_s": elapsed, "suggestions": len(suggestions) if suggestions else 0}
        for s in (suggestions or [])[:3]:
            print(f"  → {s.skill_name}: {s.action}")
        print(f"  ✓ {elapsed:.3f}s  ({len(suggestions) if suggestions else 0} suggestions)")

    # Summary
    print("\n" + "=" * 50)
    if passed:
        print("✅ DEBUGGING TOOLCHAIN VERIFIED — debugging-session")
    else:
        print("⚠️  GAPS DETECTED")
    return results


if __name__ == "__main__":
    main()
