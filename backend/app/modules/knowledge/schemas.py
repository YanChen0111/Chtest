from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TestKnowledgeCardExtractRequest(BaseModel):
    project_id: uuid.UUID
    source_artifact_id: uuid.UUID


class TestKnowledgeCardRetrieveRequest(BaseModel):
    project_id: uuid.UUID
    query_text: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)
    approved_only: bool = False


class TestKnowledgeCardExtractBatchRequest(BaseModel):
    project_id: uuid.UUID
    source_artifact_ids: list[uuid.UUID] | None = None


class TestKnowledgeCardReviewRequest(BaseModel):
    project_id: uuid.UUID
    status: str


class TestKnowledgeCardRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    source_artifact_id: uuid.UUID
    source_document_version: str
    source_section: str | None
    source_quote_hash: str
    knowledge_type: str
    title: str
    content: str
    module_key: str | None
    api_endpoint: str | None
    risk_type: str | None
    case_type_hint: str | None
    applicability: str | None
    confidence: int
    safe_to_show: bool
    allowed_for_prompt: bool
    status: str
    created_at: datetime


class TestKnowledgeCardListRead(BaseModel):
    items: list[TestKnowledgeCardRead] = Field(default_factory=list)
    total: int


class TestKnowledgeCardExtractRead(BaseModel):
    source_artifact_id: uuid.UUID
    created_count: int
    skipped_count: int
    items: list[TestKnowledgeCardRead] = Field(default_factory=list)


class TestKnowledgeCardExtractBatchRead(BaseModel):
    project_id: uuid.UUID
    source_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    created_count: int
    skipped_count: int
    items: list[TestKnowledgeCardRead] = Field(default_factory=list)


class TestKnowledgeCardRetrievalRead(BaseModel):
    project_id: uuid.UUID
    query_text: str
    approved_only: bool
    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int


class TestKnowledgeIndexRebuildRequest(BaseModel):
    project_id: uuid.UUID
    knowledge_card_ids: list[uuid.UUID] | None = None
    embedding_model: str = Field(default="deterministic-hashing-v1", min_length=1, max_length=120)
    embedding_dim: int = Field(default=64, ge=16, le=512)


class TestKnowledgeIndexRebuildRead(BaseModel):
    project_id: uuid.UUID
    indexed_count: int
    skipped_count: int
    embedding_model: str
    embedding_dim: int
    items: list[dict[str, Any]] = Field(default_factory=list)


class TestKnowledgeIndexRead(BaseModel):
    project_id: uuid.UUID
    total: int
    indexed_count: int
    embedding_models: list[str] = Field(default_factory=list)
    items: list[dict[str, Any]] = Field(default_factory=list)


class TestKnowledgeGraphRead(BaseModel):
    project_id: uuid.UUID
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    coverage: dict[str, Any] = Field(default_factory=dict)
