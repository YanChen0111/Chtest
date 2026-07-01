from __future__ import annotations

import uuid

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.cicd.models import QualityGateDecision, UnitTestPatch
from backend.app.modules.review_history.models import ReviewHistory
from backend.app.tests.golden.test_test_case_library_golden import ASGIClient, api_client
from backend.app.tests.golden.test_unit_test_patch_regression_golden import (
    GOLDEN_DIFF,
    GOLDEN_UNIT_TEST_PATCH,
    mark_test_runs_succeeded,
    seed_project_repository_command,
)


def test_golden_review_history_records_patch_approval_and_quality_gate_compute(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    with SessionLocal() as session:
        project, repository, test_command = seed_project_repository_command(session)
        session.commit()
        project_id = project.id
        repository_id = repository.id
        test_command_id = test_command.id

    create_response = client.post(
        "/api/cicd/runs",
        json_body={
            "project_id": str(project_id),
            "repository_id": str(repository_id),
            "source_type": "local_diff",
            "base_ref": "main",
            "head_ref": "HEAD",
            "diff_text": GOLDEN_DIFF,
        },
    )
    assert create_response.status_code == 202
    cicd_run_id = uuid.UUID(create_response.json()["cicd_run_id"])

    patch_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/unit-test-patches",
        json_body={
            "patch_text": GOLDEN_UNIT_TEST_PATCH,
            "target_framework": "pytest",
            "test_intent": "覆盖优惠券金额大于订单总额的新分支",
            "coverage_target": [{"path": "src/coupon.py", "reason": "coupon.amount > order_total"}],
        },
    )
    assert patch_response.status_code == 202
    patch_body = patch_response.json()
    assert patch_body["status"] == "scope_validated"
    unit_test_patch_id = uuid.UUID(patch_body["id"])

    approve_response = client.post(
        f"/api/cicd/unit-test-patches/{unit_test_patch_id}/approve",
        json_body={"review_comment": "Golden review approves test-only patch"},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    apply_response = client.post(
        f"/api/cicd/unit-test-patches/{unit_test_patch_id}/apply",
        json_body={"confirm_scope_gate_result": True},
    )
    assert apply_response.status_code == 200
    assert apply_response.json()["status"] == "applied"

    new_tests_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/run-new-tests",
        json_body={
            "unit_test_patch_id": str(unit_test_patch_id),
            "test_command_id": str(test_command_id),
        },
    )
    assert new_tests_response.status_code == 202
    new_test_run_id = uuid.UUID(new_tests_response.json()["test_run_id"])

    regression_select_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/select-regression",
        json_body={
            "skill_version": "regression-selection-skill:v1",
            "candidate_test_command_ids": [str(test_command_id)],
        },
    )
    assert regression_select_response.status_code == 200
    regression_plan_artifact_id = uuid.UUID(regression_select_response.json()["regression_plan_artifact_id"])

    regression_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/run-regression",
        json_body={
            "regression_plan_artifact_id": str(regression_plan_artifact_id),
            "test_command_ids": [str(test_command_id)],
        },
    )
    assert regression_response.status_code == 202
    regression_run_id = uuid.UUID(regression_response.json()["test_run_ids"][0])

    mark_test_runs_succeeded(SessionLocal, [new_test_run_id, regression_run_id])

    gate_response = client.post(f"/api/cicd/runs/{cicd_run_id}/quality-gate", json_body={})
    assert gate_response.status_code == 200
    gate_body = gate_response.json()
    assert gate_body["status"] == "passed"
    quality_gate_decision_id = uuid.UUID(gate_body["id"])

    with SessionLocal() as session:
        patch = session.get(UnitTestPatch, unit_test_patch_id)
        decision = session.get(QualityGateDecision, quality_gate_decision_id)
        patch_history = list(
            session.scalars(
                select(ReviewHistory).where(
                    ReviewHistory.entity_type == "UnitTestPatch",
                    ReviewHistory.entity_id == unit_test_patch_id,
                ),
            ),
        )
        gate_history = list(
            session.scalars(
                select(ReviewHistory).where(
                    ReviewHistory.entity_type == "QualityGateDecision",
                    ReviewHistory.entity_id == quality_gate_decision_id,
                ),
            ),
        )
        related_history = list(
            session.scalars(
                select(ReviewHistory).where(
                    ReviewHistory.related_entity_type == "CICDRun",
                    ReviewHistory.related_entity_id == cicd_run_id,
                ),
            ),
        )
        tables = set(inspect(session.bind).get_table_names())

    assert patch is not None
    assert patch.status == "applied"
    assert decision is not None
    assert decision.status == "passed"

    assert len(patch_history) == 1
    patch_event = patch_history[0]
    assert patch_event.project_id == project_id
    assert patch_event.entity_type == "UnitTestPatch"
    assert patch_event.entity_id == unit_test_patch_id
    assert patch_event.related_entity_type == "CICDRun"
    assert patch_event.related_entity_id == cicd_run_id
    assert patch_event.action == "approve"
    assert patch_event.from_status == "scope_validated"
    assert patch_event.to_status == "approved"
    assert patch_event.reviewer == "Default User"
    assert patch_event.comment == "Golden review approves test-only patch"
    assert patch_event.evidence_artifact_ids == []
    assert patch_event.created_at is not None

    assert len(gate_history) == 1
    gate_event = gate_history[0]
    assert gate_event.project_id == project_id
    assert gate_event.entity_type == "QualityGateDecision"
    assert gate_event.entity_id == quality_gate_decision_id
    assert gate_event.related_entity_type == "CICDRun"
    assert gate_event.related_entity_id == cicd_run_id
    assert gate_event.action == "compute_quality_gate"
    assert gate_event.from_status == "pending"
    assert gate_event.to_status == "passed"
    assert gate_event.reviewer == "Default User"
    assert gate_event.evidence_artifact_ids
    assert gate_event.created_at is not None

    assert {event.id for event in related_history} == {patch_event.id, gate_event.id}
    assert "roles" not in tables
    assert "permissions" not in tables
    assert "tenants" not in tables
