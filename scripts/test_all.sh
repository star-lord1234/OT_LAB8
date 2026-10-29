#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing project environment. Follow SETUP.md first." >&2
  exit 1
fi

"$ROOT_DIR/scripts/preflight.sh"
"$PYTHON_BIN" "$ROOT_DIR/scripts/validate_repo.py"
MPLCONFIGDIR="$ROOT_DIR/.cache/matplotlib" \
  XDG_CACHE_HOME="$ROOT_DIR/.cache/xdg" \
  "$PYTHON_BIN" -m pytest "$ROOT_DIR/tests" "$ROOT_DIR/tracks"
