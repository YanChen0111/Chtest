"""add reviewed knowledge feedback events

Revision ID: 20260715_0016
Revises: 20260715_0015
Create Date: 2026-07-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260715_0016"
down_revision = "20260715_0015"
branch_labels = None
depends_on = None


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "knowledge_feedback_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("source_entity_type", sa.String(length=80), nullable=False),
        sa.Column("source_entity_id", sa.Uuid(), nullable=False),
        sa.Column("proposed_knowledge_type", sa.String(length=80), nullable=False),
        sa.Column("proposed_content_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="proposed", nullable=False),
        sa.Column("evidence_artifact_ids_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("resulting_card_id", sa.Uuid(), nullable=True),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resulting_card_id"], ["test_knowledge_cards.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_feedback_project_status",
        "knowledge_feedback_events",
        ["project_id", "status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_feedback_project_status", table_name="knowledge_feedback_events")
    op.drop_table("knowledge_feedback_events")
