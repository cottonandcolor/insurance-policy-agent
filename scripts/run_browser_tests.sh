#!/usr/bin/env bash
# Install deps, start servers via Playwright, run browser E2E tests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Missing venv. Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

# Node for frontend + e2e
if ! command -v npm >/dev/null 2>&1; then
  if [[ -x "$ROOT/.node/bin/npm" ]]; then
    export PATH="$ROOT/.node/bin:$PATH"
  else
    echo "npm not found. Install Node.js 18+ or use capstone/.node"
    exit 1
  fi
fi

if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  echo "==> npm install (frontend)"
  (cd "$ROOT/frontend" && npm install)
fi

echo "==> npm install (e2e / Playwright)"
(cd "$ROOT/e2e" && npm install)
(cd "$ROOT/e2e" && npx playwright install chromium)

echo "==> Playwright E2E tests"
(cd "$ROOT/e2e" && npm test)

echo "==> Browser tests passed"
