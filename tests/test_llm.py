"""Tests for direct Ollama/OpenAI HTTP client."""

from unittest.mock import MagicMock, patch

import pytest

from src.llm import client as llm_client


def test_ollama_complete_parses_message():
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": {"content": "  hello world  "}}
    mock_response.raise_for_status = MagicMock()

    mock_http = MagicMock()
    mock_http.post.return_value = mock_response
    mock_http.__enter__ = MagicMock(return_value=mock_http)
    mock_http.__exit__ = MagicMock(return_value=False)

    with patch.object(llm_client, "LLM_PROVIDER", "ollama"), patch.object(
        llm_client, "OLLAMA_BASE_URL", "http://localhost:11434"
    ), patch.object(llm_client, "OLLAMA_MODEL", "mistral"), patch(
        "src.llm.client.httpx.Client", return_value=mock_http
    ):
        result = llm_client.complete("system", "user")

    assert result == "hello world"
    mock_http.post.assert_called_once()
    payload = mock_http.post.call_args.kwargs["json"]
    assert payload["model"] == "mistral"
    assert payload["messages"][0]["role"] == "system"


def test_openai_complete_requires_api_key():
    with patch.object(llm_client, "LLM_PROVIDER", "openai"), patch.object(
        llm_client, "OPENAI_API_KEY", ""
    ):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            llm_client.complete("system", "user")


def test_openai_complete_parses_choice():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "recommend plan_b"}}]
    }
    mock_response.raise_for_status = MagicMock()

    mock_http = MagicMock()
    mock_http.post.return_value = mock_response
    mock_http.__enter__ = MagicMock(return_value=mock_http)
    mock_http.__exit__ = MagicMock(return_value=False)

    with patch.object(llm_client, "LLM_PROVIDER", "openai"), patch.object(
        llm_client, "OPENAI_API_KEY", "sk-test"
    ), patch.object(llm_client, "OPENAI_MODEL", "gpt-4o-mini"), patch(
        "src.llm.client.httpx.Client", return_value=mock_http
    ):
        result = llm_client.complete("system", "user")

    assert result == "recommend plan_b"
    headers = mock_http.post.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer sk-test"
