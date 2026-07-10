from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import Artifact
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


class TestKnowledgeCard(TimestampMixin, Base):
    __tablename__ = "test_knowledge_cards"
    __test__ = False

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

    project: Mapped[Project] = relationship()
    source_artifact: Mapped[Artifact] = relationship()
    embedding_indexes: Mapped[list["TestKnowledgeEmbeddingIndex"]] = relationship(
        back_populates="knowledge_card",
        cascade="all, delete-orphan",
    )


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
