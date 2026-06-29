from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.models.base import Base
from backend.app.modules.projects import service
from backend.app.modules.projects.schemas import (
    ModuleCreate,
    ModuleListRead,
    ModuleRead,
    ModuleUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectSettingsRead,
    ProjectSettingsProjectRead,
    ProjectUpdate,
)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+pysqlite:////tmp/chtest-dev.db")
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)

router = APIRouter(prefix="/projects", tags=["projects"])


def get_session() -> Iterator[Session]:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        yield session


def project_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "PROJECT_NOT_FOUND",
            "message": "Project not found.",
            "details": {},
        },
    )


def project_already_exists() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error_code": "PROJECT_ALREADY_EXISTS",
            "message": "Project name already exists in the default workspace.",
            "details": {},
        },
    )


def module_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "MODULE_NOT_FOUND",
            "message": "Module not found.",
            "details": {},
        },
    )


def module_parent_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "MODULE_PARENT_NOT_FOUND",
            "message": "Module parent not found in this project.",
            "details": {},
        },
    )


def module_already_exists() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error_code": "MODULE_ALREADY_EXISTS",
            "message": "Module name already exists under the same parent.",
            "details": {},
        },
    )


def module_level_limit_exceeded() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error_code": "MODULE_LEVEL_LIMIT_EXCEEDED",
            "message": "Module tree cannot exceed five levels.",
            "details": {},
        },
    )


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.create_project(session, data)
    except service.ProjectAlreadyExistsError as exc:
        raise project_already_exists() from exc


@router.get("/{project_id}", response_model=ProjectRead)
def read_project(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> Any:
    project = service.get_project(session, project_id)
    if project is None:
        raise project_not_found()
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def patch_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    session: Session = Depends(get_session),
) -> Any:
    project = service.get_project(session, project_id)
    if project is None:
        raise project_not_found()
    return service.update_project(session, project, data)


@router.post("/{project_id}/modules", response_model=ModuleRead, status_code=status.HTTP_201_CREATED)
def create_module(
    project_id: uuid.UUID,
    data: ModuleCreate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.create_module(session, project_id, data)
    except service.ModuleNotFoundError as exc:
        raise project_not_found() from exc
    except service.ModuleParentNotFoundError as exc:
        raise module_parent_not_found() from exc
    except service.ModuleLevelLimitExceededError as exc:
        raise module_level_limit_exceeded() from exc
    except service.ModuleAlreadyExistsError as exc:
        raise module_already_exists() from exc


@router.get("/{project_id}/modules", response_model=ModuleListRead)
def list_modules(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ModuleListRead:
    try:
        modules = service.list_modules(session, project_id)
    except service.ModuleNotFoundError as exc:
        raise project_not_found() from exc

    return ModuleListRead(items=modules, total=len(modules))


@router.patch("/{project_id}/modules/{module_id}", response_model=ModuleRead)
def patch_module(
    project_id: uuid.UUID,
    module_id: uuid.UUID,
    data: ModuleUpdate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.update_module(session, project_id, module_id, data)
    except service.ModuleNotFoundError as exc:
        raise module_not_found() from exc
    except service.ModuleAlreadyExistsError as exc:
        raise module_already_exists() from exc


@router.get("/{project_id}/settings", response_model=ProjectSettingsRead)
def read_project_settings(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ProjectSettingsRead:
    project = service.get_project_settings(session, project_id)
    if project is None:
        raise project_not_found()

    return ProjectSettingsRead(
        project=ProjectSettingsProjectRead.model_validate(project),
        modules=project.modules,
        repositories=project.repositories,
        environments=project.environments,
        test_commands=project.test_commands,
        tool_definitions=[],
    )
