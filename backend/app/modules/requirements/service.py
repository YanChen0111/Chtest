from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.projects.models import Module, Project
from backend.app.modules.requirements.models import Requirement
from backend.app.modules.requirements.schemas import RequirementCreate


class ProjectNotFoundError(Exception):
    pass


class ModuleNotFoundError(Exception):
    pass


class RequirementNotFoundError(Exception):
    pass


def ensure_project_exists(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise ProjectNotFoundError
    return project


def ensure_module_belongs_to_project(
    session: Session,
    project_id: uuid.UUID,
    module_id: uuid.UUID | None,
) -> None:
    if module_id is None:
        return

    module = session.scalar(select(Module).where(Module.id == module_id, Module.project_id == project_id))
    if module is None:
        raise ModuleNotFoundError


def create_requirement(session: Session, data: RequirementCreate) -> Requirement:
    ensure_project_exists(session, data.project_id)
    ensure_module_belongs_to_project(session, data.project_id, data.module_id)

    requirement = Requirement(
        project_id=data.project_id,
        module_id=data.module_id,
        title=data.title,
        content=data.content,
        source_type=data.source_type,
        source_ref=data.source_ref,
    )
    session.add(requirement)
    session.commit()
    session.refresh(requirement)
    return requirement


def get_requirement(session: Session, requirement_id: uuid.UUID) -> Requirement:
    requirement = session.get(Requirement, requirement_id)
    if requirement is None:
        raise RequirementNotFoundError
    return requirement


def list_requirements(session: Session, project_id: uuid.UUID) -> list[Requirement]:
    ensure_project_exists(session, project_id)
    return list(
        session.scalars(
            select(Requirement)
            .where(Requirement.project_id == project_id)
            .order_by(Requirement.created_at.asc(), Requirement.title.asc(), Requirement.id.asc()),
        ),
    )
