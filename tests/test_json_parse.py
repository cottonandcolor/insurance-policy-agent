"""Tests for LLM JSON extraction."""

from src.utils.json_parse import extract_json


def test_extract_json_plain_object():
    assert extract_json('{"age": 35}') == {"age": 35}


def test_extract_json_fenced_codeblock():
    raw = 'Here is the result:\n```json\n{"plan_id": "plan_a"}\n```'
    assert extract_json(raw) == {"plan_id": "plan_a"}


def test_extract_json_array():
    assert extract_json('[{"branch_id": "b1"}]') == [{"branch_id": "b1"}]


def test_extract_json_embedded_in_prose():
    raw = 'Analysis complete. {"ok": true} Thanks.'
    assert extract_json(raw) == {"ok": True}


def test_extract_json_empty_returns_empty_dict():
    assert extract_json("") == {}
    assert extract_json("   ") == {}


def test_extract_json_invalid_returns_raw_wrapper():
    result = extract_json("not json at all")
    assert result == {"raw": "not json at all"}
