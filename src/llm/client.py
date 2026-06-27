"""Direct LLM client for Ollama and OpenAI (no CrewAI dependency)."""

from __future__ import annotations

import time

import httpx

from src.config import (
    LLM_CONNECT_TIMEOUT,
    LLM_MAX_RETRIES,
    LLM_PROVIDER,
    LLM_READ_TIMEOUT,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OPENROUTER_APP_NAME,
    OPENROUTER_SITE_URL,
)


class LLMRequestError(Exception):
    """Raised when the LLM HTTP API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


def complete(system: str, user: str, temperature: float = 0.0) -> str:
    if LLM_PROVIDER == "ollama":
        return _ollama_complete(system, user, temperature)
    if LLM_PROVIDER == "openai":
        return _openai_complete(system, user, temperature)
    raise ValueError("LLM not configured. Set LLM_PROVIDER=ollama|openai.")


def _http_timeout() -> httpx.Timeout:
    return httpx.Timeout(
        LLM_READ_TIMEOUT,
        connect=LLM_CONNECT_TIMEOUT,
        read=LLM_READ_TIMEOUT,
        write=60.0,
        pool=30.0,
    )


def _post_json(
    client: httpx.Client,
    url: str,
    *,
    json: dict,
    headers: dict | None = None,
    label: str = "LLM",
) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            resp = client.post(url, json=json, headers=headers)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status == 429 and attempt < LLM_MAX_RETRIES:
                wait = 20 * attempt
                print(
                    f"{label} rate limit (attempt {attempt}/{LLM_MAX_RETRIES}); "
                    f"retrying in {wait}s...",
                    flush=True,
                )
                time.sleep(wait)
                last_exc = exc
                continue
            if status == 429:
                msg = (
                    f"{label} rate limit (429). OpenRouter free tier may be exhausted — "
                    "wait a few minutes and retry, or set a different OPENAI_MODEL in .env."
                )
            else:
                msg = f"{label} API error ({status})."
            raise LLMRequestError(msg, status_code=status) from exc
        except (httpx.ReadTimeout, httpx.ConnectTimeout) as exc:
            last_exc = exc
            if attempt >= LLM_MAX_RETRIES:
                break
            wait = 5 * attempt
            print(
                f"{label} timeout (attempt {attempt}/{LLM_MAX_RETRIES}); "
                f"retrying in {wait}s...",
                flush=True,
            )
            time.sleep(wait)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"{label} request failed")


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
    with httpx.Client(timeout=_http_timeout()) as client:
        resp = _post_json(
            client,
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            label="Ollama",
        )
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
    with httpx.Client(timeout=_http_timeout()) as client:
        resp = _post_json(
            client,
            f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
            label="OpenRouter" if "openrouter.ai" in OPENAI_BASE_URL else "OpenAI",
        )
        data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        return ""
    return str(choices[0].get("message", {}).get("content", "")).strip()
