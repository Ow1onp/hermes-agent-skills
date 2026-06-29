"""
hermes run — Hermes v2 natural-language entry point.

Usage:
    hermes run "帮我发布项目"
    hermes run "fix the failing test"
    hermes run "创建一个 Python 项目"
    hermes run --mode expert "## Authority\n你是..."

Modes are auto-detected. Use --verbose to see the generated constraint prompt.
"""
import sys
from pathlib import Path

# Ensure src/ is on path
_SRC = Path(__file__).parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _prefer_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


_prefer_utf8_stdio()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="hermes run",
        description="Hermes v2 — natural language task execution",
    )
    parser.add_argument(
        "input",
        nargs="*",
        help="Natural language task description. If empty, reads from stdin.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show the generated constraint prompt (Beginner/Advanced mode).",
    )
    parser.add_argument(
        "--mode",
        choices=["beginner", "advanced", "expert"],
        help="Force a specific mode (overrides auto-detection).",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show the plan without executing.",
    )

    args = parser.parse_args()

    # Collect input
    if args.input:
        user_input = " ".join(args.input)
    elif not sys.stdin.isatty():
        user_input = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    if not user_input:
        print("Error: no input provided.")
        sys.exit(1)

    # Import v2 modules
    from hermes_v2.task_registry import TaskRegistry
    from hermes_v2.router import IntentRouter
    from hermes_v2.orchestrator import TaskOrchestrator
    from hermes_v2.constraints import ConstraintEngine
    from hermes_v2.modes import ModeRouter, Mode

    # Initialize
    registry = TaskRegistry()
    router = IntentRouter(registry)
    orchestrator = TaskOrchestrator(registry, ConstraintEngine())
    mode_router = ModeRouter(registry, router, orchestrator)

    print(f"📦 Hermes v2 · {len(registry)} tasks loaded\n")

    # Detect/dispatch
    if args.mode:
        # Force mode — bypass auto-detection
        result = mode_router.dispatch(user_input)
        result.mode = Mode(args.mode)
    else:
        result = mode_router.dispatch(user_input)

    # Show result
    if result.mode == Mode.EXPERT:
        print(f"[{result.mode.value.upper()}] Raw constraint prompt detected.")
        print("  Bypassing NL pipeline. Executing directly.\n")
        if args.verbose:
            print("─" * 40)
            print(result.raw_prompt)
            print("─" * 40)
        if args.dry_run:
            print("(Dry run — not executed)")
            return
        print("→ Delegate to Hermes v1 execution engine")
        return

    if result.routing and result.routing.clarification_needed:
        print(f"❓ {result.message}")
        return

    plan = result.plan
    if plan is None:
        print("Error: could not generate execution plan.")
        sys.exit(1)

    # Plan summary
    print(f"Mode:     {result.mode.value.upper()}")
    print(f"Task:     {plan.label} ({plan.task_id})")
    print(f"Confidence: {result.routing.confidence:.0%}" if result.routing else "")
    print(f"Steps:    {plan.step_count}")
    print(f"Skills:   {', '.join(plan.skills) if plan.skills else '(auto-detect)'}")

    if plan.workflow:
        print("\nWorkflow:")
        for i, step in enumerate(plan.workflow, 1):
            print(f"  {i}. [{step.persona}] {step.description}")

    # Show constraint prompt in verbose mode
    if args.verbose and plan.constraint_prompt:
        print("\n" + "─" * 50)
        print("Generated Constraint Prompt (invisible to user)")
        print("─" * 50)
        print(plan.constraint_prompt)
        print("─" * 50)

    # Success criteria
    if plan.success_criteria:
        print("\nSuccess Criteria:")
        for c in plan.success_criteria:
            print(f"  ✓ {c}")

    if args.dry_run:
        print("\n(Dry run — plan shown, not executed)")
        return

    print(f"\n→ Executing with {plan.step_count} step(s)...")
    # Execution happens here — delegates to v1 runtime
    # In MVP, the plan.constraint_prompt is the output that feeds into v1


if __name__ == "__main__":
    main()
