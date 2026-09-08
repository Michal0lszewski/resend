#!/usr/bin/env bash
set -euo pipefail

PIDS=$(pgrep -f "uvicorn app.main:app" || true)

if [ -z "$PIDS" ]; then
  echo "No running instance found."
  exit 0
fi

echo "Stopping: $PIDS"
kill $PIDS
