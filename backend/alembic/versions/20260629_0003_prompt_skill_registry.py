"""add prompt skill registry tables

Revision ID: 20260629_0003
Revises: 20260629_0002
Create Date: 2026-06-29
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260629_0003"
down_revision = "20260629_0002"
branch_labels = None
depends_on = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def string_list_type():
    return sa.JSON().with_variant(postgresql.ARRAY(sa.String()), "postgresql")


def empty_json_object_default():
    return sa.text("'{}'")


def empty_json_list_default():
    return sa.text("'[]'")


def empty_text_list_default():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.text("'{}'::text[]")
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
        "prompt_versions",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=40), server_default="v1", nullable=False),
        sa.Column("hash", sa.String(length=128), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("input_schema_json", json_type(), server_default=empty_json_object_default(), nullable=False),
        sa.Column("output_schema_json", json_type(), server_default=empty_json_object_default(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "version", name="uq_prompt_versions_name_version"),
    )

    op.create_table(
        "skill_versions",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=40), server_default="v1", nullable=False),
        sa.Column("hash", sa.String(length=128), nullable=False),
        sa.Column("applicable_agents", string_list_type(), server_default=empty_text_list_default(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("quality_gates_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("forbidden_actions_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("tool_permissions_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "version", name="uq_skill_versions_name_version"),
    )


def downgrade() -> None:
    op.drop_table("skill_versions")
    op.drop_table("prompt_versions")
