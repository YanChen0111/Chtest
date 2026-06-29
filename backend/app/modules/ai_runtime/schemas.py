from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AITaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None
    project_id: uuid.UUID
    agent_name: str
    task_type: str
    prompt_version_id: uuid.UUID
    skill_version_id: uuid.UUID
    model_provider: str
    model_name: str
    status: str
    input_json: dict[str, Any]
    output_json: dict[str, Any]
    error_json: dict[str, Any] | None
    token_usage_json: dict[str, Any]
    context_artifact_ids: list[uuid.UUID]
    started_at: datetime | None
    finished_at: datetime | None


class ArtifactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None
    project_id: uuid.UUID
    owner_entity_type: str
    owner_entity_id: uuid.UUID
    artifact_type: str
    file_path: str
    mime_type: str
    size_bytes: int
    sha256: str
    metadata_json: dict[str, Any]


class LLMCallLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None
    project_id: uuid.UUID
    ai_task_id: uuid.UUID
    prompt_version_id: uuid.UUID
    skill_version_id: uuid.UUID
    provider: str
    model_name: str
    call_index: int
    status: str
    request_artifact_id: uuid.UUID | None
    response_artifact_id: uuid.UUID | None
    parsed_artifact_id: uuid.UUID | None
    schema_validation_artifact_id: uuid.UUID | None
    input_summary_json: dict[str, Any]
    output_summary_json: dict[str, Any]
    token_usage_json: dict[str, Any]
    latency_ms: int | None
    error_json: dict[str, Any] | None
    started_at: datetime | None
    finished_at: datetime | None
