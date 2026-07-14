from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Uuid, bindparam, column, table, text, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


POSTGRES_FTS_INDEX = "ix_test_knowledge_cards_postgres_fts"
POSTGRES_HNSW_INDEX = "ix_test_knowledge_embedding_vector_hnsw_64"
POSTGRES_SEARCH_TEXT = """
to_tsvector(
    'simple'::regconfig,
    coalesce(c.title, '') || ' ' ||
    coalesce(c.content, '') || ' ' ||
    coalesce(c.module_key, '') || ' ' ||
    coalesce(c.api_endpoint, '') || ' ' ||
    coalesce(c.risk_type, '') || ' ' ||
    coalesce(c.case_type_hint, '')
)
""".strip()


@dataclass(frozen=True)
class PostgresKnowledgeCapabilities:
    postgresql: bool
    full_text: bool
    full_text_index: bool
    vector_extension: bool
    vector_column: bool
    vector_index: bool
    probe_error: str | None = None

    @property
    def vector_search(self) -> bool:
        return self.postgresql and self.vector_extension and self.vector_column

    def snapshot(self) -> dict[str, Any]:
        return {
            "postgresql": self.postgresql,
            "full_text": self.full_text,
            "full_text_index": self.full_text_index,
            "vector_extension": self.vector_extension,
            "vector_column": self.vector_column,
            "vector_index": self.vector_index,
            "probe_error": self.probe_error,
        }


@dataclass(frozen=True)
class PostgresKnowledgeMatch:
    knowledge_card_id: uuid.UUID
    keyword_score: float
    vector_score: float | None
    embedding_model: str | None
    embedding_dim: int | None
    content_hash: str | None


def detect_capabilities(session: Session) -> PostgresKnowledgeCapabilities:
    if session.bind is None or session.bind.dialect.name != "postgresql":
        return PostgresKnowledgeCapabilities(False, False, False, False, False, False)
    try:
        row = session.execute(
            text(
                """
                SELECT
                    EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') AS vector_extension,
                    EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_schema = current_schema()
                          AND table_name = 'test_knowledge_embedding_index'
                          AND column_name = 'embedding_vector'
                    ) AS vector_column,
                    to_regclass(:fts_index) IS NOT NULL AS fts_index,
                    to_regclass(:vector_index) IS NOT NULL AS vector_index
                """,
            ),
            {
                "fts_index": POSTGRES_FTS_INDEX,
                "vector_index": POSTGRES_HNSW_INDEX,
            },
        ).mappings().one()
    except SQLAlchemyError as exc:
        return PostgresKnowledgeCapabilities(
            True,
            False,
            False,
            False,
            False,
            False,
            probe_error=type(exc).__name__,
        )
    return PostgresKnowledgeCapabilities(
        postgresql=True,
        full_text=True,
        full_text_index=bool(row["fts_index"]),
        vector_extension=bool(row["vector_extension"]),
        vector_column=bool(row["vector_column"]),
        vector_index=bool(row["vector_index"]),
    )


def search_postgres_knowledge(
    session: Session,
    *,
    project_id: uuid.UUID,
    query_text: str,
    query_vector: list[float] | None,
    embedding_model: str,
    hnsw_ef_search: int,
    statuses: set[str],
    filters: dict[str, Any],
    limit: int,
    min_vector_similarity: float,
) -> list[PostgresKnowledgeMatch]:
    capabilities = detect_capabilities(session)
    if not capabilities.postgresql or not capabilities.full_text:
        return []
    use_vector = capabilities.vector_search and query_vector is not None
    if use_vector:
        session.execute(
            text("SELECT set_config('hnsw.ef_search', :value, true)"),
            {"value": str(hnsw_ef_search)},
        )
    sql, params = build_search_statement(
        project_id=project_id,
        query_text=query_text,
        query_vector=query_vector,
        embedding_model=embedding_model,
        statuses=statuses,
        filters=filters,
        limit=limit,
        min_vector_similarity=min_vector_similarity,
        use_vector=use_vector,
    )
    rows = session.execute(sql, params).mappings()
    return [
        PostgresKnowledgeMatch(
            knowledge_card_id=uuid.UUID(str(row["knowledge_card_id"])),
            keyword_score=float(row["keyword_score"] or 0.0),
            vector_score=float(row["vector_score"]) if row["vector_score"] is not None else None,
            embedding_model=str(row["embedding_model"]) if row["embedding_model"] else None,
            embedding_dim=int(row["embedding_dim"]) if row["embedding_dim"] is not None else None,
            content_hash=str(row["content_hash"]) if row["content_hash"] else None,
        )
        for row in rows
    ]


def build_search_statement(
    *,
    project_id: uuid.UUID,
    query_text: str,
    query_vector: list[float] | None,
    embedding_model: str,
    statuses: set[str],
    filters: dict[str, Any],
    limit: int,
    min_vector_similarity: float,
    use_vector: bool,
):
    clauses = [
        "c.project_id = :project_id",
        "c.status IN :statuses",
        "c.safe_to_show = true",
        "c.allowed_for_prompt = true",
    ]
    bind_params = [bindparam("statuses", expanding=True)]
    values: dict[str, Any] = {
        "project_id": project_id,
        "statuses": sorted(statuses),
        "query_text": query_text,
        "limit": max(limit * 4, limit),
        "min_vector_similarity": min_vector_similarity,
    }
    filter_columns = {
        "module_keys": "c.module_key",
        "knowledge_types": "c.knowledge_type",
        "risk_types": "c.risk_type",
        "api_endpoints": "c.api_endpoint",
    }
    for key, column_name in filter_columns.items():
        filter_values = list(filters.get(key) or [])
        if filter_values:
            clauses.append(f"{column_name} IN :{key}")
            bind_params.append(bindparam(key, expanding=True))
            values[key] = filter_values

    keyword_score = (
        f"LEAST(1.0, GREATEST(0.0, ts_rank_cd({POSTGRES_SEARCH_TEXT}, "
        "websearch_to_tsquery('simple'::regconfig, :query_text))))"
    )
    base_where = " AND ".join(clauses)
    if use_vector:
        embedding_dim = len(query_vector or [])
        if not 16 <= embedding_dim <= 512:
            raise ValueError("query vector dimension must be between 16 and 512")
        vector_type = f"vector({embedding_dim})"
        vector_distance = (
            f"i.embedding_vector::{vector_type} <=> "
            f"CAST(:query_vector AS {vector_type})"
        )
        vector_score = (
            "LEAST(1.0, GREATEST(0.0, "
            f"1.0 - ({vector_distance})))"
        )
        bind_params.append(bindparam("query_vector", type_=VECTOR()))
        values["query_vector"] = query_vector
        values["embedding_model"] = embedding_model
        values["embedding_dim"] = embedding_dim
        values["max_vector_distance"] = 1.0 - min_vector_similarity
        statement = text(
            f"""
            WITH text_candidates AS MATERIALIZED (
                SELECT
                    c.id AS knowledge_card_id,
                    {keyword_score} AS keyword_score
                FROM test_knowledge_cards c
                WHERE {base_where}
                  AND {POSTGRES_SEARCH_TEXT} @@
                      websearch_to_tsquery('simple'::regconfig, :query_text)
                ORDER BY keyword_score DESC, c.id ASC
                LIMIT :limit
            ),
            vector_candidates AS MATERIALIZED (
                SELECT
                    i.knowledge_card_id,
                    {vector_score} AS vector_score,
                    i.embedding_model,
                    i.embedding_dim,
                    i.content_hash
                FROM test_knowledge_embedding_index i
                JOIN test_knowledge_cards c
                  ON c.id = i.knowledge_card_id
                 AND c.project_id = i.project_id
                WHERE {base_where}
                  AND i.status = 'indexed'
                  AND i.embedding_model = :embedding_model
                  AND i.embedding_dim = :embedding_dim
                  AND i.embedding_vector IS NOT NULL
                  AND {vector_distance} <= :max_vector_distance
                ORDER BY {vector_distance} ASC
                LIMIT :limit
            ),
            candidate_ids AS (
                SELECT knowledge_card_id FROM text_candidates
                UNION
                SELECT knowledge_card_id FROM vector_candidates
            )
            SELECT
                candidate_ids.knowledge_card_id,
                coalesce(text_candidates.keyword_score, 0.0) AS keyword_score,
                vector_candidates.vector_score,
                vector_candidates.embedding_model,
                vector_candidates.embedding_dim,
                vector_candidates.content_hash
            FROM candidate_ids
            LEFT JOIN text_candidates USING (knowledge_card_id)
            LEFT JOIN vector_candidates USING (knowledge_card_id)
            ORDER BY
                GREATEST(
                    coalesce(text_candidates.keyword_score, 0.0),
                    coalesce(vector_candidates.vector_score, 0.0)
                ) DESC,
                candidate_ids.knowledge_card_id ASC
            LIMIT :limit
            """,
        ).bindparams(*bind_params)
    else:
        statement = text(
            f"""
            SELECT
                c.id AS knowledge_card_id,
                {keyword_score} AS keyword_score,
                NULL::double precision AS vector_score,
                NULL::text AS embedding_model,
                NULL::integer AS embedding_dim,
                NULL::text AS content_hash
            FROM test_knowledge_cards c
            WHERE {base_where}
              AND {POSTGRES_SEARCH_TEXT} @@
                  websearch_to_tsquery('simple'::regconfig, :query_text)
            ORDER BY keyword_score DESC, c.title ASC, c.id ASC
            LIMIT :limit
            """,
        ).bindparams(*bind_params)
    return statement, values


def sync_native_embeddings(
    session: Session,
    rows: list[tuple[uuid.UUID, list[float]]],
) -> bool:
    capabilities = detect_capabilities(session)
    if not capabilities.vector_search or not rows:
        return False
    native_table = table(
        "test_knowledge_embedding_index",
        column("id", Uuid(as_uuid=True)),
        column("embedding_vector", VECTOR()),
    )
    statement = (
        update(native_table)
        .where(native_table.c.id == bindparam("row_id"))
        .values(embedding_vector=bindparam("embedding", type_=VECTOR()))
    )
    try:
        with session.begin_nested():
            session.execute(
                statement,
                [{"row_id": row_id, "embedding": embedding} for row_id, embedding in rows],
            )
        return True
    except SQLAlchemyError:
        return False
