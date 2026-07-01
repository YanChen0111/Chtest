from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.modules.cases.models import json_dict_column
from backend.app.modules.execution.models import uuid_list_column
from backend.app.modules.projects.models import Project, TimestampMixin, uuid_pk


class ReviewHistory(TimestampMixin, Base):
    __tablename__ = "review_history"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    related_entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    related_entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reviewer: Mapped[str] = mapped_column(String(120), nullable=False, default="Default User")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_artifact_ids: Mapped[list[uuid.UUID]] = uuid_list_column()
    metadata_json: Mapped[dict[str, Any]] = json_dict_column()

    project: Mapped[Project] = relationship()
