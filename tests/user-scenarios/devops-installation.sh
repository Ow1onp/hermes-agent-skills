#!/usr/bin/env bash
# User Scenario: DevOps Installation — clone → install → create → validate
set -euo pipefail
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)
TMPDIR=$(mktemp -d)
PASS=true
echo "=========================================="
echo " Scenario: devops-installation"
echo "=========================================="

# [1/5] Clone
echo ""; echo "[1/5] Cloning..."
t_start=$(date +%s%3N)
git clone https://github.com/Ow1onp/hermes-agent-skills.git "$TMPDIR/repo" 2>&1 | tail -1
t_end=$(date +%s%3N)
echo "  ✓ clone: $(( (t_end - t_start) ))ms"

# [2/5] Install
echo ""; echo "[2/5] Installing..."
cd "$TMPDIR/repo"
t_start=$(date +%s%3N)
python -m pip install -e . --quiet 2>&1 | tail -1
t_end=$(date +%s%3N)
echo "  ✓ install: $(( (t_end - t_start) ))ms"

# [3/5] Create
echo ""; echo "[3/5] Creating first skill..."
cd "$TMPDIR/repo/src"
t_start=$(date +%s%3N)
python -m cli.main create my-first --template basic --category define --output "$TMPDIR/skills" 2>&1 | tail -1
t_end=$(date +%s%3N)
[ -f "$TMPDIR/skills/my-first/SKILL.md" ] || PASS=false
echo "  ✓ create: $(( (t_end - t_start) ))ms"

# [4/5] Validate
echo ""; echo "[4/5] Validating..."
t_start=$(date +%s%3N)
python -m cli.main validate "$TMPDIR/skills/my-first/SKILL.md" 2>&1 | head -1
t_end=$(date +%s%3N)
echo "  ✓ validate: $(( (t_end - t_start) ))ms"

# [5/5] List
echo ""; echo "[5/5] Listing skills..."
t_start=$(date +%s%3N)
python -m cli.main list skills/ 2>&1 | tail -5
t_end=$(date +%s%3N)
echo "  ✓ list: $(( (t_end - t_start) ))ms"

echo ""
if $PASS; then echo "✅ SCENARIO PASSED"; else echo "⚠️  FAILED"; fi
