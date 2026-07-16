from __future__ import annotations

from pathlib import Path

from backend.app.modules.ai_runtime.providers.mock_provider import MockLLMProvider
from backend.app.modules.prompt_skill.eval_bench import run_mock_provider_eval_bench
from backend.app.modules.prompt_skill.eval_samples import load_default_eval_samples


ROOT = Path(__file__).parents[4]


def test_eval_samples_have_fixture_backing_files() -> None:
    samples = load_default_eval_samples(ROOT)

    assert {sample.fixture_name for sample in samples} == {
        "requirements",
        "code-changes",
        "failed-runs",
        "bug-history",
    }
    assert all(sample.input_json for sample in samples)
    assert all("password" not in sample.fixture_content.lower() for sample in samples)
    assert all("sk-" not in sample.fixture_content.lower() for sample in samples)


def test_mock_provider_eval_bench_returns_required_metrics() -> None:
    result = run_mock_provider_eval_bench(
        provider=MockLLMProvider(),
        root=ROOT,
        samples=load_default_eval_samples(ROOT),
    )

    assert result.total_samples == 4
    assert set(result.metrics) == {
        "schema_valid_rate",
        "evidence_complete_rate",
        "unsafe_output_rate",
        "manual_edit_rate",
        "first_run_pass_rate",
        "repair_success_rate",
    }
    assert all(0.0 <= value <= 1.0 for value in result.metrics.values())
    assert result.metrics["evidence_complete_rate"] == 1.0
    assert result.metrics["unsafe_output_rate"] == 0.0
    assert result.metrics["manual_edit_rate"] == 0.0
    assert result.metrics["first_run_pass_rate"] == 0.0
    assert result.metrics["repair_success_rate"] == 0.0
    assert {item.prompt_name for item in result.items} == {
        "requirement_review",
        "cicd_change_analysis",
        "failure_analysis",
        "report_generation",
    }
    assert all(item.evidence_complete for item in result.items)


def test_eval_bench_uses_prompt_output_schema_for_validation() -> None:
    result = run_mock_provider_eval_bench(
        provider=MockLLMProvider(),
        root=ROOT,
        samples=load_default_eval_samples(ROOT),
        provider_mode="schema_invalid",
    )

    assert result.metrics["schema_valid_rate"] == 0.0
    assert all(not item.schema_valid for item in result.items)
