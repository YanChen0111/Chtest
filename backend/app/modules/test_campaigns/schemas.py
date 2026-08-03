from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TestCampaignScopeFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    scope_statement: str = Field(min_length=1, max_length=8000)
    target_environment_id: uuid.UUID
    target_version_ref: str = Field(min_length=1, max_length=160)
    exit_conditions: list[str] = Field(min_length=1, max_length=50)
    requirement_ids: list[uuid.UUID] = Field(default_factory=list, max_length=500)
    risk_ids: list[uuid.UUID] = Field(default_factory=list, max_length=500)
    test_plan_snapshot_ids: list[uuid.UUID] = Field(default_factory=list, max_length=200)
    approved_case_ids: list[uuid.UUID] = Field(default_factory=list, max_length=1000)


class TestCampaignCreate(TestCampaignScopeFields):
    created_by: str = Field(default="Default User", min_length=1, max_length=120)


class TestCampaignEdit(TestCampaignScopeFields):
    expected_version: int = Field(ge=0)
    reviewer: str = Field(default="Default User", min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)


class TestCampaignAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    reviewer: str = Field(default="Default User", min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)


class TestCampaignContinue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=0)
    approval_decision_id: uuid.UUID


class CoverageRowRead(BaseModel):
    kind: Literal["requirement", "risk", "test_plan", "approved_case"]
    target_id: uuid.UUID
    label: str
    coverage_status: Literal["covered", "gap"]
    evidence_case_ids: list[uuid.UUID] = Field(default_factory=list)
    evidence_snapshot_id: uuid.UUID | None = None
    gap_reason: str | None = None


class TestCampaignWorkflowRead(BaseModel):
    run_id: uuid.UUID
    stage: str
    state: str
    lock_version: int
    snapshot_id: uuid.UUID
    snapshot_hash: str
    snapshot_iteration: int
    approval_decision_id: uuid.UUID | None = None
    can_continue: bool = False


class TestCampaignRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    scope_statement: str
    target_environment_id: uuid.UUID
    target_version_ref: str
    exit_conditions: list[str]
    requirement_ids: list[uuid.UUID]
    risk_ids: list[uuid.UUID]
    test_plan_snapshot_ids: list[uuid.UUID]
    approved_case_ids: list[uuid.UUID]
    coverage_rows: list[CoverageRowRead]
    status: str
    workflow: TestCampaignWorkflowRead
    created_at: str
    updated_at: str
