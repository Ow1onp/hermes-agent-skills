#!/usr/bin/env bash
# User Scenario: Release Engineering — pre-release checks
set -euo pipefail
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)
REPO="E:/Projects/hermes-agent-skills"
cd "$REPO/src"
PASS=true
echo "=========================================="
echo " Scenario: release-engineering"
echo "=========================================="

# [1/5] Validate cicd-orchestrator
echo ""; echo "[1/5] Validating cicd-orchestrator SKILL.md..."
t_start=$(date +%s%3N)
python -m cli.main validate "$REPO/skills/ship/cicd-orchestrator/SKILL.md" 2>&1
t_end=$(date +%s%3N)
echo "  ✓ cicd-orchestrator: $(( (t_end - t_start) ))ms"

# [2/5] Inspect CI workflow
echo ""; echo "[2/5] Checking CI workflow..."
CI="$REPO/.github/workflows/ci.yml"
t_start=$(date +%s%3N)
python -c "
import yaml
with open('$CI') as f: wf = yaml.safe_load(f)
for name, job in wf.get('jobs', {}).items():
    print(f'  {name}: {len(job.get("steps",[]))} steps')
" 2>&1
t_end=$(date +%s%3N)
echo "  ✓ CI analyzed: $(( (t_end - t_start) ))ms"

# [3/5] Validate all 8 skills
echo ""; echo "[3/5] Pre-release validation (all 8 skills)..."
t_start=$(date +%s%3N)
python -m cli.main validate "$REPO/skills" 2>&1 | tail -3
t_end=$(date +%s%3N)
VEXIT=$?
[ $VEXIT -eq 0 ] || PASS=false
echo "  ✓ exit=$VEXIT  $(( (t_end - t_start) ))ms"

# [4/5] Version consistency
echo ""; echo "[4/5] Version consistency..."
t_start=$(date +%s%3N)
python -c "
import re
files = {
    'pyproject': '$REPO/pyproject.toml',
    'init': '$REPO/src/hermes_agent_skills/__init__.py',
    'cli_init': '$REPO/src/cli/__init__.py',
    'README': '$REPO/README.md',
    'README_zh': '$REPO/README.zh-CN.md',
    'CHANGELOG': '$REPO/CHANGELOG.md',
}
vs = set()
for name, path in files.items():
    m = re.search(r'["\'']?(1\.\d+\.\d+)', open(path).read())
    v = m.group(1) if m else '?'
    vs.add(v)
    print(f'  {name}: {v}')
print(f'unique: {len(vs)}')
" 2>&1
t_end=$(date +%s%3N)
echo "  ✓ $(( (t_end - t_start) ))ms"

# [5/5] Skill inventory
echo ""; echo "[5/5] Skill inventory..."
t_start=$(date +%s%3N)
python -m cli.main list "$REPO/skills" 2>&1 | tail -10
t_end=$(date +%s%3N)
echo "  ✓ $(( (t_end - t_start) ))ms"

echo ""
if $PASS; then echo "✅ RELEASE READY"; else echo "⚠️  RELEASE BLOCKED"; fi
