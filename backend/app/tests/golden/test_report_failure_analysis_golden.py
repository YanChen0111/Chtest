from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.cicd.models import QualityGateDecision
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.golden.test_test_case_library_golden import ASGIClient, api_client


def test_golden_failed_test_run_creates_failure_analysis_and_report_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    with SessionLocal() as session:
        project, test_run, result, stderr_artifact = seed_failed_test_run(session)
        session.commit()
        project_id = project.id
        test_run_id = test_run.id
        result_id = result.id
        stderr_artifact_id = stderr_artifact.id

    analysis_response = client.post(
        f"/api/test-runs/{test_run_id}/failure-analysis",
        json_body={
            "prompt_version": "failure_analysis:v1",
            "skill_version": "failure-analysis-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-failure-analysis",
        },
    )
    assert analysis_response.status_code == 202
    analysis_created = analysis_response.json()

    analysis_get_response = client.get(f"/api/test-runs/{test_run_id}/failure-analysis")
    assert analysis_get_response.status_code == 200
    analysis = analysis_get_response.json()
    assert analysis["id"] == analysis_created["failure_analysis_id"]
    assert analysis["classification"] == "test_script_issue"
    assert analysis["test_result_id"] == str(result_id)
    assert analysis["evidence_artifact_ids"] == [str(stderr_artifact_id)]
    assert analysis["root_cause"] == "fixture coupon_client not found"

    report_response = client.post(
        "/api/reports",
        json_body={
            "project_id": str(project_id),
            "report_type": "automation_execution",
            "related_entity_type": "TestRun",
            "related_entity_id": str(test_run_id),
        },
    )
    assert report_response.status_code == 202
    report_created = report_response.json()
    assert report_created["status"] == "ready"
    assert report_created["evidence_manifest_artifact_id"] is not None

    report_get_response = client.get(f"/api/reports/{report_created['report_id']}")
    assert report_get_response.status_code == 200
    report = report_get_response.json()
    assert report["conclusion"] == "failed"
    assert report["metrics"]["failed"] == 1
    assert report["evidence_manifest"]["missing_evidence"] == []
    evidence = report["evidence_manifest"]["evidence"]
    assert any(item.get("artifact_id") == str(stderr_artifact_id) for item in evidence)
    assert any(item.get("test_result_id") == str(result_id) for item in evidence)
    assert {artifact["artifact_type"] for artifact in report["artifacts"]} >= {"report_md", "report_json"}

    with SessionLocal() as session:
        persisted_analysis = session.get(FailureAnalysis, uuid.UUID(analysis["id"]))
        persisted_report = session.get(Report, uuid.UUID(report["id"]))
        persisted_ai_task = session.get(AITask, uuid.UUID(analysis["ai_task_id"]))
        report_artifacts = list(
            session.scalars(
                select(Artifact).where(
                    Artifact.owner_entity_type == "Report",
                    Artifact.owner_entity_id == uuid.UUID(report["id"]),
                ),
            ),
        )
        quality_gate_decision = session.scalar(select(QualityGateDecision))

    assert persisted_analysis is not None
    assert persisted_analysis.classification == "test_script_issue"
    assert persisted_report is not None
    assert persisted_report.conclusion == "failed"
    assert persisted_ai_task is not None
    assert persisted_ai_task.status == "succeeded"
    manifest_artifact = next(
        artifact for artifact in report_artifacts if artifact.metadata_json.get("manifest_kind") == "evidence_manifest"
    )
    assert manifest_artifact.id == uuid.UUID(report_created["evidence_manifest_artifact_id"])
    assert manifest_artifact.metadata_json["evidence_count"] >= 2
    assert manifest_artifact.metadata_json["manifest_json"]["conclusion"] == "failed"
    assert quality_gate_decision is None


def seed_failed_test_run(session: Session) -> tuple[Project, TestRun, TestResult, Artifact]:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout Golden")
    session.add(project)
    session.flush()
    test_run = TestRun(
        project_id=project.id,
        name="golden pytest failed run",
        command="pytest tests/test_coupon.py -q",
        working_directory="/Users/yanchen/VscodeProject/sample-app",
        status="failed",
        exit_code=1,
        parsed_result_json={"total": 1, "passed": 0, "failed": 1, "skipped": 0, "error": 0},
    )
    session.add(test_run)
    session.flush()
    stderr_artifact = Artifact(
        project_id=project.id,
        owner_entity_type="TestRun",
        owner_entity_id=test_run.id,
        artifact_type="stderr",
        file_path=f"test-runs/{test_run.id}/stderr.log",
        mime_type="text/plain",
        size_bytes=32,
        sha256=f"sha256:stderr:{test_run.id}",
        metadata_json={"created_by_component": "GoldenSmoke"},
    )
    session.add(stderr_artifact)
    session.flush()
    result = TestResult(
        project_id=project.id,
        test_run_id=test_run.id,
        test_name="tests/test_coupon.py::test_expired_coupon",
        test_file="tests/test_coupon.py",
        status="failed",
        duration_ms=24,
        failure_message="fixture coupon_client not found",
        failure_artifact_ids=[stderr_artifact.id],
        metadata_json={"classname": "tests.test_coupon", "source": "golden_smoke"},
    )
    session.add(result)
    session.flush()
    return project, test_run, result, stderr_artifact
