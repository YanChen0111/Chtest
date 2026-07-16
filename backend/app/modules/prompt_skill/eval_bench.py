from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.modules.ai_runtime.providers.base import LLMProviderRequest, ProviderMode
from backend.app.modules.ai_runtime.providers.mock_provider import MockLLMProvider
from backend.app.modules.prompt_skill.eval_samples import EvalSample
from backend.app.modules.prompt_skill.registry_loader import parse_prompt_file


REQUIRED_METRIC_NAMES = [
    "schema_valid_rate",
    "evidence_complete_rate",
    "unsafe_output_rate",
    "manual_edit_rate",
    "first_run_pass_rate",
    "repair_success_rate",
]


@dataclass(frozen=True)
class EvalBenchItem:
    fixture_name: str
    prompt_name: str
    model_name: str
    schema_valid: bool
    evidence_complete: bool
    unsafe_output: bool


@dataclass(frozen=True)
class EvalBenchResult:
    total_samples: int
    metrics: dict[str, float]
    items: list[EvalBenchItem]


def run_mock_provider_eval_bench(
    *,
    provider: MockLLMProvider,
    root: Path,
    samples: list[EvalSample],
    provider_mode: ProviderMode = "success",
) -> EvalBenchResult:
    items: list[EvalBenchItem] = []

    for sample in samples:
        prompt = parse_prompt_file(root / "prompts" / sample.prompt_name / "v1.md")
        response = provider.generate(
            LLMProviderRequest(
                task_type=sample.task_type,
                model_name=sample.model_name,
                input_json=sample.input_json,
                mode=provider_mode,
            ),
        )
        schema_valid = _validate_object_schema(response.output_json, prompt.output_schema_json)
        evidence_complete = _has_evidence_trace(response.output_json)
        unsafe_output = _contains_unsafe_output(response.output_json)
        items.append(
            EvalBenchItem(
                fixture_name=sample.fixture_name,
                prompt_name=sample.prompt_name,
                model_name=sample.model_name,
                schema_valid=schema_valid,
                evidence_complete=evidence_complete,
                unsafe_output=unsafe_output,
            ),
        )

    total = len(items)
    schema_valid_count = sum(item.schema_valid for item in items)
    evidence_complete_count = sum(item.evidence_complete for item in items)
    unsafe_output_count = sum(item.unsafe_output for item in items)
    metrics = {
        "schema_valid_rate": _rate(schema_valid_count, total),
        "evidence_complete_rate": _rate(evidence_complete_count, total),
        "unsafe_output_rate": _rate(unsafe_output_count, total),
        "manual_edit_rate": 0.0,
        "first_run_pass_rate": 0.0,
        "repair_success_rate": 0.0,
    }
    return EvalBenchResult(total_samples=total, metrics=metrics, items=items)


def _validate_object_schema(output: dict[str, Any], schema: dict[str, Any]) -> bool:
    if schema.get("type") != "object" or not isinstance(output, dict):
        return False
    required_fields = schema.get("required", [])
    if not isinstance(required_fields, list):
        return False
    if any(field not in output for field in required_fields):
        return False
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return True
    for field, field_schema in properties.items():
        if field in output and not _matches_json_type(output[field], field_schema.get("type")):
            return False
    return True


def _matches_json_type(value: Any, expected_type: str | None) -> bool:
    if expected_type is None:
        return True
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def _has_evidence_trace(output: dict[str, Any]) -> bool:
    return output.get("used_knowledge") is False and isinstance(output.get("used_context_artifact_ids"), list)


def _contains_unsafe_output(output: dict[str, Any]) -> bool:
    rendered = repr(output).lower()
    unsafe_patterns = ["sk-", "password=", "api_key=", "secret="]
    return any(pattern in rendered for pattern in unsafe_patterns)


def _rate(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(count / total, 4)
