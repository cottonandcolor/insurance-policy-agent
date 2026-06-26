"""Application configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
POLICY_DATA_DIR = Path(os.getenv("POLICY_DATA_DIR", ROOT / "data" / "synthetic"))
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", ROOT / "data" / "chroma"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", ROOT / "data" / "uploads"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "insurance-policy-agent")

BEAM_WIDTH = 3
MAX_DEPTH = 4
MAX_LLM_CALLS = 25
PRUNE_THRESHOLD_EARLY = 0.55
PRUNE_THRESHOLD_LATE = 0.65

MAX_UPLOAD_FILES = 3
MAX_UPLOAD_BYTES = 500_000


def get_llm_mode_label() -> str:
    if LLM_PROVIDER == "ollama":
        return f"ollama/{OLLAMA_MODEL}"
    if LLM_PROVIDER == "openai":
        return f"openai/{OPENAI_MODEL}"
    return "dry_run"
