"""add ai runtime core tables

Revision ID: 20260629_0002
Revises: 20260626_0001
Create Date: 2026-06-29
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260629_0002"
down_revision = "20260626_0001"
branch_labels = None
depends_on = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def uuid_list_type():
    return sa.JSON().with_variant(postgresql.ARRAY(postgresql.UUID(as_uuid=True)), "postgresql")


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
        "ai_tasks",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("task_type", sa.String(length=120), nullable=False),
        sa.Column("prompt_version_id", sa.Uuid(), nullable=False),
        sa.Column("skill_version_id", sa.Uuid(), nullable=False),
        sa.Column("model_provider", sa.String(length=80), server_default="mock", nullable=False),
        sa.Column("model_name", sa.String(length=120), server_default="mock-model", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="created", nullable=False),
        sa.Column("input_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("output_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("error_json", json_type(), nullable=True),
        sa.Column("token_usage_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("context_artifact_ids", uuid_list_type(), server_default=empty_uuid_list_default(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "artifacts",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("owner_entity_type", sa.String(length=80), nullable=False),
        sa.Column("owner_entity_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_type", sa.String(length=80), server_default="json", nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=120), server_default="application/json", nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("sha256", sa.String(length=128), nullable=False),
        sa.Column("metadata_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "llm_call_logs",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("ai_task_id", sa.Uuid(), nullable=False),
        sa.Column("prompt_version_id", sa.Uuid(), nullable=False),
        sa.Column("skill_version_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=80), server_default="mock", nullable=False),
        sa.Column("model_name", sa.String(length=120), server_default="mock-model", nullable=False),
        sa.Column("call_index", sa.Integer(), server_default="1", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="started", nullable=False),
        sa.Column("request_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("response_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("parsed_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("schema_validation_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("input_summary_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("output_summary_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("token_usage_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_json", json_type(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parsed_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["request_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["response_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["schema_validation_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("llm_call_logs")
    op.drop_table("artifacts")
    op.drop_table("ai_tasks")
