from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.cases.models import json_dict_column, json_list_column
from backend.app.modules.execution.models import TestResult, TestRun, uuid_list_column
from backend.app.modules.projects.models import Project, TimestampMixin, uuid_pk


class FailureAnalysis(TimestampMixin, Base):
    __tablename__ = "failure_analyses"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_runs.id", ondelete="CASCADE"),
        nullable=True,
    )
    test_result_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_results.id", ondelete="SET NULL"),
        nullable=True,
    )
    ai_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    classification: Mapped[str] = mapped_column(String(80), nullable=False, default="insufficient_evidence")
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False, default=0)
    evidence_artifact_ids: Mapped[list[uuid.UUID]] = uuid_list_column()
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_actions_json: Mapped[list[Any]] = json_list_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")

    project: Mapped[Project] = relationship()
    test_run: Mapped[TestRun | None] = relationship()
    test_result: Mapped[TestResult | None] = relationship()
    ai_task: Mapped[AITask] = relationship()


class Report(TimestampMixin, Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    report_type: Mapped[str] = mapped_column(String(80), nullable=False, default="automation_execution")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    related_entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    related_entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    conclusion: Mapped[str | None] = mapped_column(String(80), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics_json: Mapped[dict[str, Any]] = json_dict_column()
    artifact_ids: Mapped[list[uuid.UUID]] = uuid_list_column()

    project: Mapped[Project] = relationship()
