from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import QualityGateDecision
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.api.test_artifact_access import ASGIClient, api_client


FIXTURE_PATH = Path("docs/fixtures/17-execution-run-manifest-golden.md")


def test_golden_execution_run_manifest_inputs_remain_existing_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    assert FIXTURE_PATH.exists()
    client, SessionLocal, artifact_root = api_client
    project_id, test_run_id, runtime_artifact_id, stdout_artifact_id = seed_execution_run_manifest_golden(
        SessionLocal,
        artifact_root,
    )
    before_counts = table_counts(SessionLocal)
    before_artifacts = artifact_snapshots(SessionLocal)

    response = client.get(f"/api/test-runs/{test_run_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(test_run_id)
    assert body["project_id"] == str(project_id)
    assert body["command"] == "pytest tests/test_manifest.py -q"
    assert body["working_directory"] == "/workspace/checkout"
    assert body["runner_mode"] == "local_subprocess"
    assert body["run_workspace"] == f"artifacts/projects/{project_id}/test-runs/{test_run_id}/workspace"
    assert body["repository_readonly"] is True
    assert body["network_enabled"] is False
    assert body["runtime_artifact_ids"] == [str(runtime_artifact_id)]
    assert body["dependency_snapshot_artifact_id"] is None
    assert body["environment_snapshot_artifact_id"] is None
    assert body["parsed_result"] == {"total": 1, "passed": 1, "failed": 0, "skipped": 0, "error": 0}
    assert body["test_results"] == []
    artifacts_by_type = {artifact["artifact_type"]: artifact for artifact in body["artifacts"]}
    assert artifacts_by_type["runtime_manifest"]["id"] == str(runtime_artifact_id)
    assert artifacts_by_type["stdout"]["id"] == str(stdout_artifact_id)

    runtime_response = client.get(f"/api/artifacts/{runtime_artifact_id}/download")

    assert runtime_response.status_code == 200
    assert runtime_response.headers["content-type"].startswith("application/json")
    assert 'filename="runtime_manifest.json"' in runtime_response.headers["content-disposition"]
    assert b"tests/test_manifest.py" in runtime_response.body

    with SessionLocal() as session:
        persisted_run = session.get(TestRun, test_run_id)
        assert session.scalar(select(Report)) is None
        assert session.scalar(select(FailureAnalysis)) is None
        assert session.scalar(select(QualityGateDecision)) is None

    after_counts = table_counts(SessionLocal)
    after_artifacts = artifact_snapshots(SessionLocal)

    assert persisted_run is not None
    assert persisted_run.status == "passed"
    assert after_counts == before_counts
    assert after_artifacts == before_artifacts


def seed_execution_run_manifest_golden(
    SessionLocal: sessionmaker[Session],
    artifact_root: Path,
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID, uuid.UUID]:
    with SessionLocal() as session:
        workspace = Workspace(name="Personal Workspace")
        session.add(workspace)
        session.flush()
        project = Project(workspace_id=workspace.id, name="Execution Manifest Golden")
        session.add(project)
        session.flush()

        test_run = TestRun(
            project_id=project.id,
            name="golden pytest manifest run",
            command="pytest tests/test_manifest.py -q",
            working_directory="/workspace/checkout",
            runner_mode="local_subprocess",
            run_workspace=f"artifacts/projects/{project.id}/test-runs/pending/workspace",
            repository_readonly=True,
            network_enabled=False,
            status="passed",
            exit_code=0,
            duration_ms=42,
            parsed_result_json={"total": 1, "passed": 1, "failed": 0, "skipped": 0, "error": 0},
        )
        session.add(test_run)
        session.flush()
        test_run.run_workspace = f"artifacts/projects/{project.id}/test-runs/{test_run.id}/workspace"

        runtime_content = b'{"files":["tests/test_manifest.py"],"runner_mode":"local_subprocess"}\n'
        stdout_content = b"1 passed in 0.04s\n"
        runtime_artifact = write_artifact(
            artifact_root,
            project_id=project.id,
            test_run_id=test_run.id,
            artifact_type="runtime_manifest",
            filename="runtime_manifest.json",
            mime_type="application/json",
            content=runtime_content,
        )
        stdout_artifact = write_artifact(
            artifact_root,
            project_id=project.id,
            test_run_id=test_run.id,
            artifact_type="stdout",
            filename="stdout.log",
            mime_type="text/plain",
            content=stdout_content,
        )
        session.add_all([runtime_artifact, stdout_artifact])
        session.flush()
        test_run.runtime_artifact_ids = [runtime_artifact.id]
        session.add(test_run)
        session.commit()
        return project.id, test_run.id, runtime_artifact.id, stdout_artifact.id


def write_artifact(
    artifact_root: Path,
    *,
    project_id: uuid.UUID,
    test_run_id: uuid.UUID,
    artifact_type: str,
    filename: str,
    mime_type: str,
    content: bytes,
) -> Artifact:
    file_path = f"projects/{project_id}/test-runs/{test_run_id}/{filename}"
    destination = artifact_root / file_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return Artifact(
        project_id=project_id,
        owner_entity_type="TestRun",
        owner_entity_id=test_run_id,
        artifact_type=artifact_type,
        file_path=file_path,
        mime_type=mime_type,
        size_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        metadata_json={"created_by_component": "GoldenFixture", "runner_mode": "local_subprocess"},
    )


def table_counts(SessionLocal: sessionmaker[Session]) -> dict[str, int]:
    with SessionLocal() as session:
        return {
            "ai_tasks": session.scalar(select(func.count()).select_from(AITask)) or 0,
            "artifacts": session.scalar(select(func.count()).select_from(Artifact)) or 0,
            "automation_drafts": session.scalar(select(func.count()).select_from(AutomationDraft)) or 0,
            "test_runs": session.scalar(select(func.count()).select_from(TestRun)) or 0,
            "reports": session.scalar(select(func.count()).select_from(Report)) or 0,
            "failure_analyses": session.scalar(select(func.count()).select_from(FailureAnalysis)) or 0,
            "quality_gate_decisions": session.scalar(select(func.count()).select_from(QualityGateDecision)) or 0,
        }


def artifact_snapshots(SessionLocal: sessionmaker[Session]) -> dict[str, dict[str, object]]:
    with SessionLocal() as session:
        artifacts = session.scalars(select(Artifact).order_by(Artifact.id)).all()
        return {
            str(artifact.id): {
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
