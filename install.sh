#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)/skill"
TARGET_DIR="$HOME/.claude/skills"
LINK_NAME="cost-estimate"

mkdir -p "$TARGET_DIR"

if [ -L "$TARGET_DIR/$LINK_NAME" ]; then
  echo "Updating existing symlink..."
  rm "$TARGET_DIR/$LINK_NAME"
elif [ -e "$TARGET_DIR/$LINK_NAME" ]; then
  echo "Error: $TARGET_DIR/$LINK_NAME exists and is not a symlink. Remove it first."
  exit 1
fi

ln -s "$SKILL_DIR" "$TARGET_DIR/$LINK_NAME"
echo "Installed: $TARGET_DIR/$LINK_NAME -> $SKILL_DIR"
echo ""
echo "Usage: type /cost-estimate in any Claude Code session"
