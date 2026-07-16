from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.cicd.models import QualityGateDecision
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.execution.newman_runner import NewmanRunner
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.api.test_newman_execution import write_fake_npx
from backend.app.tests.golden.test_test_case_library_golden import (
    ASGIClient,
    api_client,
    create_reviewed_golden_cases,
)


def test_golden_configured_newman_command_executes_with_api_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_npx = write_fake_npx(tmp_path)
    collection = tmp_path / "collections" / "coupon.postman_collection.json"
    collection.parent.mkdir()
    collection.write_text("{}", encoding="utf-8")
    import backend.app.modules.execution.service as execution_service

    monkeypatch.setattr(execution_service, "NewmanRunner", lambda: NewmanRunner(npx_executable=str(fake_npx)))
    client, SessionLocal = api_client
    project, _library = create_reviewed_golden_cases(client, SessionLocal)

    command_response = client.post(
        "/api/test-commands",
        json_body={
            "project_id": project["id"],
            "repository_id": None,
            "environment_id": None,
            "name": "newman coupon api",
            "command": (
                "npx newman run collections/coupon.postman_collection.json "
                "--reporters json --reporter-json-export newman-report.json"
            ),
            "working_directory": str(tmp_path),
            "command_type": "newman",
            "timeout_seconds": 600,
            "parse_junit": False,
            "parse_coverage": False,
        },
    )
    # Golden setup stores TestCommand directly when no Repository fixture is
    # needed for the deterministic Newman fake.
    if command_response.status_code == 201:
        command_id = command_response.json()["id"]
    else:
        with SessionLocal() as session:
            from backend.app.modules.projects.models import TestCommand

            command = TestCommand(
                project_id=uuid.UUID(project["id"]),
                name="newman coupon api",
                command=(
                    "npx newman run collections/coupon.postman_collection.json "
                    "--reporters json --reporter-json-export newman-report.json"
                ),
                working_directory=str(tmp_path),
                command_type="newman",
                timeout_seconds=600,
                parse_junit=False,
                parse_coverage=False,
                status="active",
            )
            session.add(command)
            session.commit()
            command_id = str(command.id)

    run_response = client.post(
        "/api/test-runs",
        json_body={
            "project_id": project["id"],
            "test_command_id": command_id,
            "reason": "golden configured Newman API execution",
            "runner_mode": "newman_local",
        },
    )
    assert run_response.status_code == 202
    run = run_response.json()
    assert run["automation_draft_id"] is None
    assert run["test_command_id"] == command_id
    assert run["status"] == "failed"
    assert run["exit_code"] == 0
    assert run["runner_mode"] == "newman_local"
    assert run["repository_readonly"] is True
    assert run["network_enabled"] is False
    assert run["parsed_result"]["collection_name"] == "coupon-api"
    assert run["parsed_result"]["request_count"] == 2
    assert run["parsed_result"]["assertion_count"] == 4
    assert run["parsed_result"]["failed"] == 1
    assert {artifact["artifact_type"] for artifact in run["artifacts"]} >= {
        "runtime_manifest",
        "stdout",
        "stderr",
        "newman_json",
        "parsed_output",
    }
    assert any(result["status"] == "failed" for result in run["test_results"])
    assert any("expected clear message" == result["failure_message"] for result in run["test_results"])

    with SessionLocal() as session:
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

    assert persisted_run is not None
    assert persisted_run.status == "failed"
    assert persisted_run.parsed_result_json["failed"] == 1
    assert persisted_run.parsed_result_json["request_count"] == 2
    assert len(persisted_results) == 4
    assert {result.status for result in persisted_results} == {"passed", "failed"}
    assert {artifact.artifact_type for artifact in persisted_artifacts} >= {
        "runtime_manifest",
        "stdout",
        "stderr",
        "newman_json",
        "parsed_output",
    }
    assert report is None
    assert failure_analysis is None
    assert quality_gate_decision is None
