from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import QualityGateDecision
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.reporting.models import Report
from backend.app.tests.golden.test_test_case_library_golden import (
    ASGIClient,
    api_client,
    create_reviewed_golden_cases,
)


def test_golden_placeholder_automation_draft_cannot_be_approved(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project, library = create_reviewed_golden_cases(client, SessionLocal)
    expired_case = next(item for item in library["items"] if item["review_status"] == "approved_after_edit")

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

    draft_response = client.get(f"/api/automation/drafts/{draft_id}")
    assert draft_response.status_code == 200
    draft = draft_response.json()
    assert draft["status"] == "draft_generated"

    edit_response = client.patch(
        f"/api/automation/drafts/{draft_id}",
        json_body={
            "draft_code": "def test_golden_pytest_execution():\n    assert True\n",
            "suggested_file_path": "tests/test_golden_pytest_execution.py",
            "execution_notes": "Golden smoke executes this reviewed pytest draft.",
            "risk_notes": "No external services required.",
            "review_comment": "Golden reviewer replaced mock fixture with deterministic assertion.",
        },
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["status"] == "edited"

    approve_response = client.post(
        f"/api/automation/drafts/{draft_id}/approve",
        json_body={"action": "approve", "review_comment": "Approved for controlled pytest execution."},
    )
    assert approve_response.status_code == 400
    assert approve_response.json()["error_code"] == "AUTOMATION_DRAFT_QUALITY_GATE_FAILED"

    with SessionLocal() as session:
        persisted_draft = session.get(AutomationDraft, uuid.UUID(draft_id))
        persisted_run = session.scalar(select(TestRun).where(TestRun.automation_draft_id == uuid.UUID(draft_id)))
        report = session.scalar(select(Report))
        quality_gate_decision = session.scalar(select(QualityGateDecision))

    assert persisted_draft is not None
    assert persisted_draft.status == "edited"
    assert persisted_run is None
    assert report is None
    assert quality_gate_decision is None
