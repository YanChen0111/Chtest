from __future__ import annotations

import pytest

from backend.app.modules.cicd.service import (
    CIImportControlFieldRejectedError,
    CIImportCredentialRejectedError,
    CIImportExternalFetchForbiddenError,
    CIImportInvalidPayloadError,
    CIImportUnsupportedProviderOperationError,
    parse_ci_run_metadata_import,
)


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
