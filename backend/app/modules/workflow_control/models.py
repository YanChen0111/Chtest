from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    event,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from backend.app.models.base import Base
from backend.app.modules.projects.models import TimestampMixin, uuid_pk


def json_list_column() -> Mapped[list[str]]:
    return mapped_column(
        MutableList.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=list,
        nullable=False,
    )


def json_dict_column() -> Mapped[dict[str, Any]]:
    return mapped_column(
        MutableDict.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=dict,
        nullable=False,
    )


class WorkflowRun(TimestampMixin, Base):
    __tablename__ = "workflow_runs"
    __table_args__ = (
        UniqueConstraint("project_id", "id", name="uq_workflow_runs_project_id"),
        CheckConstraint("lock_version >= 0", name="ck_workflow_runs_lock_version"),
        Index("ix_workflow_runs_project_subject", "project_id", "workflow_kind", "subject_ref"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    workflow_kind: Mapped[str] = mapped_column(String(80), nullable=False)
    subject_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    current_stage: Mapped[str] = mapped_column(String(80), nullable=False)
    gate_state: Mapped[str] = mapped_column(String(40), nullable=False)
    input_snapshot_hash: Mapped[str] = mapped_column(String(71), nullable=False)
    current_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    completed_stages_json: Mapped[list[str]] = json_list_column()
    lock_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")


class WorkflowStageSnapshot(Base):
    __tablename__ = "workflow_stage_snapshots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id"],
            ["workflow_runs.project_id", "workflow_runs.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "previous_snapshot_id"],
            [
                "workflow_stage_snapshots.project_id",
                "workflow_stage_snapshots.workflow_run_id",
                "workflow_stage_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "project_id",
            "workflow_run_id",
            "id",
            name="uq_workflow_stage_snapshots_project_run_id",
        ),
        UniqueConstraint(
            "workflow_run_id",
            "stage",
            "stage_iteration",
            name="uq_workflow_stage_snapshots_run_stage_iteration",
        ),
        CheckConstraint("stage_iteration > 0", name="ck_workflow_stage_snapshots_iteration"),
        Index("ix_workflow_stage_snapshots_project_run", "project_id", "workflow_run_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    stage: Mapped[str] = mapped_column(String(80), nullable=False)
    stage_iteration: Mapped[int] = mapped_column(Integer, nullable=False)
    input_snapshot_hash: Mapped[str] = mapped_column(String(71), nullable=False)
    input_payload_json: Mapped[dict[str, Any]] = json_dict_column()
    previous_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    created_by_actor: Mapped[str] = mapped_column(String(40), nullable=False)
    created_by_label: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class WorkflowHumanDecision(Base):
    __tablename__ = "workflow_human_decisions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id"],
            ["workflow_runs.project_id", "workflow_runs.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "snapshot_id"],
            [
                "workflow_stage_snapshots.project_id",
                "workflow_stage_snapshots.workflow_run_id",
                "workflow_stage_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "workflow_run_id",
            "snapshot_id",
            "action",
            name="uq_workflow_human_decisions_run_snapshot_action",
        ),
        UniqueConstraint(
            "project_id",
            "workflow_run_id",
            "id",
            name="uq_workflow_human_decisions_project_run_id",
        ),
        CheckConstraint(
            "action != 'approve' OR "
            "(decision = 'approved' AND allowed_action = 'advance' "
            "AND grant_fingerprint IS NOT NULL)",
            name="ck_workflow_human_decisions_approval_grant",
        ),
        Index("ix_workflow_human_decisions_project_run", "project_id", "workflow_run_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    stage: Mapped[str] = mapped_column(String(80), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    decision: Mapped[str] = mapped_column(String(40), nullable=False)
    allowed_action: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reviewer: Mapped[str] = mapped_column(String(120), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    grant_fingerprint: Mapped[str | None] = mapped_column(String(71), nullable=True)
    source_run_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class WorkflowTransitionEvent(Base):
    __tablename__ = "workflow_transition_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id"],
            ["workflow_runs.project_id", "workflow_runs.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "source_snapshot_id"],
            [
                "workflow_stage_snapshots.project_id",
                "workflow_stage_snapshots.workflow_run_id",
                "workflow_stage_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "target_snapshot_id"],
            [
                "workflow_stage_snapshots.project_id",
                "workflow_stage_snapshots.workflow_run_id",
                "workflow_stage_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "human_decision_id"],
            [
                "workflow_human_decisions.project_id",
                "workflow_human_decisions.workflow_run_id",
                "workflow_human_decisions.id",
            ],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "consumed_approval_decision_id"],
            [
                "workflow_human_decisions.project_id",
                "workflow_human_decisions.workflow_run_id",
                "workflow_human_decisions.id",
            ],
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "workflow_run_id",
            "result_run_version",
            name="uq_workflow_transition_events_run_version",
        ),
        UniqueConstraint(
            "consumed_approval_decision_id",
            name="uq_workflow_transition_events_consumed_approval",
        ),
        Index("ix_workflow_transition_events_project_run", "project_id", "workflow_run_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    actor: Mapped[str] = mapped_column(String(40), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    from_stage: Mapped[str] = mapped_column(String(80), nullable=False)
    from_state: Mapped[str] = mapped_column(String(40), nullable=False)
    to_stage: Mapped[str] = mapped_column(String(80), nullable=False)
    to_state: Mapped[str] = mapped_column(String(40), nullable=False)
    source_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    target_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    human_decision_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    consumed_approval_decision_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    grant_fingerprint: Mapped[str | None] = mapped_column(String(71), nullable=True)
    source_run_version: Mapped[int] = mapped_column(Integer, nullable=False)
    result_run_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


def _prevent_immutable_change(*_args: object) -> None:
    raise ValueError("WORKFLOW_EVIDENCE_IMMUTABLE")


for _model in (WorkflowStageSnapshot, WorkflowHumanDecision, WorkflowTransitionEvent):
    event.listen(_model, "before_update", _prevent_immutable_change)
    event.listen(_model, "before_delete", _prevent_immutable_change)
