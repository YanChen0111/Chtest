from __future__ import annotations

import json
import re
import tempfile
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.execution.newman_runner import (
    NewmanRunner,
    NewmanRunnerCommandError,
    NewmanRunnerResult,
)
from backend.app.modules.execution.playwright_runner import (
    PlaywrightRunner,
    PlaywrightRunnerCommandError,
    PlaywrightRunnerResult,
)
from backend.app.modules.execution.pytest_runner import PytestRunner, PytestRunnerCommandError
from backend.app.modules.execution.schemas import TestRunCreateRequest
from backend.app.modules.projects.models import Project, TestCommand


class ProjectNotFoundError(Exception):
    pass


class TestRunNotFoundError(Exception):
    pass


class TestRunInvalidInputError(Exception):
    pass


def create_test_run(session: Session, data: TestRunCreateRequest) -> TestRun:
    project = session.get(Project, data.project_id)
    if project is None:
        raise ProjectNotFoundError

    if data.automation_draft_id is not None:
        return create_test_run_from_draft(session, data)
    if data.test_command_id is not None:
        return create_test_run_from_command(session, data)
    raise TestRunInvalidInputError


def get_test_run(session: Session, test_run_id: uuid.UUID) -> TestRun:
    test_run = session.get(TestRun, test_run_id)
    if test_run is None:
        raise TestRunNotFoundError
    return test_run


def create_test_run_from_draft(session: Session, data: TestRunCreateRequest) -> TestRun:
    draft = session.get(AutomationDraft, data.automation_draft_id)
    if draft is None or draft.project_id != data.project_id:
        raise TestRunInvalidInputError
    if draft.status != "approved":
        raise TestRunInvalidInputError
    if data.runner_mode == "playwright_local":
        return create_playwright_test_run_from_draft(session, data, draft)
    if draft.target_framework != "pytest":
        raise TestRunInvalidInputError

    run_workspace = Path(tempfile.mkdtemp(prefix="chtest-test-run-"))
    test_file = write_draft_file(run_workspace, draft)
    command = f"pytest {test_file.relative_to(run_workspace).as_posix()} -q"
    test_run = TestRun(
        project_id=data.project_id,
        automation_draft_id=draft.id,
        name=f"pytest approved draft: {draft.title}",
        command=command,
        working_directory=str(run_workspace),
        run_workspace=str(run_workspace),
        status="running",
    )
    session.add(test_run)
    session.flush()
    return execute_and_persist(session, test_run, run_workspace, draft.draft_code)


def create_test_run_from_command(session: Session, data: TestRunCreateRequest) -> TestRun:
    test_command = session.get(TestCommand, data.test_command_id)
    if test_command is None or test_command.project_id != data.project_id:
        raise TestRunInvalidInputError
    if data.runner_mode == "playwright_local":
        return create_playwright_test_run_from_command(session, data, test_command)
    if data.runner_mode == "newman_local":
        return create_newman_test_run_from_command(session, data, test_command)
    if test_command.command_type != "pytest" or test_command.status != "active":
        raise TestRunInvalidInputError

    workdir = Path(test_command.working_directory).expanduser().resolve()
    test_run = TestRun(
        project_id=data.project_id,
        test_command_id=test_command.id,
        name=test_command.name,
        command=test_command.command,
        working_directory=str(workdir),
        run_workspace=str(workdir),
        status="running",
    )
    session.add(test_run)
    session.flush()
    return execute_and_persist(session, test_run, workdir, None, timeout_seconds=test_command.timeout_seconds)


def create_playwright_test_run_from_draft(
    session: Session,
    data: TestRunCreateRequest,
    draft: AutomationDraft,
) -> TestRun:
    if draft.target_framework != "playwright":
        raise TestRunInvalidInputError
    run_workspace = Path(tempfile.mkdtemp(prefix="chtest-playwright-run-"))
    test_file = write_draft_file(run_workspace, draft)
    command = f"npx playwright test {test_file.relative_to(run_workspace).as_posix()}"
    test_run = TestRun(
        project_id=data.project_id,
        automation_draft_id=draft.id,
        name=f"playwright approved draft: {draft.title}",
        command=command,
        working_directory=str(run_workspace),
        runner_mode="playwright_local",
        run_workspace=str(run_workspace),
        status="running",
    )
    session.add(test_run)
    session.flush()
    return execute_playwright_and_persist(session, test_run, run_workspace, draft.draft_code)


def create_playwright_test_run_from_command(
    session: Session,
    data: TestRunCreateRequest,
    test_command: TestCommand,
) -> TestRun:
    if test_command.command_type != "playwright" or test_command.status != "active":
        raise TestRunInvalidInputError
    workdir = Path(test_command.working_directory).expanduser().resolve()
    test_run = TestRun(
        project_id=data.project_id,
        test_command_id=test_command.id,
        name=test_command.name,
        command=test_command.command,
        working_directory=str(workdir),
        runner_mode="playwright_local",
        run_workspace=str(workdir),
        status="running",
    )
    session.add(test_run)
    session.flush()
    return execute_playwright_and_persist(session, test_run, workdir, None, timeout_seconds=test_command.timeout_seconds)


def create_newman_test_run_from_command(
    session: Session,
    data: TestRunCreateRequest,
    test_command: TestCommand,
) -> TestRun:
    if test_command.command_type != "newman" or test_command.status != "active":
        raise TestRunInvalidInputError
    workdir = Path(test_command.working_directory).expanduser().resolve()
    test_run = TestRun(
        project_id=data.project_id,
        test_command_id=test_command.id,
        name=test_command.name,
        command=test_command.command,
        working_directory=str(workdir),
        runner_mode="newman_local",
        run_workspace=str(workdir),
        status="running",
    )
    session.add(test_run)
    session.flush()
    return execute_newman_and_persist(session, test_run, workdir, timeout_seconds=test_command.timeout_seconds)


def execute_and_persist(
    session: Session,
    test_run: TestRun,
    working_directory: Path,
    draft_code: str | None,
    timeout_seconds: int = 600,
) -> TestRun:
    try:
        result = PytestRunner().run(test_run.command, working_directory, timeout_seconds=timeout_seconds)
    except PytestRunnerCommandError as exc:
        test_run.status = "error"
        test_run.parsed_result_json = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "error": 1}
        session.add(test_run)
        session.commit()
        raise TestRunInvalidInputError from exc

    test_run.exit_code = result.exit_code
    test_run.duration_ms = result.duration_ms
    test_run.parsed_result_json = result.parsed_result
    test_run.status = status_from_exit_code(result.exit_code)
    session.add(test_run)
    session.flush()

    artifacts = create_execution_artifacts(session, test_run, result.stdout, result.stderr)
    test_run.runtime_artifact_ids = [artifact.id for artifact in artifacts if artifact.artifact_type == "runtime_manifest"]
    create_results(session, test_run, draft_code, result.exit_code)
    session.add(test_run)
    session.commit()
    session.refresh(test_run)
    return test_run


def execute_playwright_and_persist(
    session: Session,
    test_run: TestRun,
    working_directory: Path,
    draft_code: str | None,
    timeout_seconds: int = 600,
) -> TestRun:
    try:
        result = PlaywrightRunner().run(test_run.command, working_directory, timeout_seconds=timeout_seconds)
    except PlaywrightRunnerCommandError as exc:
        test_run.status = "error"
        test_run.parsed_result_json = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "error": 1}
        session.add(test_run)
        session.commit()
        raise TestRunInvalidInputError from exc

    test_run.exit_code = result.exit_code
    test_run.duration_ms = result.duration_ms
    test_run.parsed_result_json = result.parsed_result
    test_run.status = status_from_exit_code(result.exit_code)
    session.add(test_run)
    session.flush()

    artifacts = create_execution_artifacts(session, test_run, result.stdout, result.stderr, "PlaywrightRunner")
    artifacts.extend(create_playwright_artifacts(session, test_run, result))
    test_run.runtime_artifact_ids = [artifact.id for artifact in artifacts if artifact.artifact_type == "runtime_manifest"]
    create_results(session, test_run, playwright_test_names_from_code(draft_code), result.exit_code, "playwright_runner")
    session.add(test_run)
    session.commit()
    session.refresh(test_run)
    return test_run


def execute_newman_and_persist(
    session: Session,
    test_run: TestRun,
    working_directory: Path,
    timeout_seconds: int = 600,
) -> TestRun:
    try:
        result = NewmanRunner().run(test_run.command, working_directory, timeout_seconds=timeout_seconds)
    except NewmanRunnerCommandError as exc:
        test_run.status = "error"
        test_run.parsed_result_json = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "error": 1,
            "request_count": 0,
            "assertion_count": 0,
        }
        session.add(test_run)
        session.commit()
        raise TestRunInvalidInputError from exc

    test_run.exit_code = result.exit_code
    test_run.duration_ms = result.duration_ms
    test_run.parsed_result_json = result.parsed_result
    test_run.status = status_from_newman_result(result)
    session.add(test_run)
    session.flush()

    artifacts = create_execution_artifacts(session, test_run, result.stdout, result.stderr, "NewmanRunner")
    artifacts.extend(create_newman_artifacts(session, test_run, result))
    test_run.runtime_artifact_ids = [artifact.id for artifact in artifacts if artifact.artifact_type == "runtime_manifest"]
    create_newman_results(session, test_run, result)
    session.add(test_run)
    session.commit()
    session.refresh(test_run)
    return test_run


def write_draft_file(run_workspace: Path, draft: AutomationDraft) -> Path:
    relative_path = Path(draft.suggested_file_path or "tests/test_generated_draft.py")
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise TestRunInvalidInputError
    target = run_workspace / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(draft.draft_code, encoding="utf-8")
    return target


def create_execution_artifacts(
    session: Session,
    test_run: TestRun,
    stdout: str,
    stderr: str,
    component: str = "PytestRunner",
) -> list[Artifact]:
    artifact_specs = [
        ("runtime_manifest", "runtime_manifest.json", "{}\n", "application/json"),
        ("stdout", "stdout.log", stdout, "text/plain"),
        ("stderr", "stderr.log", stderr, "text/plain"),
    ]
    artifacts: list[Artifact] = []
    for artifact_type, name, content, mime_type in artifact_specs:
        artifact = Artifact(
            project_id=test_run.project_id,
            owner_entity_type="TestRun",
            owner_entity_id=test_run.id,
            artifact_type=artifact_type,
            file_path=f"test-runs/{test_run.id}/{name}",
            mime_type=mime_type,
            size_bytes=len(content.encode("utf-8")),
            sha256=f"sha256:{artifact_type}:{test_run.id}",
            metadata_json={"created_by_component": component, "runner_mode": test_run.runner_mode},
        )
        session.add(artifact)
        artifacts.append(artifact)
    session.flush()
    return artifacts


def create_playwright_artifacts(session: Session, test_run: TestRun, result: PlaywrightRunnerResult) -> list[Artifact]:
    artifacts: list[Artifact] = []
    for candidate in result.artifacts:
        artifact = Artifact(
            project_id=test_run.project_id,
            owner_entity_type="TestRun",
            owner_entity_id=test_run.id,
            artifact_type=candidate.artifact_type,
            file_path=f"test-runs/{test_run.id}/{candidate.file_path}",
            mime_type=candidate.mime_type,
            size_bytes=0,
            sha256=f"sha256:{candidate.artifact_type}:{test_run.id}",
            metadata_json={"created_by_component": "PlaywrightRunner", "runner_mode": test_run.runner_mode},
        )
        session.add(artifact)
        artifacts.append(artifact)
    session.flush()
    return artifacts


def create_newman_artifacts(session: Session, test_run: TestRun, result: NewmanRunnerResult) -> list[Artifact]:
    newman_content = result.newman_json_path.read_text(encoding="utf-8")
    parsed_content = json.dumps(result.parsed_result, ensure_ascii=False, sort_keys=True) + "\n"
    artifact_specs = [
        ("newman_json", "newman-report.json", newman_content, "application/json"),
        ("parsed_output", "parsed_result.json", parsed_content, "application/json"),
    ]
    artifacts: list[Artifact] = []
    for artifact_type, name, content, mime_type in artifact_specs:
        artifact = Artifact(
            project_id=test_run.project_id,
            owner_entity_type="TestRun",
            owner_entity_id=test_run.id,
            artifact_type=artifact_type,
            file_path=f"test-runs/{test_run.id}/{name}",
            mime_type=mime_type,
            size_bytes=len(content.encode("utf-8")),
            sha256=f"sha256:{artifact_type}:{test_run.id}",
            metadata_json={
                "created_by_component": "NewmanRunner",
                "runner_mode": test_run.runner_mode,
                "collection_name": result.parsed_result.get("collection_name"),
                "request_count": result.parsed_result.get("request_count"),
                "assertion_count": result.parsed_result.get("assertion_count"),
                "redaction_applied": False,
            },
        )
        session.add(artifact)
        artifacts.append(artifact)
    session.flush()
    return artifacts


def create_newman_results(session: Session, test_run: TestRun, result: NewmanRunnerResult) -> None:
    for candidate in result.test_results:
        session.add(
            TestResult(
                project_id=test_run.project_id,
                test_run_id=test_run.id,
                test_name=candidate.test_name,
                test_file=candidate.test_file,
                status=candidate.status,
                duration_ms=candidate.duration_ms,
                failure_message=candidate.failure_message,
                metadata_json=candidate.metadata,
            ),
        )


def create_results(
    session: Session,
    test_run: TestRun,
    names_or_code: list[str] | str | None,
    exit_code: int,
    source: str = "pytest_runner",
) -> None:
    names = names_or_code if isinstance(names_or_code, list) else test_names_from_code(names_or_code)
    if not names:
        names = ["pytest::session" if source == "pytest_runner" else f"{source}::session"]
    status = "passed" if exit_code == 0 else "failed"
    for name in names:
        session.add(
            TestResult(
                project_id=test_run.project_id,
                test_run_id=test_run.id,
                test_name=name,
                test_file=test_file_from_nodeid(name),
                status=status,
                duration_ms=None,
                failure_message=None if status == "passed" else "test command failed",
                metadata_json={"source": source},
            ),
        )


def test_names_from_code(code: str | None) -> list[str]:
    if not code:
        return []
    return [f"generated::{match}" for match in re.findall(r"def\s+(test_[a-zA-Z0-9_]+)\s*\(", code)]


def playwright_test_names_from_code(code: str | None) -> list[str]:
    if not code:
        return []
    return [f"generated::{match}" for match in re.findall(r"test\s*\(\s*['\"]([^'\"]+)['\"]", code)]


def test_file_from_nodeid(nodeid: str) -> str | None:
    if "::" not in nodeid:
        return None
    return nodeid.split("::", 1)[0]


def status_from_exit_code(exit_code: int) -> str:
    if exit_code == 0:
        return "passed"
    if exit_code == 1:
        return "failed"
    return "error"


def status_from_newman_result(result: NewmanRunnerResult) -> str:
    if result.parsed_result.get("error", 0) > 0:
        return "error"
    if result.parsed_result.get("failed", 0) > 0:
        return "failed"
    if result.exit_code == 0:
        return "passed"
    return "error"
