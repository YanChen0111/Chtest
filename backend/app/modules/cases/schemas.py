from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


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
