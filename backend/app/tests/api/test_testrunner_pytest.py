from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.execution.pytest_runner import PytestRunner, PytestRunnerCommandError
from backend.app.modules.execution.schemas import TestResultRead as ResultRead
from backend.app.modules.execution.schemas import TestRunCreateRequest as RunCreateRequest
from backend.app.modules.execution.schemas import TestRunRead as RunRead
from backend.app.modules.projects.models import Project, TestCommand, Workspace


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


def seed_project(session: Session) -> Project:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    return project


def test_test_run_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project = seed_project(session)
        test_command = TestCommand(
            project_id=project.id,
            name="pytest unit",
            command="python -m pytest tests/unit -q --junitxml=artifacts/junit.xml",
            working_directory="/Users/yanchen/VscodeProject/sample-app",
            command_type="pytest",
        )
        runtime_artifact = Artifact(
            project_id=project.id,
            owner_entity_type="TestRun",
            owner_entity_id=uuid.uuid4(),
            artifact_type="runtime_manifest",
            file_path="projects/test-runs/runtime_manifest.json",
            mime_type="application/json",
            size_bytes=2,
            sha256="sha256:runtime",
            metadata_json={},
        )
        session.add_all([test_command, runtime_artifact])
        session.flush()

        test_run = TestRun(
            project_id=project.id,
            test_command_id=test_command.id,
            name="pytest unit",
            command=test_command.command,
            working_directory=test_command.working_directory,
            run_workspace="artifacts/projects/checkout/test-runs/run-1/workspace",
            runtime_artifact_ids=[runtime_artifact.id],
            parsed_result_json={"total": 1, "passed": 1, "failed": 0, "skipped": 0, "error": 0},
        )
        session.add(test_run)
        session.commit()
        persisted = session.scalar(select(TestRun).where(TestRun.id == test_run.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.test_command_id == test_command.id
    assert persisted.automation_draft_id is None
    assert persisted.runner_mode == "local_subprocess"
    assert persisted.repository_readonly is True
    assert persisted.network_enabled is False
    assert persisted.status == "created"
    assert persisted.exit_code is None
    assert persisted.duration_ms is None
    assert persisted.runtime_artifact_ids == [runtime_artifact.id]
    assert persisted.parsed_result_json["passed"] == 1


def test_test_result_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project = seed_project(session)
        test_run = TestRun(
            project_id=project.id,
            name="pytest approved draft",
            command="python -m pytest tests/test_coupon.py -q",
            working_directory="/Users/yanchen/VscodeProject/sample-app",
        )
        failure_artifact = Artifact(
            project_id=project.id,
            owner_entity_type="TestResult",
            owner_entity_id=uuid.uuid4(),
            artifact_type="stderr",
            file_path="projects/test-runs/run-1/stderr.log",
            mime_type="text/plain",
            size_bytes=12,
            sha256="sha256:stderr",
            metadata_json={},
        )
        session.add_all([test_run, failure_artifact])
        session.flush()
        result = TestResult(
            project_id=project.id,
            test_run_id=test_run.id,
            test_name="tests/test_coupon.py::test_expired_coupon",
            test_file="tests/test_coupon.py",
            status="failed",
            duration_ms=123,
            failure_message="AssertionError: coupon accepted",
            failure_artifact_ids=[failure_artifact.id],
            metadata_json={"classname": "tests.test_coupon"},
        )
        session.add(result)
        session.commit()
        persisted = session.scalar(select(TestResult).where(TestResult.id == result.id))

    assert persisted is not None
    assert persisted.test_run_id == test_run.id
    assert persisted.status == "failed"
    assert persisted.duration_ms == 123
    assert persisted.failure_artifact_ids == [failure_artifact.id]
    assert persisted.metadata_json["classname"] == "tests.test_coupon"


def test_test_run_create_request_requires_one_execution_source() -> None:
    project_id = uuid.uuid4()
    automation_draft_id = uuid.uuid4()
    test_command_id = uuid.uuid4()

    by_draft = RunCreateRequest(project_id=project_id, automation_draft_id=automation_draft_id)
    by_command = RunCreateRequest(project_id=project_id, test_command_id=test_command_id)

    assert by_draft.automation_draft_id == automation_draft_id
    assert by_draft.test_command_id is None
    assert by_draft.runner_mode == "local_subprocess"
    assert by_command.test_command_id == test_command_id
    assert by_command.automation_draft_id is None


def test_test_run_read_schema_embeds_test_results() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()
    draft_id = uuid.uuid4()
    result_id = uuid.uuid4()
    runtime_artifact_id = uuid.uuid4()

    read = RunRead(
        id=run_id,
        project_id=project_id,
        automation_draft_id=draft_id,
        test_command_id=None,
        tool_invocation_id=None,
        name="pytest approved draft",
        command="python -m pytest tests/test_coupon.py -q",
        working_directory="/Users/yanchen/VscodeProject/sample-app",
        runner_mode="local_subprocess",
        run_workspace="artifacts/projects/checkout/test-runs/run-1/workspace",
        repository_readonly=True,
        network_enabled=False,
        runtime_artifact_ids=[runtime_artifact_id],
        dependency_snapshot_artifact_id=None,
        environment_snapshot_artifact_id=None,
        status="passed",
        exit_code=0,
        duration_ms=3560,
        parsed_result={"total": 1, "passed": 1, "failed": 0, "skipped": 0, "error": 0},
        test_results=[
            ResultRead(
                id=result_id,
                project_id=project_id,
                test_run_id=run_id,
                test_name="tests/test_coupon.py::test_expired_coupon",
                test_file="tests/test_coupon.py",
                status="passed",
                duration_ms=123,
                failure_message=None,
                failure_artifact_ids=[],
                metadata={},
            ),
        ],
        artifacts=[],
    )

    body = read.model_dump(mode="json")
    assert body["id"] == str(run_id)
    assert body["automation_draft_id"] == str(draft_id)
    assert body["runtime_artifact_ids"] == [str(runtime_artifact_id)]
    assert body["parsed_result"]["passed"] == 1
    assert body["test_results"][0]["id"] == str(result_id)
    assert body["test_results"][0]["test_name"].endswith("test_expired_coupon")


def test_pytest_runner_executes_allowlisted_command(tmp_path: Path) -> None:
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    runner = PytestRunner(python_executable=sys.executable)

    result = runner.run("pytest test_sample.py -q", working_directory=tmp_path)

    assert result.exit_code == 0
    assert result.duration_ms >= 0
    assert "1 passed" in result.stdout
    assert result.stderr == ""
    assert result.parsed_result["total"] == 1
    assert result.parsed_result["passed"] == 1
    assert result.parsed_result["failed"] == 0


def test_pytest_runner_rejects_forbidden_shell_operator(tmp_path: Path) -> None:
    runner = PytestRunner(python_executable=sys.executable)

    with pytest.raises(PytestRunnerCommandError):
        runner.run("pytest tests -q && rm -rf /tmp/example", working_directory=tmp_path)


def test_pytest_runner_rejects_non_pytest_command(tmp_path: Path) -> None:
    runner = PytestRunner(python_executable=sys.executable)

    with pytest.raises(PytestRunnerCommandError):
        runner.run("python -m pytest tests -q", working_directory=tmp_path)
