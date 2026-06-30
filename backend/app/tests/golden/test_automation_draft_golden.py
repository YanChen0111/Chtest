from __future__ import annotations

import uuid

from sqlalchemy import inspect
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.automation.models import AutomationDraft
from backend.app.tests.golden.test_test_case_library_golden import (
    ASGIClient,
    api_client,
    create_reviewed_golden_cases,
)


def test_golden_reviewed_case_produces_approved_automation_draft_without_execution(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project, library = create_reviewed_golden_cases(client, SessionLocal)
    expired_case = next(item for item in library["items"] if item["title"] == "过期优惠券不可用于结算")

    create_response = client.post(
        "/api/automation/drafts",
        json_body={
            "project_id": project["id"],
            "test_case_id": expired_case["id"],
            "requirement_id": None,
            "target_framework": "pytest",
            "prompt_version": "automation_draft_generation:v1",
            "skill_version": "automation-draft-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-automation-draft",
        },
    )
    assert create_response.status_code == 202
    draft_id = create_response.json()["automation_draft_id"]

    get_response = client.get(f"/api/automation/drafts/{draft_id}")
    assert get_response.status_code == 200
    draft = get_response.json()
    assert draft["status"] == "draft_generated"
    assert draft["target_framework"] == "pytest"
    assert "过期优惠券不可用于结算" in draft["draft_code"]
    assert draft["suggested_file_path"].startswith("tests/test_")
    assert draft["execution_notes"]
    assert draft["risk_notes"]
    assert draft["runtime_artifact_id"] is None
    assert draft["promoted_artifact_id"] is None

    edit_response = client.patch(
        f"/api/automation/drafts/{draft_id}",
        json_body={
            "draft_code": draft["draft_code"].replace("assert True", "assert True  # reviewed"),
            "suggested_file_path": draft["suggested_file_path"],
            "execution_notes": "Reviewed golden draft; execution is intentionally out of scope.",
            "risk_notes": "Fixture names must be confirmed before later execution.",
            "review_comment": "Golden reviewer adjusted notes.",
        },
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["status"] == "edited"

    approve_response = client.post(
        f"/api/automation/drafts/{draft_id}/approve",
        json_body={"action": "approve", "review_comment": "Approved for later controlled execution."},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    with SessionLocal() as session:
        persisted = session.get(AutomationDraft, uuid.UUID(draft_id))
        assert persisted is not None
        assert persisted.status == "approved"
        assert persisted.runtime_artifact_id is None
        assert persisted.promoted_artifact_id is None
        tables = set(inspect(session.bind).get_table_names())
        assert "test_runs" not in tables
        assert "test_results" not in tables
        assert "reports" not in tables
