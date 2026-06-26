"""Direct LLM client for Ollama and OpenAI (no CrewAI dependency)."""

from __future__ import annotations

import httpx

from src.config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OPENROUTER_APP_NAME,
    OPENROUTER_SITE_URL,
)


def complete(system: str, user: str, temperature: float = 0.0) -> str:
    if LLM_PROVIDER == "ollama":
        return _ollama_complete(system, user, temperature)
    if LLM_PROVIDER == "openai":
        return _openai_complete(system, user, temperature)
    raise ValueError("LLM not configured. Set LLM_PROVIDER=ollama|openai.")


def _ollama_complete(system: str, user: str, temperature: float) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": temperature},
    }
    with httpx.Client(timeout=300.0) as client:
        resp = client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
    message = data.get("message") or {}
    return str(message.get("content", "")).strip()


def _openai_complete(system: str, user: str, temperature: float) -> str:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    if "openrouter.ai" in OPENAI_BASE_URL:
        headers["HTTP-Referer"] = OPENROUTER_SITE_URL
        headers["X-OpenRouter-Title"] = OPENROUTER_APP_NAME
    with httpx.Client(timeout=300.0) as client:
        resp = client.post(
            f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        return ""
    return str(choices[0].get("message", {}).get("content", "")).strip()
