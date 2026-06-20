"""Section-aware chunking for policy documents."""

from __future__ import annotations

import re
from pathlib import Path

from src.schemas import RetrievedChunk


SECTION_RE = re.compile(r"^(Section [A-Z0-9]+[^\n]*)", re.MULTILINE)
PERIL_KEYWORDS = {
    "flood": ["flood", "surface water", "water backup"],
    "fire": ["fire", "smoke"],
    "theft": ["theft", "burglary"],
    "liability": ["liability", "lawsuit"],
    "wind": ["wind", "hail", "named storm"],
}


def infer_peril_tags(text: str) -> list[str]:
    lower = text.lower()
    return [peril for peril, words in PERIL_KEYWORDS.items() if any(w in lower for w in words)]


def chunk_policy_file(path: Path) -> list[RetrievedChunk]:
    plan_id = path.stem
    text = path.read_text(encoding="utf-8")
    jurisdiction = "TX"
    for line in text.splitlines():
        if line.lower().startswith("jurisdiction:"):
            jurisdiction = line.split(":", 1)[1].strip()
            break

    sections = SECTION_RE.split(text)
    chunks: list[RetrievedChunk] = []

    if len(sections) <= 1:
        chunks.append(
            RetrievedChunk(
                chunk_id=f"{plan_id}:0",
                plan_id=plan_id,
                section="Full Document",
                jurisdiction=jurisdiction,
                text=text.strip(),
                peril_tags=infer_peril_tags(text),
            )
        )
        return chunks

    # sections pattern: [preamble, header1, body1, header2, body2, ...]
    idx = 0
    if sections[0].strip():
        chunks.append(
            RetrievedChunk(
                chunk_id=f"{plan_id}:{idx}",
                plan_id=plan_id,
                section="Preamble",
                jurisdiction=jurisdiction,
                text=sections[0].strip(),
                peril_tags=infer_peril_tags(sections[0]),
            )
        )
        idx += 1

    for i in range(1, len(sections), 2):
        header = sections[i].strip()
        body = sections[i + 1].strip() if i + 1 < len(sections) else ""
        content = f"{header}\n{body}".strip()
        if not content:
            continue
        chunks.append(
            RetrievedChunk(
                chunk_id=f"{plan_id}:{idx}",
                plan_id=plan_id,
                section=header,
                jurisdiction=jurisdiction,
                text=content,
                peril_tags=infer_peril_tags(content),
            )
        )
        idx += 1

    return chunks
