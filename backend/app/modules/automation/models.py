from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, TypeDecorator

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.cases.models import GeneratedCaseCandidate, TestCase
from backend.app.modules.projects.models import Project, TimestampMixin, uuid_pk
from backend.app.modules.requirements.models import Requirement, RequirementReview


class UUIDListJSON(TypeDecorator[list[uuid.UUID]]):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(postgresql.UUID(as_uuid=True)))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: list[uuid.UUID | str] | None, dialect) -> list[str | uuid.UUID]:
        if value is None:
            return []
        if dialect.name == "postgresql":
            return [uuid.UUID(str(item)) for item in value]
        return [str(item) for item in value]

    def process_result_value(self, value: list[str | uuid.UUID] | None, dialect) -> list[uuid.UUID]:
        if value is None:
            return []
        return [uuid.UUID(str(item)) for item in value]


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


def uuid_list_column() -> Mapped[list[uuid.UUID]]:
    return mapped_column(MutableList.as_mutable(UUIDListJSON), default=list, nullable=False)


class AutomationPlan(TimestampMixin, Base):
    __tablename__ = "automation_plans"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requirements.id", ondelete="SET NULL"),
        nullable=True,
    )
    requirement_review_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requirement_reviews.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("generated_case_candidates.id", ondelete="SET NULL"),
        nullable=True,
    )
    ai_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    knowledge_retrieval_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    target_framework: Mapped[str] = mapped_column(String(60), nullable=False, default="pytest")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    plan_json: Mapped[dict[str, Any]] = json_dict_column()
    execution_steps_json: Mapped[list[Any]] = json_list_column()
    test_data_json: Mapped[dict[str, Any]] = json_dict_column()
    dependency_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    used_context_artifact_ids: Mapped[list[uuid.UUID]] = uuid_list_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="plan_generated")
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[Project] = relationship()
    test_case: Mapped[TestCase] = relationship()
    requirement: Mapped[Requirement | None] = relationship()
    requirement_review: Mapped[RequirementReview | None] = relationship()
    source_candidate: Mapped[GeneratedCaseCandidate | None] = relationship()
    ai_task: Mapped[AITask] = relationship()
    knowledge_retrieval_artifact: Mapped[Artifact | None] = relationship()
    drafts: Mapped[list[AutomationDraft]] = relationship(back_populates="automation_plan")


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
    automation_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("automation_plans.id", ondelete="SET NULL"),
        nullable=True,
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
    automation_plan: Mapped[AutomationPlan | None] = relationship(back_populates="drafts")
    runtime_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[runtime_artifact_id])
    promoted_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[promoted_artifact_id])
