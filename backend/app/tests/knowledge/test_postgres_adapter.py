from __future__ import annotations

import hashlib
import uuid
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.modules.knowledge import postgres_adapter
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.extension.models import KnowledgeAdapterConfig
from backend.app.modules.knowledge import service as knowledge_service
from backend.app.modules.knowledge.models import TestKnowledgeCard
from backend.app.modules.projects.models import Project, Workspace


def test_capability_detection_is_disabled_for_sqlite() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    with Session(engine) as session:
        capabilities = postgres_adapter.detect_capabilities(session)

    assert capabilities.postgresql is False
    assert capabilities.full_text is False
    assert capabilities.vector_search is False


def test_capability_detection_reports_postgres_native_surface() -> None:
    class FakeResult:
        def mappings(self):
            return self

        def one(self):
            return {
                "vector_extension": True,
                "vector_column": True,
                "fts_index": True,
                "vector_index": False,
            }

    class FakeSession:
        bind = SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))

        def execute(self, _statement, _params):
            return FakeResult()

    capabilities = postgres_adapter.detect_capabilities(FakeSession())

    assert capabilities.postgresql is True
    assert capabilities.full_text is True
    assert capabilities.full_text_index is True
    assert capabilities.vector_search is True
    assert capabilities.vector_index is False
    assert capabilities.snapshot()["probe_error"] is None


def test_capability_probe_failure_is_reported_as_unavailable() -> None:
    class FakeSession:
        bind = SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))

        def execute(self, _statement, _params):
            raise SQLAlchemyError("probe failed")

    capabilities = postgres_adapter.detect_capabilities(FakeSession())

    assert capabilities.postgresql is True
    assert capabilities.full_text is False
    assert capabilities.vector_search is False
    assert capabilities.probe_error == "SQLAlchemyError"


def test_keyword_statement_uses_postgres_full_text_and_bound_filters() -> None:
    query_text = "private coupon checkout query"
    statement, params = postgres_adapter.build_search_statement(
        project_id=uuid.uuid4(),
        query_text=query_text,
        query_vector=None,
        embedding_model="deterministic-hashing-v1",
        include_keyword=True,
        statuses={"approved"},
        filters={"knowledge_types": ["BoundaryCondition"]},
        limit=5,
        min_vector_similarity=0.05,
        use_vector=False,
    )

    compiled = str(
        statement.params(**params).compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"render_postcompile": True},
        ),
    )
    assert "to_tsvector" in compiled
    assert "websearch_to_tsquery" in compiled
    assert "c.project_id = %(project_id)s" in compiled
    assert "c.status IN" in compiled
    assert "c.knowledge_type IN" in compiled
    assert "<=>" not in compiled
    assert query_text not in compiled


def test_hybrid_statement_uses_bound_pgvector_cosine_distance() -> None:
    statement, params = postgres_adapter.build_search_statement(
        project_id=uuid.uuid4(),
        query_text="coupon checkout",
        query_vector=[0.0] * 64,
        embedding_model="deterministic-hashing-v1",
        include_keyword=True,
        statuses={"approved"},
        filters={},
        limit=5,
        min_vector_similarity=0.05,
        use_vector=True,
    )

    compiled = str(
        statement.params(**params).compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"render_postcompile": True},
        ),
    )
    assert "text_candidates AS MATERIALIZED" in compiled
    assert "vector_pool AS MATERIALIZED" in compiled
    assert "vector_candidates AS MATERIALIZED" in compiled
    assert "i.embedding_vector::vector(64) <=> CAST(%(query_vector)s AS vector(64))" in compiled
    assert "i.embedding_model = %(embedding_model)s" in compiled
    assert "i.embedding_dim = %(embedding_dim)s" in compiled
    assert "i.status = 'indexed'" in compiled
    assert "c.safe_to_show = true" in compiled
    assert "c.allowed_for_prompt = true" in compiled
    assert "[0.0, 0.0, 0.0" not in compiled


def test_vector_statement_excludes_full_text_candidates() -> None:
    statement, params = postgres_adapter.build_search_statement(
        project_id=uuid.uuid4(),
        query_text="coupon checkout",
        query_vector=[0.0] * 64,
        embedding_model="deterministic-hashing-v1",
        include_keyword=False,
        statuses={"approved"},
        filters={},
        limit=5,
        min_vector_similarity=0.05,
        use_vector=True,
    )

    compiled = str(
        statement.params(**params).compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"render_postcompile": True},
        ),
    )
    assert "SELECT NULL::uuid AS knowledge_card_id" in compiled
    assert "WHERE false" in compiled
    assert "websearch_to_tsquery" not in compiled
    assert "i.embedding_dim = %(embedding_dim)s" in compiled


def test_native_match_is_normalized_to_provider_neutral_evidence(monkeypatch) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        workspace = Workspace(name="Personal Workspace")
        session.add(workspace)
        session.flush()
        project = Project(workspace_id=workspace.id, name="Postgres Adapter Project")
        session.add(project)
        session.flush()
        source = Artifact(
            project_id=project.id,
            owner_entity_type="Project",
            owner_entity_id=project.id,
            artifact_type="context_markdown",
            file_path=f"projects/{project.id}/context-artifacts/source.md",
            mime_type="text/markdown",
            size_bytes=32,
            sha256="1" * 64,
            metadata_json={"safe_to_show": True, "allowed_for_prompt": True},
        )
        session.add(source)
        session.flush()
        card = TestKnowledgeCard(
            project_id=project.id,
            source_artifact_id=source.id,
            source_quote_hash="sha256:" + "2" * 64,
            knowledge_type="BoundaryCondition",
            title="Expired coupon boundary",
            content="Expired coupons cannot be used during checkout.",
            applicability="case_generation",
            status="approved",
            safe_to_show=True,
            allowed_for_prompt=True,
        )
        session.add(card)
        session.add(
            KnowledgeAdapterConfig(
                project_id=project.id,
                adapter_name="default",
                status="ready",
                provider_type="postgres_hybrid",
                config_json={"embedding_dim": 64, "embedding_model": "deterministic-hashing-v1"},
            ),
        )
        session.flush()
        content_hash = hashlib.sha256(
            knowledge_service.embedding_text_for_card(card).encode("utf-8"),
        ).hexdigest()
        capabilities = postgres_adapter.PostgresKnowledgeCapabilities(
            postgresql=True,
            full_text=True,
            full_text_index=True,
            vector_extension=True,
            vector_column=True,
            vector_index=True,
        )
        observed: dict[str, object] = {}

        monkeypatch.setattr(postgres_adapter, "detect_capabilities", lambda _session: capabilities)

        def fake_search(_session, **kwargs):
            observed.update(kwargs)
            return [
                postgres_adapter.PostgresKnowledgeMatch(
                    knowledge_card_id=card.id,
                    keyword_score=0.4,
                    vector_score=0.8,
                    embedding_model="deterministic-hashing-v1",
                    embedding_dim=64,
                    content_hash=content_hash,
                ),
            ]

        monkeypatch.setattr(postgres_adapter, "search_postgres_knowledge", fake_search)

        result = knowledge_service.match_configured_knowledge_cards(
            session,
            project_id=project.id,
            adapter_name="default",
            query_text="expired coupon checkout",
            limit=5,
            approved_only=True,
            filters={},
            retrieval_mode="hybrid",
        )

    assert observed["include_keyword"] is True
    assert result.provider_type == "postgres_hybrid"
    assert result.actual_mode == "hybrid"
    assert result.vector_available is True
    assert result.items[0]["keyword_score"] == 0.4
    assert result.items[0]["vector_score"] == 0.8
    assert result.items[0]["final_score"] == 0.6
    assert "embedding_vector" not in result.items[0]
    assert "vector_distance" not in result.items[0]
