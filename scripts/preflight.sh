#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
LOG_DIR="$ROOT_DIR/setup_logs"
LOG_FILE="${1:-$LOG_DIR/preflight-latest.txt}"
CACHE_DIR="$ROOT_DIR/.cache"
LOCK_DIR="${LOG_FILE}.lock"

mkdir -p "$LOG_DIR" "$CACHE_DIR/matplotlib" "$CACHE_DIR/xdg"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[FAIL] Another preflight appears to be writing $LOG_FILE" >&2
  echo "Remove the empty lock directory only after confirming no preflight is running: $LOCK_DIR" >&2
  exit 2
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "[FAIL] Project environment not found at $PYTHON_BIN" | tee "$LOG_FILE"
  echo "Run the documented uv sync command in SETUP.md first." | tee -a "$LOG_FILE"
  exit 1
fi

{
  echo "Preflight started: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "Project root: $ROOT_DIR"
  echo
  MPLCONFIGDIR="$CACHE_DIR/matplotlib" \
    XDG_CACHE_HOME="$CACHE_DIR/xdg" \
    PYTHONUNBUFFERED=1 \
    "$PYTHON_BIN" -u "$ROOT_DIR/scripts/verify_environment.py"
} 2>&1 | tee "$LOG_FILE"

status=${PIPESTATUS[0]}
echo "Preflight log: $LOG_FILE"
exit "$status"
