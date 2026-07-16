from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.cicd.models import QualityGateDecision
from backend.app.modules.execution.jmeter_runner import JMeterRunner
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.api.test_jmeter_execution import write_fake_jmeter
from backend.app.tests.golden.test_test_case_library_golden import (
    ASGIClient,
    api_client,
    create_reviewed_golden_cases,
)


def test_golden_configured_jmeter_command_executes_with_local_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_jmeter = write_fake_jmeter(tmp_path)
    plan = tmp_path / "plans" / "coupon.jmx"
    plan.parent.mkdir()
    plan.write_text("<jmeterTestPlan />", encoding="utf-8")
    import backend.app.modules.execution.service as execution_service

    monkeypatch.setattr(execution_service, "JMeterRunner", lambda: JMeterRunner(jmeter_executable=str(fake_jmeter)))
    client, SessionLocal = api_client
    project, _library = create_reviewed_golden_cases(client, SessionLocal)

    command_response = client.post(
        "/api/test-commands",
        json_body={
            "project_id": project["id"],
            "repository_id": None,
            "environment_id": None,
            "name": "jmeter coupon smoke",
            "command": "jmeter -n -t plans/coupon.jmx -l results.jtl",
            "working_directory": str(tmp_path),
            "command_type": "jmeter",
            "timeout_seconds": 600,
            "parse_junit": False,
            "parse_coverage": False,
        },
    )
    if command_response.status_code == 201:
        command_id = command_response.json()["id"]
    else:
        with SessionLocal() as session:
            from backend.app.modules.projects.models import TestCommand

            command = TestCommand(
                project_id=uuid.UUID(project["id"]),
                name="jmeter coupon smoke",
                command="jmeter -n -t plans/coupon.jmx -l results.jtl",
                working_directory=str(tmp_path),
                command_type="jmeter",
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
            "reason": "golden configured JMeter local execution",
            "runner_mode": "jmeter_local",
        },
    )

    assert run_response.status_code == 202
    run = run_response.json()
    assert run["automation_draft_id"] is None
    assert run["test_command_id"] == command_id
    assert run["runner_mode"] == "jmeter_local"
    assert run["status"] == "failed"
    assert run["exit_code"] == 0
    assert run["repository_readonly"] is True
    assert run["network_enabled"] is False
    assert run["command"] == "jmeter -n -t plans/coupon.jmx -l results.jtl"
    assert run["parsed_result"] == {
        "total": 3,
        "passed": 2,
        "failed": 1,
        "skipped": 0,
        "error": 0,
        "sampler_count": 3,
        "assertion_count": 3,
        "duration_ms": 450,
        "average_latency_ms": 103,
    }
    assert {artifact["artifact_type"] for artifact in run["artifacts"]} >= {
        "runtime_manifest",
        "stdout",
        "stderr",
        "jmeter_jtl",
        "parsed_output",
    }
    assert len(run["test_results"]) == 3
    assert any(result["test_name"] == "jmeter/POST /coupons" for result in run["test_results"])
    assert any(result["failure_message"] == "500 Internal Server Error" for result in run["test_results"])

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
    assert persisted_run.parsed_result_json["sampler_count"] == 3
    assert persisted_run.parsed_result_json["assertion_count"] == 3
    assert len(persisted_results) == 3
    assert {result.status for result in persisted_results} == {"passed", "failed"}
    assert {artifact.artifact_type for artifact in persisted_artifacts} >= {
        "runtime_manifest",
        "stdout",
        "stderr",
        "jmeter_jtl",
        "parsed_output",
    }
    assert report is None
    assert failure_analysis is None
    assert quality_gate_decision is None
