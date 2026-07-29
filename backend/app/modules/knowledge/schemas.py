from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class KnowledgeRetrievalFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    module_keys: list[Annotated[str, Field(min_length=1, max_length=120)]] = Field(
        default_factory=list,
        max_length=50,
    )
    knowledge_types: list[Annotated[str, Field(min_length=1, max_length=80)]] = Field(
        default_factory=list,
        max_length=50,
    )
    risk_types: list[Annotated[str, Field(min_length=1, max_length=80)]] = Field(
        default_factory=list,
        max_length=50,
    )
    api_endpoints: list[Annotated[str, Field(min_length=1, max_length=255)]] = Field(
        default_factory=list,
        max_length=50,
    )


class KnowledgeRetrievalRunCreateRequest(BaseModel):
    project_id: uuid.UUID
    query_text: str = Field(min_length=1, max_length=2000)
    filters: KnowledgeRetrievalFilters = Field(default_factory=KnowledgeRetrievalFilters)
    consumer_entity_type: Literal[
        "Requirement",
        "CaseGenerationTask",
        "TestCase",
        "AutomationPlan",
        "AITask",
    ] | None = None
    consumer_entity_id: uuid.UUID | None = None
    adapter_name: str = Field(default="default", min_length=1, max_length=120)
    retrieval_mode: Literal["metadata", "keyword", "vector", "hybrid"] = "hybrid"
    approved_only: bool = True
    limit: int = Field(default=12, ge=1, le=50)

    @model_validator(mode="after")
    def validate_consumer_pair(self) -> "KnowledgeRetrievalRunCreateRequest":
        if (self.consumer_entity_type is None) != (self.consumer_entity_id is None):
            raise ValueError("consumer_entity_type and consumer_entity_id must be provided together")
        return self


class KnowledgeEvidenceRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    retrieval_run_id: uuid.UUID
    knowledge_card_id: uuid.UUID
    source_artifact_id: uuid.UUID
    knowledge_type: str
    title: str
    snippet: str
    source_locator: dict[str, Any]
    metadata_score: float
    keyword_score: float
    vector_score: float | None
    rerank_score: float | None
    final_score: float
    matched_terms: list[str] = Field(default_factory=list)
    retrieval_reason: str
    card_status_snapshot: str
    current_card_status: str
    safe_to_show: bool
    allowed_for_prompt: bool
    currently_prompt_eligible: bool


class KnowledgeRetrievalArtifactRead(BaseModel):
    id: uuid.UUID
    artifact_type: str
    mime_type: str
    size_bytes: int
    sha256: str
    safe_to_show: bool
    download_url: str


class KnowledgeRetrievalRunRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    ai_task_id: uuid.UUID | None
    consumer_entity_type: str | None
    consumer_entity_id: uuid.UUID | None
    adapter_name: str
    provider_type: str
    requested_retrieval_mode: str
    retrieval_mode: str
    adapter_config_snapshot: dict[str, Any]
    query_text_hash: str
    query_text_redacted: str
    filters: dict[str, Any]
    status: str
    candidate_count: int
    evidence_count: int
    latency_ms: int | None
    degraded: bool
    fallback_reason: str | None
    error_code: str | None
    error_message: str | None
    evidence_artifact_id: uuid.UUID | None
    evidence_artifact: KnowledgeRetrievalArtifactRead | None
    items: list[KnowledgeEvidenceRead] = Field(default_factory=list)
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class KnowledgeRetrievalRunListRead(BaseModel):
    items: list[KnowledgeRetrievalRunRead] = Field(default_factory=list)
    total: int
    next_cursor: str | None = None


class EvidenceTraceArtifactRefRead(BaseModel):
    id: uuid.UUID
    artifact_type: str
    mime_type: str
    safe_to_show: bool
    download_url: str


class EvidenceTraceNodeRead(BaseModel):
    stage: str
    entity_type: str
    entity_id: uuid.UUID
    status: str
    timestamp: datetime
    summary: str
    artifact_refs: list[EvidenceTraceArtifactRefRead] = Field(default_factory=list)
    evidence_ids: list[uuid.UUID] = Field(default_factory=list)
    source_locator: dict[str, Any] = Field(default_factory=dict)
    provider_type: str | None = None
    requested_retrieval_mode: str | None = None
    retrieval_mode: str | None = None
    degraded: bool | None = None
    fallback_reason: str | None = None
    latency_ms: int | None = None


class EvidenceTraceStageRead(BaseModel):
    name: str
    items: list[EvidenceTraceNodeRead] = Field(default_factory=list)


class EvidenceTraceRead(BaseModel):
    project_id: uuid.UUID
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    query: str | None = None
    stages: list[EvidenceTraceStageRead] = Field(default_factory=list)
    total: int


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
    replace_unreviewed: bool = False


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


class TestKnowledgeRelationshipCreateRequest(BaseModel):
    project_id: uuid.UUID
    source_entity_type: str = Field(min_length=1, max_length=80)
    source_entity_id: uuid.UUID
    target_entity_type: str = Field(min_length=1, max_length=80)
    target_entity_id: uuid.UUID
    relationship_type: str = Field(min_length=1, max_length=120)
    evidence_artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    confidence: int = Field(default=100, ge=0, le=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeFeedbackCreateRequest(BaseModel):
    project_id: uuid.UUID
    source_entity_type: str = Field(min_length=1, max_length=80)
    source_entity_id: uuid.UUID
    proposed_knowledge_type: str = Field(min_length=1, max_length=80)
    proposed_content: dict[str, Any] = Field(default_factory=dict)
    evidence_artifact_ids: list[uuid.UUID] = Field(default_factory=list)


class KnowledgeFeedbackReviewRequest(BaseModel):
    status: str
    review_comment: str | None = Field(default=None, max_length=2000)
