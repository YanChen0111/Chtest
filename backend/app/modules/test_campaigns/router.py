from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.projects.router import get_session
from backend.app.modules.test_campaigns import service
from backend.app.modules.test_campaigns.schemas import (
    TestCampaignAction,
    TestCampaignContinue,
    TestCampaignCreate,
    TestCampaignEdit,
    TestCampaignRead,
)
from backend.app.modules.workflow_control import service as workflow_service
from backend.app.modules.workflow_control.policy import ApprovalDecision, TransitionPolicyError


router = APIRouter(tags=["test-campaigns"])


def _error(exc: Exception) -> HTTPException:
    code = getattr(exc, "code", exc.__class__.__name__.replace("Error", "").upper())
    not_found = {
        "PROJECT_NOT_FOUND",
        "TEST_CAMPAIGN_ENVIRONMENT_NOT_FOUND",
        "TEST_CAMPAIGN_NOT_FOUND",
        "TEST_CAMPAIGN_EVIDENCE_NOT_FOUND",
        "WORKFLOW_RUN_NOT_FOUND",
        "WORKFLOW_PROJECT_NOT_FOUND",
    }
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND if code in not_found else status.HTTP_409_CONFLICT,
        detail={"error_code": code, "message": "Test campaign action was rejected.", "details": {}},
    )


@router.post(
    "/projects/{project_id}/test-campaigns",
    response_model=TestCampaignRead,
    status_code=status.HTTP_201_CREATED,
)
def create_test_campaign(
    project_id: uuid.UUID,
    data: TestCampaignCreate,
    session: Session = Depends(get_session),
) -> TestCampaignRead:
    try:
        return service.create_test_campaign(session, project_id, data)
    except (service.TestCampaignError, workflow_service.WorkflowPersistenceError, ValueError) as exc:
        raise _error(exc) from exc


@router.get("/projects/{project_id}/test-campaigns", response_model=list[TestCampaignRead])
def list_test_campaigns(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> list[TestCampaignRead]:
    try:
        return service.list_test_campaigns(session, project_id)
    except (service.TestCampaignError, workflow_service.WorkflowPersistenceError) as exc:
        raise _error(exc) from exc


@router.get("/projects/{project_id}/test-campaigns/{campaign_id}", response_model=TestCampaignRead)
def read_test_campaign(
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> TestCampaignRead:
    try:
        return service.get_test_campaign(session, project_id, campaign_id)
    except (service.TestCampaignError, workflow_service.WorkflowPersistenceError) as exc:
        raise _error(exc) from exc


@router.post("/projects/{project_id}/test-campaigns/{campaign_id}/edit", response_model=TestCampaignRead)
def edit_test_campaign(
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignEdit,
    session: Session = Depends(get_session),
) -> TestCampaignRead:
    try:
        return service.edit_test_campaign(session, project_id, campaign_id, data)
    except (
        service.TestCampaignError,
        workflow_service.WorkflowPersistenceError,
        TransitionPolicyError,
        ValueError,
    ) as exc:
        raise _error(exc) from exc


@router.post("/projects/{project_id}/test-campaigns/{campaign_id}/submit", response_model=TestCampaignRead)
def submit_scope(
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignAction,
    session: Session = Depends(get_session),
) -> TestCampaignRead:
    try:
        return service.submit_scope(session, project_id, campaign_id, data)
    except (service.TestCampaignError, workflow_service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise _error(exc) from exc


@router.post(
    "/projects/{project_id}/test-campaigns/{campaign_id}/complete-review",
    response_model=TestCampaignRead,
)
def complete_scope_review(
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignAction,
    session: Session = Depends(get_session),
) -> TestCampaignRead:
    try:
        return service.complete_scope_review(session, project_id, campaign_id, data)
    except (service.TestCampaignError, workflow_service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise _error(exc) from exc


@router.post("/projects/{project_id}/test-campaigns/{campaign_id}/approve", response_model=TestCampaignRead)
def approve_scope(
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignAction,
    session: Session = Depends(get_session),
) -> TestCampaignRead:
    try:
        return service.decide_scope(
            session,
            project_id,
            campaign_id,
            data,
            decision=ApprovalDecision.APPROVED,
        )
    except (service.TestCampaignError, workflow_service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise _error(exc) from exc


@router.post("/projects/{project_id}/test-campaigns/{campaign_id}/reject", response_model=TestCampaignRead)
def reject_scope(
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignAction,
    session: Session = Depends(get_session),
) -> TestCampaignRead:
    try:
        return service.decide_scope(
            session,
            project_id,
            campaign_id,
            data,
            decision=ApprovalDecision.REJECTED,
        )
    except (service.TestCampaignError, workflow_service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise _error(exc) from exc


@router.post("/projects/{project_id}/test-campaigns/{campaign_id}/continue", response_model=TestCampaignRead)
def continue_scope(
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignContinue,
    session: Session = Depends(get_session),
) -> TestCampaignRead:
    try:
        return service.continue_scope(session, project_id, campaign_id, data)
    except (service.TestCampaignError, workflow_service.WorkflowPersistenceError, TransitionPolicyError) as exc:
        raise _error(exc) from exc
