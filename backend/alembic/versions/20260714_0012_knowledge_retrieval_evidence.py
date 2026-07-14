"""add knowledge retrieval runs and normalized evidence

Revision ID: 20260714_0012
Revises: 20260714_0011
Create Date: 2026-07-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260714_0012"
down_revision = "20260714_0011"
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
        "knowledge_retrieval_runs",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("ai_task_id", sa.Uuid(), nullable=True),
        sa.Column("consumer_entity_type", sa.String(length=80), nullable=True),
        sa.Column("consumer_entity_id", sa.Uuid(), nullable=True),
        sa.Column("adapter_name", sa.String(length=120), server_default="default", nullable=False),
        sa.Column("provider_type", sa.String(length=80), server_default="deterministic_local", nullable=False),
        sa.Column("requested_retrieval_mode", sa.String(length=80), server_default="hybrid", nullable=False),
        sa.Column("retrieval_mode", sa.String(length=80), server_default="hybrid", nullable=False),
        sa.Column("adapter_config_snapshot_json", json_type(), server_default=empty_json_dict_default(), nullable=False),
        sa.Column("query_text_hash", sa.String(length=128), nullable=False),
        sa.Column("query_text_redacted", sa.Text(), nullable=False),
        sa.Column("filters_json", json_type(), server_default=empty_json_dict_default(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="created", nullable=False),
        sa.Column("candidate_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("evidence_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("degraded", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("fallback_reason", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("evidence_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("candidate_count >= 0", name="ck_knowledge_retrieval_runs_candidate_count"),
        sa.CheckConstraint("evidence_count >= 0", name="ck_knowledge_retrieval_runs_evidence_count"),
        sa.CheckConstraint(
            "evidence_count <= candidate_count",
            name="ck_knowledge_retrieval_runs_evidence_not_above_candidates",
        ),
        sa.CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name="ck_knowledge_retrieval_runs_latency",
        ),
        sa.CheckConstraint(
            "(consumer_entity_type IS NULL) = (consumer_entity_id IS NULL)",
            name="ck_knowledge_retrieval_runs_consumer_pair",
        ),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["evidence_artifact_id"], ["artifacts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_retrieval_runs_project_created",
        "knowledge_retrieval_runs",
        ["project_id", "created_at", "id"],
    )
    op.create_index(
        "ix_knowledge_retrieval_runs_project_status",
        "knowledge_retrieval_runs",
        ["project_id", "status", "created_at", "id"],
    )
    op.create_index(
        "ix_knowledge_retrieval_runs_project_provider",
        "knowledge_retrieval_runs",
        ["project_id", "provider_type", "created_at", "id"],
    )
    op.create_index(
        "ix_knowledge_retrieval_runs_project_consumer",
        "knowledge_retrieval_runs",
        ["project_id", "consumer_entity_type", "consumer_entity_id", "created_at", "id"],
    )

    op.create_table(
        "knowledge_evidence",
        sa.Column("id", sa.Uuid(), server_default=uuid_pk_server_default(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("retrieval_run_id", sa.Uuid(), nullable=False),
        sa.Column("knowledge_card_id", sa.Uuid(), nullable=False),
        sa.Column("source_artifact_id", sa.Uuid(), nullable=False),
        sa.Column("snippet", sa.Text(), nullable=False),
        sa.Column("source_locator_json", json_type(), server_default=empty_json_dict_default(), nullable=False),
        sa.Column("metadata_score", sa.Float(), server_default="0", nullable=False),
        sa.Column("keyword_score", sa.Float(), server_default="0", nullable=False),
        sa.Column("vector_score", sa.Float(), nullable=True),
        sa.Column("rerank_score", sa.Float(), nullable=True),
        sa.Column("final_score", sa.Float(), server_default="0", nullable=False),
        sa.Column("matched_terms_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        sa.Column("retrieval_reason", sa.Text(), nullable=False),
        sa.Column("card_status_snapshot", sa.String(length=40), nullable=False),
        sa.Column("safe_to_show", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("allowed_for_prompt", sa.Boolean(), server_default=sa.true(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint("metadata_score >= 0 AND metadata_score <= 1", name="ck_knowledge_evidence_metadata_score"),
        sa.CheckConstraint("keyword_score >= 0 AND keyword_score <= 1", name="ck_knowledge_evidence_keyword_score"),
        sa.CheckConstraint(
            "vector_score IS NULL OR (vector_score >= 0 AND vector_score <= 1)",
            name="ck_knowledge_evidence_vector_score",
        ),
        sa.CheckConstraint(
            "rerank_score IS NULL OR (rerank_score >= 0 AND rerank_score <= 1)",
            name="ck_knowledge_evidence_rerank_score",
        ),
        sa.CheckConstraint("final_score >= 0 AND final_score <= 1", name="ck_knowledge_evidence_final_score"),
        sa.ForeignKeyConstraint(["knowledge_card_id"], ["test_knowledge_cards.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["retrieval_run_id"], ["knowledge_retrieval_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_artifact_id"], ["artifacts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("retrieval_run_id", "knowledge_card_id", name="uq_knowledge_evidence_run_card"),
    )
    op.create_index(
        "ix_knowledge_evidence_run_score",
        "knowledge_evidence",
        ["retrieval_run_id", "final_score"],
    )
    op.create_index(
        "ix_knowledge_evidence_project_card",
        "knowledge_evidence",
        ["project_id", "knowledge_card_id"],
    )
    op.create_index(
        "ix_knowledge_evidence_source_artifact",
        "knowledge_evidence",
        ["source_artifact_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_evidence_source_artifact", table_name="knowledge_evidence")
    op.drop_index("ix_knowledge_evidence_project_card", table_name="knowledge_evidence")
    op.drop_index("ix_knowledge_evidence_run_score", table_name="knowledge_evidence")
    op.drop_table("knowledge_evidence")
    op.drop_index("ix_knowledge_retrieval_runs_project_consumer", table_name="knowledge_retrieval_runs")
    op.drop_index("ix_knowledge_retrieval_runs_project_provider", table_name="knowledge_retrieval_runs")
    op.drop_index("ix_knowledge_retrieval_runs_project_status", table_name="knowledge_retrieval_runs")
    op.drop_index("ix_knowledge_retrieval_runs_project_created", table_name="knowledge_retrieval_runs")
    op.drop_table("knowledge_retrieval_runs")
