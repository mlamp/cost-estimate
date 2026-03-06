#!/usr/bin/env bash
set -euo pipefail

TARGET="$HOME/.claude/skills/cost-estimate"

if [ -L "$TARGET" ]; then
  rm "$TARGET"
  echo "Removed: $TARGET"
elif [ -e "$TARGET" ]; then
  echo "Error: $TARGET exists but is not a symlink. Remove manually if intended."
  exit 1
else
  echo "Nothing to remove: $TARGET does not exist."
fi
