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
        assert revision == "20260714_0011"


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
    engine.dispose()

    command.downgrade(config, "20260713_0010")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    with engine.connect() as connection:
        assert connection.execute(
            text("select count(*) from test_knowledge_cards where title = 'Existing card'"),
        ).scalar_one() == 1
