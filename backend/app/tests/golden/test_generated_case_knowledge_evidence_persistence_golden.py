from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.ai_runtime.providers import mock_provider
from backend.app.modules.cases.models import TestCase as CaseModel
from backend.app.tests.api.test_case_generation import ASGIClient, api_client, create_reviewed_requirement


FIXTURE_PATH = Path("docs/fixtures/18-test-knowledge-card-contract-golden.md")
FORBIDDEN_SIDE_EFFECT_FIELDS = {
    "test_case_id",
    "test_run_id",
    "report_id",
    "retrieval_job_id",
    "vector_index_id",
    "graph_job_id",
}


@pytest.mark.usefixtures("api_client")
def test_golden_case_generation_api_exposes_knowledge_evidence_without_side_effects(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert FIXTURE_PATH.exists()
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)

    original_success_output = mock_provider.MockLLMProvider._success_output

    def success_output_with_golden_evidence(self, request):
        output = original_success_output(self, request)
        if request.model_name == "mock-case-generator":
            output["cases"] = golden_cases()
        return output

    monkeypatch.setattr(mock_provider.MockLLMProvider, "_success_output", success_output_with_golden_evidence)

    response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": requirement["project_id"],
            "requirement_id": requirement["id"],
            "requirement_review_id": review["id"],
            "target_test_types": ["functional", "ui"],
            "prompt_version": "case_generation:v1",
            "skill_version": "test-case-generation-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-case-generator",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    )

    assert response.status_code == 202
    generation = response.json()
    candidates_response = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates")

    assert candidates_response.status_code == 200
    candidates = candidates_response.json()["items"]
    by_title = {candidate["title"]: candidate for candidate in candidates}

    accepted = by_title["Expired coupon cannot submit order"]
    assert accepted["source_knowledge_evidence_ids"] == ["ke-expired-coupon-boundary"]
    assert accepted["knowledge_evidence_refs"][0]["knowledge_card_id"] == "00000000-0000-0000-0000-000000000821"
    assert accepted["knowledge_evidence_refs"][0]["source_artifact_id"] == "00000000-0000-0000-0000-000000000371"
    assert accepted["covered_risk_ids"] == ["00000000-0000-0000-0000-000000000411"]
    assert accepted["generation_reason"] == "Boundary case for expired coupon validation."
    assert accepted["automation_readiness"] == "suitable_for_playwright"
    assert accepted["quality_score"] == 88
    assert accepted["review_findings"][0]["type"] == "evidence_complete"
    assert accepted["status"] == "generated"

    needs_review = by_title["Coupon and points cannot be combined"]
    assert needs_review["source_knowledge_evidence_ids"] == ["ke-coupon-points-conflict"]
    assert needs_review["covered_risk_ids"] == ["00000000-0000-0000-0000-000000000412"]
    assert needs_review["quality_score"] == 71
    assert needs_review["review_findings"][0]["type"] == "expected_result_needs_precision"
    assert needs_review["review_findings"][0]["severity"] == "warning"
    assert needs_review["coverage_gap_notes"] == "Precedence rule is not explicit in the requirement."
    assert needs_review["status"] == "generated"

    rejected = by_title["VIP coupon can stack with points"]
    assert rejected["source_knowledge_evidence_ids"] == []
    assert rejected["knowledge_evidence_refs"] == []
    assert rejected["covered_risk_ids"] == []
    assert rejected["automation_readiness"] == "not_suitable"
    assert rejected["quality_score"] == 22
    assert [finding["type"] for finding in rejected["review_findings"]] == ["missing_evidence", "hallucination_risk"]
    assert rejected["coverage_gap_notes"] == "No accepted source mentions VIP stacking."
    assert rejected["status"] == "generated"

    assert all(FORBIDDEN_SIDE_EFFECT_FIELDS.isdisjoint(candidate.keys()) for candidate in candidates)
    with SessionLocal() as session:
        assert list(session.scalars(select(CaseModel))) == []
        artifact_types = {artifact.artifact_type for artifact in session.scalars(select(Artifact))}
        assert {"retrieval_result", "vector_index", "graph_job", "report"}.isdisjoint(artifact_types)


def golden_cases() -> list[dict[str, Any]]:
    return [
        {
            "title": "Expired coupon cannot submit order",
            "priority": "P0",
            "test_type": "functional",
            "steps": ["Login", "Open checkout", "Select expired coupon", "Submit order"],
            "expected_results": ["Submission is blocked", "Expired coupon message is shown"],
            "requirement_refs": ["Expired coupons cannot be used"],
            "risk_refs": ["coupon expiration boundary"],
            "ai_reason": "Covers coupon expiration boundary",
            "source_knowledge_evidence_ids": ["ke-expired-coupon-boundary"],
            "knowledge_evidence_refs": [
                {
                    "evidence_id": "ke-expired-coupon-boundary",
                    "knowledge_card_id": "00000000-0000-0000-0000-000000000821",
                    "source_artifact_id": "00000000-0000-0000-0000-000000000371",
                    "snippet": "Expired coupons must be rejected before order submission.",
                    "score": 0.92,
                },
            ],
            "covered_risk_ids": ["00000000-0000-0000-0000-000000000411"],
            "generation_reason": "Boundary case for expired coupon validation.",
            "automation_readiness": "suitable_for_playwright",
            "quality_score": 88,
            "review_findings": [
                {
                    "type": "evidence_complete",
                    "severity": "info",
                    "message": "Candidate cites the required boundary-condition knowledge card.",
                },
            ],
            "coverage_gap_notes": "",
        },
        {
            "title": "Coupon and points cannot be combined",
            "priority": "P0",
            "test_type": "functional",
            "steps": ["Login", "Open checkout", "Apply coupon", "Apply points", "Submit order"],
            "expected_results": ["Only one discount method is accepted", "Conflict message is shown"],
            "requirement_refs": ["Coupons cannot be combined with points"],
            "ai_reason": "Covers coupon and points conflict.",
            "source_knowledge_evidence_ids": ["ke-coupon-points-conflict"],
            "covered_risk_ids": ["00000000-0000-0000-0000-000000000412"],
            "generation_reason": "Exception case for mutually exclusive discounts.",
            "automation_readiness": "suitable_for_playwright",
            "quality_score": 71,
            "review_findings": [
                {
                    "type": "expected_result_needs_precision",
                    "severity": "warning",
                    "message": "Expected result should name whether coupon or points takes precedence.",
                },
            ],
            "coverage_gap_notes": "Precedence rule is not explicit in the requirement.",
        },
        {
            "title": "VIP coupon can stack with points",
            "priority": "P1",
            "test_type": "functional",
            "steps": ["Login as VIP", "Apply VIP coupon", "Apply points", "Submit order"],
            "expected_results": ["Order is submitted with both discounts"],
            "requirement_refs": ["VIP coupon stacking"],
            "ai_reason": "Model proposed a VIP stacking path without supporting evidence.",
            "source_knowledge_evidence_ids": [],
            "knowledge_evidence_refs": [],
            "covered_risk_ids": [],
            "generation_reason": "Model proposed a VIP stacking path without supporting evidence.",
            "automation_readiness": "not_suitable",
            "quality_score": 22,
            "review_findings": [
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
            "coverage_gap_notes": "No accepted source mentions VIP stacking.",
        },
    ]
