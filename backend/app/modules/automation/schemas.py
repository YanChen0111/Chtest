from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class AutomationDraftCreateRequest(BaseModel):
    project_id: uuid.UUID
    test_case_id: uuid.UUID | None = None
    requirement_id: uuid.UUID | None = None
    target_framework: str = "pytest"
    prompt_version: str = "automation_draft_generation:v1"
    skill_version: str = "automation-draft-skill:v1"
    model_provider: str = "mock"
    model_name: str = "mock-automation-draft"


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


class AutomationDraftRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    test_case_id: uuid.UUID | None
    requirement_id: uuid.UUID | None
    ai_task_id: uuid.UUID
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
