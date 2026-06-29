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
    EnvironmentCreate,
    EnvironmentListRead,
    EnvironmentRead,
    EnvironmentUpdate,
    ModuleCreate,
    ModuleListRead,
    ModuleRead,
    ModuleUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectSettingsRead,
    ProjectSettingsProjectRead,
    ProjectUpdate,
    RepositoryCreate,
    RepositoryListRead,
    RepositoryRead,
    RepositoryUpdate,
)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+pysqlite:////tmp/chtest-dev.db")
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)

router = APIRouter(tags=["projects"])


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


def repository_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "REPOSITORY_NOT_FOUND",
            "message": "Repository not found.",
            "details": {},
        },
    )


def repository_already_exists() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error_code": "REPOSITORY_ALREADY_EXISTS",
            "message": "Repository name already exists in this project.",
            "details": {},
        },
    )


def repository_path_not_allowed() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "REPOSITORY_PATH_NOT_ALLOWED",
            "message": "Repository path is missing or outside configured allowlisted roots.",
            "details": {},
        },
    )


def environment_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "ENVIRONMENT_NOT_FOUND",
            "message": "Environment not found.",
            "details": {},
        },
    )


def environment_already_exists() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error_code": "ENVIRONMENT_ALREADY_EXISTS",
            "message": "Environment name already exists in this project.",
            "details": {},
        },
    )


def environment_secret_not_allowed() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "ENVIRONMENT_SECRET_NOT_ALLOWED",
            "message": "Environment secret-like values must be stored as references.",
            "details": {},
        },
    )


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.create_project(session, data)
    except service.ProjectAlreadyExistsError as exc:
        raise project_already_exists() from exc


@router.get("/projects/{project_id}", response_model=ProjectRead)
def read_project(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> Any:
    project = service.get_project(session, project_id)
    if project is None:
        raise project_not_found()
    return project


@router.patch("/projects/{project_id}", response_model=ProjectRead)
def patch_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    session: Session = Depends(get_session),
) -> Any:
    project = service.get_project(session, project_id)
    if project is None:
        raise project_not_found()
    return service.update_project(session, project, data)


@router.post("/projects/{project_id}/modules", response_model=ModuleRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/projects/{project_id}/modules", response_model=ModuleListRead)
def list_modules(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ModuleListRead:
    try:
        modules = service.list_modules(session, project_id)
    except service.ModuleNotFoundError as exc:
        raise project_not_found() from exc

    return ModuleListRead(items=modules, total=len(modules))


@router.patch("/projects/{project_id}/modules/{module_id}", response_model=ModuleRead)
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


@router.post("/repositories", response_model=RepositoryRead, status_code=status.HTTP_201_CREATED)
def create_repository(
    data: RepositoryCreate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.create_repository(session, data)
    except service.ModuleNotFoundError as exc:
        raise project_not_found() from exc
    except service.RepositoryPathNotAllowedError as exc:
        raise repository_path_not_allowed() from exc
    except service.RepositoryAlreadyExistsError as exc:
        raise repository_already_exists() from exc


@router.get("/projects/{project_id}/repositories", response_model=RepositoryListRead)
def list_repositories(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> RepositoryListRead:
    try:
        repositories = service.list_repositories(session, project_id)
    except service.ModuleNotFoundError as exc:
        raise project_not_found() from exc

    return RepositoryListRead(items=repositories, total=len(repositories))


@router.patch("/repositories/{repository_id}", response_model=RepositoryRead)
def patch_repository(
    repository_id: uuid.UUID,
    data: RepositoryUpdate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.update_repository(session, repository_id, data)
    except service.RepositoryNotFoundError as exc:
        raise repository_not_found() from exc
    except service.RepositoryPathNotAllowedError as exc:
        raise repository_path_not_allowed() from exc
    except service.RepositoryAlreadyExistsError as exc:
        raise repository_already_exists() from exc


@router.post("/environments", response_model=EnvironmentRead, status_code=status.HTTP_201_CREATED)
def create_environment(
    data: EnvironmentCreate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.create_environment(session, data)
    except service.ModuleNotFoundError as exc:
        raise project_not_found() from exc
    except service.EnvironmentSecretNotAllowedError as exc:
        raise environment_secret_not_allowed() from exc
    except service.EnvironmentAlreadyExistsError as exc:
        raise environment_already_exists() from exc


@router.get("/projects/{project_id}/environments", response_model=EnvironmentListRead)
def list_environments(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> EnvironmentListRead:
    try:
        environments = service.list_environments(session, project_id)
    except service.ModuleNotFoundError as exc:
        raise project_not_found() from exc

    return EnvironmentListRead(items=environments, total=len(environments))


@router.patch("/environments/{environment_id}", response_model=EnvironmentRead)
def patch_environment(
    environment_id: uuid.UUID,
    data: EnvironmentUpdate,
    session: Session = Depends(get_session),
) -> Any:
    try:
        return service.update_environment(session, environment_id, data)
    except service.EnvironmentNotFoundError as exc:
        raise environment_not_found() from exc
    except service.EnvironmentSecretNotAllowedError as exc:
        raise environment_secret_not_allowed() from exc
    except service.EnvironmentAlreadyExistsError as exc:
        raise environment_already_exists() from exc


@router.get("/projects/{project_id}/settings", response_model=ProjectSettingsRead)
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
