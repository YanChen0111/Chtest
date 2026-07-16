from __future__ import annotations

import hashlib
from pathlib import Path

from backend.app.tests.golden.test_artifact_access_golden import seed_artifact_access_golden
from backend.app.tests.api.test_artifact_access import ASGIClient, api_client
from sqlalchemy.orm import Session, sessionmaker


FIXTURE_PATH = Path("docs/fixtures/13-execution-evidence-summary-golden.md")


def test_golden_execution_evidence_summary_ties_manifest_to_local_artifacts(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    assert FIXTURE_PATH.exists()
    client, SessionLocal, artifact_root = api_client
    content = b"pytest summary stdout\n1 passed in 0.02s\n"
    expected_sha256 = hashlib.sha256(content).hexdigest()
    _project, _test_run, stdout_artifact, external_reference = seed_artifact_access_golden(
        SessionLocal,
        artifact_root,
        content=content,
        sha256=expected_sha256,
    )

    evidence_summary = {
        "evidence": [
            {
                "artifact_id": str(stdout_artifact.id),
                "artifact_type": stdout_artifact.artifact_type,
                "supports_claim": "golden pytest run includes stdout evidence",
                "required": True,
                "download_url": f"/api/artifacts/{stdout_artifact.id}/download",
                "downloadable": True,
                "availability": "local_artifact",
            },
            {
                "metric": "test_result:passed",
                "supports_claim": "pytest parsed result recorded one passing test",
                "required": True,
                "downloadable": False,
                "availability": "structured_evidence",
            },
        ],
        "missing_evidence": ["environment_snapshot"],
    }

    local_row = evidence_summary["evidence"][0]
    response = client.get(local_row["download_url"])

    assert response.status_code == 200
    assert response.body == content
    assert len(response.body) == stdout_artifact.size_bytes
    assert hashlib.sha256(response.body).hexdigest() == stdout_artifact.sha256

    structured_row = evidence_summary["evidence"][1]
    assert structured_row["downloadable"] is False
    assert "download_url" not in structured_row
    assert evidence_summary["missing_evidence"] == ["environment_snapshot"]

    external_response = client.get(f"/api/artifacts/{external_reference.id}/download")

    assert external_response.status_code == 422
    assert external_response.json()["error_code"] == "ARTIFACT_NOT_LOCAL"
