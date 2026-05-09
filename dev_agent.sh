#!/usr/bin/env bash
# Run the agent app locally.
#
# Loads env vars from .env at the repo root (if present), puts the
# project's venv on PATH, then delegates to agent/start.sh. start.sh
# handles secrets.toml generation and the streamlit invocation, just
# like Railway does in production.
#
# Usage:
#   bash dev_agent.sh
#   PORT=9000 bash dev_agent.sh   # override default port
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

export PORT="${PORT:-8501}"

exec bash "$SCRIPT_DIR/agent/start.sh"
