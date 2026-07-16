"""add audit columns to knowledge relationship and feedback tables

Revision ID: 20260716_0017
Revises: 20260715_0016
Create Date: 2026-07-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260716_0017"
down_revision = "20260715_0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table_name in ("test_knowledge_relationships", "knowledge_feedback_events"):
        op.add_column(table_name, sa.Column("created_by", sa.Uuid(as_uuid=True), nullable=True))
        op.add_column(table_name, sa.Column("updated_by", sa.Uuid(as_uuid=True), nullable=True))


def downgrade() -> None:
    for table_name in ("knowledge_feedback_events", "test_knowledge_relationships"):
        op.drop_column(table_name, "updated_by")
        op.drop_column(table_name, "created_by")
