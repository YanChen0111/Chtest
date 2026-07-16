from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.projects.models import Project, TimestampMixin, uuid_pk


def json_dict_column() -> Mapped[dict[str, Any]]:
    return mapped_column(
        MutableDict.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=dict,
        nullable=False,
    )


def json_list_column() -> Mapped[list[Any]]:
    return mapped_column(
        MutableList.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=list,
        nullable=False,
    )


class KnowledgeIngestionRun(TimestampMixin, Base):
    __tablename__ = "knowledge_ingestion_runs"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "idempotency_key",
            name="uq_knowledge_ingestion_runs_project_idempotency",
        ),
        CheckConstraint("parsed_count >= 0", name="ck_knowledge_ingestion_runs_parsed_count"),
        CheckConstraint(
            "extracted_card_count >= 0",
            name="ck_knowledge_ingestion_runs_extracted_count",
        ),
        CheckConstraint("skipped_count >= 0", name="ck_knowledge_ingestion_runs_skipped_count"),
        CheckConstraint("failed_count >= 0", name="ck_knowledge_ingestion_runs_failed_count"),
        Index("ix_knowledge_ingestion_runs_project_created", "project_id", "created_at"),
        Index(
            "ix_knowledge_ingestion_runs_project_status_source",
            "project_id",
            "status",
            "source_type",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False, default="artifact")
    source_refs_json: Mapped[list[Any]] = json_list_column()
    input_artifact_ids_json: Mapped[list[Any]] = json_list_column()
    parser_name: Mapped[str] = mapped_column(String(120), nullable=False, default="deterministic")
    parser_version: Mapped[str] = mapped_column(String(80), nullable=False, default="v1")
    config_snapshot_json: Mapped[dict[str, Any]] = json_dict_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="created")
    parsed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    extracted_card_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_artifact_ids_json: Mapped[list[Any]] = json_list_column()
    ai_task_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[Project] = relationship()
    ai_task: Mapped[AITask | None] = relationship()
    cards: Mapped[list["TestKnowledgeCard"]] = relationship(back_populates="ingestion_run")


class TestKnowledgeCard(TimestampMixin, Base):
    __tablename__ = "test_knowledge_cards"
    __test__ = False
    __table_args__ = (
        UniqueConstraint(
            "source_artifact_id",
            "source_quote_hash",
            name="uq_test_knowledge_cards_source_quote",
        ),
        CheckConstraint(
            "status != 'duplicate' OR duplicate_of_card_id IS NOT NULL",
            name="ck_test_knowledge_cards_duplicate_target",
        ),
        Index("ix_test_knowledge_cards_project_source", "project_id", "source_artifact_id"),
        Index("ix_test_knowledge_cards_ingestion_run", "ingestion_run_id"),
        Index("ix_test_knowledge_cards_duplicate_of", "duplicate_of_card_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_artifact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_document_version: Mapped[str] = mapped_column(String(80), nullable=False, default="v1")
    source_section: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_quote_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    source_locator_json: Mapped[dict[str, Any]] = json_dict_column()
    source_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingestion_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_ingestion_runs.id", ondelete="RESTRICT"),
        nullable=True,
    )
    knowledge_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    module_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    api_endpoint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    risk_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    case_type_hint: Mapped[str | None] = mapped_column(String(80), nullable=True)
    applicability: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=70)
    safe_to_show: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allowed_for_prompt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="extracted")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    duplicate_of_card_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_knowledge_cards.id", ondelete="RESTRICT"),
        nullable=True,
    )
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[Project] = relationship()
    source_artifact: Mapped[Artifact] = relationship()
    ingestion_run: Mapped[KnowledgeIngestionRun | None] = relationship(back_populates="cards")
    duplicate_of_card: Mapped[TestKnowledgeCard | None] = relationship(
        remote_side="TestKnowledgeCard.id",
        foreign_keys=[duplicate_of_card_id],
    )
    embedding_indexes: Mapped[list["TestKnowledgeEmbeddingIndex"]] = relationship(
        back_populates="knowledge_card",
        cascade="all, delete-orphan",
    )


class KnowledgeRetrievalRun(TimestampMixin, Base):
    __tablename__ = "knowledge_retrieval_runs"
    __table_args__ = (
        CheckConstraint("candidate_count >= 0", name="ck_knowledge_retrieval_runs_candidate_count"),
        CheckConstraint("evidence_count >= 0", name="ck_knowledge_retrieval_runs_evidence_count"),
        CheckConstraint(
            "evidence_count <= candidate_count",
            name="ck_knowledge_retrieval_runs_evidence_not_above_candidates",
        ),
        CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name="ck_knowledge_retrieval_runs_latency",
        ),
        CheckConstraint(
            "(consumer_entity_type IS NULL) = (consumer_entity_id IS NULL)",
            name="ck_knowledge_retrieval_runs_consumer_pair",
        ),
        Index("ix_knowledge_retrieval_runs_project_created", "project_id", "created_at", "id"),
        Index(
            "ix_knowledge_retrieval_runs_project_status",
            "project_id",
            "status",
            "created_at",
            "id",
        ),
        Index(
            "ix_knowledge_retrieval_runs_project_provider",
            "project_id",
            "provider_type",
            "created_at",
            "id",
        ),
        Index(
            "ix_knowledge_retrieval_runs_project_consumer",
            "project_id",
            "consumer_entity_type",
            "consumer_entity_id",
            "created_at",
            "id",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    ai_task_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("ai_tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    consumer_entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    consumer_entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    adapter_name: Mapped[str] = mapped_column(String(120), nullable=False, default="default")
    provider_type: Mapped[str] = mapped_column(String(80), nullable=False, default="deterministic_local")
    requested_retrieval_mode: Mapped[str] = mapped_column(String(80), nullable=False, default="hybrid")
    retrieval_mode: Mapped[str] = mapped_column(String(80), nullable=False, default="hybrid")
    adapter_config_snapshot_json: Mapped[dict[str, Any]] = json_dict_column()
    query_text_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    query_text_redacted: Mapped[str] = mapped_column(Text, nullable=False)
    filters_json: Mapped[dict[str, Any]] = json_dict_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="created")
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    degraded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fallback_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="RESTRICT"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[Project] = relationship()
    ai_task: Mapped[AITask | None] = relationship()
    evidence_artifact: Mapped[Artifact | None] = relationship(foreign_keys=[evidence_artifact_id])
    evidence_rows: Mapped[list["KnowledgeEvidence"]] = relationship(
        back_populates="retrieval_run",
        cascade="all, delete-orphan",
    )


class TestKnowledgeRelationship(TimestampMixin, Base):
    __tablename__ = "test_knowledge_relationships"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "source_entity_type",
            "source_entity_id",
            "target_entity_type",
            "target_entity_id",
            "relationship_type",
            name="uq_test_knowledge_relationship_edge",
        ),
        Index("ix_test_knowledge_relationship_project_type", "project_id", "relationship_type"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    source_entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    target_entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(120), nullable=False)
    evidence_artifact_ids_json: Mapped[list[Any]] = json_list_column()
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    metadata_json: Mapped[dict[str, Any]] = json_dict_column()

    project: Mapped[Project] = relationship()


class KnowledgeFeedbackEvent(TimestampMixin, Base):
    __tablename__ = "knowledge_feedback_events"
    __table_args__ = (
        Index("ix_knowledge_feedback_project_status", "project_id", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    source_entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    proposed_knowledge_type: Mapped[str] = mapped_column(String(80), nullable=False)
    proposed_content_json: Mapped[dict[str, Any]] = json_dict_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="proposed")
    evidence_artifact_ids_json: Mapped[list[Any]] = json_list_column()
    resulting_card_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("test_knowledge_cards.id", ondelete="SET NULL"), nullable=True
    )
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[Project] = relationship()
    resulting_card: Mapped[TestKnowledgeCard | None] = relationship(foreign_keys=[resulting_card_id])


class KnowledgeEvidence(TimestampMixin, Base):
    __tablename__ = "knowledge_evidence"
    __table_args__ = (
        UniqueConstraint(
            "retrieval_run_id",
            "knowledge_card_id",
            name="uq_knowledge_evidence_run_card",
        ),
        CheckConstraint(
            "metadata_score >= 0 AND metadata_score <= 1",
            name="ck_knowledge_evidence_metadata_score",
        ),
        CheckConstraint(
            "keyword_score >= 0 AND keyword_score <= 1",
            name="ck_knowledge_evidence_keyword_score",
        ),
        CheckConstraint(
            "vector_score IS NULL OR (vector_score >= 0 AND vector_score <= 1)",
            name="ck_knowledge_evidence_vector_score",
        ),
        CheckConstraint(
            "rerank_score IS NULL OR (rerank_score >= 0 AND rerank_score <= 1)",
            name="ck_knowledge_evidence_rerank_score",
        ),
        CheckConstraint(
            "final_score >= 0 AND final_score <= 1",
            name="ck_knowledge_evidence_final_score",
        ),
        Index("ix_knowledge_evidence_run_score", "retrieval_run_id", "final_score"),
        Index("ix_knowledge_evidence_project_card", "project_id", "knowledge_card_id"),
        Index("ix_knowledge_evidence_source_artifact", "source_artifact_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    retrieval_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_retrieval_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    knowledge_card_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_knowledge_cards.id", ondelete="RESTRICT"),
        nullable=False,
    )
    source_artifact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    source_locator_json: Mapped[dict[str, Any]] = json_dict_column()
    metadata_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    keyword_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vector_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rerank_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    matched_terms_json: Mapped[list[Any]] = json_list_column()
    retrieval_reason: Mapped[str] = mapped_column(Text, nullable=False)
    card_status_snapshot: Mapped[str] = mapped_column(String(40), nullable=False)
    safe_to_show: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allowed_for_prompt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    project: Mapped[Project] = relationship()
    retrieval_run: Mapped[KnowledgeRetrievalRun] = relationship(back_populates="evidence_rows")
    knowledge_card: Mapped[TestKnowledgeCard] = relationship()
    source_artifact: Mapped[Artifact] = relationship(foreign_keys=[source_artifact_id])


class TestKnowledgeEmbeddingIndex(TimestampMixin, Base):
    __tablename__ = "test_knowledge_embedding_index"
    __test__ = False
    __table_args__ = (
        UniqueConstraint(
            "knowledge_card_id",
            "embedding_model",
            name="uq_test_knowledge_embedding_card_model",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    knowledge_card_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("test_knowledge_cards.id", ondelete="CASCADE"),
        nullable=False,
    )
    index_kind: Mapped[str] = mapped_column(String(80), nullable=False, default="test_knowledge_card")
    embedding_provider: Mapped[str] = mapped_column(String(80), nullable=False, default="deterministic_local")
    embedding_model: Mapped[str] = mapped_column(String(120), nullable=False, default="deterministic-hashing-v1")
    embedding_dim: Mapped[int] = mapped_column(Integer, nullable=False, default=64)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding_json: Mapped[list[Any]] = json_list_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="indexed")
    metadata_json: Mapped[dict[str, Any]] = json_dict_column()

    project: Mapped[Project] = relationship()
    knowledge_card: Mapped[TestKnowledgeCard] = relationship(back_populates="embedding_indexes")
