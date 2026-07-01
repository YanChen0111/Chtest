"""add review history table

Revision ID: 20260701_0006
Revises: 20260629_0005
Create Date: 2026-07-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260701_0006"
down_revision = "20260629_0005"
branch_labels = None
depends_on = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def uuid_list_type():
    return sa.JSON().with_variant(postgresql.ARRAY(postgresql.UUID(as_uuid=True)), "postgresql")


def empty_json_object_default():
    return sa.text("'{}'")


def empty_uuid_list_default():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.text("'{}'::uuid[]")
    return sa.text("'[]'")


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
        "review_history",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("related_entity_type", sa.String(length=80), nullable=True),
        sa.Column("related_entity_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("from_status", sa.String(length=80), nullable=True),
        sa.Column("to_status", sa.String(length=80), nullable=True),
        sa.Column("reviewer", sa.String(length=120), server_default="Default User", nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("evidence_artifact_ids", uuid_list_type(), server_default=empty_uuid_list_default(), nullable=False),
        sa.Column("metadata_json", json_type(), server_default=empty_json_object_default(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_review_history_project_entity", "review_history", ["project_id", "entity_type", "entity_id"])
    op.create_index(
        "ix_review_history_project_related",
        "review_history",
        ["project_id", "related_entity_type", "related_entity_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_review_history_project_related", table_name="review_history")
    op.drop_index("ix_review_history_project_entity", table_name="review_history")
    op.drop_table("review_history")
