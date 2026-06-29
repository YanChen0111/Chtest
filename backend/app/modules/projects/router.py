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
