from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    default_language: str = "python"
    default_test_type: str = "functional"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    default_language: str | None = None
    default_test_type: str | None = None
    status: str | None = None


class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    created_at: datetime


class ProjectSettingsProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    default_language: str | None
    default_test_type: str | None


class ModuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    parent_id: uuid.UUID | None
    name: str
    level: int
    path: str
    sort_order: int
    status: str


class ModuleCreate(BaseModel):
    parent_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=160)
    sort_order: int = 0


class ModuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    sort_order: int | None = None
    status: str | None = None


class ModuleListRead(BaseModel):
    items: list[ModuleRead]
    total: int


class RepositoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    local_path: str
    default_base_branch: str | None
    language_hint: str | None
    status: str


class RepositoryCreate(BaseModel):
    project_id: uuid.UUID
    name: str = Field(min_length=1, max_length=160)
    local_path: str = Field(min_length=1)
    default_base_branch: str | None = "main"
    language_hint: str | None = None


class RepositoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    local_path: str | None = Field(default=None, min_length=1)
    default_base_branch: str | None = None
    language_hint: str | None = None
    status: str | None = None


class RepositoryListRead(BaseModel):
    items: list[RepositoryRead]
    total: int


class EnvironmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    variables_json: dict[str, Any]
    status: str


class EnvironmentCreate(BaseModel):
    project_id: uuid.UUID
    name: str = Field(default="dev", min_length=1, max_length=120)
    variables_json: dict[str, Any] = Field(default_factory=dict)


class EnvironmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    variables_json: dict[str, Any] | None = None
    status: str | None = None


class EnvironmentListRead(BaseModel):
    items: list[EnvironmentRead]
    total: int


class TestCommandRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    repository_id: uuid.UUID | None
    environment_id: uuid.UUID | None
    name: str
    command: str
    working_directory: str
    command_type: str
    timeout_seconds: int
    parse_junit: bool
    parse_coverage: bool
    status: str


class ProjectSettingsRead(BaseModel):
    project: ProjectSettingsProjectRead
    modules: list[ModuleRead]
    repositories: list[RepositoryRead]
    environments: list[EnvironmentRead]
    test_commands: list[TestCommandRead]
    tool_definitions: list[dict[str, Any]]
