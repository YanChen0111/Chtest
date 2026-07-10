from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import QualityGateDecision
from backend.app.modules.execution.models import TestRun
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.api.test_artifact_access import ASGIClient, api_client


FIXTURE_PATH = Path("docs/fixtures/17-execution-run-manifest-golden.md")


def test_golden_execution_run_manifest_inputs_are_existing_evidence_only(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    assert FIXTURE_PATH.exists()
    client, SessionLocal, artifact_root = api_client

    (
        test_run_id,
        artifact_ids,
        missing_runtime_artifact_id,
        missing_environment_snapshot_artifact_id,
    ) = seed_execution_run_manifest_golden(
        SessionLocal,
        artifact_root,
    )
    before_counts = table_counts(SessionLocal)
    before_artifacts = artifact_snapshots(SessionLocal)

    response = client.get(f"/api/test-runs/{test_run_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["command"] == "pytest tests/test_coupon.py -q --junitxml=artifacts/junit.xml"
    assert body["working_directory"] == "/workspace/sample-app"
    assert body["runner_mode"] == "local_subprocess"
    assert body["run_workspace"] == "/tmp/chtest-runs/run-manifest-golden"
    assert body["repository_readonly"] is True
    assert body["network_enabled"] is False
    assert body["parsed_result"] == {"total": 2, "passed": 2, "failed": 0, "skipped": 0, "error": 0}
    assert body["dependency_snapshot_artifact_id"] == str(artifact_ids["dependency_snapshot"])
    assert body["environment_snapshot_artifact_id"] == str(missing_environment_snapshot_artifact_id)
    assert body["runtime_artifact_ids"] == [
        str(artifact_ids["runtime_manifest"]),
        str(missing_runtime_artifact_id),
    ]

    artifacts_by_type = {artifact["artifact_type"]: artifact for artifact in body["artifacts"]}
    assert set(artifacts_by_type) == {
        "runtime_manifest",
        "dependency_snapshot",
        "stdout",
        "parsed_output",
    }
    assert artifacts_by_type["runtime_manifest"]["id"] == str(artifact_ids["runtime_manifest"])
    assert artifacts_by_type["dependency_snapshot"]["id"] == str(artifact_ids["dependency_snapshot"])
    assert artifacts_by_type["stdout"]["id"] == str(artifact_ids["stdout"])
    assert artifacts_by_type["parsed_output"]["id"] == str(artifact_ids["parsed_output"])
    assert artifacts_by_type["stdout"]["file_path"].endswith("/stdout.log")
    assert artifacts_by_type["stdout"]["mime_type"] == "text/plain"
    assert artifacts_by_type["stdout"]["size_bytes"] == len(b"pytest run manifest stdout\n2 passed in 0.03s\n")
    assert artifacts_by_type["stdout"]["metadata_json"] == {
        "created_by_component": "GoldenFixture",
        "runner_mode": "local_subprocess",
        "safe_to_show": True,
        "redaction_applied": False,
    }

    manifest_rows = build_manifest_rows(body)
    assert manifest_rows["runtime_file_1"] == "local_artifact"
    assert manifest_rows["runtime_file_2"] == "unavailable"
    assert manifest_rows["dependency_snapshot"] == "local_artifact"
    assert manifest_rows["environment_snapshot"] == "missing"
    assert manifest_rows["stdout"] == "local_artifact"
    assert manifest_rows["stderr"] == "unavailable"
    assert manifest_rows["parsed_output"] == "local_artifact"
    assert manifest_rows["junit"] == "unavailable"
    assert manifest_rows["coverage"] == "unavailable"

    stdout_response = client.get(f"/api/artifacts/{artifact_ids['stdout']}/download")
    assert stdout_response.status_code == 200
    assert stdout_response.body == b"pytest run manifest stdout\n2 passed in 0.03s\n"
    assert hashlib.sha256(stdout_response.body).hexdigest() == artifacts_by_type["stdout"]["sha256"]

    missing_runtime_response = client.get(f"/api/artifacts/{missing_runtime_artifact_id}/download")
    assert missing_runtime_response.status_code == 404
    assert missing_runtime_response.json()["error_code"] == "ARTIFACT_NOT_FOUND"

    after_counts = table_counts(SessionLocal)
    after_artifacts = artifact_snapshots(SessionLocal)
    assert after_counts == before_counts
    assert after_artifacts == before_artifacts
    assert after_counts["reports"] == 0
    assert after_counts["failure_analyses"] == 0
    assert after_counts["quality_gate_decisions"] == 0
    assert after_counts["automation_drafts"] == 0
    assert after_counts["automation_repair_tasks"] == 0


def seed_execution_run_manifest_golden(
    SessionLocal: sessionmaker[Session],
    artifact_root: Path,
) -> tuple[uuid.UUID, dict[str, uuid.UUID], uuid.UUID, uuid.UUID]:
    from backend.app.modules.projects.models import Project, Workspace

    with SessionLocal() as session:
        workspace = Workspace(name="Personal Workspace")
        session.add(workspace)
        session.flush()
        project = Project(workspace_id=workspace.id, name="Execution Run Manifest Golden")
        session.add(project)
        session.flush()

        test_run = TestRun(
            project_id=project.id,
            name="golden execution run manifest",
            command="pytest tests/test_coupon.py -q --junitxml=artifacts/junit.xml",
            working_directory="/workspace/sample-app",
            runner_mode="local_subprocess",
            run_workspace="/tmp/chtest-runs/run-manifest-golden",
            repository_readonly=True,
            network_enabled=False,
            status="passed",
            exit_code=0,
            duration_ms=30,
            parsed_result_json={"total": 2, "passed": 2, "failed": 0, "skipped": 0, "error": 0},
        )
        session.add(test_run)
        session.flush()

        artifact_specs = {
            "runtime_manifest": (
                "runtime_manifest.json",
                b'{"runtime_artifacts":["test_from_draft.py"]}\n',
                "application/json",
            ),
            "dependency_snapshot": (
                "dependency_snapshot.json",
                b'{"python":"3.12","pytest":"8.3.3"}\n',
                "application/json",
            ),
            "stdout": (
                "stdout.log",
                b"pytest run manifest stdout\n2 passed in 0.03s\n",
                "text/plain",
            ),
            "parsed_output": (
                "parsed_result.json",
                b'{"total":2,"passed":2,"failed":0,"skipped":0,"error":0}\n',
                "application/json",
            ),
        }
        artifact_ids: dict[str, uuid.UUID] = {}
        for artifact_type, (filename, content, mime_type) in artifact_specs.items():
            artifact = create_local_testrun_artifact(
                session,
                artifact_root,
                project_id=project.id,
                test_run_id=test_run.id,
                artifact_type=artifact_type,
                filename=filename,
                content=content,
                mime_type=mime_type,
            )
            artifact_ids[artifact_type] = artifact.id

        missing_runtime_artifact_id = uuid.uuid4()
        missing_environment_snapshot_artifact_id = uuid.uuid4()
        test_run.runtime_artifact_ids = [artifact_ids["runtime_manifest"], missing_runtime_artifact_id]
        test_run.dependency_snapshot_artifact_id = artifact_ids["dependency_snapshot"]
        test_run.environment_snapshot_artifact_id = missing_environment_snapshot_artifact_id
        session.commit()

        return test_run.id, artifact_ids, missing_runtime_artifact_id, missing_environment_snapshot_artifact_id


def create_local_testrun_artifact(
    session: Session,
    artifact_root: Path,
    *,
    project_id: uuid.UUID,
    test_run_id: uuid.UUID,
    artifact_type: str,
    filename: str,
    content: bytes,
    mime_type: str,
) -> Artifact:
    file_path = f"projects/{project_id}/test-runs/{test_run_id}/{filename}"
    destination = artifact_root / file_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    artifact = Artifact(
        project_id=project_id,
        owner_entity_type="TestRun",
        owner_entity_id=test_run_id,
        artifact_type=artifact_type,
        file_path=file_path,
        mime_type=mime_type,
        size_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        metadata_json={
            "created_by_component": "GoldenFixture",
            "runner_mode": "local_subprocess",
            "safe_to_show": True,
            "redaction_applied": False,
        },
    )
    session.add(artifact)
    session.flush()
    return artifact


def build_manifest_rows(test_run_read: dict[str, Any]) -> dict[str, str]:
    artifacts_by_id = {artifact["id"]: artifact for artifact in test_run_read["artifacts"]}
    artifacts_by_type = {artifact["artifact_type"]: artifact for artifact in test_run_read["artifacts"]}
    rows: dict[str, str] = {}
    for index, artifact_id in enumerate(test_run_read["runtime_artifact_ids"], start=1):
        rows[f"runtime_file_{index}"] = "local_artifact" if artifact_id in artifacts_by_id else "unavailable"
    rows["dependency_snapshot"] = (
        "local_artifact"
        if test_run_read["dependency_snapshot_artifact_id"] in artifacts_by_id
        else "missing"
    )
    rows["environment_snapshot"] = (
        "local_artifact"
        if test_run_read["environment_snapshot_artifact_id"] in artifacts_by_id
        else "missing"
    )
    output_labels = {
        "stdout": "stdout",
        "stderr": "stderr",
        "parsed_output": "parsed_output",
        "junit": "junit",
        "coverage": "coverage",
    }
    for artifact_type, label in output_labels.items():
        rows[label] = "local_artifact" if artifact_type in artifacts_by_type else "unavailable"
    return rows


def table_counts(SessionLocal: sessionmaker[Session]) -> dict[str, int]:
    with SessionLocal() as session:
        automation_repair_table = Base.metadata.tables.get("automation_repair_tasks")
        return {
            "artifacts": session.scalar(select(func.count()).select_from(Artifact)) or 0,
            "ai_tasks": session.scalar(select(func.count()).select_from(AITask)) or 0,
            "test_runs": session.scalar(select(func.count()).select_from(TestRun)) or 0,
            "reports": session.scalar(select(func.count()).select_from(Report)) or 0,
            "failure_analyses": session.scalar(select(func.count()).select_from(FailureAnalysis)) or 0,
            "quality_gate_decisions": session.scalar(select(func.count()).select_from(QualityGateDecision)) or 0,
            "automation_drafts": session.scalar(select(func.count()).select_from(AutomationDraft)) or 0,
            "automation_repair_tasks": (
                session.scalar(select(func.count()).select_from(automation_repair_table)) or 0
                if automation_repair_table is not None
                else 0
            ),
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
