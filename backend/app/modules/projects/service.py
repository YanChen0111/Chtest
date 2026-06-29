from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.projects.schemas import ProjectCreate, ProjectUpdate


DEFAULT_WORKSPACE_NAME = "Personal Workspace"


class ProjectAlreadyExistsError(Exception):
    pass


def get_or_create_default_workspace(session: Session) -> Workspace:
    workspace = session.scalar(select(Workspace).where(Workspace.name == DEFAULT_WORKSPACE_NAME))
    if workspace is not None:
        return workspace

    workspace = Workspace(name=DEFAULT_WORKSPACE_NAME)
    session.add(workspace)
    session.flush()
    return workspace


def create_project(session: Session, data: ProjectCreate) -> Project:
    workspace = get_or_create_default_workspace(session)
    existing_project = session.scalar(
        select(Project).where(Project.workspace_id == workspace.id, Project.name == data.name),
    )
    if existing_project is not None:
        raise ProjectAlreadyExistsError

    project = Project(
        workspace=workspace,
        name=data.name,
        description=data.description,
        default_language=data.default_language,
        default_test_type=data.default_test_type,
    )
    session.add(project)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise ProjectAlreadyExistsError from exc
    session.refresh(project)
    return project


def get_project(session: Session, project_id: uuid.UUID) -> Project | None:
    return session.get(Project, project_id)


def get_project_settings(session: Session, project_id: uuid.UUID) -> Project | None:
    return session.scalar(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.modules),
            selectinload(Project.repositories),
            selectinload(Project.environments),
            selectinload(Project.test_commands),
        ),
    )


def update_project(session: Session, project: Project, data: ProjectUpdate) -> Project:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(project, field, value)

    session.add(project)
    session.commit()
    session.refresh(project)
    return project
