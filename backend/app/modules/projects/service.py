from __future__ import annotations

import os
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from backend.app.modules.projects.models import Environment, Module, Project, Repository, Workspace
from backend.app.modules.projects.schemas import (
    EnvironmentCreate,
    EnvironmentUpdate,
    ModuleCreate,
    ModuleUpdate,
    ProjectCreate,
    ProjectUpdate,
    RepositoryCreate,
    RepositoryUpdate,
)


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


class RepositoryAlreadyExistsError(Exception):
    pass


class RepositoryNotFoundError(Exception):
    pass


class RepositoryPathNotAllowedError(Exception):
    pass


class EnvironmentAlreadyExistsError(Exception):
    pass


class EnvironmentNotFoundError(Exception):
    pass


class EnvironmentSecretNotAllowedError(Exception):
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


def repository_allowlist_roots() -> list[Path]:
    raw_roots = os.getenv("CHTEST_REPOSITORY_ALLOWLIST_ROOTS", "")
    return [Path(raw).expanduser().resolve() for raw in raw_roots.split(os.pathsep) if raw.strip()]


def validate_repository_path(local_path: str) -> str:
    path = Path(local_path).expanduser()
    if not path.exists():
        raise RepositoryPathNotAllowedError

    resolved_path = path.resolve()
    allowed_roots = repository_allowlist_roots()
    if not allowed_roots:
        raise RepositoryPathNotAllowedError

    if not any(resolved_path == root or root in resolved_path.parents for root in allowed_roots):
        raise RepositoryPathNotAllowedError

    return str(resolved_path)


def create_repository(session: Session, data: RepositoryCreate) -> Repository:
    project = get_project(session, data.project_id)
    if project is None:
        raise ModuleNotFoundError

    local_path = validate_repository_path(data.local_path)
    repository = Repository(
        project_id=data.project_id,
        name=data.name,
        local_path=local_path,
        default_base_branch=data.default_base_branch,
        language_hint=data.language_hint,
    )
    session.add(repository)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise RepositoryAlreadyExistsError from exc
    session.refresh(repository)
    return repository


def list_repositories(session: Session, project_id: uuid.UUID) -> list[Repository]:
    project = get_project(session, project_id)
    if project is None:
        raise ModuleNotFoundError

    return list(
        session.scalars(
            select(Repository)
            .where(Repository.project_id == project_id)
            .order_by(Repository.created_at.asc()),
        ),
    )


def update_repository(session: Session, repository_id: uuid.UUID, data: RepositoryUpdate) -> Repository:
    repository = session.get(Repository, repository_id)
    if repository is None:
        raise RepositoryNotFoundError

    updates = data.model_dump(exclude_unset=True)
    if "name" in updates:
        repository.name = updates["name"]
    if "local_path" in updates:
        repository.local_path = validate_repository_path(updates["local_path"])
    if "default_base_branch" in updates:
        repository.default_base_branch = updates["default_base_branch"]
    if "language_hint" in updates:
        repository.language_hint = updates["language_hint"]
    if "status" in updates:
        repository.status = updates["status"]

    session.add(repository)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise RepositoryAlreadyExistsError from exc
    session.refresh(repository)
    return repository


def create_environment(session: Session, data: EnvironmentCreate) -> Environment:
    project = get_project(session, data.project_id)
    if project is None:
        raise ModuleNotFoundError

    validate_environment_variables(data.variables_json)
    environment = Environment(
        project_id=data.project_id,
        name=data.name,
        variables_json=data.variables_json,
    )
    session.add(environment)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise EnvironmentAlreadyExistsError from exc
    session.refresh(environment)
    return environment


def list_environments(session: Session, project_id: uuid.UUID) -> list[Environment]:
    project = get_project(session, project_id)
    if project is None:
        raise ModuleNotFoundError

    return list(
        session.scalars(
            select(Environment)
            .where(Environment.project_id == project_id)
            .order_by(Environment.created_at.asc()),
        ),
    )


def update_environment(session: Session, environment_id: uuid.UUID, data: EnvironmentUpdate) -> Environment:
    environment = session.get(Environment, environment_id)
    if environment is None:
        raise EnvironmentNotFoundError

    updates = data.model_dump(exclude_unset=True)
    if "variables_json" in updates:
        validate_environment_variables(updates["variables_json"])

    for field, value in updates.items():
        setattr(environment, field, value)

    session.add(environment)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise EnvironmentAlreadyExistsError from exc
    session.refresh(environment)
    return environment


def validate_environment_variables(variables: dict[str, object]) -> None:
    secret_markers = ("password", "token", "secret", "credential", "api_key")
    for key, value in variables.items():
        key_lower = key.lower()
        if not any(marker in key_lower for marker in secret_markers):
            continue
        if isinstance(value, str) and value.startswith("ref:"):
            continue
        raise EnvironmentSecretNotAllowedError
