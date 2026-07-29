from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.projects.router import get_session
from backend.app.modules.requirements import service
from backend.app.modules.requirements.schemas import (
    RequirementCreate,
    RequirementDocumentCreate,
    RequirementDocumentListRead,
    RequirementDocumentRead,
    RequirementListRead,
    RequirementRead,
    RequirementReviewDetailRead,
    RequirementReviewStartRead,
    RequirementReviewStartRequest,
    RequirementWorkflowActionRequest,
    RequirementWorkflowContinueRequest,
    RequirementWorkflowEditRequest,
    RiskReviewEditRequest,
    TestPlanReviewEditRequest,
)
from backend.app.modules.workflow_control.policy import ApprovalDecision, TransitionPolicyError


router = APIRouter(tags=["requirements"])


def project_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "PROJECT_NOT_FOUND",
            "message": "Project not found.",
            "details": {},
        },
    )


def module_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "MODULE_NOT_FOUND",
            "message": "Module not found in this project.",
            "details": {},
        },
    )


def requirement_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "REQUIREMENT_NOT_FOUND",
            "message": "Requirement not found.",
            "details": {},
        },
    )


def prompt_or_skill_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "PROMPT_OR_SKILL_NOT_FOUND",
            "message": "Prompt or skill version not found.",
            "details": {},
        },
    )


def requirement_review_schema_invalid() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "REQUIREMENT_REVIEW_SCHEMA_INVALID",
            "message": "Requirement review output did not match the expected schema.",
            "details": {},
        },
    )


def requirement_review_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "REQUIREMENT_REVIEW_NOT_FOUND",
            "message": "Requirement review not found.",
            "details": {},
        },
    )


def requirement_document_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "REQUIREMENT_DOCUMENT_NOT_FOUND",
            "message": "Requirement document not found.",
            "details": {},
        },
    )


def context_artifact_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "CONTEXT_ARTIFACT_NOT_FOUND",
            "message": "Context artifact not found in this project.",
            "details": {},
        },
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


def requirement_document_approval_required() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error_code": "REQUIREMENT_REVIEW_APPROVAL_REQUIRED",
            "message": "Approve the current requirement review before creating a formal document.",
            "details": {},
        },
    )


@router.post("/requirements", response_model=RequirementRead, status_code=status.HTTP_201_CREATED)
def create_requirement(
    data: RequirementCreate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.create_requirement(session, data)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc
    except service.ModuleNotFoundError as exc:
        raise module_not_found() from exc


@router.get("/requirements/{requirement_id}", response_model=RequirementRead)
def read_requirement(
    requirement_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.get_requirement(session, requirement_id)
    except service.RequirementNotFoundError as exc:
        raise requirement_not_found() from exc


@router.get("/projects/{project_id}/requirements", response_model=RequirementListRead)
def list_requirements(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> RequirementListRead:
    try:
        requirements = service.list_requirements(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc

    return RequirementListRead(items=requirements, total=len(requirements))


@router.get("/projects/{project_id}/requirement-documents", response_model=RequirementDocumentListRead)
def list_requirement_documents(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> RequirementDocumentListRead:
    try:
        items = service.list_requirement_documents(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc
    return RequirementDocumentListRead(items=items, total=len(items))


@router.post(
    "/requirements/{requirement_id}/review",
    response_model=RequirementReviewStartRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_requirement_review(
    requirement_id: uuid.UUID,
    data: RequirementReviewStartRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> RequirementReviewStartRead:
    try:
        ai_task, _review = service.start_requirement_review(session, store, requirement_id, data)
    except service.RequirementNotFoundError as exc:
        raise requirement_not_found() from exc
    except (service.PromptVersionNotFoundError, service.SkillVersionNotFoundError) as exc:
        raise prompt_or_skill_not_found() from exc
    except service.ContextArtifactNotFoundError as exc:
        raise context_artifact_not_found() from exc
    except service.RequirementReviewSchemaInvalidError as exc:
        raise requirement_review_schema_invalid() from exc

    return RequirementReviewStartRead(
        ai_task_id=ai_task.id,
        requirement_id=requirement_id,
        status="pending",
        next_poll_url=f"/api/ai-tasks/{ai_task.id}",
        used_knowledge=bool(ai_task.output_json.get("used_knowledge", False)),
        used_context_artifact_ids=[
            uuid.UUID(str(context_id))
            for context_id in ai_task.output_json.get("used_context_artifact_ids", ai_task.context_artifact_ids)
        ],
    )


@router.post(
    "/requirements/{requirement_id}/documents",
    response_model=RequirementDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_requirement_document(
    requirement_id: uuid.UUID,
    data: RequirementDocumentCreate,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> RequirementDocumentRead:
    try:
        return service.create_requirement_document(session, store, requirement_id, data)
    except service.RequirementNotFoundError as exc:
        raise requirement_not_found() from exc
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except service.RequirementDocumentApprovalRequiredError as exc:
        raise requirement_document_approval_required() from exc


@router.get("/requirements/{requirement_id}/review", response_model=RequirementReviewDetailRead)
def read_requirement_review(
    requirement_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.get_requirement_review_detail(session, requirement_id)
    except service.RequirementNotFoundError as exc:
        raise requirement_not_found() from exc
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except service.RequirementReviewSchemaInvalidError as exc:
        raise requirement_review_schema_invalid() from exc


@router.get(
    "/projects/{project_id}/requirement-reviews/{review_id}",
    response_model=RequirementReviewDetailRead,
)
def read_project_requirement_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.get_requirement_review_detail_in_project(session, project_id, review_id)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/complete-review",
    response_model=RequirementReviewDetailRead,
)
def complete_requirement_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.complete_requirement_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/edit",
    response_model=RequirementReviewDetailRead,
)
def edit_requirement_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowEditRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.edit_requirement_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/approve",
    response_model=RequirementReviewDetailRead,
)
def approve_requirement_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.approve_requirement_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/reject",
    response_model=RequirementReviewDetailRead,
)
def reject_requirement_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.reject_requirement_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/regenerate-selected",
    response_model=RequirementReviewDetailRead,
)
def regenerate_selected_requirement_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowEditRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.regenerate_selected_requirement_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/approve-and-continue",
    response_model=RequirementReviewDetailRead,
)
def approve_and_continue_requirement_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.approve_and_continue_requirement_workflow(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/continue",
    response_model=RequirementReviewDetailRead,
)
def continue_requirement_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowContinueRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.continue_requirement_workflow(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.get(
    "/projects/{project_id}/requirement-reviews/{review_id}/risk-review",
    response_model=RequirementReviewDetailRead,
)
def read_risk_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.get_risk_review_detail_in_project(session, project_id, review_id)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/risk-review/submit",
    response_model=RequirementReviewDetailRead,
)
def submit_risk_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.submit_risk_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/risk-review/complete-review",
    response_model=RequirementReviewDetailRead,
)
def complete_risk_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.complete_risk_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/risk-review/edit",
    response_model=RequirementReviewDetailRead,
)
def edit_risk_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RiskReviewEditRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.edit_risk_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/risk-review/approve",
    response_model=RequirementReviewDetailRead,
)
def approve_risk_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.decide_risk_workflow_review(
            session, project_id, review_id, data, decision=ApprovalDecision.APPROVED,
        )
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/risk-review/reject",
    response_model=RequirementReviewDetailRead,
)
def reject_risk_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.decide_risk_workflow_review(
            session, project_id, review_id, data, decision=ApprovalDecision.REJECTED,
        )
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/risk-review/continue",
    response_model=RequirementReviewDetailRead,
)
def continue_risk_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowContinueRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.continue_risk_workflow(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/risk-review/approve-and-continue",
    response_model=RequirementReviewDetailRead,
)
def approve_and_continue_risk_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.approve_and_continue_risk_workflow(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.get(
    "/projects/{project_id}/requirement-reviews/{review_id}/test-plan-review",
    response_model=RequirementReviewDetailRead,
)
def read_test_plan_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.get_test_plan_review_detail_in_project(session, project_id, review_id)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/test-plan-review/submit",
    response_model=RequirementReviewDetailRead,
)
def submit_test_plan_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.submit_test_plan_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/test-plan-review/complete-review",
    response_model=RequirementReviewDetailRead,
)
def complete_test_plan_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.complete_test_plan_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/test-plan-review/edit",
    response_model=RequirementReviewDetailRead,
)
def edit_test_plan_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: TestPlanReviewEditRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.edit_test_plan_workflow_review(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/test-plan-review/approve",
    response_model=RequirementReviewDetailRead,
)
def approve_test_plan_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.decide_test_plan_workflow_review(
            session, project_id, review_id, data, decision=ApprovalDecision.APPROVED,
        )
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/test-plan-review/reject",
    response_model=RequirementReviewDetailRead,
)
def reject_test_plan_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.decide_test_plan_workflow_review(
            session, project_id, review_id, data, decision=ApprovalDecision.REJECTED,
        )
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/test-plan-review/continue",
    response_model=RequirementReviewDetailRead,
)
def continue_test_plan_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowContinueRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.continue_test_plan_workflow(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{review_id}/test-plan-review/approve-and-continue",
    response_model=RequirementReviewDetailRead,
)
def approve_and_continue_test_plan_review(
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    data: RequirementWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> RequirementReviewDetailRead:
    try:
        return service.approve_and_continue_test_plan_workflow(session, project_id, review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise requirement_review_not_found() from exc
    except (service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc
