from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.app.models.base import Base
from backend.app.modules.projects.models import Environment, Project, TimestampMixin, uuid_pk


def json_list_column() -> Mapped[list[Any]]:
    return mapped_column(
        MutableList.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=list,
        nullable=False,
    )


class TestCampaign(TimestampMixin, Base):
    __tablename__ = "test_campaigns"
    __test__ = False
    __table_args__ = (
        Index("ix_test_campaigns_project_status", "project_id", "status"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    scope_statement: Mapped[str] = mapped_column(Text, nullable=False)
    target_environment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("environments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    target_version_ref: Mapped[str] = mapped_column(String(160), nullable=False)
    exit_conditions_json: Mapped[list[Any]] = json_list_column()
    requirement_ids_json: Mapped[list[Any]] = json_list_column()
    risk_ids_json: Mapped[list[Any]] = json_list_column()
    test_plan_snapshot_ids_json: Mapped[list[Any]] = json_list_column()
    approved_case_ids_json: Mapped[list[Any]] = json_list_column()
    coverage_rows_json: Mapped[list[Any]] = json_list_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project] = relationship()
    target_environment: Mapped[Environment] = relationship()
