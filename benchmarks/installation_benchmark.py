"""
Installation Benchmark — measures end-to-end install experience for hermes-agent-skills.

Metrics:
  - pip install time (cold)
  - pip install time (warm/cached)
  - import time for core modules
  - dependency resolution overhead
"""
import subprocess
import time
import sys
import json
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent


def time_command(cmd: str, cwd=None, env=None) -> dict:
    """Run a shell command and return timing + result."""
    t0 = time.perf_counter()
    r = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        cwd=cwd or str(PROJ_ROOT), env=env
    )
    elapsed = time.perf_counter() - t0
    return {
        "command": cmd,
        "elapsed_s": round(elapsed, 3),
        "exit_code": r.returncode,
        "stdout_lines": len(r.stdout.splitlines()) if r.stdout else 0,
        "stderr_lines": len(r.stderr.splitlines()) if r.stderr else 0,
    }


def bench_import_time() -> dict:
    """Measure import time for each core module."""
    modules = [
        "hermes_agent_skills",
        "hermes_agent_skills.validator",
        "hermes_agent_skills.evolution",
        "hermes_agent_skills.soul_reader",
        "hermes_agent_skills.models",
    ]
    results = {}
    for mod in modules:
        t0 = time.perf_counter()
        __import__(mod)
        results[mod] = round(time.perf_counter() - t0, 4)
    return results


def bench_pip_install_dry() -> dict:
    """Measure pip install --dry-run time (dependency resolution)."""
    return time_command(
        f"{sys.executable} -m pip install --dry-run -e .",
        cwd=str(PROJ_ROOT)
    )


def bench_pip_install_live() -> dict:
    """Measure actual pip install time (editable, already installed = fast)."""
    return time_command(
        f"{sys.executable} -m pip install -e . --quiet",
        cwd=str(PROJ_ROOT)
    )


def bench_cli_help() -> dict:
    """Measure CLI startup + help rendering."""
    return time_command(
        f"{sys.executable} -m cli.main --help",
        cwd=str(PROJ_ROOT / "src")
    )


def main():
    report = {
        "benchmark": "installation",
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": {}
    }

    print("=" * 50)
    print(" Installation Benchmark")
    print("=" * 50)

    print("\n[1/5] Import time...")
    report["results"]["import_time"] = bench_import_time()
    for mod, t in report["results"]["import_time"].items():
        print(f"  {mod:<45} {t:.4f}s")

    print("\n[2/5] pip install --dry-run (dependency resolution)...")
    report["results"]["pip_dry_run"] = bench_pip_install_dry()
    print(f"  elapsed: {report['results']['pip_dry_run']['elapsed_s']:.3f}s")

    print("\n[3/5] pip install -e . (live)...")
    report["results"]["pip_install_live"] = bench_pip_install_live()
    print(f"  elapsed: {report['results']['pip_install_live']['elapsed_s']:.3f}s")

    print("\n[4/5] CLI startup (--help)...")
    report["results"]["cli_help"] = bench_cli_help()
    print(f"  elapsed: {report['results']['cli_help']['elapsed_s']:.3f}s")

    # Summary
    print("\n[5/5] Summary...")
    total_import = sum(report["results"]["import_time"].values())
    report["results"]["total_import_time"] = round(total_import, 4)
    report["results"]["threshold_pass"] = (
        report["results"]["cli_help"]["elapsed_s"] < 1.0
        and report["results"]["pip_dry_run"]["elapsed_s"] < 30.0
    )

    print(f"\n  Total import time:     {total_import:.4f}s")
    print(f"  CLI startup:           {report['results']['cli_help']['elapsed_s']:.3f}s")
    print(f"  Thresholds passed:     {report['results']['threshold_pass']}")

    # Write JSON report
    out_path = PROJ_ROOT / "benchmarks" / "results_installation.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n✅ Report saved to {out_path}")

    return report


if __name__ == "__main__":
    main()
