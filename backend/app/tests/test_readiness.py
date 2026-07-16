from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text

from backend.app import main, readiness


def _ready_database(tmp_path: Path):
    engine = create_engine(f"sqlite+pysqlite:///{(tmp_path / 'ready.db').as_posix()}", future=True)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        connection.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:head)"),
            {"head": readiness._expected_alembic_heads()[0]},
        )
        for table_name in sorted(readiness.REQUIRED_TABLES):
            connection.execute(text(f'CREATE TABLE "{table_name}" (id VARCHAR(32) PRIMARY KEY)'))
    return engine


def test_readiness_reports_all_required_checks(tmp_path: Path, monkeypatch) -> None:
    engine = _ready_database(tmp_path)
    monkeypatch.setattr(readiness, "_resolve_tesseract_command", lambda: "tesseract")
    monkeypatch.setattr(
        readiness.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, "tesseract 5.4.0\n", ""),
    )

    report = readiness.check_readiness(engine, tmp_path / "artifacts")

    assert report["status"] == "ready"
    assert report["error_code"] is None
    assert set(report["checks"]) == {"database", "migrations", "artifact_root", "tesseract"}
    assert all(check["status"] == "ok" for check in report["checks"].values())
    engine.dispose()


def test_readiness_is_degraded_when_only_ocr_is_unavailable(tmp_path: Path, monkeypatch) -> None:
    engine = _ready_database(tmp_path)
    monkeypatch.setattr(readiness, "_resolve_tesseract_command", lambda: None)

    report = readiness.check_readiness(engine, tmp_path / "artifacts")

    assert report["status"] == "degraded"
    assert report["checks"]["tesseract"]["error_code"] == "TESSERACT_UNAVAILABLE"
    assert report["checks"]["database"]["status"] == "ok"
    engine.dispose()


def test_readiness_blocks_when_runtime_table_is_missing(tmp_path: Path, monkeypatch) -> None:
    engine = _ready_database(tmp_path)
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE tool_definitions"))
    monkeypatch.setattr(readiness, "_resolve_tesseract_command", lambda: None)

    report = readiness.check_readiness(engine, tmp_path / "artifacts")

    assert report["status"] == "not_ready"
    assert report["error_code"] == "READINESS_CHECK_FAILED"
    assert report["checks"]["migrations"]["error_code"] == "DATABASE_TABLES_MISSING"
    assert report["checks"]["migrations"]["details"]["missing_tables"] == ["tool_definitions"]
    engine.dispose()


def test_readiness_blocks_when_artifact_root_is_not_a_directory(tmp_path: Path, monkeypatch) -> None:
    engine = _ready_database(tmp_path)
    invalid_root = tmp_path / "artifact-file"
    invalid_root.write_text("not a directory", encoding="utf-8")
    monkeypatch.setattr(readiness, "_resolve_tesseract_command", lambda: None)

    report = readiness.check_readiness(engine, invalid_root)

    assert report["status"] == "not_ready"
    assert report["checks"]["artifact_root"]["error_code"] == "ARTIFACT_ROOT_UNAVAILABLE"
    engine.dispose()


def test_api_ready_returns_503_with_structured_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "check_readiness",
        lambda *_args: {
            "status": "not_ready",
            "error_code": "READINESS_CHECK_FAILED",
            "message": "Required checks failed: migrations.",
            "checks": {
                "database": {"status": "ok", "error_code": None, "message": "ok", "details": {}},
                "migrations": {
                    "status": "failed",
                    "error_code": "ALEMBIC_REVISION_MISMATCH",
                    "message": "outdated",
                    "details": {},
                },
                "artifact_root": {"status": "ok", "error_code": None, "message": "ok", "details": {}},
                "tesseract": {"status": "ok", "error_code": None, "message": "ok", "details": {}},
            },
        },
    )

    status_code, payload = asyncio.run(_asgi_get_json("/api/ready"))

    assert status_code == 503
    assert payload["status"] == "not_ready"
    assert payload["checks"]["migrations"]["error_code"] == "ALEMBIC_REVISION_MISMATCH"


async def _asgi_get_json(path: str) -> tuple[int, dict[str, Any]]:
    import json

    status_code: int | None = None
    body_chunks: list[bytes] = []
    request_complete = False

    async def receive() -> dict[str, Any]:
        nonlocal request_complete
        if not request_complete:
            request_complete = True
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        nonlocal status_code
        if message["type"] == "http.response.start":
            status_code = message["status"]
        elif message["type"] == "http.response.body":
            body_chunks.append(message.get("body", b""))

    await main.app(
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [(b"host", b"testserver")],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        },
        receive,
        send,
    )
    assert status_code is not None
    return status_code, json.loads(b"".join(body_chunks))
