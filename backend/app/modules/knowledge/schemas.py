from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeIngestionSourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: uuid.UUID


class KnowledgeIngestionRunCreateRequest(BaseModel):
    project_id: uuid.UUID
    source_type: Literal[
        "requirement",
        "openapi",
        "api_document",
        "test_design",
        "historical_case",
        "failure_analysis",
        "report",
        "artifact",
    ] = "artifact"
    source_refs: list[KnowledgeIngestionSourceRef] = Field(min_length=1, max_length=100)
    parser_name: str = Field(default="deterministic", min_length=1, max_length=120)
    parser_version: str = Field(default="v1", min_length=1, max_length=80)
    config_snapshot: dict[str, Any] = Field(default_factory=dict)
    extract_cards: bool = True
    force: bool = False


class KnowledgeIngestionArtifactRead(BaseModel):
    id: uuid.UUID
    artifact_type: str
    mime_type: str
    size_bytes: int
    sha256: str
    safe_to_show: bool
    download_url: str


class KnowledgeIngestionRunRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    idempotency_key: str
    source_type: str
    source_refs: list[dict[str, Any]] = Field(default_factory=list)
    input_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    parser_name: str
    parser_version: str
    config_snapshot: dict[str, Any] = Field(default_factory=dict)
    status: str
    parsed_count: int
    extracted_card_count: int
    skipped_count: int
    failed_count: int
    error_code: str | None
    error_message: str | None
    evidence_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    evidence_artifacts: list[KnowledgeIngestionArtifactRead] = Field(default_factory=list)
    produced_card_ids: list[uuid.UUID] = Field(default_factory=list)
    ai_task_id: uuid.UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class KnowledgeIngestionRunListRead(BaseModel):
    items: list[KnowledgeIngestionRunRead] = Field(default_factory=list)
    total: int
    next_cursor: str | None = None


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
    review_comment: str | None = Field(default=None, max_length=2000)
    duplicate_of_card_id: uuid.UUID | None = None


class TestKnowledgeCardRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    source_artifact_id: uuid.UUID
    source_document_version: str
    source_section: str | None
    source_quote_hash: str
    source_locator_json: dict[str, Any]
    source_ref: str | None
    ingestion_run_id: uuid.UUID | None
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
    reviewed_at: datetime | None
    review_comment: str | None
    duplicate_of_card_id: uuid.UUID | None
    last_verified_at: datetime | None
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
