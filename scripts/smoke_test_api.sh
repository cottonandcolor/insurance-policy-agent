#!/usr/bin/env bash
# Quick HTTP smoke test against a running API (default http://127.0.0.1:8000).
set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8000}"

echo "==> Health"
curl -sf "$API_BASE/api/health" | python3 -m json.tool

echo "==> Models"
curl -sf "$API_BASE/api/models" | python3 -m json.tool

echo "==> Analyze (dry-run, quick)"
curl -sf -X POST "$API_BASE/api/analyze?dry_run=true&quick=true" \
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
assert d.get('mode') == 'dry_run', d
assert d.get('recommendation'), 'missing recommendation'
assert 'plan_b' in d['recommendation'].lower(), d['recommendation'][:200]
print('OK mode=', d['mode'], 'llm_calls=', d.get('llm_call_count'))
"

echo "==> Smoke test passed"
