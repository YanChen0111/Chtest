from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.modules.ai_runtime.schemas import ArtifactRead


class TestRunCreateRequest(BaseModel):
    project_id: uuid.UUID
    automation_draft_id: uuid.UUID | None = None
    test_command_id: uuid.UUID | None = None
    execution_approval_decision_id: uuid.UUID | None = None
    reason: str | None = None
    runner_mode: str = "local_subprocess"

    @model_validator(mode="after")
    def require_one_execution_source(self) -> TestRunCreateRequest:
        source_count = sum(
            source is not None
            for source in (self.automation_draft_id, self.test_command_id)
        )
        if source_count != 1:
            raise ValueError("Exactly one of automation_draft_id or test_command_id is required.")
        return self


class TestResultRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    test_run_id: uuid.UUID
    test_name: str
    test_file: str | None
    status: str
    duration_ms: int | None
    failure_message: str | None
    failure_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TestRunRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    automation_draft_id: uuid.UUID | None
    test_command_id: uuid.UUID | None
    tool_invocation_id: uuid.UUID | None
    name: str
    command: str
    working_directory: str
    runner_mode: str
    run_workspace: str | None
    repository_readonly: bool
    network_enabled: bool
    runtime_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    dependency_snapshot_artifact_id: uuid.UUID | None
    environment_snapshot_artifact_id: uuid.UUID | None
    status: str
    exit_code: int | None
    duration_ms: int | None
    parsed_result: dict[str, Any] = Field(default_factory=dict)
    test_results: list[TestResultRead] = Field(default_factory=list)
    artifacts: list[ArtifactRead] = Field(default_factory=list)


class ExecutionApprovalWorkflowActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    reviewer: str = Field(default="Default User", min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)


class ExecutionApprovalWorkflowEditRequest(ExecutionApprovalWorkflowActionRequest):
    execution_decisions: list[dict[str, Any]] = Field(default_factory=list)


class ExecutionApprovalWorkflowContinueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    approval_decision_id: uuid.UUID


class ExecutionApprovalWorkflowRead(BaseModel):
    project_id: uuid.UUID
    requirement_review_id: uuid.UUID
    workflow: dict[str, Any]
    source_automation_draft_review_snapshot_id: str | None = None
    source_automation_draft_review_snapshot_hash: str | None = None
    source_automation_plan_review_snapshot_id: str | None = None
    source_automation_plan_review_snapshot_hash: str | None = None
    source_case_review_snapshot_id: str | None = None
    source_case_review_snapshot_hash: str | None = None
    approved_automation_plan_ids: list[str] = Field(default_factory=list)
    approved_test_case_ids: list[str] = Field(default_factory=list)
    approved_automation_draft_ids: list[str] = Field(default_factory=list)
    generated_test_run_ids: list[uuid.UUID] = Field(default_factory=list)
    draft_decisions: list[dict[str, Any]] = Field(default_factory=list)
    execution_decisions: list[dict[str, Any]] = Field(default_factory=list)


class ExecutionResultReviewWorkflowActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    reviewer: str = Field(default="Default User", min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)


class ExecutionResultReviewWorkflowEditRequest(ExecutionResultReviewWorkflowActionRequest):
    result_decisions: list[dict[str, Any]] = Field(default_factory=list)


class ExecutionResultReviewWorkflowContinueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    approval_decision_id: uuid.UUID


class ExecutionResultReviewWorkflowRead(BaseModel):
    project_id: uuid.UUID
    requirement_review_id: uuid.UUID
    workflow: dict[str, Any]
    source_execution_approval_snapshot_id: str | None = None
    source_execution_approval_snapshot_hash: str | None = None
    source_automation_draft_review_snapshot_id: str | None = None
    source_automation_draft_review_snapshot_hash: str | None = None
    source_automation_plan_review_snapshot_id: str | None = None
    source_automation_plan_review_snapshot_hash: str | None = None
    source_case_review_snapshot_id: str | None = None
    source_case_review_snapshot_hash: str | None = None
    approved_automation_draft_ids: list[str] = Field(default_factory=list)
    generated_test_run_ids: list[uuid.UUID] = Field(default_factory=list)
    execution_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    execution_decisions: list[dict[str, Any]] = Field(default_factory=list)
    result_decisions: list[dict[str, Any]] = Field(default_factory=list)
