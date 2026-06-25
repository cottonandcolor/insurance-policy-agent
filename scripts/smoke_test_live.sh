#!/usr/bin/env bash
# Optional live Ollama smoke test against a running API (default http://127.0.0.1:8000).
# Skips gracefully if Ollama is not reachable. Expect ~3-5 minutes.
set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8000}"

echo "==> Health (checking Ollama)"
health=$(curl -sf "$API_BASE/api/health")
echo "$health" | python3 -m json.tool

reachable=$(echo "$health" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ollama_reachable', False))")
if [[ "$reachable" != "True" ]]; then
  echo "SKIP: Ollama not reachable. Start with: ollama serve"
  exit 0
fi

echo "==> Analyze (live Ollama, quick mode) — this may take several minutes"
curl -sf -X POST "$API_BASE/api/analyze?dry_run=false&quick=true" \
  -F "use_defaults=true" \
  -F "age=35" \
  -F "location=Cedar Park, TX" \
  -F "flood_zone=true" \
  -F "home_value=350000" \
  -F "coverage_breadth=0.4" \
  -F "low_cost=0.3" \
  -F "few_exclusions=0.3" \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('mode') != 'dry_run', d
assert d.get('recommendation'), 'missing recommendation'
print('OK mode=', d.get('mode'), 'llm_calls=', d.get('llm_call_count'))
print('preview:', (d.get('recommendation') or '')[:200])
"

echo "==> Live smoke test passed"
