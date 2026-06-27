"""Helpers for working with long policy documents."""

from __future__ import annotations

_KEYWORDS = (
    "flood",
    "water damage",
    "exclusion",
    "deductible",
    "coverage a",
    "dwelling",
    "perils insured",
)


def excerpt_for_ingest(text: str, max_chars: int = 12_000) -> str:
    """Prefer header plus flood/coverage sections for long regulatory forms."""
    if len(text) <= max_chars:
        return text

    header = text[:4000]
    lower = text.lower()
    snippets: list[str] = []
    for kw in _KEYWORDS:
        pos = lower.find(kw)
        if pos == -1:
            continue
        start = max(0, pos - 400)
        end = min(len(text), pos + 1200)
        snippets.append(text[start:end])

    combined = header + "\n\n--- KEY EXCERPTS ---\n\n" + "\n\n".join(snippets)
    return combined[:max_chars]
