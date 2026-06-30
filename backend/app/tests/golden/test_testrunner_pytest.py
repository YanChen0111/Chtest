from __future__ import annotations

import uuid

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.tests.golden.test_test_case_library_golden import (
    ASGIClient,
    api_client,
    create_reviewed_golden_cases,
)


def test_golden_approved_automation_draft_executes_pytest_with_evidence(
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
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    run_response = client.post(
        "/api/test-runs",
        json_body={
            "project_id": project["id"],
            "automation_draft_id": draft_id,
            "reason": "golden approved draft execution",
            "runner_mode": "local_subprocess",
        },
    )
    assert run_response.status_code == 202
    run = run_response.json()
    assert run["automation_draft_id"] == draft_id
    assert run["status"] == "passed"
    assert run["exit_code"] == 0
    assert run["runner_mode"] == "local_subprocess"
    assert run["repository_readonly"] is True
    assert run["network_enabled"] is False
    assert run["parsed_result"]["passed"] == 1
    assert run["test_results"][0]["test_name"] == "generated::test_golden_pytest_execution"
    assert {artifact["artifact_type"] for artifact in run["artifacts"]} >= {"runtime_manifest", "stdout", "stderr"}

    get_response = client.get(f"/api/test-runs/{run['id']}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["id"] == run["id"]
    assert fetched["test_results"][0]["status"] == "passed"

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
        tables = set(inspect(session.bind).get_table_names())

    assert persisted_draft is not None
    assert persisted_draft.status == "approved"
    assert persisted_run is not None
    assert persisted_run.status == "passed"
    assert persisted_run.parsed_result_json["passed"] == 1
    assert len(persisted_results) == 1
    assert persisted_results[0].status == "passed"
    assert {artifact.artifact_type for artifact in persisted_artifacts} >= {"runtime_manifest", "stdout", "stderr"}
    assert "reports" not in tables
    assert "quality_gate_decisions" not in tables
