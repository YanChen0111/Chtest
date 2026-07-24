from __future__ import annotations

import copy

import pytest

from backend.app.modules.cases.grounding import (
    CaseGroundingInvalidError,
    build_requirement_claim_snapshot,
    validate_case_grounding,
)


def _snapshot() -> dict:
    return build_requirement_claim_snapshot(
        requirement_id="req-1",
        requirement_title="OTA upgrade",
        requirement_content="The device downloads the signed package. An expired signature is rejected.",
        requirement_document=None,
        risk_items=[
            {
                "id": "risk-1",
                "title": "Interrupted installation",
                "impact": "The device may become unavailable.",
                "suggestion": "Verify recovery after interrupted installation.",
            },
        ],
        knowledge_evidence=[],
    )


def _case_for_claim(claim: dict) -> dict:
    text = claim["text"]
    source_ref = str(claim["source_ref"])
    return {
        "title": f"Verify {text}",
        "precondition": "Device is available",
        "steps": [f"Exercise behavior: {text}"],
        "expected_results": [f"Observed result conforms to: {text}"],
        "ai_reason": f"Tests {text}",
        "risk_refs": [source_ref.partition(":")[2]] if claim["source_type"] == "risk" else [],
        "source_knowledge_evidence": [],
        "coverage_claims": [{"claim_id": claim["claim_id"], "evidence": text}],
    }


def test_requirement_claim_snapshot_is_stable_and_source_bound() -> None:
    first = _snapshot()
    second = _snapshot()

    assert first == second
    assert first["snapshot_hash"].startswith("sha256:")
    assert {claim["source_type"] for claim in first["claims"]} == {"requirement", "risk"}
    assert len({claim["claim_id"] for claim in first["claims"]}) == len(first["claims"])


def test_each_generated_case_must_cite_a_real_semantically_matching_claim() -> None:
    snapshot = _snapshot()
    cases = [_case_for_claim(snapshot["claims"][0]), _case_for_claim(snapshot["claims"][1])]
    invalid = copy.deepcopy(cases[1])
    invalid["coverage_claims"] = [{"claim_id": "CLM-invented", "evidence": "unrelated"}]

    with pytest.raises(CaseGroundingInvalidError):
        validate_case_grounding({"cases": [cases[0], invalid]}, snapshot)

    validate_case_grounding({"cases": cases}, snapshot)
    assert all(case["grounding_assessment"]["status"] == "pass" for case in cases)


def test_risk_claim_requires_matching_risk_reference() -> None:
    snapshot = _snapshot()
    risk_claim = next(claim for claim in snapshot["claims"] if claim["source_type"] == "risk")
    case = _case_for_claim(risk_claim)
    case["risk_refs"] = []

    with pytest.raises(CaseGroundingInvalidError):
        validate_case_grounding({"cases": [case]}, snapshot)
