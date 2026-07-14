from __future__ import annotations

import uuid
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.modules.knowledge import postgres_adapter


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
    assert "WITH text_candidates AS MATERIALIZED" in compiled
    assert "vector_candidates AS MATERIALIZED" in compiled
    assert "i.embedding_vector::vector(64) <=> CAST(%(query_vector)s AS vector(64))" in compiled
    assert "i.embedding_model = %(embedding_model)s" in compiled
    assert "i.embedding_dim = %(embedding_dim)s" in compiled
    assert "i.status = 'indexed'" in compiled
    assert "c.safe_to_show = true" in compiled
    assert "c.allowed_for_prompt = true" in compiled
    assert "[0.0, 0.0, 0.0" not in compiled
