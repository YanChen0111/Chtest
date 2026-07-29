from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.modules.workflow_control.policy import ApprovalDecision, ControlledStage, WorkflowKind


class WorkflowRunCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: uuid.UUID
    workflow_kind: WorkflowKind
    subject_ref: str = Field(min_length=1, max_length=255)
    input_payload: dict[str, Any]
    created_by: str = Field(min_length=1, max_length=120)
    initial_stage: ControlledStage | None = None
    completed_stages: list[ControlledStage] | None = None


class HumanReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer: str = Field(min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)


class HumanApprovalCreate(HumanReviewCreate):
    decision: ApprovalDecision


class WorkflowRevisionCreate(HumanReviewCreate):
    input_payload: dict[str, Any]


class WorkflowStageSnapshotRead(BaseModel):
    id: uuid.UUID
    stage: ControlledStage
    stage_iteration: int
    input_snapshot_hash: str
    created_by_actor: str
    created_by_label: str
    created_at: str


class WorkflowRunRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    workflow_kind: WorkflowKind
    subject_ref: str
    current_stage: ControlledStage
    gate_state: str
    input_snapshot_hash: str
    current_snapshot_id: uuid.UUID
    completed_stages: list[ControlledStage]
    lock_version: int
    status: str
    snapshot: WorkflowStageSnapshotRead
