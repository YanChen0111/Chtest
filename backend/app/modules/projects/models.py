from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.app.models.base import Base


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


def json_dict_column() -> Mapped[dict[str, Any]]:
    return mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)


class Workspace(TimestampMixin, Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    projects: Mapped[list[Project]] = relationship(back_populates="workspace")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    username: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False, default="Default User")
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")


class Project(TimestampMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="uq_projects_workspace_name"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_language: Mapped[str | None] = mapped_column(String(60), nullable=True, default="python")
    default_test_type: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
        default="functional",
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    workspace: Mapped[Workspace] = relationship(back_populates="projects")
    modules: Mapped[list[Module]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    repositories: Mapped[list[Repository]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    environments: Mapped[list[Environment]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    test_commands: Mapped[list[TestCommand]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Module(TimestampMixin, Base):
    __tablename__ = "modules"
    __table_args__ = (
        UniqueConstraint("project_id", "parent_id", "name", name="uq_modules_project_parent_name"),
        CheckConstraint("level >= 1 AND level <= 5", name="ck_modules_level_1_5"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    path: Mapped[str] = mapped_column(String(800), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project] = relationship(back_populates="modules")
    parent: Mapped[Module | None] = relationship(
        remote_side="Module.id",
        back_populates="children",
    )
    children: Mapped[list[Module]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
    )


class Repository(TimestampMixin, Base):
    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_repositories_project_name"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    local_path: Mapped[str] = mapped_column(Text, nullable=False)
    default_base_branch: Mapped[str | None] = mapped_column(String(120), nullable=True, default="main")
    language_hint: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project] = relationship(back_populates="repositories")
    test_commands: Mapped[list[TestCommand]] = relationship(back_populates="repository")


class Environment(TimestampMixin, Base):
    __tablename__ = "environments"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_environments_project_name"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="dev")
    variables_json: Mapped[dict[str, Any]] = json_dict_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project] = relationship(back_populates="environments")
    test_commands: Mapped[list[TestCommand]] = relationship(back_populates="environment")


class TestCommand(TimestampMixin, Base):
    __tablename__ = "test_commands"
    __test__ = False
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_test_commands_project_name"),
        CheckConstraint("timeout_seconds > 0", name="ck_test_commands_timeout_positive"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("repositories.id", ondelete="SET NULL"),
        nullable=True,
    )
    environment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("environments.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)
    working_directory: Mapped[str] = mapped_column(Text, nullable=False)
    command_type: Mapped[str] = mapped_column(String(40), nullable=False, default="pytest")
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=600)
    parse_junit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    parse_coverage: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project] = relationship(back_populates="test_commands")
    repository: Mapped[Repository | None] = relationship(back_populates="test_commands")
    environment: Mapped[Environment | None] = relationship(back_populates="test_commands")
