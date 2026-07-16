"""add test knowledge embedding index

Revision ID: 20260710_0009
Revises: 20260709_0008
Create Date: 2026-07-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260710_0009"
down_revision = "20260709_0008"
branch_labels = None
depends_on = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def empty_json_dict_default():
    return sa.text("'{}'")


def empty_json_list_default():
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
        "test_knowledge_embedding_index",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("knowledge_card_id", sa.Uuid(), nullable=False),
        sa.Column("index_kind", sa.String(length=80), server_default="test_knowledge_card", nullable=False),
        sa.Column("embedding_provider", sa.String(length=80), server_default="deterministic_local", nullable=False),
        sa.Column("embedding_model", sa.String(length=120), server_default="deterministic-hashing-v1", nullable=False),
        sa.Column("embedding_dim", sa.Integer(), server_default="64", nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("embedding_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="indexed", nullable=False),
        sa.Column("metadata_json", json_type(), server_default=empty_json_dict_default(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["knowledge_card_id"], ["test_knowledge_cards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "knowledge_card_id",
            "embedding_model",
            name="uq_test_knowledge_embedding_card_model",
        ),
    )
    op.create_index(
        "ix_test_knowledge_embedding_project_model",
        "test_knowledge_embedding_index",
        ["project_id", "embedding_model"],
    )
    op.create_index(
        "ix_test_knowledge_embedding_project_card",
        "test_knowledge_embedding_index",
        ["project_id", "knowledge_card_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_test_knowledge_embedding_project_card", table_name="test_knowledge_embedding_index")
    op.drop_index("ix_test_knowledge_embedding_project_model", table_name="test_knowledge_embedding_index")
    op.drop_table("test_knowledge_embedding_index")
