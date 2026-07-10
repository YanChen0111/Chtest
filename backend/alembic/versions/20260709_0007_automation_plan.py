"""add automation plan bridge

Revision ID: 20260709_0007
Revises: 20260709_0006a
Create Date: 2026-07-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260709_0007"
down_revision = "20260709_0006a"
branch_labels = None
depends_on = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def uuid_list_type():
    return sa.JSON().with_variant(postgresql.ARRAY(postgresql.UUID(as_uuid=True)), "postgresql")


def empty_json_object_default():
    return sa.text("'{}'")


def empty_json_list_default():
    return sa.text("'[]'")


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
        "automation_plans",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_id", sa.Uuid(), nullable=True),
        sa.Column("requirement_review_id", sa.Uuid(), nullable=True),
        sa.Column("source_candidate_id", sa.Uuid(), nullable=True),
        sa.Column("ai_task_id", sa.Uuid(), nullable=False),
        sa.Column("knowledge_retrieval_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("target_framework", sa.String(length=60), server_default="pytest", nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("plan_json", json_type(), server_default=empty_json_object_default(), nullable=False),
        sa.Column("execution_steps_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("test_data_json", json_type(), server_default=empty_json_object_default(), nullable=False),
        sa.Column("dependency_notes", sa.Text(), nullable=True),
        sa.Column("risk_notes", sa.Text(), nullable=True),
        sa.Column("used_context_artifact_ids", uuid_list_type(), server_default=empty_uuid_list_default(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="plan_generated", nullable=False),
        sa.Column("review_comment", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["knowledge_retrieval_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requirement_review_id"], ["requirement_reviews.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_candidate_id"], ["generated_case_candidates.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_automation_plans_project_test_case", "automation_plans", ["project_id", "test_case_id"])

    with op.batch_alter_table("automation_drafts") as batch_op:
        batch_op.add_column(sa.Column("automation_plan_id", sa.Uuid(), nullable=True))
        batch_op.create_foreign_key(
            "fk_automation_drafts_automation_plan_id_automation_plans",
            "automation_plans",
            ["automation_plan_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("automation_drafts") as batch_op:
        batch_op.drop_constraint(
            "fk_automation_drafts_automation_plan_id_automation_plans",
            type_="foreignkey",
        )
        batch_op.drop_column("automation_plan_id")
    op.drop_index("ix_automation_plans_project_test_case", table_name="automation_plans")
    op.drop_table("automation_plans")
