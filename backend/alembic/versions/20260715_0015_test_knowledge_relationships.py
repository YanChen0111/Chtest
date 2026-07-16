"""add typed test knowledge relationships

Revision ID: 20260715_0015
Revises: 20260715_0014
Create Date: 2026-07-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260715_0015"
down_revision = "20260715_0014"
branch_labels = None
depends_on = None


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "test_knowledge_relationships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("source_entity_type", sa.String(length=80), nullable=False),
        sa.Column("source_entity_id", sa.Uuid(), nullable=False),
        sa.Column("target_entity_type", sa.String(length=80), nullable=False),
        sa.Column("target_entity_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_type", sa.String(length=120), nullable=False),
        sa.Column("evidence_artifact_ids_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("confidence", sa.Integer(), server_default="100", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        sa.Column("metadata_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "source_entity_type",
            "source_entity_id",
            "target_entity_type",
            "target_entity_id",
            "relationship_type",
            name="uq_test_knowledge_relationship_edge",
        ),
    )
    op.create_index(
        "ix_test_knowledge_relationship_project_type",
        "test_knowledge_relationships",
        ["project_id", "relationship_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_test_knowledge_relationship_project_type", table_name="test_knowledge_relationships")
    op.drop_table("test_knowledge_relationships")
