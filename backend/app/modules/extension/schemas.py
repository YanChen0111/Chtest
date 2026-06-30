from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class KnowledgeAdapterRead(BaseModel):
    project_id: uuid.UUID
    adapter_name: str
    status: str
    provider_type: str
    config: dict[str, Any] = Field(default_factory=dict)
    safety_policy: dict[str, Any] = Field(default_factory=dict)
    last_checked_at: datetime | None = None
    notes: str | None = None
    used_knowledge: bool = False


class KnowledgeAdapterUpdate(BaseModel):
    adapter_name: str = Field(default="default", min_length=1, max_length=120)
    status: str = "configured_stub"
    provider_type: str = "stub"
    config: dict[str, Any] = Field(default_factory=dict)
    safety_policy: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
