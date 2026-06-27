"""Persist session metadata and workflow artifacts between API turns."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import ROOT

SESSION_DIR = Path(ROOT / "data" / "sessions")
SESSION_DIR.mkdir(parents=True, exist_ok=True)


def _session_path(thread_id: str) -> Path:
    safe = "".join(c for c in thread_id if c.isalnum() or c in "-_")
    return SESSION_DIR / f"{safe}.json"


def save_session(thread_id: str, payload: dict[str, Any]) -> None:
    data = {"thread_id": thread_id, **payload}
    _session_path(thread_id).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_session(thread_id: str) -> dict[str, Any] | None:
    path = _session_path(thread_id)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
