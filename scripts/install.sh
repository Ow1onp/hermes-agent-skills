#!/bin/bash
# install.sh — Quick install script for hermes-agent-skills
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Ow1onp/hermes-agent-skills/main/scripts/install.sh | bash
#   # or locally:
#   bash scripts/install.sh

set -euo pipefail

HERMES_SKILLS_DIR="${HERMES_HOME:-$HOME/.hermes}/skills"
REPO_URL="https://github.com/Ow1onp/hermes-agent-skills.git"
TEMP_DIR=$(mktemp -d)

echo "🎯 Installing hermes-agent-skills..."
echo "   Hermes skills dir: $HERMES_SKILLS_DIR"

# Clone the repo
echo "📥 Cloning repository..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR" 2>/dev/null

# Copy skills to Hermes skills directory
echo "📋 Copying skills..."
mkdir -p "$HERMES_SKILLS_DIR"
cp -r "$TEMP_DIR/skills/"* "$HERMES_SKILLS_DIR/"

# Cleanup
rm -rf "$TEMP_DIR"

# Count installed skills
SKILL_COUNT=$(find "$HERMES_SKILLS_DIR" -name "SKILL.md" -path "*/hermes-agent-skills/*" 2>/dev/null | wc -l)

echo ""
echo "✅ Installation complete!"
echo "   $SKILL_COUNT skills installed to $HERMES_SKILLS_DIR"
echo ""
echo "   To use a skill in Hermes:"
echo "     /skill requirement-analyzer"
echo "     /skill test-driven-dev"
echo "     /skill code-quality-guardian"
echo ""
echo "   To list all skills:"
echo "     hermes skills list"
