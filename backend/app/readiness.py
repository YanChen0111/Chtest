from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, inspect, text


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_TABLES = {
    "ai_tasks",
    "artifacts",
    "automation_drafts",
    "cicd_runs",
    "failure_analyses",
    "knowledge_adapter_configs",
    "knowledge_ingestion_runs",
    "knowledge_retrieval_runs",
    "projects",
    "reports",
    "test_knowledge_cards",
    "test_results",
    "test_runs",
    "tool_definitions",
}


def check_readiness(engine: Engine, artifact_root: str | Path) -> dict[str, Any]:
    database, migrations = _check_database(engine)
    artifacts = _check_artifact_root(Path(artifact_root))
    tesseract = _check_tesseract()
    checks = {
        "database": database,
        "migrations": migrations,
        "artifact_root": artifacts,
        "tesseract": tesseract,
    }

    blocking = [name for name, check in checks.items() if check["status"] == "failed"]
    degraded = [name for name, check in checks.items() if check["status"] == "degraded"]
    if blocking:
        return {
            "status": "not_ready",
            "error_code": "READINESS_CHECK_FAILED",
            "message": f"Required checks failed: {', '.join(blocking)}.",
            "checks": checks,
        }
    if degraded:
        return {
            "status": "degraded",
            "error_code": "READINESS_OPTIONAL_CAPABILITY_UNAVAILABLE",
            "message": f"Core workflows are ready; optional capabilities are unavailable: {', '.join(degraded)}.",
            "checks": checks,
        }
    return {
        "status": "ready",
        "error_code": None,
        "message": "All required services and local capabilities are ready.",
        "checks": checks,
    }


def _check_database(engine: Engine) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            inspector = inspect(connection)
            table_names = set(inspector.get_table_names())
            current_revisions = (
                sorted(
                    str(row[0])
                    for row in connection.execute(text("SELECT version_num FROM alembic_version"))
                )
                if "alembic_version" in table_names
                else []
            )
    except Exception as exc:
        database = _failed_check(
            "DATABASE_UNAVAILABLE",
            "Database connection failed.",
            {"reason": type(exc).__name__},
        )
        migrations = _failed_check(
            "MIGRATION_STATUS_UNKNOWN",
            "Migration status could not be inspected because the database is unavailable.",
        )
        return database, migrations

    missing_tables = sorted(REQUIRED_TABLES - table_names)
    database = {
        "status": "ok",
        "error_code": None,
        "message": "Database connection succeeded.",
        "details": {"dialect": engine.dialect.name},
    }
    expected_heads = _expected_alembic_heads()
    if not current_revisions:
        migrations = _failed_check(
            "ALEMBIC_VERSION_MISSING",
            "Database has no Alembic revision record.",
            {"current_revisions": [], "expected_heads": expected_heads, "missing_tables": missing_tables},
        )
    elif current_revisions != expected_heads:
        migrations = _failed_check(
            "ALEMBIC_REVISION_MISMATCH",
            "Database revision does not match the application migration head.",
            {
                "current_revisions": current_revisions,
                "expected_heads": expected_heads,
                "missing_tables": missing_tables,
            },
        )
    elif missing_tables:
        migrations = _failed_check(
            "DATABASE_TABLES_MISSING",
            "Database is at migration head but required runtime tables are missing.",
            {
                "current_revisions": current_revisions,
                "expected_heads": expected_heads,
                "missing_tables": missing_tables,
            },
        )
    else:
        migrations = {
            "status": "ok",
            "error_code": None,
            "message": "Database schema is at the expected migration head.",
            "details": {
                "current_revisions": current_revisions,
                "expected_heads": expected_heads,
                "missing_tables": [],
            },
        }
    return database, migrations


def _expected_alembic_heads() -> list[str]:
    config = Config(str(REPO_ROOT / "backend" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "backend" / "alembic"))
    return sorted(ScriptDirectory.from_config(config).get_heads())


def _check_artifact_root(root: Path) -> dict[str, Any]:
    try:
        resolved = root.expanduser().resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=".chtest-ready-", dir=resolved, delete=True) as probe:
            probe.write(b"ready")
            probe.flush()
        return {
            "status": "ok",
            "error_code": None,
            "message": "Artifact root exists and is writable.",
            "details": {"path": str(resolved)},
        }
    except OSError as exc:
        return _failed_check(
            "ARTIFACT_ROOT_UNAVAILABLE",
            "Artifact root cannot be created or written.",
            {"path": str(root), "reason": type(exc).__name__},
        )


def _check_tesseract() -> dict[str, Any]:
    command = _resolve_tesseract_command()
    if command is None:
        return {
            "status": "degraded",
            "error_code": "TESSERACT_UNAVAILABLE",
            "message": "Image OCR is unavailable; non-image knowledge imports remain ready.",
            "details": {"capability": "image_ocr"},
        }
    try:
        completed = subprocess.run(
            [command, "--version"],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "status": "degraded",
            "error_code": "TESSERACT_CHECK_FAILED",
            "message": "Image OCR executable was found but could not be verified.",
            "details": {"capability": "image_ocr", "reason": type(exc).__name__},
        }
    if completed.returncode != 0:
        return {
            "status": "degraded",
            "error_code": "TESSERACT_CHECK_FAILED",
            "message": "Image OCR executable returned an error during verification.",
            "details": {"capability": "image_ocr", "exit_code": completed.returncode},
        }
    version = next((line.strip() for line in completed.stdout.splitlines() if line.strip()), "unknown")
    return {
        "status": "ok",
        "error_code": None,
        "message": "Image OCR is available.",
        "details": {"capability": "image_ocr", "version": version},
    }


def _resolve_tesseract_command() -> str | None:
    configured = os.getenv("CHTEST_TESSERACT_CMD")
    if configured:
        return configured
    default_windows_path = Path("D:/tools/tesseract/tesseract.exe")
    if default_windows_path.is_file():
        return str(default_windows_path)
    return shutil.which("tesseract")


def _failed_check(
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "status": "failed",
        "error_code": error_code,
        "message": message,
        "details": details or {},
    }
