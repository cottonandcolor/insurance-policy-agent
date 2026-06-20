"""Run CrewAI crews and parse structured output."""

from __future__ import annotations

from crewai import Crew, Process

from src.crews.tasks import (
    critic_task,
    ingest_task,
    intake_task,
    reasoning_task,
    synthesize_task,
)
from src.utils.json_parse import extract_json


def run_intake(user_messages: list[str]) -> dict:
    task = intake_task(user_messages)
    crew = Crew(agents=[task.agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    parsed = extract_json(str(result.raw))
    return parsed if isinstance(parsed, dict) else {}


def run_ingest(policy_text: str, plan_id: str) -> dict:
    task = ingest_task(policy_text, plan_id)
    crew = Crew(agents=[task.agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    parsed = extract_json(str(result.raw))
    if isinstance(parsed, dict):
        parsed.setdefault("plan_id", plan_id)
        return parsed
    return {"plan_id": plan_id, "raw": str(result.raw)}


def run_reasoning(context: dict, depth: int) -> list[dict]:
    task = reasoning_task(context, depth)
    crew = Crew(agents=[task.agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    parsed = extract_json(str(result.raw))
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [parsed]
    return []


def run_critic(branches: list[dict], profile: dict) -> list[dict]:
    task = critic_task(branches, profile)
    crew = Crew(agents=[task.agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    parsed = extract_json(str(result.raw))
    return parsed if isinstance(parsed, list) else []


def run_synthesize(winning_branch: dict, plans: list[dict]) -> str:
    task = synthesize_task(winning_branch, plans)
    crew = Crew(agents=[task.agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    return str(result.raw)
