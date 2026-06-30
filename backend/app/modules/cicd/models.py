from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.cases.models import json_dict_column, json_list_column
from backend.app.modules.execution.models import uuid_list_column
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


class UnitTestPatch(TimestampMixin, Base):
    __tablename__ = "unit_test_patches"

    id: Mapped[uuid.UUID] = uuid_pk()
    cicd_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cicd_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    ai_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    patch_text: Mapped[str] = mapped_column(Text, nullable=False)
    target_framework: Mapped[str] = mapped_column(String(60), nullable=False, default="pytest")
    scope_gate_result_json: Mapped[dict[str, Any]] = json_dict_column()
    test_intent: Mapped[str] = mapped_column(Text, nullable=False)
    coverage_target_json: Mapped[list[Any]] = json_list_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="generated")
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    cicd_run: Mapped[CICDRun] = relationship()
    ai_task: Mapped[AITask] = relationship()


class QualityGateDecision(TimestampMixin, Base):
    __tablename__ = "quality_gate_decisions"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    cicd_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cicd_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="needs_review")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    blocking_reasons_json: Mapped[list[Any]] = json_list_column()
    evidence_artifact_ids: Mapped[list[uuid.UUID]] = uuid_list_column()
    decided_by: Mapped[str] = mapped_column(String(40), nullable=False, default="system")
    status_detail_json: Mapped[dict[str, Any]] = json_dict_column()

    project: Mapped[Project] = relationship()
    cicd_run: Mapped[CICDRun] = relationship()
