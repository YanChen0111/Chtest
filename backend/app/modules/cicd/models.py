from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.modules.cases.models import json_list_column
from backend.app.modules.projects.models import Project, Repository, TimestampMixin, uuid_pk


class CICDRun(TimestampMixin, Base):
    __tablename__ = "cicd_runs"

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
    source_type: Mapped[str] = mapped_column(String(40), nullable=False, default="local_diff")
    trigger_type: Mapped[str] = mapped_column(String(40), nullable=False, default="manual")
    provider: Mapped[str] = mapped_column(String(40), nullable=False, default="local")
    pipeline_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    base_ref: Mapped[str | None] = mapped_column(String(160), nullable=True)
    head_ref: Mapped[str | None] = mapped_column(String(160), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_risk: Mapped[str] = mapped_column(String(40), nullable=False, default="medium")
    quality_gate_status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="created")

    project: Mapped[Project] = relationship()
    repository: Mapped[Repository | None] = relationship()
    changed_files: Mapped[list[CICDChangedFile]] = relationship(
        back_populates="cicd_run",
        cascade="all, delete-orphan",
    )


class CICDChangedFile(TimestampMixin, Base):
    __tablename__ = "cicd_changed_files"

    id: Mapped[uuid.UUID] = uuid_pk()
    cicd_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cicd_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    path: Mapped[str] = mapped_column(Text, nullable=False)
    old_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_type: Mapped[str] = mapped_column(String(40), nullable=False, default="modified")
    language: Mapped[str | None] = mapped_column(String(60), nullable=True)
    file_role: Mapped[str] = mapped_column(String(60), nullable=False, default="unknown")
    risk_level: Mapped[str] = mapped_column(String(40), nullable=False, default="medium")
    risk_reasons_json: Mapped[list[str]] = json_list_column()
    lines_added: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lines_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    cicd_run: Mapped[CICDRun] = relationship(back_populates="changed_files")
