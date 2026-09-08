#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

uv run uvicorn app.main:app --reload --port 8000
