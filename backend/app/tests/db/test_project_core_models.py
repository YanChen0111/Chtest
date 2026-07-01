from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.base import Base
from backend.app.modules.projects.models import (
    Environment,
    Module,
    Project,
    Repository,
    TestCommand,
    Workspace,
)


MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260626_0001_project_core.py"


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def load_project_core_migration():
    spec = importlib.util.spec_from_file_location("project_core_migration", MIGRATION_PATH)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def test_project_core_migration_creates_contract_tables() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    migration = load_project_core_migration()

    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        operations = Operations(context)
        original_op = migration.op
        migration.op = operations
        try:
            migration.upgrade()
        finally:
            migration.op = original_op

        tables = set(inspect(connection).get_table_names())

    assert {
        "workspaces",
        "users",
        "projects",
        "modules",
        "repositories",
        "environments",
        "test_commands",
    }.issubset(tables)


def test_project_core_models_persist_project_context(session: Session) -> None:
    workspace = Workspace(name="Personal Workspace")
    project = Project(
        workspace=workspace,
        name="Checkout System",
        description="Sample checkout evidence project",
        default_language="python",
        default_test_type="functional",
    )
    module = Module(
        project=project,
        name="Coupon",
        level=1,
        path="/coupon",
        sort_order=10,
    )
    repository = Repository(
        project=project,
        name="sample-checkout",
        local_path="/Users/yanchen/VscodeProject/sample-checkout",
        default_base_branch="main",
        language_hint="python",
    )
    environment = Environment(
        project=project,
        name="local",
        variables_json={"BASE_URL": "http://localhost:8000"},
    )
    test_command = TestCommand(
        project=project,
        repository=repository,
        environment=environment,
        name="pytest unit",
        command="pytest tests -q --junitxml=artifacts/junit.xml",
        working_directory="/Users/yanchen/VscodeProject/sample-checkout",
        command_type="pytest",
        timeout_seconds=600,
        parse_junit=True,
        parse_coverage=False,
    )

    session.add(test_command)
    session.commit()
    session.refresh(project)

    assert project.id is not None
    assert project.status == "active"
    assert project.modules == [module]
    assert project.repositories == [repository]
    assert project.environments == [environment]
    assert project.test_commands == [test_command]
    assert test_command.repository is repository
    assert test_command.environment is environment


def test_module_tree_keeps_parent_project_and_five_level_contract(session: Session) -> None:
    workspace = Workspace(name="Personal Workspace")
    project = Project(workspace=workspace, name="Checkout System")
    root = Module(project=project, name="Checkout", level=1, path="/checkout")
    child = Module(
        project=project,
        parent=root,
        name="Coupon",
        level=2,
        path="/checkout/coupon",
    )

    session.add(child)
    session.commit()

    assert child.parent is root
    assert child.project is project
    assert child.level == 2


def test_project_names_are_unique_inside_workspace(session: Session) -> None:
    workspace_id = uuid.uuid4()
    first = Project(workspace_id=workspace_id, name="Checkout System")
    duplicate = Project(workspace_id=workspace_id, name="Checkout System")

    session.add_all([first, duplicate])

    with pytest.raises(IntegrityError):
        session.commit()
