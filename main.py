#!/usr/bin/env python3
"""
Insurance Policy Comparison Agent — CrewAI + LangGraph

Examples:
  python main.py --dry-run
  python main.py
  python main.py --build-index
  python -m pytest tests/ -q
  uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
DEFAULT_POLICIES = [
    str(ROOT / "data" / "synthetic" / "plan_a.txt"),
    str(ROOT / "data" / "synthetic" / "plan_b.txt"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Insurance comparison agent")
    parser.add_argument("--dry-run", action="store_true", help="Run without LLM API")
    parser.add_argument("--build-index", action="store_true", help="Build Chroma index only")
    parser.add_argument("--policies", nargs="*", help="Paths to policy .txt files")
    parser.add_argument("--beam-width", type=int, default=3)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--max-llm-calls", type=int, default=25)
    parser.add_argument("--start-depth", type=int, default=1)
    parser.add_argument("--json", action="store_true", help="Print full state as JSON")
    args = parser.parse_args()

    if args.build_index:
        from src.tools.retrieval import build_index

        print(f"Indexed {build_index()} chunks.")
        return

    from src.runner import format_response, run_agent

    print("Starting workflow...")
    print(f"  mode={'dry-run' if args.dry_run else 'live'}")
    print(f"  policies={args.policies or DEFAULT_POLICIES}")
    print(f"  beam_width={args.beam_width} max_depth={args.max_depth}\n")

    result = run_agent(
        policy_paths=args.policies or DEFAULT_POLICIES,
        dry_run=args.dry_run,
        beam_width=args.beam_width,
        max_depth=args.max_depth,
        max_llm_calls=args.max_llm_calls,
        start_depth=args.start_depth,
    )

    if args.json:
        payload = format_response(result)
        print(json.dumps(payload, indent=2, default=str))
    else:
        print("\n=== FINAL RECOMMENDATION ===\n")
        print(result.get("final_recommendation") or result.get("error"))
        print(f"\nLLM calls: {result.get('llm_call_count', 0)}")
        print(f"Mode: {result.get('mode')}")
        if result.get("winning_branch"):
            wb = result["winning_branch"]
            print(f"Winning branch: {wb.get('branch_id')} (score={wb.get('composite_score')})")


if __name__ == "__main__":
    main()
