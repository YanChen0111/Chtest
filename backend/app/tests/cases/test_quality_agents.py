from __future__ import annotations

from backend.app.modules.cases.quality_agents import (
    evaluate_case_quality,
    evaluate_case_quality_bundle,
    evaluate_coverage_gaps,
)


def test_case_review_agent_is_deterministic_and_reports_missing_evidence() -> None:
    case = {
        "title": "Expired coupon is rejected",
        "steps": ["Apply expired coupon"],
        "expected_results": ["Checkout is blocked"],
        "coverage_dimensions": [{"key": "negative", "evidence": "Rejected before submit"}],
        "ai_reason": "Covers expiry validation",
    }

    first = evaluate_case_quality(case)
    second = evaluate_case_quality(case)

    assert first == second
    assert first["agent"] == "CaseReviewAgent"
    assert first["status"] == "needs_review"
    assert first["findings"][0]["code"] == "missing_evidence"


def test_coverage_gap_agent_reports_uncovered_dimensions() -> None:
    result = evaluate_coverage_gaps(
        {
            "coverage_dimensions": [
                {"key": "positive"},
                {"key": "boundary"},
                {"key": "unknown"},
            ],
        },
    )

    assert result["status"] == "gap"
    assert result["covered_dimensions"] == ["boundary", "positive"]
    assert "permission" in result["missing_dimensions"]
    assert "unknown" not in result["covered_dimensions"]


def test_quality_bundle_keeps_provider_neutral_fields() -> None:
    review, readiness = evaluate_case_quality_bundle(
        {
            "title": "Valid login",
            "test_type": "ui",
            "steps": ["Open login"],
            "expected_results": ["Login form is shown"],
            "source_knowledge_evidence": [{"knowledge_evidence_id": "evidence-1", "payload": "secret"}],
            "coverage_dimensions": [{"key": key} for key in ("positive", "negative", "boundary", "state", "permission", "risk")],
            "generation_reason": "Covers the login entry point",
        },
    )

    assert review["status"] == "pass"
    assert review["evidence_ids"] == ["evidence-1"]
    assert "payload" not in str(review)
    assert readiness["framework"] == "playwright"
    assert readiness["status"] == "ready_for_review"
