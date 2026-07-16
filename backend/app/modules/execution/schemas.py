from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field, model_validator

from backend.app.modules.ai_runtime.schemas import ArtifactRead


class TestRunCreateRequest(BaseModel):
    project_id: uuid.UUID
    automation_draft_id: uuid.UUID | None = None
    test_command_id: uuid.UUID | None = None
    reason: str | None = None
    runner_mode: str = "local_subprocess"

    @model_validator(mode="after")
    def require_one_execution_source(self) -> TestRunCreateRequest:
        source_count = sum(
            source is not None
            for source in (self.automation_draft_id, self.test_command_id)
        )
        if source_count != 1:
            raise ValueError("Exactly one of automation_draft_id or test_command_id is required.")
        return self


class TestResultRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    test_run_id: uuid.UUID
    test_name: str
    test_file: str | None
    status: str
    duration_ms: int | None
    failure_message: str | None
    failure_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TestRunRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    automation_draft_id: uuid.UUID | None
    test_command_id: uuid.UUID | None
    tool_invocation_id: uuid.UUID | None
    name: str
    command: str
    working_directory: str
    runner_mode: str
    run_workspace: str | None
    repository_readonly: bool
    network_enabled: bool
    runtime_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    dependency_snapshot_artifact_id: uuid.UUID | None
    environment_snapshot_artifact_id: uuid.UUID | None
    status: str
    exit_code: int | None
    duration_ms: int | None
    parsed_result: dict[str, Any] = Field(default_factory=dict)
    test_results: list[TestResultRead] = Field(default_factory=list)
    artifacts: list[ArtifactRead] = Field(default_factory=list)
