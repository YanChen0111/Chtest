"""add generated case knowledge evidence fields

Revision ID: 20260701_0007
Revises: 20260701_0006
Create Date: 2026-07-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260701_0007"
down_revision = "20260701_0006"
branch_labels = None
depends_on = None
AUTOMATION_READINESS_CHECK = (
    "automation_readiness IN ("
    "'unknown', "
    "'not_suitable', "
    "'suitable_for_pytest', "
    "'suitable_for_playwright', "
    "'suitable_for_newman', "
    "'suitable_for_jmeter'"
    ")"
)
AUTOMATION_READINESS_CONSTRAINT = "ck_generated_case_candidates_automation_readiness"
QUALITY_SCORE_CONSTRAINT = "ck_generated_case_candidates_quality_score_0_100"


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def string_list_type():
    return sa.JSON().with_variant(postgresql.ARRAY(sa.String()), "postgresql")


def uuid_list_type():
    return sa.JSON().with_variant(postgresql.ARRAY(postgresql.UUID(as_uuid=True)), "postgresql")


def empty_json_list_default():
    return sa.text("'[]'")


def empty_text_list_default():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.text("'{}'::text[]")
    return sa.text("'[]'")


def empty_uuid_list_default():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.text("'{}'::uuid[]")
    return sa.text("'[]'")


def upgrade() -> None:
    with op.batch_alter_table("generated_case_candidates") as batch_op:
        batch_op.add_column(
            sa.Column(
                "source_knowledge_evidence_ids",
                string_list_type(),
                server_default=empty_text_list_default(),
                nullable=False,
            ),
        )
        batch_op.add_column(
            sa.Column(
                "knowledge_evidence_refs_json",
                json_type(),
                server_default=empty_json_list_default(),
                nullable=False,
            ),
        )
        batch_op.add_column(
            sa.Column("covered_risk_ids", uuid_list_type(), server_default=empty_uuid_list_default(), nullable=False),
        )
        batch_op.add_column(sa.Column("generation_reason", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("automation_readiness", sa.String(length=40), server_default="unknown", nullable=False),
        )
        batch_op.add_column(sa.Column("quality_score", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("review_findings_json", json_type(), server_default=empty_json_list_default(), nullable=False),
        )
        batch_op.add_column(sa.Column("coverage_gap_notes", sa.Text(), nullable=True))
        batch_op.create_check_constraint(AUTOMATION_READINESS_CONSTRAINT, AUTOMATION_READINESS_CHECK)
        batch_op.create_check_constraint(
            QUALITY_SCORE_CONSTRAINT,
            "quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 100)",
        )


def downgrade() -> None:
    with op.batch_alter_table("generated_case_candidates") as batch_op:
        batch_op.drop_constraint(QUALITY_SCORE_CONSTRAINT, type_="check")
        batch_op.drop_constraint(AUTOMATION_READINESS_CONSTRAINT, type_="check")
        batch_op.drop_column("coverage_gap_notes")
        batch_op.drop_column("review_findings_json")
        batch_op.drop_column("quality_score")
        batch_op.drop_column("automation_readiness")
        batch_op.drop_column("generation_reason")
        batch_op.drop_column("covered_risk_ids")
        batch_op.drop_column("knowledge_evidence_refs_json")
        batch_op.drop_column("source_knowledge_evidence_ids")
