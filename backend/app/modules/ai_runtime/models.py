from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, TypeDecorator

from backend.app.models.base import Base
from backend.app.modules.projects.models import Project, TimestampMixin, uuid_pk


class UUIDListJSON(TypeDecorator[list[uuid.UUID]]):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(postgresql.UUID(as_uuid=True)))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: list[uuid.UUID | str] | None, dialect) -> list[str]:
        if value is None:
            return []
        if dialect.name == "postgresql":
            return [uuid.UUID(str(item)) for item in value]
        return [str(item) for item in value]

    def process_result_value(self, value: list[str] | None, dialect) -> list[uuid.UUID]:
        if value is None:
            return []
        return [uuid.UUID(str(item)) for item in value]


def json_dict_column() -> Mapped[dict[str, Any]]:
    return mapped_column(
        MutableDict.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=dict,
        nullable=False,
    )


def uuid_list_column() -> Mapped[list[uuid.UUID]]:
    return mapped_column(MutableList.as_mutable(UUIDListJSON), default=list, nullable=False)


class AITask(TimestampMixin, Base):
    __tablename__ = "ai_tasks"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    agent_name: Mapped[str] = mapped_column(String(120), nullable=False)
    task_type: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_version_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    skill_version_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    model_provider: Mapped[str] = mapped_column(String(80), nullable=False, default="mock")
    model_name: Mapped[str] = mapped_column(String(120), nullable=False, default="mock-model")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="created")
    input_json: Mapped[dict[str, Any]] = json_dict_column()
    output_json: Mapped[dict[str, Any]] = json_dict_column()
    error_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    token_usage_json: Mapped[dict[str, Any]] = json_dict_column()
    context_artifact_ids: Mapped[list[uuid.UUID]] = uuid_list_column()
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[Project] = relationship()
    llm_call_logs: Mapped[list[LLMCallLog]] = relationship(
        back_populates="ai_task",
        cascade="all, delete-orphan",
    )


class Artifact(TimestampMixin, Base):
    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    owner_entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    owner_entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(80), nullable=False, default="json")
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False, default="application/json")
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    sha256: Mapped[str] = mapped_column(String(128), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = json_dict_column()

    project: Mapped[Project] = relationship()


class LLMCallLog(TimestampMixin, Base):
    __tablename__ = "llm_call_logs"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    ai_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    prompt_version_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    skill_version_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False, default="mock")
    model_name: Mapped[str] = mapped_column(String(120), nullable=False, default="mock-model")
    call_index: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="started")
    request_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    response_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    parsed_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    schema_validation_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    input_summary_json: Mapped[dict[str, Any]] = json_dict_column()
    output_summary_json: Mapped[dict[str, Any]] = json_dict_column()
    token_usage_json: Mapped[dict[str, Any]] = json_dict_column()
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[Project] = relationship()
    ai_task: Mapped[AITask] = relationship(back_populates="llm_call_logs")
    request_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[request_artifact_id])
    response_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[response_artifact_id])
    parsed_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[parsed_artifact_id])
    schema_validation_artifact: Mapped[Artifact | None] = relationship(
        foreign_keys=[schema_validation_artifact_id],
    )
