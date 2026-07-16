"""add runtime surface tables omitted from the migration chain

Revision ID: 20260716_0018
Revises: 20260716_0017
Create Date: 2026-07-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260716_0018"
down_revision = "20260716_0017"
branch_labels = None
depends_on = None


def json_type() -> sa.TypeEngine:
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
    ]


def json_column(name: str, default: str) -> sa.Column:
    return sa.Column(name, json_type(), server_default=sa.text(f"'{default}'"), nullable=False)


def upgrade() -> None:
    op.create_table(
        "knowledge_adapter_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("adapter_name", sa.String(length=120), server_default="default", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="not_configured", nullable=False),
        sa.Column("provider_type", sa.String(length=80), server_default="none", nullable=False),
        json_column("config_json", "{}"),
        json_column("safety_policy_json", "{}"),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "adapter_name",
            name="uq_knowledge_adapter_configs_project_adapter",
        ),
    )

    op.create_table(
        "tool_definitions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tool_type", sa.String(length=80), server_default="test_runner", nullable=False),
        json_column("input_schema_json", "{}"),
        json_column("output_schema_json", "{}"),
        sa.Column("risk_level", sa.String(length=40), server_default="medium", nullable=False),
        sa.Column("approval_required", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), server_default="600", nullable=False),
        json_column("command_allowlist_json", "[]"),
        json_column("allowed_working_directories_json", "[]"),
        json_column("forbidden_shell_operators_json", "[]"),
        sa.Column("max_stdout_bytes", sa.Integer(), server_default="1048576", nullable=False),
        sa.Column("max_stderr_bytes", sa.Integer(), server_default="1048576", nullable=False),
        json_column("artifact_policy_json", "{}"),
        sa.Column("is_mcp_ready", sa.Boolean(), server_default=sa.false(), nullable=False),
        json_column("mcp_metadata_json", "{}"),
        sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_tool_definitions_project_name"),
    )

    op.create_table(
        "cicd_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=True),
        sa.Column("source_type", sa.String(length=40), server_default="local_diff", nullable=False),
        sa.Column("trigger_type", sa.String(length=40), server_default="manual", nullable=False),
        sa.Column("provider", sa.String(length=40), server_default="local", nullable=False),
        sa.Column("pipeline_name", sa.String(length=160), nullable=True),
        sa.Column("base_ref", sa.String(length=160), nullable=True),
        sa.Column("head_ref", sa.String(length=160), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("overall_risk", sa.String(length=40), server_default="medium", nullable=False),
        sa.Column("quality_gate_status", sa.String(length=40), server_default="pending", nullable=False),
        sa.Column("status", sa.String(length=40), server_default="created", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cicd_changed_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cicd_run_id", sa.Uuid(), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("old_path", sa.Text(), nullable=True),
        sa.Column("change_type", sa.String(length=40), server_default="modified", nullable=False),
        sa.Column("language", sa.String(length=60), nullable=True),
        sa.Column("file_role", sa.String(length=60), server_default="unknown", nullable=False),
        sa.Column("risk_level", sa.String(length=40), server_default="medium", nullable=False),
        json_column("risk_reasons_json", "[]"),
        sa.Column("lines_added", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lines_deleted", sa.Integer(), server_default="0", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["cicd_run_id"], ["cicd_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "unit_test_patches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cicd_run_id", sa.Uuid(), nullable=False),
        sa.Column("ai_task_id", sa.Uuid(), nullable=False),
        sa.Column("patch_text", sa.Text(), nullable=False),
        sa.Column("target_framework", sa.String(length=60), server_default="pytest", nullable=False),
        json_column("scope_gate_result_json", "{}"),
        sa.Column("test_intent", sa.Text(), nullable=False),
        json_column("coverage_target_json", "[]"),
        sa.Column("status", sa.String(length=40), server_default="generated", nullable=False),
        sa.Column("review_comment", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cicd_run_id"], ["cicd_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "quality_gate_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("cicd_run_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="needs_review", nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        json_column("blocking_reasons_json", "[]"),
        json_column("evidence_artifact_ids", "[]"),
        sa.Column("decided_by", sa.String(length=40), server_default="system", nullable=False),
        json_column("status_detail_json", "{}"),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["cicd_run_id"], ["cicd_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "test_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("cicd_run_id", sa.Uuid(), nullable=True),
        sa.Column("automation_draft_id", sa.Uuid(), nullable=True),
        sa.Column("test_command_id", sa.Uuid(), nullable=True),
        sa.Column("tool_invocation_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("command", sa.Text(), nullable=False),
        sa.Column("working_directory", sa.Text(), nullable=False),
        sa.Column("runner_mode", sa.String(length=40), server_default="local_subprocess", nullable=False),
        sa.Column("run_workspace", sa.Text(), nullable=True),
        sa.Column("repository_readonly", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("network_enabled", sa.Boolean(), server_default=sa.false(), nullable=False),
        json_column("runtime_artifact_ids", "[]"),
        sa.Column("dependency_snapshot_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("environment_snapshot_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="created", nullable=False),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        json_column("parsed_result_json", "{}"),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["automation_draft_id"], ["automation_drafts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["dependency_snapshot_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["environment_snapshot_artifact_id"], ["artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_command_id"], ["test_commands.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "test_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("test_run_id", sa.Uuid(), nullable=False),
        sa.Column("test_name", sa.Text(), nullable=False),
        sa.Column("test_file", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="passed", nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        json_column("failure_artifact_ids", "[]"),
        json_column("metadata_json", "{}"),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "failure_analyses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("test_run_id", sa.Uuid(), nullable=True),
        sa.Column("test_result_id", sa.Uuid(), nullable=True),
        sa.Column("ai_task_id", sa.Uuid(), nullable=False),
        sa.Column("classification", sa.String(length=80), server_default="insufficient_evidence", nullable=False),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), server_default="0", nullable=False),
        json_column("evidence_artifact_ids", "[]"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("root_cause", sa.Text(), nullable=True),
        json_column("suggested_actions_json", "[]"),
        sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["ai_task_id"], ["ai_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_result_id"], ["test_results.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("report_type", sa.String(length=80), server_default="automation_execution", nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("related_entity_type", sa.String(length=80), nullable=True),
        sa.Column("related_entity_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=40), server_default="draft", nullable=False),
        sa.Column("conclusion", sa.String(length=80), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        json_column("metrics_json", "{}"),
        json_column("artifact_ids", "[]"),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    for table_name in (
        "reports",
        "failure_analyses",
        "test_results",
        "test_runs",
        "quality_gate_decisions",
        "unit_test_patches",
        "cicd_changed_files",
        "cicd_runs",
        "tool_definitions",
        "knowledge_adapter_configs",
    ):
        op.drop_table(table_name)
