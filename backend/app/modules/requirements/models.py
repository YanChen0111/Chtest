from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.projects.models import Module, Project, TimestampMixin, uuid_pk


def json_list_column() -> Mapped[list[Any]]:
    return mapped_column(
        MutableList.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=list,
        nullable=False,
    )


SCORE_CHECKS = tuple(
    CheckConstraint(f"{column_name} >= 0 AND {column_name} <= 100", name=f"ck_requirement_reviews_{column_name}_0_100")
    for column_name in (
        "completeness_score",
        "clarity_score",
        "consistency_score",
        "testability_score",
        "feasibility_score",
        "logic_score",
        "overall_score",
    )
)


class Requirement(TimestampMixin, Base):
    __tablename__ = "requirements"

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
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(40), nullable=False, default="manual")
    source_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project] = relationship()
    module: Mapped[Module | None] = relationship()
    reviews: Mapped[list[RequirementReview]] = relationship(
        back_populates="requirement",
        cascade="all, delete-orphan",
    )


class RequirementReview(TimestampMixin, Base):
    __tablename__ = "requirement_reviews"
    __table_args__ = SCORE_CHECKS

    id: Mapped[uuid.UUID] = uuid_pk()
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requirements.id", ondelete="CASCADE"),
        nullable=False,
    )
    ai_task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    completeness_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clarity_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consistency_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    testability_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    feasibility_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    logic_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    issues_json: Mapped[list[Any]] = json_list_column()
    clarification_questions_json: Mapped[list[Any]] = json_list_column()
    test_design_notes_json: Mapped[list[Any]] = json_list_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")

    requirement: Mapped[Requirement] = relationship(back_populates="reviews")
    ai_task: Mapped[AITask] = relationship()
    risk_items: Mapped[list[RiskItem]] = relationship(
        back_populates="requirement_review",
    )


class RiskItem(TimestampMixin, Base):
    __tablename__ = "risk_items"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    requirement_review_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requirement_reviews.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(40), nullable=False, default="medium")
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="business")
    impact: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    project: Mapped[Project] = relationship()
    requirement_review: Mapped[RequirementReview | None] = relationship(back_populates="risk_items")
