from __future__ import annotations

import uuid
import json

import pytest

from backend.app.modules.ai_runtime.providers.base import (
    LLMProviderError,
    LLMProviderRequest,
    LLMProviderTimeoutError,
)
from backend.app.modules.ai_runtime.providers.mock_provider import MockLLMProvider


def test_success_response_is_deterministic_and_echoes_context_artifacts() -> None:
    provider = MockLLMProvider()
    context_id = uuid.uuid4()
    request = LLMProviderRequest(
        task_type="requirement_review",
        model_name="mock-requirement-review",
        input_json={
            "requirement": "# 优惠券结算规则",
            "context_artifact_ids": [str(context_id)],
        },
        context_artifact_ids=[context_id],
        context_manifest=[
            {
                "artifact_id": str(context_id),
                "title": "coupon-api-notes.md",
                "mime_type": "text/markdown",
                "sha256": "sha256:example",
                "redaction_applied": False,
            },
        ],
    )

    first = provider.generate(request)
    second = provider.generate(request)

    assert first.provider == "mock"
    assert first.model_name == "mock-requirement-review"
    assert first.status == "succeeded"
    assert first.output_json == second.output_json
    assert first.output_json["used_context_artifact_ids"] == [str(context_id)]
    assert first.output_json["used_knowledge"] is False
    assert first.output_json["overall_score"] == 82
    assert set(first.output_json["scores"]) == {
        "completeness",
        "clarity",
        "consistency",
        "testability",
        "feasibility",
        "logic",
    }
    artifacts_by_file = {artifact.file_name: artifact for artifact in first.artifacts}
    assert {artifact.artifact_type for artifact in first.artifacts} == {
        "input_json",
        "raw_llm_output",
        "parsed_output",
        "schema_validation",
    }
    context_manifest = json.loads(artifacts_by_file["context_manifest.json"].content.decode("utf-8"))
    assert context_manifest["context_artifact_ids"] == [str(context_id)]
    assert context_manifest["context_manifest"][0]["title"] == "coupon-api-notes.md"


def test_case_generator_returns_golden_candidate_shape() -> None:
    provider = MockLLMProvider()

    response = provider.generate(
        LLMProviderRequest(
            task_type="case_generation",
            model_name="mock-case-generator",
            input_json={"requirement": "# 优惠券结算规则"},
        ),
    )

    assert response.status == "succeeded"
    assert len(response.output_json["cases"]) >= 5
    first_case = response.output_json["cases"][0]
    assert first_case["title"] == "可用优惠券可成功抵扣订单金额"
    assert first_case["priority"] == "P0"
    assert first_case["steps"]
    assert first_case["expected_results"]
    assert first_case["requirement_refs"]
    assert first_case["ai_reason"]


def test_provider_error_mode_raises_without_network() -> None:
    provider = MockLLMProvider()

    with pytest.raises(LLMProviderError, match="forced provider error"):
        provider.generate(
            LLMProviderRequest(
                task_type="requirement_review",
                model_name="mock-requirement-review",
                input_json={},
                mode="provider_error",
            ),
        )


@pytest.mark.parametrize(
    ("model_name", "expected_key"),
    [
        ("mock-automation-draft", "draft_code"),
        ("mock-cicd-analysis", "changed_files"),
        ("mock-unit-test-generator", "patch"),
        ("mock-failure-analysis", "classification"),
        ("mock-report-generator", "report_markdown"),
    ],
)
def test_supported_models_return_specific_deterministic_shapes(
    model_name: str,
    expected_key: str,
) -> None:
    provider = MockLLMProvider()

    response = provider.generate(
        LLMProviderRequest(
            task_type=model_name.removeprefix("mock-").replace("-", "_"),
            model_name=model_name,
            input_json={},
        ),
    )

    assert response.status == "succeeded"
    assert expected_key in response.output_json
    assert response.output_json["used_knowledge"] is False
    assert response.output_json["used_context_artifact_ids"] == []


def test_unknown_mock_model_is_rejected() -> None:
    provider = MockLLMProvider()

    with pytest.raises(LLMProviderError, match="unsupported mock model"):
        provider.generate(
            LLMProviderRequest(
                task_type="unknown",
                model_name="mock-unknown",
                input_json={},
            ),
        )


def test_schema_invalid_mode_returns_schema_invalid_status_and_artifact() -> None:
    provider = MockLLMProvider()

    response = provider.generate(
        LLMProviderRequest(
            task_type="requirement_review",
            model_name="mock-requirement-review",
            input_json={},
            mode="schema_invalid",
        ),
    )

    assert response.status == "schema_invalid"
    assert response.output_json == {"invalid": True}
    assert any(artifact.artifact_type == "schema_validation" for artifact in response.artifacts)
    assert response.error_json is not None
    assert response.error_json["error_code"] == "MOCK_SCHEMA_INVALID"


def test_timeout_mode_raises_timeout_error_without_sleeping() -> None:
    provider = MockLLMProvider()

    with pytest.raises(LLMProviderTimeoutError, match="forced timeout"):
        provider.generate(
            LLMProviderRequest(
                task_type="requirement_review",
                model_name="mock-requirement-review",
                input_json={},
                mode="timeout",
            ),
        )
