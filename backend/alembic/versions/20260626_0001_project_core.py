"""add project core tables

Revision ID: 20260626_0001
Revises:
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260626_0001"
down_revision = None
branch_labels = None
depends_on = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=120), server_default="Default User", nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_language", sa.String(length=60), server_default="python", nullable=True),
        sa.Column("default_test_type", sa.String(length=40), server_default="functional", nullable=True),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "name", name="uq_projects_workspace_name"),
    )

    op.create_table(
        "modules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("path", sa.String(length=800), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint("level >= 1 AND level <= 5", name="ck_modules_level_1_5"),
        sa.ForeignKeyConstraint(["parent_id"], ["modules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "parent_id", "name", name="uq_modules_project_parent_name"),
    )

    op.create_table(
        "repositories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("local_path", sa.Text(), nullable=False),
        sa.Column("default_base_branch", sa.String(length=120), server_default="main", nullable=True),
        sa.Column("language_hint", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_repositories_project_name"),
    )

    op.create_table(
        "environments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), server_default="dev", nullable=False),
        sa.Column(
            "variables_json",
            sa.JSON().with_variant(postgresql.JSONB(), "postgresql"),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_environments_project_name"),
    )

    op.create_table(
        "test_commands",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=True),
        sa.Column("environment_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("command", sa.Text(), nullable=False),
        sa.Column("working_directory", sa.Text(), nullable=False),
        sa.Column("command_type", sa.String(length=40), server_default="pytest", nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), server_default="600", nullable=False),
        sa.Column("parse_junit", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("parse_coverage", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint("timeout_seconds > 0", name="ck_test_commands_timeout_positive"),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_test_commands_project_name"),
    )


def downgrade() -> None:
    op.drop_table("test_commands")
    op.drop_table("environments")
    op.drop_table("repositories")
    op.drop_table("modules")
    op.drop_table("projects")
    op.drop_table("users")
    op.drop_table("workspaces")
