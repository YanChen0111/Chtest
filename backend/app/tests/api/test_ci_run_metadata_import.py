from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from backend.app.main import app
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import CICDChangedFile, CICDRun, QualityGateDecision, UnitTestPatch
from backend.app.modules.cicd.service import (
    CIImportControlFieldRejectedError,
    CIImportCredentialRejectedError,
    CIImportExternalFetchForbiddenError,
    CIImportInvalidPayloadError,
    CIImportUnsupportedProviderOperationError,
    parse_ci_run_metadata_import,
)
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.router import get_session
from backend.app.modules.reporting.models import Report
from backend.app.tests.api.test_cicd_quality_center import ASGIClient, seed_project_repository, session_factory


def valid_import_payload() -> dict:
    return {
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


def valid_import_api_payload(project_id: uuid.UUID, repository_id: uuid.UUID) -> dict:
    payload = valid_import_payload()
    payload["project_id"] = str(project_id)
    payload["repository_id"] = str(repository_id)
    return payload


def response_error_code(body: dict) -> str:
    detail = body.get("detail")
    if isinstance(detail, dict):
        return detail["error_code"]
    return body["error_code"]


def test_import_ci_run_metadata_api_persists_evidence_only_records() -> None:
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
        response = client.post("/api/cicd/runs/import", valid_import_api_payload(project_id, repository_id))

        assert response.status_code == 202
        body = response.json()
        assert body["source_type"] == "ci_import"
        assert body["provider"] == "github_actions"
        assert body["trigger_type"] == "imported"
        assert body["import_status"] == "imported"
        assert body["quality_gate_status"] == "pending"
        assert body["ci_conclusion"] == "success"
        assert body["created_artifacts"] == [
            {"artifact_type": "ci_run_metadata", "file_name": "ci_run_metadata.json"},
            {"artifact_type": "changed_files", "file_name": "changed_files.json"},
        ]

        cicd_run_id = uuid.UUID(body["cicd_run_id"])
        get_response = client.get(f"/api/cicd/runs/{cicd_run_id}")
        assert get_response.status_code == 200
        read_body = get_response.json()
        assert read_body["source_type"] == "ci_import"
        assert read_body["trigger_type"] == "imported"
        assert read_body["provider"] == "github_actions"
        assert read_body["pipeline_name"] == "CI"
        assert read_body["base_ref"] == "main"
        assert read_body["head_ref"] == "feature/coupon-boundary"
        assert read_body["quality_gate_status"] == "pending"
        assert read_body["status"] == "imported"
        assert [item["path"] for item in read_body["changed_files"]] == ["app/coupon.py", "tests/test_coupon.py"]
        assert {artifact["artifact_type"] for artifact in read_body["analysis_artifacts"]} == {"ci_run_metadata"}
        imported_metadata = read_body["analysis_artifacts"][0]["metadata_json"]
        assert imported_metadata["content_json"]["conclusion"] == "success"
        assert imported_metadata["content_json"]["artifact_references"][0]["kind"] == "test_report"

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
        assert cicd_run.project_id == project_id
        assert cicd_run.repository_id == repository_id
        assert cicd_run.source_type == "ci_import"
        assert cicd_run.trigger_type == "imported"
        assert cicd_run.provider == "github_actions"
        assert cicd_run.pipeline_name == "CI"
        assert cicd_run.base_ref == "main"
        assert cicd_run.head_ref == "feature/coupon-boundary"
        assert cicd_run.status == "imported"
        assert cicd_run.quality_gate_status == "pending"
        assert [item.file_role for item in changed_files] == ["source", "test"]
        assert [item.risk_level for item in changed_files] == ["medium", "low"]

        artifact_by_type = {artifact.artifact_type: artifact for artifact in artifacts}
        assert set(artifact_by_type) == {"changed_files", "ci_run_metadata"}
        ci_metadata = artifact_by_type["ci_run_metadata"].metadata_json
        assert ci_metadata["created_by_component"] == "CICDRunMetadataImport"
        assert ci_metadata["source_type"] == "ci_import"
        assert ci_metadata["provider"] == "github_actions"
        assert ci_metadata["provider_is_inert_label"] is True
        assert ci_metadata["remote_fetch_performed"] is False
        assert ci_metadata["quality_gate_auto_decision"] is False
        assert ci_metadata["artifact_reference_count"] == 1
        assert ci_metadata["content_json"]["conclusion"] == "success"
        assert ci_metadata["content_json"]["artifact_references"][0]["inert_reference"] is True
        changed_manifest = artifact_by_type["changed_files"].metadata_json["manifest_json"]
        assert changed_manifest["changed_files"][0]["path"] == "app/coupon.py"
    finally:
        app.dependency_overrides.clear()


def test_import_ci_run_metadata_api_rejects_duplicate_external_run() -> None:
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
        payload = valid_import_api_payload(project_id, repository_id)
        first_response = client.post("/api/cicd/runs/import", payload)
        second_response = client.post("/api/cicd/runs/import", payload)

        assert first_response.status_code == 202
        assert second_response.status_code == 409
        assert response_error_code(second_response.json()) == "CI_IMPORT_DUPLICATE_EXTERNAL_RUN"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("patch", "error_code"),
    [
        ({"token": "secret"}, "CI_IMPORT_CREDENTIAL_REJECTED"),
        ({"rerun": True}, "CI_IMPORT_CONTROL_FIELD_REJECTED"),
        ({"fetch_artifacts": True}, "CI_IMPORT_EXTERNAL_FETCH_FORBIDDEN"),
        ({"provider_operation": "trigger"}, "CI_IMPORT_UNSUPPORTED_PROVIDER_OPERATION"),
        ({"conclusion": "passed"}, "INVALID_CI_IMPORT_PAYLOAD"),
    ],
)
def test_import_ci_run_metadata_api_maps_import_errors(patch: dict, error_code: str) -> None:
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

        payload = valid_import_api_payload(project_id, repository_id)
        payload.update(patch)
        response = ASGIClient(app).post("/api/cicd/runs/import", payload)

        assert response.status_code == 400
        assert response_error_code(response.json()) == error_code
    finally:
        app.dependency_overrides.clear()


def test_parse_ci_run_metadata_import_normalizes_evidence() -> None:
    parsed = parse_ci_run_metadata_import(valid_import_payload())

    assert parsed.source_type == "ci_import"
    assert parsed.provider == "github_actions"
    assert parsed.trigger_type == "imported"
    assert parsed.external_run_id == "123456"
    assert parsed.pipeline_name == "CI"
    assert parsed.job_name == "pytest"
    assert parsed.conclusion == "success"
    assert parsed.status == "completed"
    assert parsed.base_ref == "main"
    assert parsed.head_ref == "feature/coupon-boundary"
    assert parsed.commit_sha == "abc123"
    assert parsed.started_at == "2026-07-01T01:00:00Z"
    assert parsed.finished_at == "2026-07-01T01:05:00Z"
    assert parsed.duration_ms == 300000
    assert parsed.external_url == "https://example.invalid/runs/123456"

    assert [item.path for item in parsed.changed_files] == ["app/coupon.py", "tests/test_coupon.py"]
    assert [item.file_role for item in parsed.changed_files] == ["source", "test"]
    assert [item.language for item in parsed.changed_files] == ["python", "python"]
    assert [item.risk_level for item in parsed.changed_files] == ["medium", "low"]
    assert parsed.changed_files[0].risk_reasons == ["source file changed"]
    assert parsed.changed_files[1].risk_reasons == ["test file changed"]

    assert len(parsed.artifact_references) == 1
    assert parsed.artifact_references[0].name == "pytest report"
    assert parsed.artifact_references[0].kind == "test_report"
    assert parsed.artifact_references[0].external_url == "https://example.invalid/artifacts/1"
    assert parsed.artifact_references[0].sha256 == "abc"
    assert parsed.artifact_references[0].size_bytes == 1024

    metadata = parsed.to_artifact_metadata()
    assert metadata == {
        "created_by_component": "CICDRunMetadataImport",
        "source_type": "ci_import",
        "provider": "github_actions",
        "provider_is_inert_label": True,
        "import_mode": "static_json",
        "changed_file_count": 2,
        "artifact_reference_count": 1,
        "remote_fetch_performed": False,
        "quality_gate_auto_decision": False,
    }

    content = parsed.to_artifact_content()
    assert content["source_type"] == "ci_import"
    assert content["provider_is_inert_label"] is True
    assert content["import_mode"] == "static_json"
    assert content["changed_files"][0]["file_role"] == "source"
    assert content["artifact_references"][0]["kind"] == "test_report"
    assert content["remote_fetch_performed"] is False
    assert content["quality_gate_auto_decision"] is False


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("webhook", {"action": "completed"}),
        ("event_action", "completed"),
        ("signature", "sha256=abc"),
        ("delivery_id", "delivery-1"),
        ("callback_url", "https://example.invalid/callback"),
        ("trigger", "workflow_dispatch"),
        ("rerun", True),
        ("cancel", True),
        ("schedule", "nightly"),
        ("pr_comment", "run tests"),
        ("commit_status_update", {"state": "success"}),
        ("branch_protection", {"required": True}),
        ("merge", True),
        ("deploy", True),
        ("release", True),
        ("tag", "v1.0.0"),
        ("publish", True),
        ("environment_promotion", "prod"),
    ],
)
def test_parse_ci_run_metadata_import_rejects_remote_control_fields(field_name: str, field_value: object) -> None:
    payload = valid_import_payload()
    payload[field_name] = field_value

    with pytest.raises(CIImportControlFieldRejectedError) as exc_info:
        parse_ci_run_metadata_import(payload)

    assert exc_info.value.error_code == "CI_IMPORT_CONTROL_FIELD_REJECTED"


@pytest.mark.parametrize(
    "field_name",
    ["token", "secret", "oauth_token", "pat", "private_key", "password", "credential_id", "organization_permissions"],
)
def test_parse_ci_run_metadata_import_rejects_credentials(field_name: str) -> None:
    payload = valid_import_payload()
    payload[field_name] = "sensitive"

    with pytest.raises(CIImportCredentialRejectedError) as exc_info:
        parse_ci_run_metadata_import(payload)

    assert exc_info.value.error_code == "CI_IMPORT_CREDENTIAL_REJECTED"


@pytest.mark.parametrize("field_name", ["fetch_artifacts", "download_artifacts", "fetch_logs", "fetch_external_urls"])
def test_parse_ci_run_metadata_import_rejects_external_fetch_requests(field_name: str) -> None:
    payload = valid_import_payload()
    payload[field_name] = True

    with pytest.raises(CIImportExternalFetchForbiddenError) as exc_info:
        parse_ci_run_metadata_import(payload)

    assert exc_info.value.error_code == "CI_IMPORT_EXTERNAL_FETCH_FORBIDDEN"


@pytest.mark.parametrize("operation", ["rerun", "cancel", "trigger", "fetch_logs"])
def test_parse_ci_run_metadata_import_rejects_provider_operations(operation: str) -> None:
    payload = valid_import_payload()
    payload["provider_operation"] = operation

    with pytest.raises(CIImportUnsupportedProviderOperationError) as exc_info:
        parse_ci_run_metadata_import(payload)

    assert exc_info.value.error_code == "CI_IMPORT_UNSUPPORTED_PROVIDER_OPERATION"


@pytest.mark.parametrize(
    "patch",
    [
        {"source_type": "local_diff"},
        {"trigger_type": "manual"},
        {"conclusion": "passed"},
        {"provider": "github"},
        {"changed_files": []},
        {"changed_files": [{"path": "", "change_type": "modified", "lines_added": 1, "lines_deleted": 0}]},
        {"changed_files": [{"path": "../secret.py", "change_type": "modified", "lines_added": 1, "lines_deleted": 0}]},
        {"changed_files": [{"path": "app/coupon.py", "change_type": "copied", "lines_added": 1, "lines_deleted": 0}]},
        {"changed_files": [{"path": "app/coupon.py", "change_type": "modified", "lines_added": -1, "lines_deleted": 0}]},
        {"artifact_references": [{"name": "", "kind": "test_report", "external_url": "https://example.invalid/a"}]},
        {"artifact_references": [{"name": "pytest", "kind": "", "external_url": "https://example.invalid/a"}]},
    ],
)
def test_parse_ci_run_metadata_import_rejects_invalid_payloads(patch: dict) -> None:
    payload = valid_import_payload()
    payload.update(patch)

    with pytest.raises(CIImportInvalidPayloadError) as exc_info:
        parse_ci_run_metadata_import(payload)

    assert exc_info.value.error_code == "INVALID_CI_IMPORT_PAYLOAD"
