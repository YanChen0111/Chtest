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


def test_golden_approved_playwright_draft_executes_with_browser_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_npx = write_fake_npx(tmp_path)
    import backend.app.modules.execution.service as execution_service

    monkeypatch.setattr(execution_service, "PlaywrightRunner", lambda: PlaywrightRunner(npx_executable=str(fake_npx)))
    client, SessionLocal = api_client
    project, library = create_reviewed_golden_cases(client, SessionLocal)
    ui_case = next(item for item in library["items"] if item["test_type"] == "ui")

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
    assert create_response.status_code == 202
    draft_id = create_response.json()["automation_draft_id"]

    edit_response = client.patch(
        f"/api/automation/drafts/{draft_id}",
        json_body={
            "draft_code": "import { test } from '@playwright/test';\ntest('checkout smoke', async () => {});\n",
            "suggested_file_path": "tests/checkout.spec.ts",
            "execution_notes": "Golden smoke uses deterministic fake Playwright output.",
            "risk_notes": "No real browser binary is required for this smoke.",
            "review_comment": "Golden reviewer replaced draft with deterministic smoke.",
        },
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["status"] == "edited"

    approve_response = client.post(
        f"/api/automation/drafts/{draft_id}/approve",
        json_body={"action": "approve", "review_comment": "Approved for controlled Playwright execution."},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    run_response = client.post(
        "/api/test-runs",
        json_body={
            "project_id": project["id"],
            "automation_draft_id": draft_id,
            "reason": "golden approved Playwright draft execution",
            "runner_mode": "playwright_local",
        },
    )
    assert run_response.status_code == 202
    run = run_response.json()
    assert run["automation_draft_id"] == draft_id
    assert run["status"] == "passed"
    assert run["exit_code"] == 0
    assert run["runner_mode"] == "playwright_local"
    assert run["parsed_result"]["passed"] == 1
    assert run["test_results"][0]["test_name"] == "generated::checkout smoke"
    assert {artifact["artifact_type"] for artifact in run["artifacts"]} >= {
        "runtime_manifest",
        "stdout",
        "stderr",
        "playwright_trace",
        "screenshot",
    }

    with SessionLocal() as session:
        persisted_draft = session.get(AutomationDraft, uuid.UUID(draft_id))
        persisted_run = session.get(TestRun, uuid.UUID(run["id"]))
        persisted_results = list(session.scalars(select(TestResult).where(TestResult.test_run_id == uuid.UUID(run["id"]))))
        persisted_artifacts = list(
            session.scalars(
                select(Artifact).where(
                    Artifact.owner_entity_type == "TestRun",
                    Artifact.owner_entity_id == uuid.UUID(run["id"]),
                ),
            ),
        )
        report = session.scalar(select(Report))
        failure_analysis = session.scalar(select(FailureAnalysis))
        quality_gate_decision = session.scalar(select(QualityGateDecision))

    assert persisted_draft is not None
    assert persisted_draft.status == "approved"
    assert persisted_run is not None
    assert persisted_run.status == "passed"
    assert len(persisted_results) == 1
    assert {artifact.artifact_type for artifact in persisted_artifacts} >= {
        "runtime_manifest",
        "stdout",
        "stderr",
        "playwright_trace",
        "screenshot",
    }
    assert report is None
    assert failure_analysis is None
    assert quality_gate_decision is None
