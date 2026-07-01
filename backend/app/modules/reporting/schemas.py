from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from backend.app.modules.ai_runtime.schemas import ArtifactRead


class FailureAnalysisCreateRequest(BaseModel):
    prompt_version: str = "failure_analysis:v1"
    skill_version: str = "failure-analysis-skill:v1"
    model_provider: str = "mock"
    model_name: str = "mock-failure-analysis"


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


class ReportCreateRead(BaseModel):
    report_id: uuid.UUID
    status: str
    evidence_manifest_artifact_id: uuid.UUID | None = None


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
