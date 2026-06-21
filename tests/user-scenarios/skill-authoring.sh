#!/usr/bin/env bash
# User Scenario: Skill Authoring — create → validate → evolve
set -euo pipefail
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)
TMPDIR=$(mktemp -d)
REPO="E:/Projects/hermes-agent-skills"
cd "$REPO/src"
PASS=true
echo "=========================================="
echo " Scenario: skill-authoring"
echo "=========================================="

# [1/4] Create from all 3 templates
echo ""; echo "[1/4] Creating skills from all 3 templates..."
for tmpl in basic advanced minimal; do
    t_start=$(date +%s%3N)
    python -m cli.main create "authoring-$tmpl" --template "$tmpl" --category define --output "$TMPDIR/skills" 2>&1 | tail -1
    t_end=$(date +%s%3N)
    echo "  ✓ $tmpl: $(( (t_end - t_start) ))ms"
    [ -f "$TMPDIR/skills/authoring-$tmpl/SKILL.md" ] || { echo "  ✗ $tmpl FAILED"; PASS=false; }
done

# [2/4] Validate table
echo ""; echo "[2/4] Validating (table)..."
t_start=$(date +%s%3N)
python -m cli.main validate "$TMPDIR/skills" 2>&1 | tail -3
t_end=$(date +%s%3N)
echo "  ✓ table: $(( (t_end - t_start) ))ms"

# [3/4] Validate JSON
echo ""; echo "[3/4] Validating (JSON)..."
t_start=$(date +%s%3N)
python -m cli.main validate "$TMPDIR/skills" --format json 2>&1 | python -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d) if isinstance(d,list) else 1} skills')"
t_end=$(date +%s%3N)
echo "  ✓ json: $(( (t_end - t_start) ))ms"

# [4/4] Evolution Engine
echo ""; echo "[4/4] Evolution Engine analysis..."
t_start=$(date +%s%3N)
python -c "
import sys; sys.path.insert(0, '$REPO/src')
from hermes_agent_skills.evolution import EvolutionEngine, TaskExecutionRecord
e = EvolutionEngine()
for i in range(10):
    e.record_task(TaskExecutionRecord(task_description=f'task-{i}', skills_used=[f'skill-{i%3}'], success=(i%4!=0), user_corrections=i%3))
s = e.analyze()
print(f'suggestions: {len(s) if s else 0}')
" 2>&1
t_end=$(date +%s%3N)
echo "  ✓ evolution: $(( (t_end - t_start) ))ms"

echo ""
if $PASS; then echo "✅ SCENARIO PASSED"; else echo "⚠️  SCENARIO FAILED"; fi
