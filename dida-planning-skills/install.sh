#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "$(dirname "$0")" && pwd)"
DESTINATION="${1:-$HOME/.agents/skills}"
if [[ $# -gt 0 ]]; then shift; fi
exec python "$SOURCE/install.py" --destination "$DESTINATION" "$@"
