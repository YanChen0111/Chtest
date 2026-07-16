"""add test knowledge cards

Revision ID: 20260709_0008
Revises: 20260709_0007
Create Date: 2026-07-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260709_0008"
down_revision = "20260709_0007"
branch_labels = None
depends_on = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


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
        "test_knowledge_cards",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("source_artifact_id", sa.Uuid(), nullable=False),
        sa.Column("source_document_version", sa.String(length=80), server_default="v1", nullable=False),
        sa.Column("source_section", sa.Text(), nullable=True),
        sa.Column("source_quote_hash", sa.String(length=128), nullable=False),
        sa.Column("knowledge_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("module_key", sa.String(length=160), nullable=True),
        sa.Column("api_endpoint", sa.String(length=255), nullable=True),
        sa.Column("risk_type", sa.String(length=80), nullable=True),
        sa.Column("case_type_hint", sa.String(length=80), nullable=True),
        sa.Column("applicability", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Integer(), server_default="70", nullable=False),
        sa.Column("safe_to_show", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("allowed_for_prompt", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="extracted", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_artifact_id"], ["artifacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_test_knowledge_cards_project_source",
        "test_knowledge_cards",
        ["project_id", "source_artifact_id"],
    )

    with op.batch_alter_table("generated_case_candidates") as batch_op:
        batch_op.add_column(
            sa.Column("source_knowledge_evidence_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        )


def downgrade() -> None:
    with op.batch_alter_table("generated_case_candidates") as batch_op:
        batch_op.drop_column("source_knowledge_evidence_json")
    op.drop_index("ix_test_knowledge_cards_project_source", table_name="test_knowledge_cards")
    op.drop_table("test_knowledge_cards")
