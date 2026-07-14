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
        } <= table_names
        revision = connection.execute(text("select version_num from alembic_version")).scalar_one()
        assert revision == "20260713_0010"
