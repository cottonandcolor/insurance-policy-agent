#!/usr/bin/env python3
"""
Insurance Policy Comparison Agent — CrewAI + LangGraph

Steps implemented:
  1. Profile intake        (CrewAI Profile Intake Agent)
  2. Index + ingest        (Chroma retrieval + CrewAI Document Agent)
  3. ToT beam loop         (CrewAI Reasoning + Critic, LangGraph orchestrator)
  4. Synthesis             (CrewAI Recommendation Synthesizer)

Examples:
  python main.py --dry-run              # no API key required
  python main.py                        # uses OPENAI_API_KEY
  python main.py --build-index          # rebuild Chroma index only
  python -m pytest tests/ -q            # unit tests
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


def build_initial_state(args: argparse.Namespace) -> dict:
    return {
        "dry_run": args.dry_run,
        "user_messages": [
            "I'm 35, live in a flood zone in Cedar Park TX, own a $350K home.",
            "Priorities: broad coverage 0.4, low cost 0.3, few exclusions 0.3.",
        ],
        "policy_paths": args.policies or DEFAULT_POLICIES,
        "llm_call_count": 0,
        "max_llm_calls": args.max_llm_calls,
        "beam_width": args.beam_width,
        "max_depth": args.max_depth,
        "start_depth": args.start_depth,
        "retrieval_cache": {},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Insurance comparison agent")
    parser.add_argument("--dry-run", action="store_true", help="Run without OpenAI API")
    parser.add_argument("--build-index", action="store_true", help="Build Chroma index only")
    parser.add_argument("--policies", nargs="*", help="Paths to synthetic policy .txt files")
    parser.add_argument("--beam-width", type=int, default=3)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--max-llm-calls", type=int, default=25)
    parser.add_argument("--start-depth", type=int, default=1, help="For follow-up re-entry")
    parser.add_argument("--json", action="store_true", help="Print full state as JSON")
    args = parser.parse_args()

    if args.build_index:
        from src.tools.retrieval import build_index

        count = build_index()
        print(f"Indexed {count} chunks.")
        return

    from src.graph.workflow import build_graph

    app = build_graph()
    state = build_initial_state(args)

    print("Starting workflow...")
    print(f"  mode={'dry-run' if args.dry_run else 'live'}")
    print(f"  policies={state['policy_paths']}")
    print(f"  beam_width={state['beam_width']} max_depth={state['max_depth']}\n")

    result = app.invoke(state, config={"recursion_limit": 50})

    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "retrieval_cache"}, indent=2, default=str))
    else:
        print("\n=== FINAL RECOMMENDATION ===\n")
        print(result.get("final_recommendation") or result.get("error"))
        print(f"\nLLM calls: {result.get('llm_call_count', 0)}")
        if result.get("winning_branch"):
            wb = result["winning_branch"]
            print(f"Winning branch: {wb.get('branch_id')} (score={wb.get('composite_score')})")


if __name__ == "__main__":
    main()
