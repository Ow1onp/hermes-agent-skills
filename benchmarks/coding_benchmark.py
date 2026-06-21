"""
Coding Benchmark — measures throughput of skill validation, creation, and listing.

Metrics:
  - Validate single SKILL.md (cold + warm)
  - Validate entire skills/ directory (8 skills)
  - Create skill from each template (basic/advanced/minimal)
  - List all skills
  - JSON output throughput
"""
import subprocess
import time
import sys
import json
import tempfile
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJ_ROOT / "src"
SKILLS_DIR = PROJ_ROOT / "skills"


def time_command(cmd: str, cwd=None) -> dict:
    t0 = time.perf_counter()
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or str(PROJ_ROOT))
    elapsed = time.perf_counter() - t0
    return {
        "command": cmd, "elapsed_s": round(elapsed, 3),
        "exit_code": r.returncode,
        "stdout_len": len(r.stdout),
    }


def bench_validate_single(skill_path: str) -> dict:
    return time_command(
        f"{sys.executable} -m cli.main validate \"{skill_path}\"",
        cwd=str(SRC_DIR)
    )


def bench_validate_directory() -> dict:
    return time_command(
        f"{sys.executable} -m cli.main validate \"{SKILLS_DIR}\"",
        cwd=str(SRC_DIR)
    )


def bench_validate_json() -> dict:
    return time_command(
        f"{sys.executable} -m cli.main validate \"{SKILLS_DIR}\" --format json",
        cwd=str(SRC_DIR)
    )


def bench_create_skill(template: str, name: str, tmpdir: str) -> dict:
    return time_command(
        f"{sys.executable} -m cli.main create {name} --template {template} --category define --output {tmpdir}",
        cwd=str(SRC_DIR)
    )


def bench_list_skills() -> dict:
    return time_command(
        f"{sys.executable} -m cli.main list \"{SKILLS_DIR}\"",
        cwd=str(SRC_DIR)
    )


def bench_list_json() -> dict:
    return time_command(
        f"{sys.executable} -m cli.main list \"{SKILLS_DIR}\" --format json",
        cwd=str(SRC_DIR)
    )


def main():
    report = {
        "benchmark": "coding",
        "python_version": sys.version.split()[0],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": {}
    }

    print("=" * 50)
    print(" Coding Benchmark")
    print("=" * 50)

    # 1. Validate single skill
    print("\n[1/7] Validate single SKILL.md...")
    skills = sorted(SKILLS_DIR.rglob("SKILL.md"))
    for sp in skills:
        r = bench_validate_single(str(sp))
        print(f"  {sp.parent.name:<30} {r['elapsed_s']:.3f}s  exit={r['exit_code']}")
    report["results"]["validate_single"] = [
        {"skill": sp.parent.name, "elapsed_s": bench_validate_single(str(sp))["elapsed_s"]}
        for sp in skills
    ]

    # 2. Validate directory
    print("\n[2/7] Validate entire skills/ directory...")
    r = bench_validate_directory()
    report["results"]["validate_directory"] = r["elapsed_s"]
    print(f"  elapsed: {r['elapsed_s']:.3f}s  stdout: {r['stdout_len']} chars")

    # 3. Validate with JSON output
    print("\n[3/7] Validate directory (JSON)...")
    r = bench_validate_json()
    report["results"]["validate_json"] = r["elapsed_s"]
    print(f"  elapsed: {r['elapsed_s']:.3f}s  stdout: {r['stdout_len']} chars")

    # 4. Create skills from each template
    print("\n[4/7] Create skills (3 templates)...")
    with tempfile.TemporaryDirectory() as tmp:
        for tmpl in ["basic", "advanced", "minimal"]:
            r = bench_create_skill(tmpl, f"bench-{tmpl}", tmp)
            print(f"  {tmpl:<15} {r['elapsed_s']:.3f}s  exit={r['exit_code']}")
            key = f"create_{tmpl}"
            report["results"][key] = r["elapsed_s"]

    # 5. List skills (table)
    print("\n[5/7] List skills (table)...")
    r = bench_list_skills()
    report["results"]["list_table"] = r["elapsed_s"]
    print(f"  elapsed: {r['elapsed_s']:.3f}s  stdout: {r['stdout_len']} chars")

    # 6. List skills (JSON)
    print("\n[6/7] List skills (JSON)...")
    r = bench_list_json()
    report["results"]["list_json"] = r["elapsed_s"]
    print(f"  elapsed: {r['elapsed_s']:.3f}s  stdout: {r['stdout_len']} chars")

    # 7. Summary
    print("\n[7/7] Summary...")
    times = [
        report["results"]["validate_directory"],
        report["results"]["validate_json"],
        report["results"]["list_table"],
        report["results"]["list_json"],
    ]
    report["results"]["mean_operation_s"] = round(sum(times) / len(times), 3)
    report["results"]["threshold_pass"] = report["results"]["mean_operation_s"] < 2.0

    print(f"  Mean operation time:  {report['results']['mean_operation_s']:.3f}s")
    print(f"  Thresholds passed:    {report['results']['threshold_pass']}")

    out_path = PROJ_ROOT / "benchmarks" / "results_coding.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n✅ Report saved to {out_path}")

    return report


if __name__ == "__main__":
    main()
