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
    GeneratedCaseCandidateListRead,
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
