from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import QualityGateDecision
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.execution.playwright_runner import PlaywrightRunner
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.api.test_playwright_minimal_loop import write_fake_npx
from backend.app.tests.golden.test_test_case_library_golden import (
    ASGIClient,
    api_client,
    create_reviewed_golden_cases,
)


def test_golden_incompatible_mock_output_cannot_create_playwright_draft(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_npx = write_fake_npx(tmp_path)
    import backend.app.modules.execution.service as execution_service

    monkeypatch.setattr(execution_service, "PlaywrightRunner", lambda: PlaywrightRunner(npx_executable=str(fake_npx)))
    client, SessionLocal = api_client
    project, library = create_reviewed_golden_cases(client, SessionLocal)
    ui_case = library["items"][0]

    create_response = client.post(
        "/api/automation/drafts",
        json_body={
            "project_id": project["id"],
            "test_case_id": ui_case["id"],
            "requirement_id": None,
            "target_framework": "playwright",
            "prompt_version": "automation_draft_generation:v1",
            "skill_version": "automation-draft-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-automation-draft",
        },
    )
    assert create_response.status_code == 422
    assert create_response.json()["error_code"] == "AUTOMATION_DRAFT_SCHEMA_INVALID"

    with SessionLocal() as session:
        assert session.scalar(select(AutomationDraft)) is None
