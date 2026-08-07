#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "$(dirname "$0")" && pwd)"
DESTINATION="${1:-$HOME/.agents/skills}"
ITEMS=(
  dida-cli dida-task-capture dida-task-breakdown dida-task-estimator
  dida-daily-planner dida-task-progress dida-weekly-review
  dida-planning-profile dida-planning-memory dida-planning-core
)
mkdir -p "$DESTINATION"
for item in "${ITEMS[@]}"; do
  rm -rf "$DESTINATION/$item"
  cp -R "$SOURCE/$item" "$DESTINATION/$item"
  echo "Installed $item -> $DESTINATION/$item"
done
python "$DESTINATION/dida-planning-core/scripts/package_validator.py" --root "$SOURCE"
echo "Done. Restart Codex only if /skills does not refresh automatically."
