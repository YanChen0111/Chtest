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
    retrieval_mode: str | None = None
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


class KnowledgeRetrievalRequest(BaseModel):
    query_text: str = Field(min_length=1)
    adapter_name: str = Field(default="default", min_length=1, max_length=120)
    max_results: int = Field(default=5, ge=1, le=10)
    max_snippet_chars: int = Field(default=320, ge=40, le=1000)


class KnowledgeRetrievalResultItem(BaseModel):
    context_artifact_id: uuid.UUID
    title: str
    source_ref: str
    score: int
    matched_terms: list[str] = Field(default_factory=list)
    snippet: str
    sha256: str
    redaction_applied: bool
    allowed_for_prompt: bool


class KnowledgeRetrievalRead(BaseModel):
    adapter_name: str = "default"
    retrieval_mode: str = "deterministic_local"
    query_text: str
    query_terms: list[str] = Field(default_factory=list)
    used_knowledge: bool = False
    used_context_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    results: list[KnowledgeRetrievalResultItem] = Field(default_factory=list)


class KnowledgeBaseContextArtifactRead(BaseModel):
    id: uuid.UUID
    title: str
    artifact_type: str
    mime_type: str
    source_ref: str
    safe_to_show: bool
    redaction_applied: bool
    allowed_for_prompt: bool
    usage_count: int = 0
    latest_used_at: datetime | None = None
    retrieved_count: int = 0
    latest_retrieved_at: datetime | None = None


class KnowledgeBaseRetrievalResultRead(BaseModel):
    context_artifact_id: uuid.UUID
    title: str
    source_ref: str
    score: int
    matched_terms: list[str] = Field(default_factory=list)
    snippet: str
    sha256: str
    redaction_applied: bool
    allowed_for_prompt: bool


class KnowledgeBaseLatestRetrievalRead(BaseModel):
    ai_task_id: uuid.UUID
    retrieval_evidence_artifact_id: uuid.UUID
    query_terms: list[str] = Field(default_factory=list)
    used_context_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    snippet_count: int
    created_at: datetime
    results: list[KnowledgeBaseRetrievalResultRead] = Field(default_factory=list)


class KnowledgeBaseRead(BaseModel):
    project_id: uuid.UUID
    knowledge_adapter: KnowledgeAdapterRead
    context_artifacts: list[KnowledgeBaseContextArtifactRead] = Field(default_factory=list)
    latest_retrievals: list[KnowledgeBaseLatestRetrievalRead] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)


class ToolDefinitionRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID | None
    name: str
    description: str | None
    tool_type: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    risk_level: str
    approval_required: bool
    timeout_seconds: int
    command_allowlist: list[Any] = Field(default_factory=list)
    allowed_working_directories: list[Any] = Field(default_factory=list)
    forbidden_shell_operators: list[Any] = Field(default_factory=list)
    max_stdout_bytes: int
    max_stderr_bytes: int
    artifact_policy: dict[str, Any] = Field(default_factory=dict)
    is_mcp_ready: bool
    mcp_metadata: dict[str, Any] = Field(default_factory=dict)
    status: str


class ToolDefinitionListRead(BaseModel):
    items: list[ToolDefinitionRead] = Field(default_factory=list)
    total: int
