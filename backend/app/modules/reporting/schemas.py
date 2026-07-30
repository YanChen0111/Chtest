from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.modules.ai_runtime.schemas import ArtifactRead


class FailureAnalysisCreateRequest(BaseModel):
    prompt_version: str = "failure_analysis:v1"
    skill_version: str = "failure-analysis-skill:v1"
    model_provider: str | None = None
    model_name: str | None = None
    execution_result_review_decision_id: uuid.UUID | None = None


class FailureAnalysisCreateRead(BaseModel):
    ai_task_id: uuid.UUID
    failure_analysis_id: uuid.UUID
    status: str


class FailureAnalysisRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    test_run_id: uuid.UUID | None
    test_result_id: uuid.UUID | None
    ai_task_id: uuid.UUID
    classification: str
    confidence: float
    evidence_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    summary: str
    root_cause: str | None
    suggested_actions: list[Any] = Field(default_factory=list)
    status: str


class ReportCreateRequest(BaseModel):
    project_id: uuid.UUID
    report_type: str = "automation_execution"
    related_entity_type: str
    related_entity_id: uuid.UUID
    execution_result_review_decision_id: uuid.UUID | None = None


class ReportCreateRead(BaseModel):
    report_id: uuid.UUID
    status: str
    evidence_manifest_artifact_id: uuid.UUID | None = None


class ReportReviewWorkflowActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    reviewer: str = Field(default="Default User", min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)


class ReportReviewWorkflowEditRequest(ReportReviewWorkflowActionRequest):
    report_decisions: list[dict[str, Any]] = Field(default_factory=list)


class ReportReviewWorkflowContinueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    approval_decision_id: uuid.UUID


class ReportReviewWorkflowRead(BaseModel):
    project_id: uuid.UUID
    requirement_review_id: uuid.UUID
    workflow: dict[str, Any]
    source_execution_result_review_snapshot_id: str | None = None
    source_execution_result_review_snapshot_hash: str | None = None
    source_execution_approval_snapshot_id: str | None = None
    source_execution_approval_snapshot_hash: str | None = None
    generated_test_run_ids: list[str] = Field(default_factory=list)
    execution_artifact_ids: list[str] = Field(default_factory=list)
    generated_report_ids: list[str] = Field(default_factory=list)
    report_artifact_ids: list[str] = Field(default_factory=list)
    execution_decisions: list[dict[str, Any]] = Field(default_factory=list)
    result_decisions: list[dict[str, Any]] = Field(default_factory=list)
    report_decisions: list[dict[str, Any]] = Field(default_factory=list)


class ReportRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    report_type: str
    title: str
    related_entity_type: str | None
    related_entity_id: uuid.UUID | None
    status: str
    conclusion: str | None
    summary: str | None
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    evidence_manifest: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[ArtifactRead] = Field(default_factory=list)
