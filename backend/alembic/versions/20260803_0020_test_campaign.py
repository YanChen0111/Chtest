"""add controlled test campaign scope

Revision ID: 20260803_0020
Revises: 20260728_0019
Create Date: 2026-08-03
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260803_0020"
down_revision = "20260728_0019"
branch_labels = None
depends_on = None


def json_type() -> sa.TypeEngine:
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "test_campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("scope_statement", sa.Text(), nullable=False),
        sa.Column("target_environment_id", sa.Uuid(), nullable=False),
        sa.Column("target_version_ref", sa.String(length=160), nullable=False),
        sa.Column("exit_conditions_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("requirement_ids_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("risk_ids_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("test_plan_snapshot_ids_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("approved_case_ids_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("coverage_rows_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_environment_id"], ["environments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_test_campaigns_project_status",
        "test_campaigns",
        ["project_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_test_campaigns_project_status", table_name="test_campaigns")
    op.drop_table("test_campaigns")
