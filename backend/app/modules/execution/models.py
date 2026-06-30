from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, TypeDecorator

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cases.models import json_dict_column
from backend.app.modules.projects.models import Project, TestCommand, TimestampMixin, uuid_pk


class UUIDListJSON(TypeDecorator[list[uuid.UUID]]):
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: list[uuid.UUID] | None, dialect) -> list[str]:
        if value is None:
            return []
        return [str(item) for item in value]

    def process_result_value(self, value: list[str] | None, dialect) -> list[uuid.UUID]:
        if value is None:
            return []
        return [uuid.UUID(str(item)) for item in value]


def uuid_list_column() -> Mapped[list[uuid.UUID]]:
    return mapped_column(MutableList.as_mutable(UUIDListJSON), default=list, nullable=False)


class TestRun(TimestampMixin, Base):
    __tablename__ = "test_runs"
    __test__ = False

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    cicd_run_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    automation_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("automation_drafts.id", ondelete="SET NULL"),
        nullable=True,
    )
    test_command_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_commands.id", ondelete="SET NULL"),
        nullable=True,
    )
    tool_invocation_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)
    working_directory: Mapped[str] = mapped_column(Text, nullable=False)
    runner_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="local_subprocess")
    run_workspace: Mapped[str | None] = mapped_column(Text, nullable=True)
    repository_readonly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    network_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    runtime_artifact_ids: Mapped[list[uuid.UUID]] = uuid_list_column()
    dependency_snapshot_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    environment_snapshot_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="created")
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parsed_result_json: Mapped[dict[str, Any]] = json_dict_column()

    project: Mapped[Project] = relationship()
    automation_draft: Mapped[AutomationDraft | None] = relationship()
    test_command: Mapped[TestCommand | None] = relationship()
    dependency_snapshot_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[dependency_snapshot_artifact_id])
    environment_snapshot_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[environment_snapshot_artifact_id])
    test_results: Mapped[list[TestResult]] = relationship(
        back_populates="test_run",
        cascade="all, delete-orphan",
    )


class TestResult(TimestampMixin, Base):
    __tablename__ = "test_results"
    __test__ = False

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_name: Mapped[str] = mapped_column(Text, nullable=False)
    test_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="passed")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failure_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_artifact_ids: Mapped[list[uuid.UUID]] = uuid_list_column()
    metadata_json: Mapped[dict[str, Any]] = json_dict_column()

    project: Mapped[Project] = relationship()
    test_run: Mapped[TestRun] = relationship(back_populates="test_results")
