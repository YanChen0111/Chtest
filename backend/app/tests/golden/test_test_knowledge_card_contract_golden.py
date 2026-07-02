from __future__ import annotations

from pathlib import Path

from backend.app.modules.cases.schemas import GeneratedCaseCandidateListItemRead


FIXTURE_PATH = Path("docs/fixtures/18-test-knowledge-card-contract-golden.md")


def test_golden_generated_case_candidate_keeps_knowledge_evidence_fields() -> None:
    assert FIXTURE_PATH.exists()

    candidate = GeneratedCaseCandidateListItemRead(
        id="00000000-0000-0000-0000-000000000801",
        title="Expired coupon cannot submit order",
        priority="P0",
        test_type="functional",
        precondition=None,
        steps=["Login", "Open checkout", "Select expired coupon", "Submit order"],
        expected_results=["Submission is blocked", "Expired coupon message is shown"],
        input_data={"coupon_state": "expired"},
        requirement_refs=["Expired coupons cannot be used"],
        risk_refs=["coupon expiration boundary"],
        ai_reason="Covers coupon expiration boundary",
        source_knowledge_evidence_ids=["ke-expired-coupon-boundary"],
        knowledge_evidence_refs=[
            {
                "evidence_id": "ke-expired-coupon-boundary",
                "knowledge_card_id": "00000000-0000-0000-0000-000000000821",
                "source_artifact_id": "00000000-0000-0000-0000-000000000371",
                "snippet": "Expired coupons must be rejected before order submission.",
                "score": 0.92,
                "retrieval_reason": "Supports the expired-coupon rejection path.",
            },
        ],
        covered_risk_ids=["00000000-0000-0000-0000-000000000411"],
        generation_reason="Boundary case for expired coupon validation.",
        automation_readiness="suitable_for_playwright",
        quality_score=88,
        review_findings=[
            {
                "type": "evidence_complete",
                "severity": "info",
                "message": "Candidate cites the required boundary-condition knowledge card.",
            },
        ],
        coverage_gap_notes="",
        status="generated",
    )

    body = candidate.model_dump(mode="json")

    assert body["source_knowledge_evidence_ids"] == ["ke-expired-coupon-boundary"]
    assert body["knowledge_evidence_refs"][0]["knowledge_card_id"] == "00000000-0000-0000-0000-000000000821"
    assert body["knowledge_evidence_refs"][0]["source_artifact_id"] == "00000000-0000-0000-0000-000000000371"
    assert body["covered_risk_ids"] == ["00000000-0000-0000-0000-000000000411"]
    assert body["generation_reason"] == "Boundary case for expired coupon validation."
    assert body["automation_readiness"] == "suitable_for_playwright"
    assert body["quality_score"] == 88
    assert body["review_findings"][0]["type"] == "evidence_complete"
    assert body["coverage_gap_notes"] == ""
    assert body["status"] == "generated"


def test_golden_missing_knowledge_evidence_remains_review_evidence_only() -> None:
    candidate = GeneratedCaseCandidateListItemRead(
        id="00000000-0000-0000-0000-000000000803",
        title="VIP coupon can stack with points",
        priority="P1",
        test_type="functional",
        precondition=None,
        steps=["Login as VIP", "Apply VIP coupon", "Apply points", "Submit order"],
        expected_results=["Order is submitted with both discounts"],
        input_data={},
        requirement_refs=[],
        risk_refs=[],
        ai_reason="Model proposed a VIP stacking path without supporting evidence.",
        source_knowledge_evidence_ids=[],
        knowledge_evidence_refs=[],
        covered_risk_ids=[],
        generation_reason="Model proposed a VIP stacking path without supporting evidence.",
        automation_readiness="not_suitable",
        quality_score=22,
        review_findings=[
            {
                "type": "missing_evidence",
                "severity": "error",
                "message": "No KnowledgeEvidence supports VIP coupon stacking.",
            },
            {
                "type": "hallucination_risk",
                "severity": "error",
                "message": "Requirement says coupons cannot be combined with points.",
            },
        ],
        coverage_gap_notes="No accepted source mentions VIP stacking.",
        status="generated",
    )

    body = candidate.model_dump(mode="json")

    assert body["source_knowledge_evidence_ids"] == []
    assert body["knowledge_evidence_refs"] == []
    assert body["automation_readiness"] == "not_suitable"
    assert body["quality_score"] == 22
    assert [finding["type"] for finding in body["review_findings"]] == ["missing_evidence", "hallucination_risk"]
    assert body["coverage_gap_notes"] == "No accepted source mentions VIP stacking."
    assert body["status"] == "generated"
    assert "test_case_id" not in body
    assert "test_run_id" not in body
    assert "report_id" not in body
    assert "retrieval_job_id" not in body
    assert "vector_index_id" not in body
    assert "graph_job_id" not in body
