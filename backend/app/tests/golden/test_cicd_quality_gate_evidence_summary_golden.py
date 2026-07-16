from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import CICDRun, QualityGateDecision, UnitTestPatch
from backend.app.modules.execution.models import TestRun
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.golden.test_test_case_library_golden import ASGIClient, api_client
from backend.app.tests.golden.test_unit_test_patch_regression_golden import (
    GOLDEN_DIFF,
    GOLDEN_UNIT_TEST_PATCH,
    mark_test_runs_succeeded,
    seed_project_repository_command,
)


def test_golden_quality_gate_summary_inputs_remain_evidence_only(
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
    unit_test_patch_id = uuid.UUID(patch_response.json()["id"])

    approve_response = client.post(
        f"/api/cicd/unit-test-patches/{unit_test_patch_id}/approve",
        json_body={"review_comment": "Golden summary keeps patch evidence readable"},
    )
    assert approve_response.status_code == 200

    apply_response = client.post(
        f"/api/cicd/unit-test-patches/{unit_test_patch_id}/apply",
        json_body={"confirm_scope_gate_result": True},
    )
    assert apply_response.status_code == 200
    applied_artifact_id = uuid.UUID(apply_response.json()["applied_artifact_id"])

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

    before_gate_counts = table_counts(SessionLocal)
    before_gate_artifacts = artifact_snapshots(SessionLocal)
    gate_response = client.post(f"/api/cicd/runs/{cicd_run_id}/quality-gate", json_body={})
    assert gate_response.status_code == 200
    gate_body = gate_response.json()
    assert gate_body["status"] == "passed"
    assert gate_body["summary"] == "CI/CD quality gate passed with patch, new-test, and regression evidence."
    assert gate_body["blocking_reasons"] == []
    assert gate_body["evidence_artifact_ids"] == [str(applied_artifact_id)]
    assert gate_body["status_detail"]["patch_scope_gate"]["allowed"] is True
    assert gate_body["status_detail"]["unit_test_patch"] == {
        "id": str(unit_test_patch_id),
        "status": "applied",
    }
    assert gate_body["status_detail"]["new_tests"]["status"] == "succeeded"
    assert gate_body["status_detail"]["new_tests"]["test_run_ids"] == [str(new_test_run_id)]
    assert gate_body["status_detail"]["regression"]["status"] == "succeeded"
    assert gate_body["status_detail"]["regression"]["test_run_ids"] == [str(regression_run_id)]
    assert gate_body["status_detail"]["failure_analysis"] == "not_available"

    after_gate_counts = table_counts(SessionLocal)
    after_gate_artifacts = artifact_snapshots(SessionLocal)
    assert after_gate_counts["artifacts"] == before_gate_counts["artifacts"]
    assert after_gate_artifacts == before_gate_artifacts
    assert after_gate_counts["ai_tasks"] == before_gate_counts["ai_tasks"]
    assert after_gate_counts["test_runs"] == before_gate_counts["test_runs"]
    assert after_gate_counts["quality_gate_decisions"] == before_gate_counts["quality_gate_decisions"] + 1
    assert after_gate_counts["reports"] == 0
    assert after_gate_counts["failure_analyses"] == 0
    assert after_gate_counts["automation_drafts"] == 0

    quality_gate_decision_id = uuid.UUID(gate_body["id"])
    with SessionLocal() as session:
        run = session.get(CICDRun, cicd_run_id)
        patch = session.get(UnitTestPatch, unit_test_patch_id)
        applied_artifact = session.get(Artifact, applied_artifact_id)
        regression_plan_artifact = session.get(Artifact, regression_plan_artifact_id)
        decision = session.get(QualityGateDecision, quality_gate_decision_id)

        assert session.scalar(select(Report)) is None
        assert session.scalar(select(FailureAnalysis)) is None
        assert session.scalar(select(AutomationDraft)) is None

    assert run is not None
    assert run.quality_gate_status == "passed"
    assert patch is not None
    assert patch.status == "applied"
    assert applied_artifact is not None
    assert applied_artifact.artifact_type == "unit_test_patch"
    assert applied_artifact.owner_entity_type == "UnitTestPatch"
    assert applied_artifact.owner_entity_id == unit_test_patch_id
    assert regression_plan_artifact is not None
    assert regression_plan_artifact.artifact_type == "regression_plan"
    assert decision is not None
    assert decision.status == "passed"
    assert decision.blocking_reasons_json == gate_body["blocking_reasons"]
    assert decision.evidence_artifact_ids == [applied_artifact_id]
    assert decision.status_detail_json == gate_body["status_detail"]

    missing_run_response = client.post(
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
    assert missing_run_response.status_code == 202
    missing_run_id = uuid.UUID(missing_run_response.json()["cicd_run_id"])

    missing_gate_response = client.post(f"/api/cicd/runs/{missing_run_id}/quality-gate", json_body={})
    assert missing_gate_response.status_code == 200
    missing_body = missing_gate_response.json()
    assert missing_body["status"] == "needs_review"
    assert missing_body["summary"] == "CI/CD quality gate needs review because required evidence is missing."
    assert missing_body["evidence_artifact_ids"] == []
    assert "missing applied UnitTestPatch evidence" in missing_body["blocking_reasons"]
    assert "missing new-test evidence" in missing_body["blocking_reasons"]
    assert "missing regression evidence" in missing_body["blocking_reasons"]
    assert missing_body["status_detail"]["unit_test_patch"] == {"id": None, "status": "missing"}
    assert missing_body["status_detail"]["new_tests"] == {"status": "missing", "test_run_ids": []}
    assert missing_body["status_detail"]["regression"] == {"status": "missing", "test_run_ids": []}

    with SessionLocal() as session:
        missing_run = session.get(CICDRun, missing_run_id)
        missing_decision = session.get(QualityGateDecision, uuid.UUID(missing_body["id"]))
        assert session.scalar(select(Report)) is None
        assert session.scalar(select(FailureAnalysis)) is None
        assert session.scalar(select(AutomationDraft)) is None

    assert missing_run is not None
    assert missing_run.quality_gate_status == "needs_review"
    assert missing_decision is not None
    assert missing_decision.status == "needs_review"
    assert missing_decision.blocking_reasons_json == missing_body["blocking_reasons"]
    assert missing_decision.evidence_artifact_ids == []
    assert missing_decision.status_detail_json == missing_body["status_detail"]


def table_counts(SessionLocal: sessionmaker[Session]) -> dict[str, int]:
    with SessionLocal() as session:
        return {
            "artifacts": session.scalar(select(func.count()).select_from(Artifact)) or 0,
            "ai_tasks": session.scalar(select(func.count()).select_from(AITask)) or 0,
            "test_runs": session.scalar(select(func.count()).select_from(TestRun)) or 0,
            "quality_gate_decisions": session.scalar(select(func.count()).select_from(QualityGateDecision)) or 0,
            "reports": session.scalar(select(func.count()).select_from(Report)) or 0,
            "failure_analyses": session.scalar(select(func.count()).select_from(FailureAnalysis)) or 0,
            "automation_drafts": session.scalar(select(func.count()).select_from(AutomationDraft)) or 0,
        }


def artifact_snapshots(SessionLocal: sessionmaker[Session]) -> dict[str, dict[str, Any]]:
    with SessionLocal() as session:
        artifacts = session.scalars(select(Artifact).order_by(Artifact.id)).all()
        return {
            str(artifact.id): {
                "project_id": str(artifact.project_id),
                "owner_entity_type": artifact.owner_entity_type,
                "owner_entity_id": str(artifact.owner_entity_id),
                "artifact_type": artifact.artifact_type,
                "file_path": artifact.file_path,
                "mime_type": artifact.mime_type,
                "size_bytes": artifact.size_bytes,
                "sha256": artifact.sha256,
                "metadata_json": artifact.metadata_json,
            }
            for artifact in artifacts
        }
