"""add human-controlled workflow persistence

Revision ID: 20260728_0019
Revises: 20260716_0018
Create Date: 2026-07-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260728_0019"
down_revision = "20260716_0018"
branch_labels = None
depends_on = None


def json_type() -> sa.TypeEngine:
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_kind", sa.String(length=80), nullable=False),
        sa.Column("subject_ref", sa.String(length=255), nullable=False),
        sa.Column("current_stage", sa.String(length=80), nullable=False),
        sa.Column("gate_state", sa.String(length=40), nullable=False),
        sa.Column("input_snapshot_hash", sa.String(length=71), nullable=False),
        sa.Column("current_snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("completed_stages_json", json_type(), server_default="[]", nullable=False),
        sa.Column("lock_version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.CheckConstraint("lock_version >= 0", name="ck_workflow_runs_lock_version"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "id", name="uq_workflow_runs_project_id"),
    )
    op.create_index(
        "ix_workflow_runs_project_subject",
        "workflow_runs",
        ["project_id", "workflow_kind", "subject_ref"],
    )

    op.create_table(
        "workflow_stage_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("stage", sa.String(length=80), nullable=False),
        sa.Column("stage_iteration", sa.Integer(), nullable=False),
        sa.Column("input_snapshot_hash", sa.String(length=71), nullable=False),
        sa.Column("input_payload_json", json_type(), nullable=False),
        sa.Column("previous_snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("created_by_actor", sa.String(length=40), nullable=False),
        sa.Column("created_by_label", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("stage_iteration > 0", name="ck_workflow_stage_snapshots_iteration"),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id"],
            ["workflow_runs.project_id", "workflow_runs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "previous_snapshot_id"],
            [
                "workflow_stage_snapshots.project_id",
                "workflow_stage_snapshots.workflow_run_id",
                "workflow_stage_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "workflow_run_id",
            "id",
            name="uq_workflow_stage_snapshots_project_run_id",
        ),
        sa.UniqueConstraint(
            "workflow_run_id",
            "stage",
            "stage_iteration",
            name="uq_workflow_stage_snapshots_run_stage_iteration",
        ),
    )
    op.create_index(
        "ix_workflow_stage_snapshots_project_run",
        "workflow_stage_snapshots",
        ["project_id", "workflow_run_id"],
    )

    op.create_table(
        "workflow_human_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("stage", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("decision", sa.String(length=40), nullable=False),
        sa.Column("allowed_action", sa.String(length=80), nullable=True),
        sa.Column("reviewer", sa.String(length=120), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("grant_fingerprint", sa.String(length=71), nullable=True),
        sa.Column("source_run_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "action != 'approve' OR "
            "(decision = 'approved' AND allowed_action = 'advance' "
            "AND grant_fingerprint IS NOT NULL)",
            name="ck_workflow_human_decisions_approval_grant",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id"],
            ["workflow_runs.project_id", "workflow_runs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "snapshot_id"],
            [
                "workflow_stage_snapshots.project_id",
                "workflow_stage_snapshots.workflow_run_id",
                "workflow_stage_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workflow_run_id",
            "snapshot_id",
            "action",
            name="uq_workflow_human_decisions_run_snapshot_action",
        ),
        sa.UniqueConstraint(
            "project_id",
            "workflow_run_id",
            "id",
            name="uq_workflow_human_decisions_project_run_id",
        ),
    )
    op.create_index(
        "ix_workflow_human_decisions_project_run",
        "workflow_human_decisions",
        ["project_id", "workflow_run_id"],
    )

    op.create_table(
        "workflow_transition_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("actor", sa.String(length=40), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("from_stage", sa.String(length=80), nullable=False),
        sa.Column("from_state", sa.String(length=40), nullable=False),
        sa.Column("to_stage", sa.String(length=80), nullable=False),
        sa.Column("to_state", sa.String(length=40), nullable=False),
        sa.Column("source_snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("target_snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("human_decision_id", sa.Uuid(), nullable=True),
        sa.Column("consumed_approval_decision_id", sa.Uuid(), nullable=True),
        sa.Column("grant_fingerprint", sa.String(length=71), nullable=True),
        sa.Column("source_run_version", sa.Integer(), nullable=False),
        sa.Column("result_run_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id"],
            ["workflow_runs.project_id", "workflow_runs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "source_snapshot_id"],
            [
                "workflow_stage_snapshots.project_id",
                "workflow_stage_snapshots.workflow_run_id",
                "workflow_stage_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "target_snapshot_id"],
            [
                "workflow_stage_snapshots.project_id",
                "workflow_stage_snapshots.workflow_run_id",
                "workflow_stage_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "human_decision_id"],
            [
                "workflow_human_decisions.project_id",
                "workflow_human_decisions.workflow_run_id",
                "workflow_human_decisions.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "workflow_run_id", "consumed_approval_decision_id"],
            [
                "workflow_human_decisions.project_id",
                "workflow_human_decisions.workflow_run_id",
                "workflow_human_decisions.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workflow_run_id",
            "result_run_version",
            name="uq_workflow_transition_events_run_version",
        ),
        sa.UniqueConstraint(
            "consumed_approval_decision_id",
            name="uq_workflow_transition_events_consumed_approval",
        ),
    )
    op.create_index(
        "ix_workflow_transition_events_project_run",
        "workflow_transition_events",
        ["project_id", "workflow_run_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_workflow_transition_events_project_run", table_name="workflow_transition_events")
    op.drop_table("workflow_transition_events")
    op.drop_index("ix_workflow_human_decisions_project_run", table_name="workflow_human_decisions")
    op.drop_table("workflow_human_decisions")
    op.drop_index("ix_workflow_stage_snapshots_project_run", table_name="workflow_stage_snapshots")
    op.drop_table("workflow_stage_snapshots")
    op.drop_index("ix_workflow_runs_project_subject", table_name="workflow_runs")
    op.drop_table("workflow_runs")
