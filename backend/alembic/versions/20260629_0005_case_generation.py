"""add case generation tables

Revision ID: 20260629_0005
Revises: 20260629_0004
Create Date: 2026-06-29
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260629_0005"
down_revision = "20260629_0004"
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
        "case_generation_tasks",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_review_id", sa.Uuid(), nullable=True),
        sa.Column("ai_task_id", sa.Uuid(), nullable=False),
        sa.Column("target_test_types", string_list_type(), server_default=empty_text_list_default(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="created", nullable=False),
        sa.Column("generated_count", sa.Integer(), server_default="0", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_review_id"], ["requirement_reviews.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "generated_case_candidates",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("generation_task_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("module_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("priority", sa.String(length=20), server_default="P2", nullable=False),
        sa.Column("test_type", sa.String(length=40), server_default="functional", nullable=False),
        sa.Column("precondition", sa.Text(), nullable=True),
        sa.Column("steps_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("expected_results_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("input_data_json", json_type(), server_default=empty_json_object_default(), nullable=False),
        sa.Column("tags", string_list_type(), server_default=empty_text_list_default(), nullable=False),
        sa.Column("requirement_refs_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("risk_refs_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("ai_reason", sa.Text(), nullable=False),
        sa.Column("duplicate_of_case_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="generated", nullable=False),
        sa.Column("review_comment", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["generation_task_id"], ["case_generation_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "test_cases",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("module_id", sa.Uuid(), nullable=True),
        sa.Column("source_candidate_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("priority", sa.String(length=20), server_default="P2", nullable=False),
        sa.Column("test_type", sa.String(length=40), server_default="functional", nullable=False),
        sa.Column("precondition", sa.Text(), nullable=True),
        sa.Column("steps_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("expected_results_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("input_data_json", json_type(), server_default=empty_json_object_default(), nullable=False),
        sa.Column("tags", string_list_type(), server_default=empty_text_list_default(), nullable=False),
        sa.Column("source_type", sa.String(length=40), server_default="ai", nullable=False),
        sa.Column("review_status", sa.String(length=40), server_default="approved", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_candidate_id"], ["generated_case_candidates.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("generated_case_candidates") as batch_op:
        batch_op.create_foreign_key(
            "fk_generated_case_candidates_duplicate_of_case_id_test_cases",
            "test_cases",
            ["duplicate_of_case_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("generated_case_candidates") as batch_op:
        batch_op.drop_constraint(
            "fk_generated_case_candidates_duplicate_of_case_id_test_cases",
            type_="foreignkey",
        )
    op.drop_table("test_cases")
    op.drop_table("generated_case_candidates")
    op.drop_table("case_generation_tasks")
