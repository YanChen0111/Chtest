"""add automation drafts

Revision ID: 20260709_0006a
Revises: 20260701_0006
Create Date: 2026-07-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260709_0006a"
down_revision = "20260701_0006"
branch_labels = None
depends_on = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def uuid_pk_server_default():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.text("gen_random_uuid()")
    return None


def default_user_server_default():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.text(f"'{DEFAULT_USER_ID}'::uuid")
    return DEFAULT_USER_ID


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Uuid(), server_default=default_user_server_default(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), server_default=default_user_server_default(), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "automation_drafts",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=True),
        sa.Column("requirement_id", sa.Uuid(), nullable=True),
        sa.Column("ai_task_id", sa.Uuid(), nullable=False),
        sa.Column("target_framework", sa.String(length=60), server_default="pytest", nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("draft_code", sa.Text(), nullable=False),
        sa.Column("draft_language", sa.String(length=60), server_default="python", nullable=False),
        sa.Column("suggested_file_path", sa.Text(), nullable=True),
        sa.Column("execution_notes", sa.Text(), nullable=True),
        sa.Column("risk_notes", sa.Text(), nullable=True),
        sa.Column("execution_strategy", sa.String(length=60), server_default="artifact_runtime_copy", nullable=False),
        sa.Column("approval_required", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="draft_generated", nullable=False),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("runtime_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("promoted_artifact_id", sa.Uuid(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["promoted_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["runtime_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("automation_drafts")
