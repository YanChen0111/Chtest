from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RequirementCreate(BaseModel):
    project_id: uuid.UUID
    module_id: uuid.UUID | None = None
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    source_type: Literal["manual"] = "manual"
    source_ref: str | None = None


class RequirementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    module_id: uuid.UUID | None
    title: str
    content: str
    source_type: str
    source_ref: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class RequirementListRead(BaseModel):
    items: list[RequirementRead]
    total: int


class RequirementReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    requirement_id: uuid.UUID
    ai_task_id: uuid.UUID
    completeness_score: int
    clarity_score: int
    consistency_score: int
    testability_score: int
    feasibility_score: int
    logic_score: int
    overall_score: int
    issues_json: list[Any]
    clarification_questions_json: list[Any]
    test_design_notes_json: list[Any]
    status: str
    created_at: datetime
    updated_at: datetime


class RiskItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    requirement_review_id: uuid.UUID | None
    title: str
    risk_level: str
    category: str
    impact: str
    suggestion: str
    status: str
    created_at: datetime
    updated_at: datetime
