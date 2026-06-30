from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
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
