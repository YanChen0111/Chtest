from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from backend.app.modules.cases.grounding_eval import run_claim_grounding_eval


FIXTURE = Path(__file__).parents[1] / "fixtures" / "claim_grounding_eval.json"


def _corpus() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_claim_grounding_eval_fixture_has_fixed_version_pairs() -> None:
    corpus = _corpus()

    assert [
        (run["prompt_version"], run["skill_version"])
        for run in corpus["version_runs"]
    ] == [
        ("case_generation:v1", "test-case-generation-skill:v1"),
        ("case_generation:v2", "test-case-generation-skill:v2"),
    ]
    assert corpus["baseline_version"] == "case_generation:v1|test-case-generation-skill:v1"
    assert len(corpus["expected_valid_citation_claim_keys"]) == 5
    assert len(corpus["unsupported_cases"]) == 5


def test_claim_grounding_eval_measures_recall_rejection_and_version_drift() -> None:
    result = run_claim_grounding_eval(_corpus())
    metrics = {item.version: item for item in result.versions}
    v1 = metrics["case_generation:v1|test-case-generation-skill:v1"]
    v2 = metrics["case_generation:v2|test-case-generation-skill:v2"]

    assert v1.valid_citation_recall == 0.0
    assert v1.requirement_coverage == 0.0
    assert v1.accepted_cases == 0
    assert len(v1.missing_expected_claim_ids) == 5
    assert v1.unexpected_claim_ids == ()
    assert all(item.status == "grounding_invalid" for item in v1.case_diagnostics)

    assert v2.valid_citation_recall == 1.0
    assert v2.requirement_coverage == 1.0
    assert v2.accepted_cases == v2.total_cases == 5
    assert v2.missing_expected_claim_ids == ()
    assert v2.unexpected_claim_ids == ()
    assert all(item.status == "pass" and item.claim_ids for item in v2.case_diagnostics)

    assert result.unsupported_case_rejection == 1.0
    assert result.rejected_unsupported_cases == result.total_unsupported_cases == 5
    assert result.requirement_coverage_drift == {
        "case_generation:v1|test-case-generation-skill:v1": 0.0,
        "case_generation:v2|test-case-generation-skill:v2": 1.0,
    }


def test_claim_grounding_eval_is_order_independent_and_repeatable() -> None:
    corpus = _corpus()
    original = copy.deepcopy(corpus)
    first = run_claim_grounding_eval(corpus)
    second = run_claim_grounding_eval(corpus)
    reordered = copy.deepcopy(corpus)
    reordered["version_runs"].reverse()

    assert first == second == run_claim_grounding_eval(reordered)
    assert corpus == original


def test_claim_grounding_eval_reports_unexpected_valid_claim_ids() -> None:
    corpus = _corpus()
    corpus["expected_valid_citation_claim_keys"].remove("amount_tampering")

    result = run_claim_grounding_eval(corpus)
    v2 = next(item for item in result.versions if item.version.startswith("case_generation:v2"))
    risk_case = next(
        item for item in v2.case_diagnostics if item.case_name == "Verify payment amount tampering is rejected"
    )

    assert risk_case.accepted is True
    assert v2.unexpected_claim_ids == risk_case.claim_ids


@pytest.mark.parametrize(
    "mutation",
    [
        lambda corpus: corpus.update(version_runs=[]),
        lambda corpus: corpus["version_runs"][0].update(cases=[]),
        lambda corpus: corpus.update(unsupported_cases=[]),
        lambda corpus: corpus.update(expected_valid_citation_claim_keys=[]),
        lambda corpus: corpus.update(expected_requirement_claim_keys=[]),
        lambda corpus: corpus.update(baseline_version="missing:v1|missing-skill:v1"),
    ],
    ids=[
        "empty-version-runs",
        "empty-version-cases",
        "empty-unsupported-cases",
        "empty-citation-gold",
        "empty-requirement-gold",
        "unknown-baseline",
    ],
)
def test_claim_grounding_eval_fails_closed_for_empty_metric_inputs(mutation) -> None:
    corpus = _corpus()
    mutation(corpus)

    with pytest.raises(ValueError):
        run_claim_grounding_eval(corpus)
