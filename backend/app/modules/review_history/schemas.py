from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReviewHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    related_entity_type: str | None = None
    related_entity_id: uuid.UUID | None = None
    action: str
    from_status: str | None = None
    to_status: str | None = None
    reviewer: str
    comment: str | None = None
    evidence_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ReviewHistoryListRead(BaseModel):
    items: list[ReviewHistoryRead] = Field(default_factory=list)
    total: int
