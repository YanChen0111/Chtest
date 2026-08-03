from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def test_alembic_upgrade_head_from_empty_sqlite_database(tmp_path: Path) -> None:
    backend_dir = Path(__file__).parents[3]
    db_path = tmp_path / "alembic-upgrade-head.db"
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{db_path.as_posix()}")

    command.upgrade(config, "head")

    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    with engine.connect() as connection:
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())
        assert {
            "projects",
            "ai_tasks",
            "requirements",
            "generated_case_candidates",
            "automation_drafts",
            "automation_plans",
            "test_knowledge_cards",
            "test_knowledge_embedding_index",
            "knowledge_ingestion_runs",
            "knowledge_retrieval_runs",
            "knowledge_evidence",
            "test_knowledge_relationships",
            "knowledge_feedback_events",
            "knowledge_adapter_configs",
            "tool_definitions",
            "cicd_runs",
            "cicd_changed_files",
            "unit_test_patches",
            "quality_gate_decisions",
            "test_runs",
            "test_results",
            "failure_analyses",
            "reports",
            "workflow_runs",
            "workflow_stage_snapshots",
            "workflow_human_decisions",
            "workflow_transition_events",
            "test_campaigns",
        } <= table_names
        candidate_columns = {column["name"] for column in inspector.get_columns("test_knowledge_cards")}
        assert {
            "source_locator_json",
            "source_ref",
            "ingestion_run_id",
            "reviewed_at",
            "review_comment",
            "duplicate_of_card_id",
            "last_verified_at",
        } <= candidate_columns
        revision = connection.execute(text("select version_num from alembic_version")).scalar_one()
        assert revision == "20260803_0020"
        relationship_columns = {column["name"] for column in inspector.get_columns("test_knowledge_relationships")}
        feedback_columns = {column["name"] for column in inspector.get_columns("knowledge_feedback_events")}
        assert {"created_by", "updated_by"} <= relationship_columns
        assert {"created_by", "updated_by"} <= feedback_columns
        generated_candidate_columns = {
            column["name"] for column in inspector.get_columns("generated_case_candidates")
        }
        assert {
            "covered_requirement_ids_json",
            "covered_risk_ids_json",
            "case_type",
            "generation_reason",
            "coverage_gap_notes",
            "automation_readiness_json",
            "quality_assessment_json",
        } <= generated_candidate_columns


def test_postgres_hybrid_migration_generates_optional_capability_sql(capsys) -> None:
    backend_dir = Path(__file__).parents[3]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", "postgresql+psycopg://user:pass@localhost/chtest")

    command.upgrade(config, "head", sql=True)

    sql = capsys.readouterr().out
    assert "ix_test_knowledge_cards_postgres_fts" in sql
    assert "to_tsvector" in sql
    assert "CREATE EXTENSION IF NOT EXISTS vector" in sql
    assert "embedding_vector vector" in sql
    assert "ix_test_knowledge_embedding_vector_hnsw_64" in sql

    command.downgrade(config, "20260714_0013:20260714_0012", sql=True)
    downgrade_sql = capsys.readouterr().out
    assert "DROP INDEX IF EXISTS ix_test_knowledge_cards_postgres_fts" in downgrade_sql
    assert "DROP COLUMN IF EXISTS embedding_vector" in downgrade_sql
    assert "DROP EXTENSION" not in downgrade_sql


def test_sqlite_postgres_hybrid_migration_is_noop(tmp_path: Path) -> None:
    backend_dir = Path(__file__).parents[3]
    db_path = tmp_path / "postgres-hybrid-sqlite.db"
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{db_path.as_posix()}")

    command.upgrade(config, "20260714_0012")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    with engine.connect() as connection:
        assert connection.execute(text("select version_num from alembic_version")).scalar_one() == "20260803_0020"
        columns = {item["name"] for item in inspect(connection).get_columns("test_knowledge_embedding_index")}
        assert "embedding_vector" not in columns
    engine.dispose()


def test_knowledge_ingestion_migration_preserves_existing_cards_and_round_trips(tmp_path: Path) -> None:
    backend_dir = Path(__file__).parents[3]
    db_path = tmp_path / "knowledge-ingestion-upgrade.db"
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{db_path.as_posix()}")
    command.upgrade(config, "20260713_0010")

    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                insert into test_knowledge_cards (
                    id, project_id, source_artifact_id, source_quote_hash,
                    knowledge_type, title, content, applicability
                ) values (
                    :id, :project_id, :artifact_id, :quote_hash,
                    'BusinessRule', 'Existing card', 'Existing content', 'case_generation'
                )
                """,
            ),
            {
                "id": "00000000000000000000000000000c01",
                "project_id": "00000000000000000000000000000101",
                "artifact_id": "00000000000000000000000000000371",
                "quote_hash": "sha256:" + "a" * 64,
            },
        )
    engine.dispose()

    command.upgrade(config, "head")
    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    with engine.connect() as connection:
        inspector = inspect(connection)
        columns = {column["name"] for column in inspector.get_columns("test_knowledge_cards")}
        assert "ingestion_run_id" in columns
        unique_names = {item["name"] for item in inspector.get_unique_constraints("test_knowledge_cards")}
        assert "uq_test_knowledge_cards_source_quote" in unique_names
        check_names = {item["name"] for item in inspector.get_check_constraints("test_knowledge_cards")}
        assert "ck_test_knowledge_cards_duplicate_target" in check_names
        index_names = {item["name"] for item in inspector.get_indexes("test_knowledge_cards")}
        assert {
            "ix_test_knowledge_cards_ingestion_run",
            "ix_test_knowledge_cards_duplicate_of",
        } <= index_names
        locator = connection.execute(
            text("select source_locator_json from test_knowledge_cards where title = 'Existing card'"),
        ).scalar_one()
        assert locator == "{}"
        retrieval_columns = {
            column["name"]: column
            for column in inspector.get_columns("knowledge_evidence")
        }
        assert retrieval_columns["vector_score"]["nullable"] is True
        evidence_unique_names = {
            item["name"]
            for item in inspector.get_unique_constraints("knowledge_evidence")
        }
        assert "uq_knowledge_evidence_run_card" in evidence_unique_names
        retrieval_check_names = {
            item["name"]
            for item in inspector.get_check_constraints("knowledge_retrieval_runs")
        }
        assert "ck_knowledge_retrieval_runs_consumer_pair" in retrieval_check_names
        retrieval_index_names = {
            item["name"]
            for item in inspector.get_indexes("knowledge_retrieval_runs")
        }
        assert "ix_knowledge_retrieval_runs_project_consumer" in retrieval_index_names
    engine.dispose()

    command.downgrade(config, "20260714_0011")
    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    with engine.connect() as connection:
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())
        assert "knowledge_retrieval_runs" not in table_names
        assert "knowledge_evidence" not in table_names
        assert "knowledge_ingestion_runs" in table_names
        assert "ingestion_run_id" in {
            column["name"] for column in inspector.get_columns("test_knowledge_cards")
        }
    engine.dispose()
    command.upgrade(config, "head")

    command.downgrade(config, "20260713_0010")
    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    with engine.connect() as connection:
        table_names = set(inspect(connection).get_table_names())
        assert "knowledge_retrieval_runs" not in table_names
        assert "knowledge_evidence" not in table_names
    engine.dispose()
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    with engine.connect() as connection:
        assert connection.execute(
            text("select count(*) from test_knowledge_cards where title = 'Existing card'"),
        ).scalar_one() == 1
