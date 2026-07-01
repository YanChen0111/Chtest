from __future__ import annotations

import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import CICDRun, QualityGateDecision, UnitTestPatch
from backend.app.modules.execution.models import TestRun
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.api.test_artifact_access import ASGIClient, api_client


FIXTURE_PATH = Path("docs/fixtures/14-ci-imported-artifact-reference-clarity-golden.md")


def test_golden_ci_imported_artifact_reference_stays_inert(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    assert FIXTURE_PATH.exists()
    client, SessionLocal, artifact_root = api_client
    local_content = b"ci metadata\n"

    with SessionLocal() as session:
        from backend.app.modules.projects.models import Project, Workspace

        workspace = Workspace(name="Personal Workspace")
        session.add(workspace)
        session.flush()
        project = Project(workspace_id=workspace.id, name="CI Imported Reference Clarity")
        session.add(project)
        session.flush()
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

        local_path = f"projects/{project.id}/cicd-quality/{cicd_run.id}/ci_run_metadata.json"
        destination = artifact_root / local_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(local_content)
        ci_metadata_artifact = Artifact(
            project_id=project.id,
            owner_entity_type="CICDRun",
            owner_entity_id=cicd_run.id,
            artifact_type="ci_run_metadata",
            file_path=local_path,
            mime_type="application/json",
            size_bytes=len(local_content),
            sha256=hashlib.sha256(local_content).hexdigest(),
            metadata_json={
                "created_by_component": "CICDRunMetadataImport",
                "provider_is_inert_label": True,
                "remote_fetch_performed": False,
                "quality_gate_auto_decision": False,
                "artifact_reference_count": 1,
                "content_json": {
                    "artifact_references": [
                        {
                            "name": "pytest report",
                            "kind": "test_report",
                            "external_url": "https://example.invalid/artifacts/1",
                            "sha256": "remote-sha",
                            "size_bytes": 1024,
                            "inert_reference": True,
                        },
                    ],
                },
            },
        )
        external_reference = Artifact(
            project_id=project.id,
            owner_entity_type="CICDRun",
            owner_entity_id=cicd_run.id,
            artifact_type="ci_run_metadata",
            file_path="https://example.invalid/artifacts/1",
            mime_type="application/json",
            size_bytes=1024,
            sha256="remote-sha",
            metadata_json={
                "created_by_component": "CICDRunMetadataImport",
                "inert_reference": True,
                "remote_fetch_performed": False,
                "external_url": "https://example.invalid/artifacts/1",
            },
        )
        session.add_all([ci_metadata_artifact, external_reference])
        session.commit()
        cicd_run_id = cicd_run.id
        ci_metadata_id = ci_metadata_artifact.id
        external_reference_id = external_reference.id

    external_response = client.get(f"/api/artifacts/{external_reference_id}/download")

    assert external_response.status_code == 422
    assert external_response.json()["error_code"] == "ARTIFACT_NOT_LOCAL"

    local_response = client.get(f"/api/artifacts/{ci_metadata_id}/download")

    assert local_response.status_code == 200
    assert local_response.body == local_content

    with SessionLocal() as session:
        artifacts = list(
            session.scalars(
                select(Artifact).where(
                    Artifact.owner_entity_type == "CICDRun",
                    Artifact.owner_entity_id == cicd_run_id,
                ),
            ),
        )
        ci_metadata = session.get(Artifact, ci_metadata_id)
        assert session.scalar(select(TestRun)) is None
        assert session.scalar(select(Report)) is None
        assert session.scalar(select(FailureAnalysis)) is None
        assert session.scalar(select(QualityGateDecision)) is None
        assert session.scalar(select(UnitTestPatch)) is None
        assert session.scalar(select(AutomationDraft)) is None

    assert len(artifacts) == 2
    assert ci_metadata is not None
    reference = ci_metadata.metadata_json["content_json"]["artifact_references"][0]
    assert reference["name"] == "pytest report"
    assert reference["inert_reference"] is True
    assert ci_metadata.metadata_json["remote_fetch_performed"] is False
    assert ci_metadata.metadata_json["quality_gate_auto_decision"] is False
