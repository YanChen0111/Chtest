from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.ai_runtime.schemas import ArtifactRead
from backend.app.modules.execution import service
from backend.app.modules.execution.models import TestRun
from backend.app.modules.execution.schemas import (
    ExecutionApprovalWorkflowActionRequest,
    ExecutionApprovalWorkflowContinueRequest,
    ExecutionApprovalWorkflowEditRequest,
    ExecutionApprovalWorkflowRead,
    ExecutionResultReviewWorkflowActionRequest,
    ExecutionResultReviewWorkflowContinueRequest,
    ExecutionResultReviewWorkflowEditRequest,
    ExecutionResultReviewWorkflowRead,
    TestResultRead,
    TestRunCreateRequest,
    TestRunRead,
)
from backend.app.modules.projects.router import get_session
from backend.app.modules.workflow_control.policy import ApprovalDecision, TransitionPolicyError


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


def workflow_error(exc: Exception) -> HTTPException:
    error_code = getattr(exc, "code", exc.__class__.__name__.replace("Error", "").upper())
    status_code = (
        status.HTTP_404_NOT_FOUND
        if error_code in {"WORKFLOW_RUN_NOT_FOUND", "WORKFLOW_PROJECT_NOT_FOUND"}
        else status.HTTP_409_CONFLICT
    )
    return HTTPException(
        status_code=status_code,
        detail={"error_code": error_code, "message": "Workflow action was rejected.", "details": {}},
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


@router.get(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-approval",
    response_model=ExecutionApprovalWorkflowRead,
)
def read_execution_approval_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ExecutionApprovalWorkflowRead:
    try:
        return service.get_execution_approval_workflow_detail(session, project_id, requirement_review_id)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionApprovalWorkflowStageError,
        service.ExecutionApprovalGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-approval/submit",
    response_model=ExecutionApprovalWorkflowRead,
)
def submit_execution_approval_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionApprovalWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionApprovalWorkflowRead:
    try:
        return service.submit_execution_approval_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionApprovalWorkflowStageError,
        service.ExecutionApprovalGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-approval/complete-review",
    response_model=ExecutionApprovalWorkflowRead,
)
def complete_execution_approval_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionApprovalWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionApprovalWorkflowRead:
    try:
        return service.complete_execution_approval_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionApprovalWorkflowStageError,
        service.ExecutionApprovalGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-approval/edit",
    response_model=ExecutionApprovalWorkflowRead,
)
def edit_execution_approval_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionApprovalWorkflowEditRequest,
    session: Session = Depends(get_session),
) -> ExecutionApprovalWorkflowRead:
    try:
        return service.edit_execution_approval_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionApprovalWorkflowStageError,
        service.ExecutionApprovalGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-approval/approve",
    response_model=ExecutionApprovalWorkflowRead,
)
def approve_execution_approval_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionApprovalWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionApprovalWorkflowRead:
    try:
        return service.decide_execution_approval_workflow(
            session,
            project_id,
            requirement_review_id,
            data,
            decision=ApprovalDecision.APPROVED,
        )
    except (
        service.WorkflowPersistenceError,
        service.ExecutionApprovalWorkflowStageError,
        service.ExecutionApprovalGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-approval/reject",
    response_model=ExecutionApprovalWorkflowRead,
)
def reject_execution_approval_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionApprovalWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionApprovalWorkflowRead:
    try:
        return service.decide_execution_approval_workflow(
            session,
            project_id,
            requirement_review_id,
            data,
            decision=ApprovalDecision.REJECTED,
        )
    except (
        service.WorkflowPersistenceError,
        service.ExecutionApprovalWorkflowStageError,
        service.ExecutionApprovalGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-approval/continue",
    response_model=ExecutionApprovalWorkflowRead,
)
def continue_execution_approval_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionApprovalWorkflowContinueRequest,
    session: Session = Depends(get_session),
) -> ExecutionApprovalWorkflowRead:
    try:
        return service.continue_execution_approval_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionApprovalWorkflowStageError,
        service.ExecutionApprovalGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-approval/approve-and-continue",
    response_model=ExecutionApprovalWorkflowRead,
)
def approve_and_continue_execution_approval_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionApprovalWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionApprovalWorkflowRead:
    try:
        return service.approve_and_continue_execution_approval_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionApprovalWorkflowStageError,
        service.ExecutionApprovalGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.get(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-result-review",
    response_model=ExecutionResultReviewWorkflowRead,
)
def read_execution_result_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ExecutionResultReviewWorkflowRead:
    try:
        return service.get_execution_result_review_workflow_detail(session, project_id, requirement_review_id)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionResultReviewWorkflowStageError,
        service.ExecutionResultReviewGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-result-review/submit",
    response_model=ExecutionResultReviewWorkflowRead,
)
def submit_execution_result_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionResultReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionResultReviewWorkflowRead:
    try:
        return service.submit_execution_result_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionResultReviewWorkflowStageError,
        service.ExecutionResultReviewGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-result-review/complete-review",
    response_model=ExecutionResultReviewWorkflowRead,
)
def complete_execution_result_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionResultReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionResultReviewWorkflowRead:
    try:
        return service.complete_execution_result_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionResultReviewWorkflowStageError,
        service.ExecutionResultReviewGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-result-review/edit",
    response_model=ExecutionResultReviewWorkflowRead,
)
def edit_execution_result_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionResultReviewWorkflowEditRequest,
    session: Session = Depends(get_session),
) -> ExecutionResultReviewWorkflowRead:
    try:
        return service.edit_execution_result_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionResultReviewWorkflowStageError,
        service.ExecutionResultReviewGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-result-review/approve",
    response_model=ExecutionResultReviewWorkflowRead,
)
def approve_execution_result_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionResultReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionResultReviewWorkflowRead:
    try:
        return service.decide_execution_result_review_workflow(
            session,
            project_id,
            requirement_review_id,
            data,
            decision=ApprovalDecision.APPROVED,
        )
    except (
        service.WorkflowPersistenceError,
        service.ExecutionResultReviewWorkflowStageError,
        service.ExecutionResultReviewGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-result-review/reject",
    response_model=ExecutionResultReviewWorkflowRead,
)
def reject_execution_result_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionResultReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionResultReviewWorkflowRead:
    try:
        return service.decide_execution_result_review_workflow(
            session,
            project_id,
            requirement_review_id,
            data,
            decision=ApprovalDecision.REJECTED,
        )
    except (
        service.WorkflowPersistenceError,
        service.ExecutionResultReviewWorkflowStageError,
        service.ExecutionResultReviewGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-result-review/continue",
    response_model=ExecutionResultReviewWorkflowRead,
)
def continue_execution_result_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionResultReviewWorkflowContinueRequest,
    session: Session = Depends(get_session),
) -> ExecutionResultReviewWorkflowRead:
    try:
        return service.continue_execution_result_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionResultReviewWorkflowStageError,
        service.ExecutionResultReviewGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/execution-result-review/approve-and-continue",
    response_model=ExecutionResultReviewWorkflowRead,
)
def approve_and_continue_execution_result_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ExecutionResultReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ExecutionResultReviewWorkflowRead:
    try:
        return service.approve_and_continue_execution_result_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.WorkflowPersistenceError,
        service.ExecutionResultReviewWorkflowStageError,
        service.ExecutionResultReviewGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


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
