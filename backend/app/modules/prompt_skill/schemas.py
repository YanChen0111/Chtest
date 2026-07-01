from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PromptVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None
    name: str
    version: str
    hash: str
    agent_name: str
    content: str
    input_schema_json: dict[str, Any]
    output_schema_json: dict[str, Any]
    status: str


class PromptVersionListRead(BaseModel):
    items: list[PromptVersionRead]
    total: int


class SkillVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None
    updated_by: uuid.UUID | None
    name: str
    version: str
    hash: str
    applicable_agents: list[str]
    content: str
    quality_gates_json: list[Any]
    forbidden_actions_json: list[Any]
    tool_permissions_json: list[Any]
    status: str


class SkillVersionListRead(BaseModel):
    items: list[SkillVersionRead]
    total: int
