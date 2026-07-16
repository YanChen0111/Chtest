from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import select

from backend.app.main import app
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import CICDChangedFile, CICDRun, QualityGateDecision, UnitTestPatch
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.router import get_session
from backend.app.modules.reporting.models import Report
from backend.app.tests.api.test_cicd_quality_center import ASGIClient, seed_project_repository, session_factory


FIXTURE_PATH = Path("docs/fixtures/09-ci-run-metadata-import-golden.md")


def golden_payload(project_id: uuid.UUID, repository_id: uuid.UUID) -> dict:
    return {
        "project_id": str(project_id),
        "repository_id": str(repository_id),
        "source_type": "ci_import",
        "provider": "github_actions",
        "trigger_type": "imported",
        "external_run_id": "123456",
        "pipeline_name": "CI",
        "job_name": "pytest",
        "conclusion": "success",
        "status": "completed",
        "base_ref": "main",
        "head_ref": "feature/coupon-boundary",
        "commit_sha": "abc123",
        "started_at": "2026-07-01T01:00:00Z",
        "finished_at": "2026-07-01T01:05:00Z",
        "duration_ms": 300000,
        "external_url": "https://example.invalid/runs/123456",
        "changed_files": [
            {
                "path": "app/coupon.py",
                "old_path": None,
                "change_type": "modified",
                "lines_added": 12,
                "lines_deleted": 4,
            },
            {
                "path": "tests/test_coupon.py",
                "old_path": None,
                "change_type": "added",
                "lines_added": 8,
                "lines_deleted": 0,
            },
        ],
        "artifact_references": [
            {
                "name": "pytest report",
                "kind": "test_report",
                "external_url": "https://example.invalid/artifacts/1",
                "sha256": "abc",
                "size_bytes": 1024,
            },
        ],
    }


def test_golden_ci_run_metadata_import_is_evidence_only() -> None:
    assert FIXTURE_PATH.exists()
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project, repository = seed_project_repository(session)
            session.commit()
            project_id = project.id
            repository_id = repository.id

        client = ASGIClient(app)
        import_response = client.post("/api/cicd/runs/import", golden_payload(project_id, repository_id))

        assert import_response.status_code == 202
        imported = import_response.json()
        assert imported["source_type"] == "ci_import"
        assert imported["provider"] == "github_actions"
        assert imported["trigger_type"] == "imported"
        assert imported["import_status"] == "imported"
        assert imported["quality_gate_status"] == "pending"
        assert imported["ci_conclusion"] == "success"
        assert imported["created_artifacts"] == [
            {"artifact_type": "ci_run_metadata", "file_name": "ci_run_metadata.json"},
            {"artifact_type": "changed_files", "file_name": "changed_files.json"},
        ]

        cicd_run_id = uuid.UUID(imported["cicd_run_id"])
        detail_response = client.get(f"/api/cicd/runs/{cicd_run_id}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["source_type"] == "ci_import"
        assert detail["trigger_type"] == "imported"
        assert detail["provider"] == "github_actions"
        assert detail["status"] == "imported"
        assert detail["quality_gate_status"] == "pending"
        assert {artifact["artifact_type"] for artifact in detail["analysis_artifacts"]} == {"ci_run_metadata"}
        detail_metadata = detail["analysis_artifacts"][0]["metadata_json"]
        assert detail_metadata["content_json"]["conclusion"] == "success"
        assert detail_metadata["content_json"]["artifact_references"][0]["inert_reference"] is True

        with SessionLocal() as session:
            cicd_run = session.get(CICDRun, cicd_run_id)
            changed_files = list(
                session.scalars(
                    select(CICDChangedFile)
                    .where(CICDChangedFile.cicd_run_id == cicd_run_id)
                    .order_by(CICDChangedFile.path.asc()),
                ),
            )
            artifacts = list(
                session.scalars(
                    select(Artifact)
                    .where(Artifact.owner_entity_type == "CICDRun", Artifact.owner_entity_id == cicd_run_id)
                    .order_by(Artifact.artifact_type.asc()),
                ),
            )
            assert session.scalar(select(QualityGateDecision)) is None
            assert session.scalar(select(UnitTestPatch)) is None
            assert session.scalar(select(AutomationDraft)) is None
            assert session.scalar(select(TestRun)) is None
            assert session.scalar(select(Report)) is None

        assert cicd_run is not None
        assert cicd_run.source_type == "ci_import"
        assert cicd_run.trigger_type == "imported"
        assert cicd_run.provider == "github_actions"
        assert cicd_run.pipeline_name == "CI"
        assert cicd_run.base_ref == "main"
        assert cicd_run.head_ref == "feature/coupon-boundary"
        assert cicd_run.status == "imported"
        assert cicd_run.quality_gate_status == "pending"
        assert [item.path for item in changed_files] == ["app/coupon.py", "tests/test_coupon.py"]
        assert [item.file_role for item in changed_files] == ["source", "test"]
        assert [item.risk_level for item in changed_files] == ["medium", "low"]

        artifact_by_type = {artifact.artifact_type: artifact for artifact in artifacts}
        assert set(artifact_by_type) == {"changed_files", "ci_run_metadata"}
        ci_metadata = artifact_by_type["ci_run_metadata"].metadata_json
        assert ci_metadata["created_by_component"] == "CICDRunMetadataImport"
        assert ci_metadata["provider_is_inert_label"] is True
        assert ci_metadata["remote_fetch_performed"] is False
        assert ci_metadata["quality_gate_auto_decision"] is False
        assert ci_metadata["content_json"]["external_run_id"] == "123456"
        assert ci_metadata["content_json"]["artifact_references"] == [
            {
                "name": "pytest report",
                "kind": "test_report",
                "external_url": "https://example.invalid/artifacts/1",
                "sha256": "abc",
                "size_bytes": 1024,
                "inert_reference": True,
            },
        ]
        changed_manifest = artifact_by_type["changed_files"].metadata_json["manifest_json"]
        assert [item["path"] for item in changed_manifest["changed_files"]] == ["app/coupon.py", "tests/test_coupon.py"]
    finally:
        app.dependency_overrides.clear()
