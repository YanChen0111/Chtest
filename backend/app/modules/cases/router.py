from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.cases import service
from backend.app.modules.cases.schemas import (
    CaseGenerationStartRead,
    CaseGenerationStartRequest,
    CaseMetricsRead,
    CaseReviewRead,
    CaseReviewRequest,
    GeneratedCaseCandidateListRead,
    TestCaseListRead,
)
from backend.app.modules.projects.router import get_session


router = APIRouter(tags=["cases"])


def not_found(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def schema_invalid() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CASE_GENERATION_SCHEMA_INVALID",
            "message": "Case generation output did not match the expected schema.",
            "details": {},
        },
    )


def conflict(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def bad_request(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


@router.post(
    "/case-generation/tasks",
    response_model=CaseGenerationStartRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_case_generation(
    data: CaseGenerationStartRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> CaseGenerationStartRead:
    try:
        generation_task, ai_task = service.start_case_generation(session, store, data)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.RequirementNotFoundError as exc:
        raise not_found("REQUIREMENT_NOT_FOUND", "Requirement not found.") from exc
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (service.PromptVersionNotFoundError, service.SkillVersionNotFoundError) as exc:
        raise not_found("PROMPT_OR_SKILL_NOT_FOUND", "Prompt or skill version not found.") from exc
    except service.ContextArtifactNotFoundError as exc:
        raise not_found("CONTEXT_ARTIFACT_NOT_FOUND", "Context artifact not found in this project.") from exc
    except service.CaseGenerationSchemaInvalidError as exc:
        raise schema_invalid() from exc

    return CaseGenerationStartRead(
        case_generation_task_id=generation_task.id,
        ai_task_id=ai_task.id,
        status="pending",
        used_knowledge=bool(ai_task.output_json.get("used_knowledge", False)),
        used_context_artifact_ids=[
            uuid.UUID(str(context_id))
            for context_id in ai_task.output_json.get("used_context_artifact_ids", ai_task.context_artifact_ids)
        ],
    )


@router.get(
    "/case-generation/tasks/{generation_task_id}/candidates",
    response_model=GeneratedCaseCandidateListRead,
)
def list_candidates(
    generation_task_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> GeneratedCaseCandidateListRead:
    try:
        items = service.list_candidates(session, generation_task_id)
    except service.CaseGenerationTaskNotFoundError as exc:
        raise not_found("CASE_GENERATION_TASK_NOT_FOUND", "Case generation task not found.") from exc
    return GeneratedCaseCandidateListRead(items=items, total=len(items))


@router.get(
    "/case-generation/tasks/{generation_task_id}/metrics",
    response_model=CaseMetricsRead,
)
def get_case_metrics(
    generation_task_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> CaseMetricsRead:
    try:
        return service.calculate_case_metrics(session, generation_task_id)
    except service.CaseGenerationTaskNotFoundError as exc:
        raise not_found("CASE_GENERATION_TASK_NOT_FOUND", "Case generation task not found.") from exc


@router.get("/test-cases", response_model=TestCaseListRead)
def list_test_cases(
    project_id: uuid.UUID,
    module_id: uuid.UUID | None = None,
    status: str | None = None,
    test_type: str | None = None,
    priority: str | None = None,
    keyword: str | None = None,
    session: Session = Depends(get_session),
) -> TestCaseListRead:
    try:
        items = service.list_test_cases(
            session,
            project_id=project_id,
            module_id=module_id,
            status=status,
            test_type=test_type,
            priority=priority,
            keyword=keyword,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return TestCaseListRead(items=items, total=len(items))


@router.post("/case-review/items/{candidate_id}/approve", response_model=CaseReviewRead)
def review_candidate(
    candidate_id: uuid.UUID,
    data: CaseReviewRequest,
    session: Session = Depends(get_session),
) -> CaseReviewRead:
    try:
        candidate, test_case = service.review_candidate(session, candidate_id, data)
    except service.CaseCandidateNotFoundError as exc:
        raise not_found("CASE_CANDIDATE_NOT_FOUND", "Case candidate not found.") from exc
    except service.CaseCandidateAlreadyFinalError as exc:
        raise conflict("CASE_CANDIDATE_ALREADY_FINAL", "Case candidate is already in a final review state.") from exc
    except service.CaseReviewInvalidActionError as exc:
        raise bad_request("CASE_REVIEW_INVALID_ACTION", "Case review action payload is invalid.") from exc

    return CaseReviewRead(
        candidate_id=candidate.id,
        status=candidate.status,
        test_case_id=test_case.id if test_case is not None else None,
    )
