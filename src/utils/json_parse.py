"""Extract JSON from LLM / CrewAI raw output."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_json(raw: str) -> Any:
    text = raw.strip()
    if not text:
        return {}

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            pass

    for opener, closer in [("{", "}"), ("[", "]")]:
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue

    return {"raw": text}
