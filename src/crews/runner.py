"""Run agent steps via direct LLM calls (Ollama or OpenAI)."""

from __future__ import annotations

from src.llm.client import complete
from src.llm.prompts import (
    critic_prompt,
    ingest_prompt,
    intake_prompt,
    reasoning_prompt,
    synthesize_prompt,
)
from src.utils.json_parse import extract_json


def run_intake(user_messages: list[str]) -> dict:
    system, user = intake_prompt(user_messages)
    raw = complete(system, user)
    parsed = extract_json(raw)
    return parsed if isinstance(parsed, dict) else {}


def run_ingest(policy_text: str, plan_id: str) -> dict:
    system, user = ingest_prompt(policy_text, plan_id)
    raw = complete(system, user)
    parsed = extract_json(raw)
    if isinstance(parsed, dict):
        parsed.setdefault("plan_id", plan_id)
        return parsed
    return {"plan_id": plan_id, "raw": raw}


def run_reasoning(context: dict, depth: int) -> list[dict]:
    system, user = reasoning_prompt(context, depth)
    raw = complete(system, user)
    parsed = extract_json(raw)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [parsed]
    return []


def run_critic(branches: list[dict], profile: dict) -> list[dict]:
    system, user = critic_prompt(branches, profile)
    raw = complete(system, user)
    parsed = extract_json(raw)
    return parsed if isinstance(parsed, list) else []


def run_synthesize(winning_branch: dict, plans: list[dict]) -> str:
    system, user = synthesize_prompt(winning_branch, plans)
    return complete(system, user)
