"""add optional postgres hybrid knowledge capability

Revision ID: 20260714_0013
Revises: 20260714_0012
Create Date: 2026-07-14
"""

from __future__ import annotations

from alembic import op


revision = "20260714_0013"
down_revision = "20260714_0012"
branch_labels = None
depends_on = None

POSTGRES_FTS_INDEX = "ix_test_knowledge_cards_postgres_fts"
POSTGRES_HNSW_INDEX = "ix_test_knowledge_embedding_vector_hnsw_64"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS {POSTGRES_FTS_INDEX}
        ON test_knowledge_cards
        USING gin (
            to_tsvector(
                'simple'::regconfig,
                coalesce(title, '') || ' ' ||
                coalesce(content, '') || ' ' ||
                coalesce(module_key, '') || ' ' ||
                coalesce(api_endpoint, '') || ' ' ||
                coalesce(risk_type, '') || ' ' ||
                coalesce(case_type_hint, '')
            )
        )
        WHERE status IN ('approved', 'extracted')
          AND safe_to_show = true
          AND allowed_for_prompt = true
        """,
    )
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_available_extensions WHERE name = 'vector'
            ) THEN
                BEGIN
                    EXECUTE 'CREATE EXTENSION IF NOT EXISTS vector';
                EXCEPTION
                    WHEN insufficient_privilege OR undefined_file OR
                         undefined_object OR feature_not_supported THEN
                        RAISE NOTICE 'pgvector extension unavailable: %', SQLERRM;
                END;
            END IF;

            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
                BEGIN
                    EXECUTE 'ALTER TABLE test_knowledge_embedding_index '
                            'ADD COLUMN IF NOT EXISTS embedding_vector vector';
                EXCEPTION
                    WHEN insufficient_privilege OR undefined_object OR
                         feature_not_supported THEN
                        RAISE NOTICE 'pgvector column unavailable: %', SQLERRM;
                END;

                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = current_schema()
                      AND table_name = 'test_knowledge_embedding_index'
                      AND column_name = 'embedding_vector'
                ) THEN
                    BEGIN
                        EXECUTE 'CREATE INDEX IF NOT EXISTS {POSTGRES_HNSW_INDEX} '
                                'ON test_knowledge_embedding_index USING hnsw '
                                '((embedding_vector::vector(64)) vector_cosine_ops) '
                                'WHERE embedding_dim = 64 '
                                'AND embedding_model = ''deterministic-hashing-v1'' '
                                'AND status = ''indexed'' '
                                'AND embedding_vector IS NOT NULL';
                    EXCEPTION
                        WHEN insufficient_privilege OR undefined_object OR
                             feature_not_supported THEN
                            RAISE NOTICE 'pgvector HNSW index unavailable: %', SQLERRM;
                    END;
                END IF;
            END IF;
        END $$
        """,
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(f"DROP INDEX IF EXISTS {POSTGRES_HNSW_INDEX}")
    op.execute(f"DROP INDEX IF EXISTS {POSTGRES_FTS_INDEX}")
    op.execute(
        "ALTER TABLE test_knowledge_embedding_index "
        "DROP COLUMN IF EXISTS embedding_vector",
    )
