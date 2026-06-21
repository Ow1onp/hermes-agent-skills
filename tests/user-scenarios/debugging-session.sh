#!/usr/bin/env bash
# User Scenario: Debugging Session — validate corrupt → fix → re-validate
set -euo pipefail
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)
TMPDIR=$(mktemp -d)
REPO="E:/Projects/hermes-agent-skills"
cd "$REPO/src"
PASS=true
echo "=========================================="
echo " Scenario: debugging-session"
echo "=========================================="

# [1/6] Create buggy skill
echo ""; echo "[1/6] Creating buggy skill..."
BUGGY="$TMPDIR/buggy-skill"
mkdir -p "$BUGGY"
cat > "$BUGGY/SKILL.md" << 'EOF'
---
name: BAD NAME!!
description: ""
version: not-a-version
license: proprietary
---
# Bad Skill
Multiple violations.
EOF
echo "  ✓ Created at $BUGGY"

# [2/6] Validate buggy skill
echo ""; echo "[2/6] Validating buggy skill..."
t_start=$(date +%s%3N)
OUT=$(python -m cli.main validate "$BUGGY/SKILL.md" --strict --format json 2>&1) || true
t_end=$(date +%s%3N)
ISSUES=$(echo "$OUT" | python -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('issues',[])))" 2>/dev/null || echo "0")
echo "  Issues found: $ISSUES  $(( (t_end - t_start) ))ms"
[ "$ISSUES" -ge 2 ] || PASS=false

# [3/6] Validate known-good
echo ""; echo "[3/6] Validating known-good skill..."
t_start=$(date +%s%3N)
python -m cli.main validate "$REPO/skills/verify/debugger-coordinator/SKILL.md" 2>&1 | head -1
t_end=$(date +%s%3N)
echo "  ✓ $(( (t_end - t_start) ))ms"

# [4/6] Strict validate all
echo ""; echo "[4/6] Strict validate all skills..."
t_start=$(date +%s%3N)
python -m cli.main validate "$REPO/skills" --strict 2>&1 | tail -2
t_end=$(date +%s%3N)
echo "  ✓ $(( (t_end - t_start) ))ms"

# [5/6] SoulReader
echo ""; echo "[5/6] SoulReader..."
t_start=$(date +%s%3N)
python -c "
import sys,os,tempfile; sys.path.insert(0,'$REPO/src')
from hermes_agent_skills.soul_reader import SoulReader
with tempfile.NamedTemporaryFile(mode='w',suffix='.md',delete=False) as f:
    f.write('# Test\n## Identity\n- Name: DB\n## Code Style\n- naming: snake_case\n')
    tmp=f.name
p = SoulReader().read(tmp); os.unlink(tmp)
print(f'name={p.name} traits={p.traits}')
" 2>&1
t_end=$(date +%s%3N)
echo "  ✓ $(( (t_end - t_start) ))ms"

# [6/6] Evolution Engine
echo ""; echo "[6/6] Evolution Engine..."
t_start=$(date +%s%3N)
python -c "
import sys; sys.path.insert(0,'$REPO/src')
from hermes_agent_skills.evolution import EvolutionEngine, TaskExecutionRecord
e = EvolutionEngine()
for i in range(15):
    e.record_task(TaskExecutionRecord(task_description=f't{i}', skills_used=[f's-{i%4}'], success=(i%5!=0), user_corrections=i%5))
s = e.analyze()
for x in (s or [])[:3]: print(f'  {x.skill_name}: {x.action}')
" 2>&1
t_end=$(date +%s%3N)
echo "  ✓ $(( (t_end - t_start) ))ms"

echo ""
if $PASS; then echo "✅ DEBUGGING TOOLCHAIN VERIFIED"; else echo "⚠️  GAPS DETECTED"; fi
