"""add evidence-backed case candidate fields

Revision ID: 20260715_0014
Revises: 20260714_0013
Create Date: 2026-07-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260715_0014"
down_revision = "20260714_0013"
branch_labels = None
depends_on = None


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.add_column(
        "generated_case_candidates",
        sa.Column("covered_requirement_ids_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
    )
    op.add_column(
        "generated_case_candidates",
        sa.Column("covered_risk_ids_json", json_type(), server_default=sa.text("'[]'"), nullable=False),
    )
    op.add_column(
        "generated_case_candidates",
        sa.Column("case_type", sa.String(length=80), server_default="functional", nullable=False),
    )
    op.add_column(
        "generated_case_candidates",
        sa.Column("generation_reason", sa.Text(), server_default="", nullable=False),
    )
    op.add_column("generated_case_candidates", sa.Column("coverage_gap_notes", sa.Text(), nullable=True))
    op.add_column(
        "generated_case_candidates",
        sa.Column("automation_readiness_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
    )
    op.add_column(
        "generated_case_candidates",
        sa.Column("quality_assessment_json", json_type(), server_default=sa.text("'{}'"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("generated_case_candidates", "quality_assessment_json")
    op.drop_column("generated_case_candidates", "automation_readiness_json")
    op.drop_column("generated_case_candidates", "coverage_gap_notes")
    op.drop_column("generated_case_candidates", "generation_reason")
    op.drop_column("generated_case_candidates", "case_type")
    op.drop_column("generated_case_candidates", "covered_risk_ids_json")
    op.drop_column("generated_case_candidates", "covered_requirement_ids_json")
