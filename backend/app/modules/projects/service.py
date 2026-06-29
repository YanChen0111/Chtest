from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from backend.app.modules.projects.models import Module, Project, Workspace
from backend.app.modules.projects.schemas import ModuleCreate, ModuleUpdate, ProjectCreate, ProjectUpdate


DEFAULT_WORKSPACE_NAME = "Personal Workspace"


class ProjectAlreadyExistsError(Exception):
    pass


class ModuleAlreadyExistsError(Exception):
    pass


class ModuleLevelLimitExceededError(Exception):
    pass


class ModuleParentNotFoundError(Exception):
    pass


class ModuleNotFoundError(Exception):
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


def module_path(parent: Module | None, name: str) -> str:
    if parent is None:
        return f"/{name}"
    return f"{parent.path}/{name}"


def ensure_module_name_available(
    session: Session,
    project_id: uuid.UUID,
    parent_id: uuid.UUID | None,
    name: str,
    exclude_module_id: uuid.UUID | None = None,
) -> None:
    statement = select(Module).where(
        Module.project_id == project_id,
        Module.parent_id == parent_id,
        Module.name == name,
    )
    if exclude_module_id is not None:
        statement = statement.where(Module.id != exclude_module_id)

    if session.scalar(statement) is not None:
        raise ModuleAlreadyExistsError


def create_module(session: Session, project_id: uuid.UUID, data: ModuleCreate) -> Module:
    project = get_project(session, project_id)
    if project is None:
        raise ModuleNotFoundError

    parent: Module | None = None
    level = 1
    if data.parent_id is not None:
        parent = session.scalar(
            select(Module).where(Module.id == data.parent_id, Module.project_id == project_id),
        )
        if parent is None:
            raise ModuleParentNotFoundError
        level = parent.level + 1

    if level > 5:
        raise ModuleLevelLimitExceededError

    ensure_module_name_available(session, project_id, data.parent_id, data.name)
    module = Module(
        project_id=project_id,
        parent_id=data.parent_id,
        name=data.name,
        level=level,
        path=module_path(parent, data.name),
        sort_order=data.sort_order,
    )
    session.add(module)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise ModuleAlreadyExistsError from exc
    session.refresh(module)
    return module


def list_modules(session: Session, project_id: uuid.UUID) -> list[Module]:
    project = get_project(session, project_id)
    if project is None:
        raise ModuleNotFoundError

    return list(
        session.scalars(
            select(Module)
            .where(Module.project_id == project_id)
            .order_by(Module.level.asc(), Module.sort_order.asc(), Module.created_at.asc()),
        ),
    )


def update_module(
    session: Session,
    project_id: uuid.UUID,
    module_id: uuid.UUID,
    data: ModuleUpdate,
) -> Module:
    module = session.scalar(select(Module).where(Module.id == module_id, Module.project_id == project_id))
    if module is None:
        raise ModuleNotFoundError

    updates = data.model_dump(exclude_unset=True)
    new_name = updates.get("name", module.name)
    if new_name != module.name:
        ensure_module_name_available(session, project_id, module.parent_id, new_name, module.id)
        parent = session.get(Module, module.parent_id) if module.parent_id is not None else None
        module.name = new_name
        module.path = module_path(parent, new_name)
        refresh_descendant_paths(session, project_id, module)

    if "sort_order" in updates:
        module.sort_order = updates["sort_order"]
    if "status" in updates:
        module.status = updates["status"]

    session.add(module)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise ModuleAlreadyExistsError from exc
    session.refresh(module)
    return module


def refresh_descendant_paths(session: Session, project_id: uuid.UUID, parent: Module) -> None:
    children = list(
        session.scalars(
            select(Module)
            .where(Module.project_id == project_id, Module.parent_id == parent.id)
            .order_by(Module.sort_order.asc(), Module.created_at.asc()),
        ),
    )
    for child in children:
        child.path = module_path(parent, child.name)
        session.add(child)
        refresh_descendant_paths(session, project_id, child)
