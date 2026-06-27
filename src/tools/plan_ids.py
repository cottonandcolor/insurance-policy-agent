"""Map LLM plan aliases to normalized plan_id values."""

from __future__ import annotations

_ALIAS_INDEX = {
    "plan_a": 0,
    "plana": 0,
    "policy_a": 0,
    "plan_1": 0,
    "plan1": 0,
    "plan_b": 1,
    "planb": 1,
    "policy_b": 1,
    "plan_2": 1,
    "plan2": 1,
}


def resolve_plan_id(raw_id: str, plan_ids: list[str]) -> str:
    """Resolve plan_a/plan_b aliases to actual stems (e.g. travelers_ho3_nv)."""
    if not plan_ids:
        return raw_id
    if raw_id in plan_ids:
        return raw_id

    key = raw_id.lower().strip().replace(" ", "_").replace("-", "_")
    if key in _ALIAS_INDEX:
        idx = _ALIAS_INDEX[key]
        if idx < len(plan_ids):
            return plan_ids[idx]

    lower = raw_id.lower()
    for pid in plan_ids:
        stem = pid.lower()
        if lower in stem or stem in lower:
            return pid
    return raw_id
