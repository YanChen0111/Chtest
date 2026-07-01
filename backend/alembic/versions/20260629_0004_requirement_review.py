"""add requirement review tables

Revision ID: 20260629_0004
Revises: 20260629_0003
Create Date: 2026-06-29
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260629_0004"
down_revision = "20260629_0003"
branch_labels = None
depends_on = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"
SCORE_COLUMNS = (
    "completeness_score",
    "clarity_score",
    "consistency_score",
    "testability_score",
    "feasibility_score",
    "logic_score",
    "overall_score",
)


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


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


def score_constraints() -> list[sa.CheckConstraint]:
    return [
        sa.CheckConstraint(f"{column_name} >= 0 AND {column_name} <= 100", name=f"ck_requirement_reviews_{column_name}_0_100")
        for column_name in SCORE_COLUMNS
    ]


def upgrade() -> None:
    op.create_table(
        "requirements",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("module_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=40), server_default="manual", nullable=False),
        sa.Column("source_ref", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "requirement_reviews",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("requirement_id", sa.Uuid(), nullable=False),
        sa.Column("ai_task_id", sa.Uuid(), nullable=False),
        sa.Column("completeness_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("clarity_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("consistency_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("testability_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("feasibility_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("logic_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("overall_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("issues_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("clarification_questions_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("test_design_notes_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
        *timestamp_columns(),
        *score_constraints(),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "risk_items",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_review_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("risk_level", sa.String(length=40), server_default="medium", nullable=False),
        sa.Column("category", sa.String(length=80), server_default="business", nullable=False),
        sa.Column("impact", sa.Text(), nullable=False),
        sa.Column("suggestion", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_review_id"], ["requirement_reviews.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("risk_items")
    op.drop_table("requirement_reviews")
    op.drop_table("requirements")
