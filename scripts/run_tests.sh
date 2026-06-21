#!/usr/bin/env bash
# Run the full pytest suite for the insurance policy agent.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> Running pytest"
python -m pytest tests/ -v --tb=short "$@"
