from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, TypeDecorator

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.projects.models import Module, Project, TimestampMixin, uuid_pk
from backend.app.modules.requirements.models import Requirement, RequirementReview


class StringListJSON(TypeDecorator[list[str]]):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(String()))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: list[str] | None, dialect) -> list[str]:
        if value is None:
            return []
        return [str(item) for item in value]

    def process_result_value(self, value: list[str] | None, dialect) -> list[str]:
        if value is None:
            return []
        return [str(item) for item in value]


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


def string_list_column() -> Mapped[list[str]]:
    return mapped_column(MutableList.as_mutable(StringListJSON), default=list, nullable=False)


class CaseGenerationTask(TimestampMixin, Base):
    __tablename__ = "case_generation_tasks"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requirements.id", ondelete="CASCADE"),
        nullable=False,
    )
    requirement_review_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requirement_reviews.id", ondelete="SET NULL"),
        nullable=True,
    )
    ai_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_test_types: Mapped[list[str]] = string_list_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="created")
    generated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    project: Mapped[Project] = relationship()
    requirement: Mapped[Requirement] = relationship()
    requirement_review: Mapped[RequirementReview | None] = relationship()
    ai_task: Mapped[AITask] = relationship()
    candidates: Mapped[list[GeneratedCaseCandidate]] = relationship(
        back_populates="generation_task",
        cascade="all, delete-orphan",
    )


class GeneratedCaseCandidate(TimestampMixin, Base):
    __tablename__ = "generated_case_candidates"

    id: Mapped[uuid.UUID] = uuid_pk()
    generation_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("case_generation_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    module_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("modules.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="P2")
    test_type: Mapped[str] = mapped_column(String(40), nullable=False, default="functional")
    precondition: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps_json: Mapped[list[Any]] = json_list_column()
    expected_results_json: Mapped[list[Any]] = json_list_column()
    input_data_json: Mapped[dict[str, Any]] = json_dict_column()
    tags: Mapped[list[str]] = string_list_column()
    requirement_refs_json: Mapped[list[Any]] = json_list_column()
    risk_refs_json: Mapped[list[Any]] = json_list_column()
    ai_reason: Mapped[str] = mapped_column(Text, nullable=False)
    duplicate_of_case_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_cases.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="generated")
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    generation_task: Mapped[CaseGenerationTask] = relationship(back_populates="candidates")
    project: Mapped[Project] = relationship()
    module: Mapped[Module | None] = relationship()
    duplicate_of_case: Mapped[TestCase | None] = relationship(foreign_keys=[duplicate_of_case_id])


class TestCase(TimestampMixin, Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    module_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("modules.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("generated_case_candidates.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="P2")
    test_type: Mapped[str] = mapped_column(String(40), nullable=False, default="functional")
    precondition: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps_json: Mapped[list[Any]] = json_list_column()
    expected_results_json: Mapped[list[Any]] = json_list_column()
    input_data_json: Mapped[dict[str, Any]] = json_dict_column()
    tags: Mapped[list[str]] = string_list_column()
    source_type: Mapped[str] = mapped_column(String(40), nullable=False, default="ai")
    review_status: Mapped[str] = mapped_column(String(40), nullable=False, default="approved")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project] = relationship()
    module: Mapped[Module | None] = relationship()
    source_candidate: Mapped[GeneratedCaseCandidate | None] = relationship(foreign_keys=[source_candidate_id])
