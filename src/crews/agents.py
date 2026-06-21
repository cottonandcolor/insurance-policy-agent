"""CrewAI agent definitions with pluggable LLM providers."""

from __future__ import annotations

from crewai import Agent, LLM

from src.config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    get_llm_mode_label,
)


def _llm() -> LLM:
    if LLM_PROVIDER == "ollama":
        return LLM(
            model=f"ollama/{OLLAMA_MODEL}",
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )
    if LLM_PROVIDER == "openai":
        return LLM(
            model=f"openai/{OPENAI_MODEL}",
            api_key=OPENAI_API_KEY,
            temperature=0,
        )
    raise ValueError(
        "LLM not configured for dry_run. Set dry_run=True in run_agent() "
        "or set LLM_PROVIDER=ollama|openai."
    )


def profile_intake_agent() -> Agent:
    return Agent(
        role="Profile Intake Specialist",
        goal=(
            "Collect user age, location, assets, existing coverage, flood-zone risk, "
            "and priority weights. Output ONLY valid JSON."
        ),
        backstory="Structured insurance intake interviewer.",
        llm=_llm(),
        verbose=True,
    )


def document_retrieval_agent() -> Agent:
    return Agent(
        role="Document and Retrieval Analyst",
        goal=(
            "Extract coverage limits, deductibles, exclusions, riders from policy text. "
            "Output ONLY valid JSON matching the normalized plan schema."
        ),
        backstory="Policy normalization specialist with citation discipline.",
        llm=_llm(),
        verbose=True,
    )


def scenario_reasoning_agent() -> Agent:
    return Agent(
        role="Scenario Reasoning Analyst",
        goal=(
            "Generate up to 3 alternative interpretation branches with flood scenario "
            "thoughts. Output ONLY a JSON array."
        ),
        backstory="Explores ambiguous policy language using evidence only.",
        llm=_llm(),
        verbose=True,
    )


def policy_critic_agent() -> Agent:
    return Agent(
        role="Policy Critic",
        goal="Score branches and return ONLY a JSON array of evaluations.",
        backstory="Adversarial reviewer; rejects uncited claims.",
        llm=_llm(),
        verbose=True,
    )


def recommendation_synthesizer_agent() -> Agent:
    return Agent(
        role="Recommendation Synthesizer",
        goal="Produce markdown comparison and recommendation from validated branch only.",
        backstory="Consumer-facing writer; no new coverage claims.",
        llm=_llm(),
        verbose=True,
    )
