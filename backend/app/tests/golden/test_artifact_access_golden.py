from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.cicd.models import CICDRun
from backend.app.modules.execution.models import TestRun
from backend.app.tests.api.test_artifact_access import ASGIClient, api_client


FIXTURE_PATH = Path("docs/fixtures/12-local-artifact-access-golden.md")


def test_golden_local_testrun_artifact_access_preserves_evidence_boundary(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    assert FIXTURE_PATH.exists()
    client, SessionLocal, artifact_root = api_client
    content = b"pytest golden stdout\n1 passed in 0.02s\n"
    expected_sha256 = hashlib.sha256(content).hexdigest()

    project, test_run, stdout_artifact, external_reference = seed_artifact_access_golden(
        SessionLocal,
        artifact_root,
        content=content,
        sha256=expected_sha256,
    )
    original_artifact_state = {
        "owner_entity_type": stdout_artifact.owner_entity_type,
        "owner_entity_id": stdout_artifact.owner_entity_id,
        "file_path": stdout_artifact.file_path,
        "size_bytes": stdout_artifact.size_bytes,
        "sha256": stdout_artifact.sha256,
    }

    download_response = client.get(f"/api/artifacts/{stdout_artifact.id}/download")

    assert download_response.status_code == 200
    assert download_response.body == content
    assert download_response.headers["content-type"].startswith("text/plain")
    assert "attachment" in download_response.headers["content-disposition"]
    assert 'filename="stdout.log"' in download_response.headers["content-disposition"]
    assert "projects/" not in download_response.headers["content-disposition"]

    persisted_size = len(download_response.body)
    persisted_sha256 = hashlib.sha256(download_response.body).hexdigest()
    assert persisted_size == stdout_artifact.size_bytes == len(content)
    assert persisted_sha256 == stdout_artifact.sha256 == expected_sha256

    external_response = client.get(f"/api/artifacts/{external_reference.id}/download")

    assert external_response.status_code == 422
    assert external_response.json()["error_code"] == "ARTIFACT_NOT_LOCAL"

    with SessionLocal() as session:
        persisted_run = session.get(TestRun, test_run.id)
        persisted_artifacts = list(
            session.scalars(
                select(Artifact).where(
                    Artifact.project_id == project.id,
                    Artifact.owner_entity_type == "TestRun",
                    Artifact.owner_entity_id == test_run.id,
                ),
            ),
        )
        persisted_stdout = session.get(Artifact, stdout_artifact.id)
        persisted_external = session.get(Artifact, external_reference.id)

    assert persisted_run is not None
    assert persisted_run.status == "passed"
    assert persisted_run.runtime_artifact_ids == [stdout_artifact.id]
    assert [artifact.artifact_type for artifact in persisted_artifacts] == ["stdout"]
    assert persisted_stdout is not None
    assert persisted_stdout.owner_entity_type == original_artifact_state["owner_entity_type"]
    assert persisted_stdout.owner_entity_id == original_artifact_state["owner_entity_id"]
    assert persisted_stdout.file_path == original_artifact_state["file_path"]
    assert persisted_stdout.size_bytes == original_artifact_state["size_bytes"]
    assert persisted_stdout.sha256 == original_artifact_state["sha256"]
    assert persisted_external is not None
    assert persisted_external.metadata_json["provider_is_inert_label"] is True
    assert persisted_external.metadata_json["remote_fetch_performed"] is False


def seed_artifact_access_golden(
    SessionLocal: sessionmaker[Session],
    artifact_root: Path,
    *,
    content: bytes,
    sha256: str,
) -> tuple[object, TestRun, Artifact, Artifact]:
    with SessionLocal() as session:
        from backend.app.modules.projects.models import Project, Workspace

        workspace = Workspace(name="Personal Workspace")
        session.add(workspace)
        session.flush()
        project = Project(workspace_id=workspace.id, name="Artifact Access Golden")
        session.add(project)
        session.flush()

        test_run = TestRun(
            project_id=project.id,
            name="golden pytest evidence run",
            command="pytest tests/test_coupon.py -q",
            working_directory="/workspace/sample-app",
            runner_mode="local_subprocess",
            repository_readonly=True,
            network_enabled=False,
            status="passed",
            exit_code=0,
            duration_ms=20,
            parsed_result_json={"total": 1, "passed": 1, "failed": 0, "skipped": 0, "error": 0},
        )
        session.add(test_run)
        session.flush()

        file_path = f"projects/{project.id}/test-runs/{test_run.id}/stdout.log"
        destination = artifact_root / file_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

        stdout_artifact = Artifact(
            project_id=project.id,
            owner_entity_type="TestRun",
            owner_entity_id=test_run.id,
            artifact_type="stdout",
            file_path=file_path,
            mime_type="text/plain",
            size_bytes=len(content),
            sha256=sha256,
            metadata_json={
                "created_by_component": "GoldenFixture",
                "runner_mode": "local_subprocess",
                "safe_to_show": True,
                "redaction_applied": False,
            },
        )
        session.add(stdout_artifact)
        session.flush()
        test_run.runtime_artifact_ids = [stdout_artifact.id]

        cicd_run = CICDRun(
            project_id=project.id,
            source_type="ci_import",
            trigger_type="imported",
            provider="github_actions",
            pipeline_name="CI",
            status="imported",
            quality_gate_status="pending",
        )
        session.add(cicd_run)
        session.flush()
        external_reference = Artifact(
            project_id=project.id,
            owner_entity_type="CICDRun",
            owner_entity_id=cicd_run.id,
            artifact_type="ci_run_metadata",
            file_path="https://example.invalid/artifacts/pytest-report",
            mime_type="application/json",
            size_bytes=1024,
            sha256="external-reference-sha256",
            metadata_json={
                "created_by_component": "GoldenFixture",
                "provider_is_inert_label": True,
                "remote_fetch_performed": False,
                "external_url": "https://example.invalid/artifacts/pytest-report",
            },
        )
        session.add(external_reference)
        session.commit()

        return project, test_run, stdout_artifact, external_reference
