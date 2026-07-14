from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from backend.app.db_preflight import discover_expected_heads, run_preflight
from backend.app.modules.prompt_skill.registry_loader import (
    discover_builtin_prompt_files,
    parse_prompt_file,
)


ROOT = Path(__file__).parents[4]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _create_candidate_table(connection: sqlite3.Connection, *, current: bool) -> None:
    columns = ["id TEXT PRIMARY KEY"]
    if current:
        columns.extend(
            [
                "source_knowledge_evidence_json JSON NOT NULL DEFAULT '[]'",
                "coverage_dimensions_json JSON NOT NULL DEFAULT '[]'",
            ],
        )
    connection.execute(f"CREATE TABLE generated_case_candidates ({', '.join(columns)})")


def _create_prompt_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE prompt_versions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            hash TEXT NOT NULL,
            content TEXT NOT NULL
        )
        """,
    )


def _seed_current_prompts(connection: sqlite3.Connection) -> None:
    for index, path in enumerate(discover_builtin_prompt_files(ROOT).values()):
        prompt = parse_prompt_file(path)
        connection.execute(
            "INSERT INTO prompt_versions (id, name, version, hash, content) VALUES (?, ?, ?, ?, ?)",
            (str(index), prompt.name, prompt.version, prompt.hash, prompt.content),
        )


def test_preflight_reports_unversioned_schema_and_prompt_drift(tmp_path: Path) -> None:
    database_path = tmp_path / "blocked.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE alembic_version (version_num TEXT NOT NULL)")
        _create_candidate_table(connection, current=False)
        _create_prompt_table(connection)
        connection.execute(
            "INSERT INTO prompt_versions (id, name, version, hash, content) VALUES (?, ?, ?, ?, ?)",
            (
                "drifted",
                "automation_draft_generation",
                "v1",
                "sha256:" + "0" * 64,
                "changed content",
            ),
        )

    before = _sha256(database_path)
    report = run_preflight(database_path=database_path, repo_root=ROOT)
    after = _sha256(database_path)

    assert report.ready is False
    assert report.source_unchanged is True
    assert report.source_mutation_performed is False
    assert before == after == report.source_after.sha256
    assert {diagnostic.code for diagnostic in report.diagnostics} >= {
        "ALEMBIC_VERSION_MISSING",
        "CANDIDATE_COLUMNS_MISSING",
        "PROMPT_VERSION_CONTENT_DRIFT",
    }
    assert report.candidate_schema.missing_columns == [
        "coverage_dimensions_json",
        "source_knowledge_evidence_json",
    ]
    assert report.prompt_registry.drifted_refs == ["automation_draft_generation:v1"]
    assert report.safe_next_command.startswith("& ")
    assert "--copy-to" in report.safe_next_command
    assert "upgrade" not in report.safe_next_command


def test_preflight_accepts_current_schema_and_registry(tmp_path: Path) -> None:
    database_path = tmp_path / "ready.db"
    expected_head = discover_expected_heads(ROOT)[0]
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE alembic_version (version_num TEXT NOT NULL)")
        connection.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (expected_head,))
        _create_candidate_table(connection, current=True)
        _create_prompt_table(connection)
        _seed_current_prompts(connection)

    report = run_preflight(database_path=database_path, repo_root=ROOT)

    assert report.ready is True
    assert report.alembic.current_revisions == [expected_head]
    assert report.candidate_schema.missing_columns == []
    assert report.prompt_registry.drifted_refs == []
    assert report.prompt_registry.missing_refs == []
    assert report.safe_next_command == "Database is ready for local acceptance; no recovery command is required."


def test_copy_mode_uses_explicit_copy_and_preserves_source(tmp_path: Path) -> None:
    database_path = tmp_path / "source.db"
    copied_path = tmp_path / "diagnostics" / "source-copy.db"
    with sqlite3.connect(database_path) as connection:
        _create_candidate_table(connection, current=False)
        _create_prompt_table(connection)

    before = _sha256(database_path)
    report = run_preflight(
        database_path=database_path,
        copy_to=copied_path,
        repo_root=ROOT,
    )
    after = _sha256(database_path)

    assert report.mode == "copied_database_diagnostic"
    assert report.inspected_path == copied_path.resolve()
    assert copied_path.exists()
    assert report.source_unchanged is True
    assert report.source_mutation_performed is False
    assert before == after
    assert copied_path.resolve().as_posix() in report.safe_next_command
    assert "alembic" in report.safe_next_command
    assert "current" in report.safe_next_command
    assert "upgrade" not in report.safe_next_command
