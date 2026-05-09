#!/usr/bin/env bash
# Run the survey app locally.
#
# Loads env vars from .env at the repo root (if present), puts the
# project's venv on PATH, then delegates to research/start.sh. Defaults
# to port 8502 so it can run alongside dev_agent.sh on 8501.
#
# Usage:
#   bash dev_research.sh
#   PORT=9001 bash dev_research.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.env"
    set +a
else
    echo "warning: $SCRIPT_DIR/.env not found — start.sh will write empty secrets" >&2
fi

if [ -d "$SCRIPT_DIR/.venv/bin" ]; then
    export PATH="$SCRIPT_DIR/.venv/bin:$PATH"
else
    echo "warning: no .venv at $SCRIPT_DIR/.venv — using system Python" >&2
fi

export PORT="${PORT:-8502}"

exec bash "$SCRIPT_DIR/research/start.sh"
