from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.automation import service
from backend.app.modules.automation.schemas import (
    AutomationDraftApproveRequest,
    AutomationDraftCreateRead,
    AutomationDraftCreateRequest,
    AutomationDraftEditRequest,
    AutomationDraftRead,
    AutomationDraftReviewRead,
)
from backend.app.modules.projects.router import get_session


router = APIRouter(tags=["automation"])


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


@router.post(
    "/automation/drafts",
    response_model=AutomationDraftCreateRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_automation_draft(
    data: AutomationDraftCreateRequest,
    session: Session = Depends(get_session),
) -> AutomationDraftCreateRead:
    try:
        draft, ai_task = service.create_automation_draft(session, data)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.TestCaseNotFoundError as exc:
        raise not_found("TEST_CASE_NOT_FOUND", "Test case not found.") from exc
    except service.RequirementNotFoundError as exc:
        raise not_found("REQUIREMENT_NOT_FOUND", "Requirement not found.") from exc
    except service.AutomationDraftInvalidInputError as exc:
        raise bad_request("AUTOMATION_DRAFT_INVALID_INPUT", "TestCase or Requirement reference is required.") from exc

    return AutomationDraftCreateRead(
        automation_draft_id=draft.id,
        ai_task_id=ai_task.id,
        status=draft.status,
    )


@router.get("/automation/drafts/{draft_id}", response_model=AutomationDraftRead)
def get_automation_draft(
    draft_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> AutomationDraftRead:
    try:
        return automation_draft_read(service.get_automation_draft(session, draft_id))
    except service.AutomationDraftNotFoundError as exc:
        raise not_found("AUTOMATION_DRAFT_NOT_FOUND", "Automation draft not found.") from exc


@router.patch("/automation/drafts/{draft_id}", response_model=AutomationDraftReviewRead)
def edit_automation_draft(
    draft_id: uuid.UUID,
    data: AutomationDraftEditRequest,
    session: Session = Depends(get_session),
) -> AutomationDraftReviewRead:
    try:
        draft = service.edit_automation_draft(session, draft_id, data)
    except service.AutomationDraftNotFoundError as exc:
        raise not_found("AUTOMATION_DRAFT_NOT_FOUND", "Automation draft not found.") from exc
    except service.AutomationDraftInvalidActionError as exc:
        raise bad_request("AUTOMATION_DRAFT_INVALID_ACTION", "Automation draft action is invalid.") from exc
    return AutomationDraftReviewRead(automation_draft_id=draft.id, status=draft.status)


@router.post("/automation/drafts/{draft_id}/approve", response_model=AutomationDraftReviewRead)
def approve_automation_draft(
    draft_id: uuid.UUID,
    data: AutomationDraftApproveRequest,
    session: Session = Depends(get_session),
) -> AutomationDraftReviewRead:
    try:
        draft = service.approve_automation_draft(session, draft_id, data)
    except service.AutomationDraftNotFoundError as exc:
        raise not_found("AUTOMATION_DRAFT_NOT_FOUND", "Automation draft not found.") from exc
    except service.AutomationDraftInvalidActionError as exc:
        raise bad_request("AUTOMATION_DRAFT_INVALID_ACTION", "Automation draft action is invalid.") from exc
    return AutomationDraftReviewRead(automation_draft_id=draft.id, status=draft.status)


def automation_draft_read(draft) -> AutomationDraftRead:
    return AutomationDraftRead(
        id=draft.id,
        project_id=draft.project_id,
        test_case_id=draft.test_case_id,
        requirement_id=draft.requirement_id,
        ai_task_id=draft.ai_task_id,
        target_framework=draft.target_framework,
        title=draft.title,
        draft_code=draft.draft_code,
        draft_language=draft.draft_language,
        suggested_file_path=draft.suggested_file_path,
        execution_notes=draft.execution_notes,
        risk_notes=draft.risk_notes,
        execution_strategy=draft.execution_strategy,
        approval_required=draft.approval_required,
        status=draft.status,
        review_comment=draft.review_comment,
        runtime_artifact_id=draft.runtime_artifact_id,
        promoted_artifact_id=draft.promoted_artifact_id,
    )
