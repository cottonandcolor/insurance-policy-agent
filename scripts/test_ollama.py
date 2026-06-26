#!/usr/bin/env python3
"""
Verify Ollama is running and mistral responds.

Usage (from capstone project root, venv active):
  python scripts/test_ollama.py
  python scripts/test_ollama.py --full    # also test capstone LLM client
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"OK   {msg}")


def check_server(client: httpx.Client) -> list[str]:
    print(f"\n1. Ollama server ({OLLAMA_BASE_URL})")
    try:
        resp = client.get(f"{OLLAMA_BASE_URL}/api/tags")
        resp.raise_for_status()
    except httpx.ConnectError:
        fail(
            "Cannot connect. Is Ollama running? "
            "Open the Ollama Mac app or run: ollama serve"
        )
    except httpx.HTTPError as exc:
        fail(f"HTTP error: {exc}")

    data = resp.json()
    models = [m.get("name", "") for m in data.get("models", [])]
    if not models:
        fail("Server is up but no models listed. Run: ollama pull mistral")
    ok(f"reachable — {len(models)} model(s) installed")
    for name in models:
        print(f"     · {name}")
    return models


def model_installed(models: list[str], target: str) -> bool:
    target = target.lower()
    return any(target in m.lower() for m in models)


def check_chat(client: httpx.Client) -> None:
    print(f"\n2. Chat test (model: {OLLAMA_MODEL})")
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": "Reply with exactly one word: ready"}],
        "stream": False,
        "options": {"temperature": 0},
    }
    started = time.perf_counter()
    try:
        resp = client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        fail(f"Chat request failed: {exc}")

    elapsed = time.perf_counter() - started
    reply = (resp.json().get("message") or {}).get("content", "").strip()
    if not reply:
        fail("Empty response from model")
    ok(f"reply in {elapsed:.1f}s — {reply[:120]!r}")


def check_capstone_client() -> None:
    print("\n3. Capstone LLM client (src.llm.client.complete)")
    from src.llm.client import complete

    started = time.perf_counter()
    try:
        reply = complete(
            "You are a test assistant.",
            'Respond with valid JSON only: {"status": "ok"}',
            temperature=0,
        )
    except Exception as exc:
        fail(f"complete() failed: {exc}")

    elapsed = time.perf_counter() - started
    if not reply:
        fail("complete() returned empty string")
    ok(f"complete() in {elapsed:.1f}s — preview: {reply[:100]!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Ollama + mistral for capstone")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also run capstone complete() wrapper (slower)",
    )
    args = parser.parse_args()

    print("Ollama smoke test")
    print(f"  base_url = {OLLAMA_BASE_URL}")
    print(f"  model    = {OLLAMA_MODEL}")

    with httpx.Client(timeout=120.0) as client:
        models = check_server(client)
        if not model_installed(models, OLLAMA_MODEL):
            fail(f"Model '{OLLAMA_MODEL}' not found. Run: ollama pull {OLLAMA_MODEL}")
        ok(f"model '{OLLAMA_MODEL}' is available")
        check_chat(client)

    if args.full:
        check_capstone_client()

    print("\nAll checks passed. Ollama is ready for live analysis in the UI.")
    print("Tip: uncheck Dry-run, keep Quick mode, click Analyze Plans (3–5 min).")


if __name__ == "__main__":
    main()
