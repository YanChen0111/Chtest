"""add case candidate coverage dimensions

Revision ID: 20260713_0010
Revises: 20260710_0009
Create Date: 2026-07-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260713_0010"
down_revision = "20260710_0009"
branch_labels = None
depends_on = None


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def empty_json_list_default():
    return sa.text("'[]'")


def upgrade() -> None:
    op.add_column(
        "generated_case_candidates",
        sa.Column(
            "coverage_dimensions_json",
            json_type(),
            server_default=empty_json_list_default(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("generated_case_candidates", "coverage_dimensions_json")
