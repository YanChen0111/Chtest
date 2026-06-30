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
