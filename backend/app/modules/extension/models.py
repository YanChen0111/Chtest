from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.app.models.base import Base
from backend.app.modules.projects.models import Project, TimestampMixin, uuid_pk


def json_dict_column() -> Mapped[dict[str, Any]]:
    return mapped_column(
        MutableDict.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=dict,
        nullable=False,
    )


def json_list_column() -> Mapped[list[Any]]:
    return mapped_column(
        MutableList.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=list,
        nullable=False,
    )


class KnowledgeAdapterConfig(TimestampMixin, Base):
    __tablename__ = "knowledge_adapter_configs"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "adapter_name",
            name="uq_knowledge_adapter_configs_project_adapter",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    adapter_name: Mapped[str] = mapped_column(String(120), nullable=False, default="default")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="not_configured")
    provider_type: Mapped[str] = mapped_column(String(80), nullable=False, default="none")
    config_json: Mapped[dict[str, Any]] = json_dict_column()
    safety_policy_json: Mapped[dict[str, Any]] = json_dict_column()
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[Project] = relationship()


class ToolDefinition(TimestampMixin, Base):
    __tablename__ = "tool_definitions"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_tool_definitions_project_name"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tool_type: Mapped[str] = mapped_column(String(80), nullable=False, default="test_runner")
    input_schema_json: Mapped[dict[str, Any]] = json_dict_column()
    output_schema_json: Mapped[dict[str, Any]] = json_dict_column()
    risk_level: Mapped[str] = mapped_column(String(40), nullable=False, default="medium")
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=600)
    command_allowlist_json: Mapped[list[Any]] = json_list_column()
    allowed_working_directories_json: Mapped[list[Any]] = json_list_column()
    forbidden_shell_operators_json: Mapped[list[Any]] = json_list_column()
    max_stdout_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=1048576)
    max_stderr_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=1048576)
    artifact_policy_json: Mapped[dict[str, Any]] = json_dict_column()
    is_mcp_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mcp_metadata_json: Mapped[dict[str, Any]] = json_dict_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project | None] = relationship()
