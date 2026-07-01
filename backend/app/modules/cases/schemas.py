from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CaseGenerationStartRequest(BaseModel):
    project_id: uuid.UUID
    requirement_id: uuid.UUID
    requirement_review_id: uuid.UUID | None = None
    target_test_types: list[str] = Field(default_factory=list)
    prompt_version: Literal["case_generation:v1"] = "case_generation:v1"
    skill_version: Literal["test-case-generation-skill:v1"] = "test-case-generation-skill:v1"
    model_provider: Literal["mock"] = "mock"
    model_name: Literal["mock-case-generator"] = "mock-case-generator"
    use_knowledge: bool = False
    context_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    mock_mode: Literal["success", "schema_invalid"] = "success"


class CaseGenerationStartRead(BaseModel):
    case_generation_task_id: uuid.UUID
    ai_task_id: uuid.UUID
    status: str
    used_knowledge: bool
    used_context_artifact_ids: list[uuid.UUID]


class CaseGenerationTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    requirement_id: uuid.UUID
    requirement_review_id: uuid.UUID | None
    ai_task_id: uuid.UUID
    target_test_types: list[str]
    status: str
    generated_count: int
    created_at: datetime
    updated_at: datetime


class GeneratedCaseCandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    generation_task_id: uuid.UUID
    project_id: uuid.UUID
    module_id: uuid.UUID | None
    title: str
    priority: str
    test_type: str
    precondition: str | None
    steps_json: list[Any]
    expected_results_json: list[Any]
    input_data_json: dict[str, Any]
    tags: list[str]
    requirement_refs_json: list[Any]
    risk_refs_json: list[Any]
    ai_reason: str
    duplicate_of_case_id: uuid.UUID | None
    status: str
    review_comment: str | None
    created_at: datetime
    updated_at: datetime


class GeneratedCaseCandidateListItemRead(BaseModel):
    id: uuid.UUID
    title: str
    priority: str
    test_type: str
    precondition: str | None
    steps: list[Any]
    expected_results: list[Any]
    input_data: dict[str, Any]
    requirement_refs: list[Any]
    risk_refs: list[Any]
    ai_reason: str
    status: str


class GeneratedCaseCandidateListRead(BaseModel):
    items: list[GeneratedCaseCandidateListItemRead]
    total: int


class CaseReviewEditedCase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    priority: str = "P2"
    test_type: str = "functional"
    precondition: str | None = None
    steps: list[Any] = Field(default_factory=list)
    expected_results: list[Any] = Field(default_factory=list)
    input_data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class CaseReviewRequest(BaseModel):
    action: Literal["approve", "approve_after_edit", "reject", "needs_optimization"]
    edited_case: CaseReviewEditedCase | None = None
    review_comment: str | None = None


class CaseReviewRead(BaseModel):
    candidate_id: uuid.UUID
    status: str
    test_case_id: uuid.UUID | None


class CaseMetricsRead(BaseModel):
    generation_task_id: uuid.UUID
    generated_count: int
    approved_count: int
    edited_count: int
    rejected_count: int
    optimization_count: int
    reviewed_count: int
    acceptance_rate: float
    edit_rate: float
    rejection_rate: float
    optimization_rate: float
    review_progress: float
    field_complete_rate: float


class TestCaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    module_id: uuid.UUID | None
    source_candidate_id: uuid.UUID | None
    title: str
    priority: str
    test_type: str
    precondition: str | None
    steps_json: list[Any]
    expected_results_json: list[Any]
    input_data_json: dict[str, Any]
    tags: list[str]
    source_type: str
    review_status: str
    status: str
    created_at: datetime
    updated_at: datetime


class TestCaseListItemRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    module_id: uuid.UUID | None
    source_candidate_id: uuid.UUID | None
    title: str
    priority: str
    test_type: str
    precondition: str | None
    steps: list[Any]
    expected_results: list[Any]
    input_data: dict[str, Any]
    tags: list[str]
    source_type: str
    review_status: str
    status: str


class TestCaseListRead(BaseModel):
    items: list[TestCaseListItemRead]
    total: int
