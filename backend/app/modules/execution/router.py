from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.ai_runtime.schemas import ArtifactRead
from backend.app.modules.execution import service
from backend.app.modules.execution.models import TestRun
from backend.app.modules.execution.schemas import TestResultRead, TestRunCreateRequest, TestRunRead
from backend.app.modules.projects.router import get_session


router = APIRouter(tags=["execution"])


def not_found(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def bad_request(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


@router.post("/test-runs", response_model=TestRunRead, status_code=status.HTTP_202_ACCEPTED)
def create_test_run(
    data: TestRunCreateRequest,
    session: Session = Depends(get_session),
) -> TestRunRead:
    try:
        return test_run_read(session, service.create_test_run(session, data))
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.TestRunInvalidInputError as exc:
        raise bad_request("TEST_RUN_INVALID_INPUT", "Test run input is invalid.") from exc


@router.get("/test-runs/{test_run_id}", response_model=TestRunRead)
def get_test_run(
    test_run_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> TestRunRead:
    try:
        return test_run_read(session, service.get_test_run(session, test_run_id))
    except service.TestRunNotFoundError as exc:
        raise not_found("TEST_RUN_NOT_FOUND", "Test run not found.") from exc


def test_run_read(session: Session, test_run: TestRun) -> TestRunRead:
    artifacts = list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.owner_entity_type == "TestRun",
                Artifact.owner_entity_id == test_run.id,
            )
            .order_by(Artifact.created_at.asc()),
        ),
    )
    return TestRunRead(
        id=test_run.id,
        project_id=test_run.project_id,
        automation_draft_id=test_run.automation_draft_id,
        test_command_id=test_run.test_command_id,
        tool_invocation_id=test_run.tool_invocation_id,
        name=test_run.name,
        command=test_run.command,
        working_directory=test_run.working_directory,
        runner_mode=test_run.runner_mode,
        run_workspace=test_run.run_workspace,
        repository_readonly=test_run.repository_readonly,
        network_enabled=test_run.network_enabled,
        runtime_artifact_ids=test_run.runtime_artifact_ids,
        dependency_snapshot_artifact_id=test_run.dependency_snapshot_artifact_id,
        environment_snapshot_artifact_id=test_run.environment_snapshot_artifact_id,
        status=test_run.status,
        exit_code=test_run.exit_code,
        duration_ms=test_run.duration_ms,
        parsed_result=test_run.parsed_result_json,
        test_results=[
            TestResultRead(
                id=result.id,
                project_id=result.project_id,
                test_run_id=result.test_run_id,
                test_name=result.test_name,
                test_file=result.test_file,
                status=result.status,
                duration_ms=result.duration_ms,
                failure_message=result.failure_message,
                failure_artifact_ids=result.failure_artifact_ids,
                metadata=result.metadata_json,
            )
            for result in test_run.test_results
        ],
        artifacts=[ArtifactRead.model_validate(artifact) for artifact in artifacts],
    )
