from __future__ import annotations

import json
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

import pytest

from backend.app.modules.ai_runtime.providers.base import LLMProviderError, LLMProviderRequest
from backend.app.modules.ai_runtime.providers.factory import create_llm_provider
from backend.app.modules.ai_runtime.providers.openai_responses_provider import OpenAIResponsesProvider


class FakeHTTPResponse:
    status = 200

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def __enter__(self) -> FakeHTTPResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def close(self) -> None:
        return None


@pytest.fixture(autouse=True)
def isolate_model_connection_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHTEST_MODEL_CONNECTION_PATH", str(tmp_path / "missing-model-connection.json"))


def test_openai_responses_provider_posts_responses_request_and_records_artifacts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: urllib.request.Request, timeout: int) -> FakeHTTPResponse:
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["authorization"] = request.get_header("Authorization")
        captured["accept"] = request.get_header("Accept")
        captured["user_agent"] = request.get_header("User-agent")
        captured["payload"] = json.loads(request.data.decode("utf-8")) if request.data else {}
        return FakeHTTPResponse(
            {
                "id": "resp_123",
                "output": [
                    {
                        "content": [
                                {
                                    "type": "output_text",
                                    "text": json.dumps(
                                        {
                                            "overall_score": 88,
                                            "scores": {
                                                "completeness": 90,
                                                "clarity": 85,
                                                "consistency": 90,
                                                "testability": 88,
                                                "feasibility": 90,
                                                "logic": 85,
                                            },
                                            "issues": [],
                                            "clarification_questions": [],
                                            "test_design_notes": ["Cover coupon success and rejection paths."],
                                            "risk_items": [],
                                        },
                                    ),
                                },
                        ],
                    },
                ],
                "usage": {
                    "input_tokens": 11,
                    "output_tokens": 7,
                    "total_tokens": 18,
                },
            },
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    provider = OpenAIResponsesProvider(
        base_url="https://api.example.test",
        api_key="test-key",
        timeout_seconds=12,
    )

    response = provider.generate(
        LLMProviderRequest(
            task_type="requirement_review",
            model_name="gpt-test",
            input_json={"requirement": "Review checkout coupon rules."},
            context_artifact_ids=[uuid.UUID("00000000-0000-0000-0000-000000000371")],
        ),
    )

    assert captured["url"] == "https://api.example.test/v1/responses"
    assert captured["timeout"] == 12
    assert captured["authorization"] == "Bearer test-key"
    assert captured["accept"] == "application/json"
    assert captured["user_agent"] == "chtest-ai-runtime/0.1"
    assert captured["payload"]["model"] == "gpt-test"
    assert captured["payload"]["max_output_tokens"] == 800
    assert captured["payload"]["reasoning"] == {"effort": "low"}
    assert captured["payload"]["text"] == {"format": {"type": "json_object"}}
    assert "Review checkout coupon rules." in captured["payload"]["input"]
    assert response.provider == "openai"
    assert response.status == "succeeded"
    assert response.output_json["overall_score"] == 88
    assert response.output_json["provider_response_id"] == "resp_123"
    assert response.output_json["used_context_artifact_ids"] == ["00000000-0000-0000-0000-000000000371"]
    assert response.token_usage_json == {
        "prompt_tokens": 11,
        "completion_tokens": 7,
        "total_tokens": 18,
    }
    assert {artifact.file_name for artifact in response.artifacts} == {
        "raw_output.json",
        "parsed_output.json",
        "schema_validation.json",
    }


def test_openai_responses_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAIResponsesProvider(base_url="https://api.example.test")

    with pytest.raises(LLMProviderError, match="requires LLM_API_KEY"):
        provider.generate(
            LLMProviderRequest(
                task_type="requirement_review",
                model_name="gpt-test",
                input_json={},
            ),
        )


def test_openai_responses_provider_falls_back_to_chat_completions_when_responses_has_no_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_urls: list[str] = []
    captured_payloads: list[dict[str, Any]] = []

    def fake_urlopen(request: urllib.request.Request, timeout: int) -> FakeHTTPResponse:
        captured_urls.append(request.full_url)
        captured_payloads.append(json.loads(request.data.decode("utf-8")) if request.data else {})
        if request.full_url.endswith("/responses"):
            return FakeHTTPResponse(
                {
                    "id": "resp_reasoning_only",
                    "status": "completed",
                    "output": [{"type": "reasoning", "content": []}],
                    "usage": {"input_tokens": 10, "output_tokens": 8, "total_tokens": 18},
                },
            )
        return FakeHTTPResponse(
            {
                "id": "chat_123",
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "overall_score": 90,
                                    "scores": {
                                        "completeness": 90,
                                        "clarity": 90,
                                        "consistency": 90,
                                        "testability": 90,
                                        "feasibility": 90,
                                        "logic": 90,
                                    },
                                    "issues": [],
                                    "clarification_questions": [],
                                    "test_design_notes": [],
                                    "risk_items": [],
                                },
                            ),
                        },
                    },
                ],
                "usage": {"prompt_tokens": 20, "completion_tokens": 12, "total_tokens": 32},
            },
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    provider = OpenAIResponsesProvider(
        base_url="https://gateway.example.test/v1",
        api_key="test-key",
        wire_api="responses",
    )

    response = provider.generate(
        LLMProviderRequest(
            task_type="requirement_review",
            model_name="gpt-test",
            input_json={"requirement": "Review coupon boundaries."},
        ),
    )

    assert captured_urls == [
        "https://gateway.example.test/v1/responses",
        "https://gateway.example.test/v1/chat/completions",
    ]
    assert captured_payloads[1]["reasoning_effort"] == "low"
    assert response.status == "succeeded"
    assert response.output_json["overall_score"] == 90
    assert response.token_usage_json == {
        "prompt_tokens": 20,
        "completion_tokens": 12,
        "total_tokens": 32,
    }
    assert {artifact.file_name for artifact in response.artifacts} == {
        "raw_responses_output.json",
        "raw_output.json",
        "parsed_output.json",
        "schema_validation.json",
    }


def test_openai_responses_provider_falls_back_to_chat_completions_on_recoverable_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_urls: list[str] = []

    def fake_urlopen(request: urllib.request.Request, timeout: int) -> FakeHTTPResponse:
        captured_urls.append(request.full_url)
        if request.full_url.endswith("/responses"):
            raise urllib.error.HTTPError(
                request.full_url,
                524,
                "Gateway Timeout",
                hdrs={},
                fp=None,
            )
        return FakeHTTPResponse(
            {
                "id": "chat_524_fallback",
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "cases": [
                                        {
                                            "title": "NFC fallback path",
                                            "priority": "P1",
                                            "test_type": "functional",
                                            "precondition": "NFC is unavailable.",
                                            "steps": ["Open Add card."],
                                            "expected_results": ["Legacy card flow is shown."],
                                            "requirement_refs": ["REQ-NFC"],
                                            "risk_refs": [],
                                            "input_data": {},
                                            "tags": ["nfc"],
                                            "ai_reason": "Covers no-NFC fallback.",
                                            "source_knowledge_evidence": [],
                                        },
                                    ],
                                    "used_knowledge": False,
                                    "used_context_artifact_ids": [],
                                },
                            ),
                        },
                    },
                ],
                "usage": {"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50},
            },
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    provider = OpenAIResponsesProvider(
        base_url="https://gateway.example.test/v1",
        api_key="test-key",
        wire_api="responses",
    )

    response = provider.generate(
        LLMProviderRequest(
            task_type="case_generation",
            model_name="gpt-test",
            input_json={"requirement": "Generate NFC tests."},
        ),
    )

    assert captured_urls == [
        "https://gateway.example.test/v1/responses",
        "https://gateway.example.test/v1/chat/completions",
    ]
    assert response.status == "succeeded"
    assert response.output_json["cases"][0]["title"] == "NFC fallback path"
    assert response.token_usage_json == {
        "prompt_tokens": 30,
        "completion_tokens": 20,
        "total_tokens": 50,
    }
    assert {artifact.file_name for artifact in response.artifacts} == {
        "raw_responses_error.json",
        "raw_output.json",
        "parsed_output.json",
        "schema_validation.json",
    }


def test_openai_responses_provider_can_use_chat_completions_wire_api_directly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: urllib.request.Request, timeout: int) -> FakeHTTPResponse:
        captured["url"] = request.full_url
        captured["payload"] = json.loads(request.data.decode("utf-8")) if request.data else {}
        return FakeHTTPResponse(
            {
                "id": "chat_456",
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4},
            },
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    provider = OpenAIResponsesProvider(
        base_url="https://gateway.example.test",
        api_key="test-key",
        wire_api="chat_completions",
        max_output_tokens=32,
    )

    response = provider.generate(
        LLMProviderRequest(
            task_type="model_connection_test",
            model_name="gpt-test",
            input_json={"instruction": "Reply with ok."},
        ),
    )

    assert captured["url"] == "https://gateway.example.test/v1/chat/completions"
    assert captured["payload"]["max_tokens"] == 32
    assert captured["payload"]["messages"][0]["role"] == "user"
    assert response.status == "succeeded"
    assert response.output_json["response_text"] == "ok"


def test_openai_responses_provider_reads_timeout_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "123")

    provider = OpenAIResponsesProvider(base_url="https://api.example.test", api_key="test-key")

    assert provider.timeout_seconds == 123


def test_factory_preserves_openai_provider_timeout_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "124")

    provider = create_llm_provider("OpenAI", base_url="https://api.example.test", api_key="test-key")

    assert isinstance(provider, OpenAIResponsesProvider)
    assert provider.timeout_seconds == 124


def test_openai_responses_provider_maps_http_error_without_response_body_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: urllib.request.Request, timeout: int) -> FakeHTTPResponse:
        raise urllib.error.HTTPError(
            request.full_url,
            403,
            "Forbidden",
            hdrs={},
            fp=FakeHTTPResponse({"error": {"message": "blocked sk-local-secret"}}),
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    provider = OpenAIResponsesProvider(
        base_url="https://api.example.test/v1",
        api_key="test-key",
    )

    with pytest.raises(LLMProviderError, match="HTTP 403") as exc_info:
        provider.generate(
            LLMProviderRequest(
                task_type="requirement_review",
                model_name="gpt-test",
                input_json={},
            ),
        )
    assert "sk-local-secret" not in str(exc_info.value)


def test_openai_responses_provider_reads_local_model_connection_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "model-connection.json"
    monkeypatch.setenv("CHTEST_MODEL_CONNECTION_PATH", str(config_path))
    config_path.write_text(
        json.dumps(
            {
                "provider": "OpenAI",
                "model_name": "gpt-5.5",
                "base_url": "https://api.example.test",
                "wire_api": "responses",
                "api_key": "sk-local-secret",
            },
        ),
        encoding="utf-8",
    )

    provider = OpenAIResponsesProvider()

    assert provider.base_url == "https://api.example.test"
    assert provider.api_key == "sk-local-secret"


def test_openai_responses_provider_explicit_args_do_not_read_local_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "invalid-model-connection.json"
    monkeypatch.setenv("CHTEST_MODEL_CONNECTION_PATH", str(config_path))
    config_path.write_text("[]", encoding="utf-8")

    provider = OpenAIResponsesProvider(base_url="https://api.example.test", api_key="test-key")

    assert provider.base_url == "https://api.example.test"
    assert provider.api_key == "test-key"


@pytest.mark.parametrize("provider_name", ["OpenAI", "openai-compatible", "openai_compatible", "responses"])
def test_factory_selects_openai_responses_provider_aliases(provider_name: str) -> None:
    provider = create_llm_provider(provider_name)

    assert isinstance(provider, OpenAIResponsesProvider)
