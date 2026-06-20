"""Application configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
POLICY_DATA_DIR = Path(os.getenv("POLICY_DATA_DIR", ROOT / "data" / "synthetic"))
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", ROOT / "data" / "chroma"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

BEAM_WIDTH = 3
MAX_DEPTH = 4
MAX_LLM_CALLS = 25
PRUNE_THRESHOLD_EARLY = 0.55
PRUNE_THRESHOLD_LATE = 0.65
