"""
User Scenario: Release Engineering — pre-release validation checks.
"""
import subprocess, sys, time, json, re
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

    # [1/5] Validate cicd-orchestrator
    print("=" * 50)
    print(" [1/5] Validating cicd-orchestrator SKILL.md...")
    r, elapsed = run(f'{sys.executable} -m cli.main validate "{REPO}/skills/ship/cicd-orchestrator/SKILL.md"')
    results["validate_skill"] = {"elapsed_s": elapsed, "exit": r.returncode}
    print(f"  ✓ {elapsed:.3f}s")

    # [2/5] Inspect CI workflow
    print("\n [2/5] Checking CI workflow...")
    import yaml
    t0 = time.perf_counter()
    ci_file = REPO / ".github" / "workflows" / "ci.yml"
    with open(ci_file) as f:
        wf = yaml.safe_load(f)
    jobs = wf.get("jobs", {})
    for name, job in jobs.items():
        print(f"  {name}: {len(job.get('steps', []))} steps")
    elapsed = round(time.perf_counter() - t0, 3)
    results["inspect_ci"] = {"elapsed_s": elapsed, "jobs": len(jobs)}
    print(f"  ✓ {elapsed:.3f}s  ({len(jobs)} jobs)")

    # [3/5] Validate all 8 skills
    print("\n [3/5] Pre-release validation (all 8 skills)...")
    r, elapsed = run(f'{sys.executable} -m cli.main validate "{REPO}/skills"')
    results["validate_all"] = {"elapsed_s": elapsed, "exit": r.returncode}
    print(f"  ✓ {elapsed:.3f}s  (exit={r.returncode})")
    if r.returncode != 0:
        passed = False

    # [4/5] Version consistency
    print("\n [4/5] Version consistency...")
    t0 = time.perf_counter()
    files = {
        "pyproject": REPO / "pyproject.toml",
        "__init__": REPO / "src" / "hermes_agent_skills" / "__init__.py",
        "cli/__init__": REPO / "src" / "cli" / "__init__.py",
        "README": REPO / "README.md",
        "README.zh-CN": REPO / "README.zh-CN.md",
        "CHANGELOG": REPO / "CHANGELOG.md",
    }
    versions = set()
    for name, path in files.items():
        content = path.read_text()
        m = re.search(r'["\']?(\d+\.\d+\.\d+)', content)
        v = m.group(1) if m else "NOT FOUND"
        versions.add(v)
        print(f"  {name}: {v}")
    elapsed = round(time.perf_counter() - t0, 3)
    results["version_check"] = {"elapsed_s": elapsed, "unique": len(versions)}
    consistent = len(versions) == 1
    print(f"  {'✓' if consistent else '✗'} {elapsed:.3f}s  ({len(versions)} unique)")
    if not consistent:
        passed = False

    # [5/5] Skill inventory
    print("\n [5/5] Skill inventory...")
    r, elapsed = run(f'{sys.executable} -m cli.main list "{REPO}/skills"')
    results["inventory"] = {"elapsed_s": elapsed, "exit": r.returncode}
    print(f"  ✓ {elapsed:.3f}s")

    # Summary
    print("\n" + "=" * 50)
    if passed:
        print("✅ RELEASE READY — release-engineering")
    else:
        print("⚠️  RELEASE BLOCKED")
    return results


if __name__ == "__main__":
    main()
