from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class AutomationPlanCreateRequest(BaseModel):
    project_id: uuid.UUID
    test_case_id: uuid.UUID
    target_framework: str = "pytest"
    use_knowledge: bool = True
    context_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    prompt_version: str = "automation_plan_generation:v1"
    skill_version: str = "automation-plan-skill:v1"
    model_provider: str | None = None
    model_name: str | None = None


class AutomationPlanUpdateRequest(BaseModel):
    title: str | None = None
    execution_steps: list[str] | None = None
    test_data: dict | None = None
    dependency_notes: str | None = None
    risk_notes: str | None = None
    review_comment: str | None = None


class AutomationPlanApproveRequest(BaseModel):
    action: str = "approve"
    review_comment: str | None = None


class AutomationPlanGenerateDraftRequest(BaseModel):
    prompt_version: str = "automation_draft_generation:v1"
    skill_version: str = "automation-draft-skill:v1"
    model_provider: str | None = None
    model_name: str | None = None


class AutomationPlanRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    test_case_id: uuid.UUID
    requirement_id: uuid.UUID | None
    requirement_review_id: uuid.UUID | None
    source_candidate_id: uuid.UUID | None
    ai_task_id: uuid.UUID
    knowledge_retrieval_artifact_id: uuid.UUID | None
    target_framework: str
    title: str
    plan: dict
    execution_steps: list
    test_data: dict
    dependency_notes: str | None
    risk_notes: str | None
    used_context_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    status: str
    review_comment: str | None


class AutomationPlanReviewRead(BaseModel):
    automation_plan_id: uuid.UUID
    status: str


class AutomationDraftCreateRequest(BaseModel):
    project_id: uuid.UUID
    test_case_id: uuid.UUID | None = None
    requirement_id: uuid.UUID | None = None
    automation_plan_id: uuid.UUID | None = None
    target_framework: str = "pytest"
    prompt_version: str = "automation_draft_generation:v1"
    skill_version: str = "automation-draft-skill:v1"
    model_provider: str | None = None
    model_name: str | None = None


class AutomationDraftCreateRead(BaseModel):
    automation_draft_id: uuid.UUID
    ai_task_id: uuid.UUID
    status: str


class AutomationDraftEditRequest(BaseModel):
    draft_code: str = Field(min_length=1)
    suggested_file_path: str | None = None
    execution_notes: str | None = None
    risk_notes: str | None = None
    review_comment: str | None = None


class AutomationDraftApproveRequest(BaseModel):
    action: str = "approve"
    review_comment: str | None = None


class AutomationDraftReviewRead(BaseModel):
    automation_draft_id: uuid.UUID
    status: str


class AutomationDraftQualityGateRead(BaseModel):
    status: str = "ready_for_approval"
    execution_evidence_level: str = "reviewed_candidate"
    approval_blocking_reasons: list[str] = Field(default_factory=list)
    evidence_warnings: list[str] = Field(default_factory=list)


class AutomationDraftRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    test_case_id: uuid.UUID | None
    requirement_id: uuid.UUID | None
    ai_task_id: uuid.UUID
    automation_plan_id: uuid.UUID | None
    target_framework: str
    title: str
    draft_code: str
    draft_language: str
    suggested_file_path: str | None
    execution_notes: str | None
    risk_notes: str | None
    execution_strategy: str
    approval_required: bool
    status: str
    review_comment: str | None
    runtime_artifact_id: uuid.UUID | None
    promoted_artifact_id: uuid.UUID | None
    quality_gate: AutomationDraftQualityGateRead = Field(
        default_factory=AutomationDraftQualityGateRead,
    )
