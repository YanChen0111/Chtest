"""add knowledge ingestion runs and card provenance

Revision ID: 20260714_0011
Revises: 20260713_0010
Create Date: 2026-07-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260714_0011"
down_revision = "20260713_0010"
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
        "knowledge_ingestion_runs",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("source_type", sa.String(length=80), server_default="artifact", nullable=False),
        sa.Column("source_refs_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("input_artifact_ids_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("parser_name", sa.String(length=120), server_default="deterministic", nullable=False),
        sa.Column("parser_version", sa.String(length=80), server_default="v1", nullable=False),
        sa.Column("config_snapshot_json", json_type(), server_default=empty_json_dict_default(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="created", nullable=False),
        sa.Column("parsed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("extracted_card_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("skipped_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("evidence_artifact_ids_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("ai_task_id", sa.Uuid(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("parsed_count >= 0", name="ck_knowledge_ingestion_runs_parsed_count"),
        sa.CheckConstraint(
            "extracted_card_count >= 0",
            name="ck_knowledge_ingestion_runs_extracted_count",
        ),
        sa.CheckConstraint("skipped_count >= 0", name="ck_knowledge_ingestion_runs_skipped_count"),
        sa.CheckConstraint("failed_count >= 0", name="ck_knowledge_ingestion_runs_failed_count"),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "idempotency_key",
            name="uq_knowledge_ingestion_runs_project_idempotency",
        ),
    )
    op.create_index(
        "ix_knowledge_ingestion_runs_project_created",
        "knowledge_ingestion_runs",
        ["project_id", "created_at"],
    )
    op.create_index(
        "ix_knowledge_ingestion_runs_project_status_source",
        "knowledge_ingestion_runs",
        ["project_id", "status", "source_type"],
    )

    with op.batch_alter_table("test_knowledge_cards") as batch_op:
        batch_op.add_column(
            sa.Column("source_locator_json", json_type(), server_default=empty_json_dict_default(), nullable=False),
        )
        batch_op.add_column(sa.Column("source_ref", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("ingestion_run_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("review_comment", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("duplicate_of_card_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_foreign_key(
            "fk_test_knowledge_cards_ingestion_run",
            "knowledge_ingestion_runs",
            ["ingestion_run_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_foreign_key(
            "fk_test_knowledge_cards_duplicate_of",
            "test_knowledge_cards",
            ["duplicate_of_card_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_unique_constraint(
            "uq_test_knowledge_cards_source_quote",
            ["source_artifact_id", "source_quote_hash"],
        )
        batch_op.create_check_constraint(
            "ck_test_knowledge_cards_duplicate_target",
            "status != 'duplicate' OR duplicate_of_card_id IS NOT NULL",
        )

    op.create_index(
        "ix_test_knowledge_cards_ingestion_run",
        "test_knowledge_cards",
        ["ingestion_run_id"],
    )
    op.create_index(
        "ix_test_knowledge_cards_duplicate_of",
        "test_knowledge_cards",
        ["duplicate_of_card_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_test_knowledge_cards_duplicate_of", table_name="test_knowledge_cards")
    op.drop_index("ix_test_knowledge_cards_ingestion_run", table_name="test_knowledge_cards")
    with op.batch_alter_table("test_knowledge_cards") as batch_op:
        batch_op.drop_constraint("ck_test_knowledge_cards_duplicate_target", type_="check")
        batch_op.drop_constraint("uq_test_knowledge_cards_source_quote", type_="unique")
        batch_op.drop_constraint("fk_test_knowledge_cards_duplicate_of", type_="foreignkey")
        batch_op.drop_constraint("fk_test_knowledge_cards_ingestion_run", type_="foreignkey")
        batch_op.drop_column("last_verified_at")
        batch_op.drop_column("duplicate_of_card_id")
        batch_op.drop_column("review_comment")
        batch_op.drop_column("reviewed_at")
        batch_op.drop_column("ingestion_run_id")
        batch_op.drop_column("source_ref")
        batch_op.drop_column("source_locator_json")

    op.drop_index("ix_knowledge_ingestion_runs_project_status_source", table_name="knowledge_ingestion_runs")
    op.drop_index("ix_knowledge_ingestion_runs_project_created", table_name="knowledge_ingestion_runs")
    op.drop_table("knowledge_ingestion_runs")
