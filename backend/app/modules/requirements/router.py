from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.projects.router import get_session
from backend.app.modules.requirements import service
from backend.app.modules.requirements.schemas import RequirementCreate, RequirementListRead, RequirementRead


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
