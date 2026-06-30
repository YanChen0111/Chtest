from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from backend.app.modules.ai_runtime.schemas import ArtifactRead


class CICDRunCreateRequest(BaseModel):
    project_id: uuid.UUID
    repository_id: uuid.UUID | None = None
    source_type: str = "local_diff"
    trigger_type: str = "manual"
    provider: str = "local"
    pipeline_name: str | None = None
    base_ref: str | None = None
    head_ref: str | None = None
    diff_text: str | None = None


class CICDRunCreateRead(BaseModel):
    cicd_run_id: uuid.UUID
    status: str


class CICDRunAnalyzeRequest(BaseModel):
    prompt_version: str = "cicd_change_analysis:v1"
    skill_version: str = "regression-selection-skill:v1"
    model_provider: str = "mock"
    model_name: str = "mock-cicd-analysis"


class CICDRunAnalyzeRead(BaseModel):
    cicd_run_id: uuid.UUID
    ai_task_id: uuid.UUID
    risk_analysis_artifact_id: uuid.UUID
    status: str


class CICDChangedFileRead(BaseModel):
    id: uuid.UUID
    cicd_run_id: uuid.UUID
    path: str
    old_path: str | None
    change_type: str
    language: str | None
    file_role: str
    risk_level: str
    risk_reasons: list[str] = Field(default_factory=list)
    lines_added: int
    lines_deleted: int


class UnitTestPatchCreate(BaseModel):
    cicd_run_id: uuid.UUID
    ai_task_id: uuid.UUID
    patch_text: str
    target_framework: str = "pytest"
    scope_gate_result: dict[str, Any] = Field(default_factory=dict)
    test_intent: str
    coverage_target: list[dict[str, Any]] = Field(default_factory=list)
    status: str = "generated"
    review_comment: str | None = None


class UnitTestPatchRead(BaseModel):
    id: uuid.UUID
    cicd_run_id: uuid.UUID
    ai_task_id: uuid.UUID
    patch_text: str
    target_framework: str
    scope_gate_result: dict[str, Any] = Field(default_factory=dict)
    test_intent: str
    coverage_target: list[dict[str, Any]] = Field(default_factory=list)
    status: str
    review_comment: str | None


class QualityGateDecisionCreate(BaseModel):
    project_id: uuid.UUID
    cicd_run_id: uuid.UUID
    status: str = "needs_review"
    summary: str
    blocking_reasons: list[str] = Field(default_factory=list)
    evidence_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    decided_by: str = "system"
    status_detail: dict[str, Any] = Field(default_factory=dict)


class QualityGateDecisionRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    cicd_run_id: uuid.UUID
    status: str
    summary: str
    blocking_reasons: list[str] = Field(default_factory=list)
    evidence_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    decided_by: str
    status_detail: dict[str, Any] = Field(default_factory=dict)


class CICDRunRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    repository_id: uuid.UUID | None
    source_type: str
    trigger_type: str
    provider: str
    pipeline_name: str | None
    base_ref: str | None
    head_ref: str | None
    summary: str | None
    overall_risk: str
    quality_gate_status: str
    status: str
    changed_files: list[CICDChangedFileRead] = Field(default_factory=list)
    analysis_artifacts: list[ArtifactRead | dict[str, Any]] = Field(default_factory=list)


class CICDRunListRead(BaseModel):
    items: list[CICDRunRead] = Field(default_factory=list)
    total: int
