from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.cases.models import TestCase
from backend.app.modules.projects.models import Project, TimestampMixin, uuid_pk
from backend.app.modules.requirements.models import Requirement


class AutomationDraft(TimestampMixin, Base):
    __tablename__ = "automation_drafts"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_case_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_cases.id", ondelete="SET NULL"),
        nullable=True,
    )
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requirements.id", ondelete="SET NULL"),
        nullable=True,
    )
    ai_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_framework: Mapped[str] = mapped_column(String(60), nullable=False, default="pytest")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    draft_code: Mapped[str] = mapped_column(Text, nullable=False)
    draft_language: Mapped[str] = mapped_column(String(60), nullable=False, default="python")
    suggested_file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_strategy: Mapped[str] = mapped_column(String(60), nullable=False, default="artifact_runtime_copy")
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft_generated")
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    runtime_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    promoted_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )

    project: Mapped[Project] = relationship()
    test_case: Mapped[TestCase | None] = relationship()
    requirement: Mapped[Requirement | None] = relationship()
    ai_task: Mapped[AITask] = relationship()
    runtime_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[runtime_artifact_id])
    promoted_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[promoted_artifact_id])
