from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.automation import service
from backend.app.modules.automation.schemas import (
    AutomationDraftApproveRequest,
    AutomationDraftCreateRead,
    AutomationDraftCreateRequest,
    AutomationDraftEditRequest,
    AutomationDraftRead,
    AutomationDraftReviewRead,
    AutomationPlanApproveRequest,
    AutomationPlanCreateRequest,
    AutomationPlanGenerateDraftRequest,
    AutomationPlanRead,
    AutomationPlanReviewRead,
    AutomationPlanUpdateRequest,
)
from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill import service as prompt_skill_service


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


def schema_invalid(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def bad_gateway(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def conflict(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


@router.post(
    "/automation/plans",
    response_model=AutomationPlanRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_automation_plan(
    data: AutomationPlanCreateRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> AutomationPlanRead:
    try:
        return automation_plan_read(service.create_automation_plan(session, store, data))
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.TestCaseNotFoundError as exc:
        raise not_found("TEST_CASE_NOT_FOUND", "Test case not found.") from exc
    except service.ContextArtifactNotFoundError as exc:
        raise not_found("CONTEXT_ARTIFACT_NOT_FOUND", "Context artifact not found in this project.") from exc
    except (prompt_skill_service.PromptVersionNotFoundError, prompt_skill_service.SkillVersionNotFoundError) as exc:
        raise not_found("PROMPT_OR_SKILL_NOT_FOUND", "Prompt or skill version not found.") from exc
    except service.AutomationPlanSourceNotApprovedError as exc:
        raise conflict(
            "AUTOMATION_PLAN_SOURCE_NOT_APPROVED",
            "Automation plan source TestCase must be approved and generated from a reviewed candidate.",
        ) from exc


@router.get("/automation/plans/{plan_id}", response_model=AutomationPlanRead)
def get_automation_plan(
    plan_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> AutomationPlanRead:
    try:
        return automation_plan_read(service.get_automation_plan(session, plan_id))
    except service.AutomationPlanNotFoundError as exc:
        raise not_found("AUTOMATION_PLAN_NOT_FOUND", "Automation plan not found.") from exc


@router.patch("/automation/plans/{plan_id}", response_model=AutomationPlanReviewRead)
def edit_automation_plan(
    plan_id: uuid.UUID,
    data: AutomationPlanUpdateRequest,
    session: Session = Depends(get_session),
) -> AutomationPlanReviewRead:
    try:
        plan = service.edit_automation_plan(session, plan_id, data)
    except service.AutomationPlanNotFoundError as exc:
        raise not_found("AUTOMATION_PLAN_NOT_FOUND", "Automation plan not found.") from exc
    except service.AutomationPlanInvalidActionError as exc:
        raise bad_request("AUTOMATION_PLAN_INVALID_ACTION", "Automation plan action is invalid.") from exc
    return AutomationPlanReviewRead(automation_plan_id=plan.id, status=plan.status)


@router.post("/automation/plans/{plan_id}/approve", response_model=AutomationPlanReviewRead)
def approve_automation_plan(
    plan_id: uuid.UUID,
    data: AutomationPlanApproveRequest,
    session: Session = Depends(get_session),
) -> AutomationPlanReviewRead:
    try:
        plan = service.approve_automation_plan(session, plan_id, data)
    except service.AutomationPlanNotFoundError as exc:
        raise not_found("AUTOMATION_PLAN_NOT_FOUND", "Automation plan not found.") from exc
    except service.AutomationPlanInvalidActionError as exc:
        raise bad_request("AUTOMATION_PLAN_INVALID_ACTION", "Automation plan action is invalid.") from exc
    return AutomationPlanReviewRead(automation_plan_id=plan.id, status=plan.status)


@router.post(
    "/automation/plans/{plan_id}/generate-draft",
    response_model=AutomationDraftCreateRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def generate_automation_draft_from_plan(
    plan_id: uuid.UUID,
    data: AutomationPlanGenerateDraftRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> AutomationDraftCreateRead:
    try:
        plan = service.get_automation_plan(session, plan_id)
        draft, ai_task = service.create_automation_draft(
            session,
            store,
            AutomationDraftCreateRequest(
                project_id=plan.project_id,
                automation_plan_id=plan.id,
                prompt_version=data.prompt_version,
                skill_version=data.skill_version,
                model_provider=data.model_provider,
                model_name=data.model_name,
            ),
        )
    except service.AutomationPlanNotFoundError as exc:
        raise not_found("AUTOMATION_PLAN_NOT_FOUND", "Automation plan not found.") from exc
    except service.AutomationPlanNotApprovedError as exc:
        raise conflict("AUTOMATION_PLAN_NOT_APPROVED", "Automation plan must be approved before draft generation.") from exc
    except service.AutomationDraftInvalidInputError as exc:
        raise bad_request("AUTOMATION_DRAFT_INVALID_INPUT", "Automation draft input is invalid.") from exc
    except service.AutomationDraftGenerationFailedError as exc:
        raise bad_gateway("AUTOMATION_DRAFT_GENERATION_FAILED", "Automation draft model generation failed.") from exc
    except service.AutomationDraftSchemaInvalidError as exc:
        raise schema_invalid(
            "AUTOMATION_DRAFT_SCHEMA_INVALID",
            "Automation draft output did not match the expected schema.",
        ) from exc
    except (prompt_skill_service.PromptVersionNotFoundError, prompt_skill_service.SkillVersionNotFoundError) as exc:
        raise not_found("PROMPT_OR_SKILL_NOT_FOUND", "Prompt or skill version not found.") from exc

    return AutomationDraftCreateRead(
        automation_draft_id=draft.id,
        ai_task_id=ai_task.id,
        status=draft.status,
    )


@router.post(
    "/automation/drafts",
    response_model=AutomationDraftCreateRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_automation_draft(
    data: AutomationDraftCreateRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> AutomationDraftCreateRead:
    try:
        draft, ai_task = service.create_automation_draft(session, store, data)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.TestCaseNotFoundError as exc:
        raise not_found("TEST_CASE_NOT_FOUND", "Test case not found.") from exc
    except service.RequirementNotFoundError as exc:
        raise not_found("REQUIREMENT_NOT_FOUND", "Requirement not found.") from exc
    except service.AutomationPlanNotFoundError as exc:
        raise not_found("AUTOMATION_PLAN_NOT_FOUND", "Automation plan not found.") from exc
    except service.AutomationPlanNotApprovedError as exc:
        raise conflict("AUTOMATION_PLAN_NOT_APPROVED", "Automation plan must be approved before draft generation.") from exc
    except service.AutomationDraftInvalidInputError as exc:
        raise bad_request("AUTOMATION_DRAFT_INVALID_INPUT", "TestCase or Requirement reference is required.") from exc
    except service.AutomationDraftGenerationFailedError as exc:
        raise bad_gateway("AUTOMATION_DRAFT_GENERATION_FAILED", "Automation draft model generation failed.") from exc
    except service.AutomationDraftSchemaInvalidError as exc:
        raise schema_invalid(
            "AUTOMATION_DRAFT_SCHEMA_INVALID",
            "Automation draft output did not match the expected schema.",
        ) from exc
    except (prompt_skill_service.PromptVersionNotFoundError, prompt_skill_service.SkillVersionNotFoundError) as exc:
        raise not_found("PROMPT_OR_SKILL_NOT_FOUND", "Prompt or skill version not found.") from exc

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
    except service.AutomationDraftQualityGateError as exc:
        raise bad_request(
            "AUTOMATION_DRAFT_QUALITY_GATE_FAILED",
            "Automation draft must contain non-placeholder executable test code before approval.",
        ) from exc
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
    except service.AutomationDraftQualityGateError as exc:
        raise bad_request(
            "AUTOMATION_DRAFT_QUALITY_GATE_FAILED",
            "Automation draft must contain non-placeholder executable test code before approval.",
        ) from exc
    return AutomationDraftReviewRead(automation_draft_id=draft.id, status=draft.status)


def automation_plan_read(plan) -> AutomationPlanRead:
    return AutomationPlanRead(
        id=plan.id,
        project_id=plan.project_id,
        test_case_id=plan.test_case_id,
        requirement_id=plan.requirement_id,
        requirement_review_id=plan.requirement_review_id,
        source_candidate_id=plan.source_candidate_id,
        ai_task_id=plan.ai_task_id,
        knowledge_retrieval_artifact_id=plan.knowledge_retrieval_artifact_id,
        target_framework=plan.target_framework,
        title=plan.title,
        plan=plan.plan_json,
        execution_steps=plan.execution_steps_json,
        test_data=plan.test_data_json,
        dependency_notes=plan.dependency_notes,
        risk_notes=plan.risk_notes,
        used_context_artifact_ids=plan.used_context_artifact_ids,
        status=plan.status,
        review_comment=plan.review_comment,
    )


def automation_draft_read(draft) -> AutomationDraftRead:
    return AutomationDraftRead(
        id=draft.id,
        project_id=draft.project_id,
        test_case_id=draft.test_case_id,
        requirement_id=draft.requirement_id,
        ai_task_id=draft.ai_task_id,
        automation_plan_id=draft.automation_plan_id,
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
