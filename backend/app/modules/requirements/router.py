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
    RequirementListRead,
    RequirementRead,
    RequirementReviewDetailRead,
    RequirementReviewStartRead,
    RequirementReviewStartRequest,
)


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


def context_artifact_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "CONTEXT_ARTIFACT_NOT_FOUND",
            "message": "Context artifact not found in this project.",
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
