from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from contextlib import closing
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.engine import make_url

from backend.app.modules.prompt_skill.registry_loader import (
    discover_builtin_prompt_files,
    parse_prompt_file,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_CANDIDATE_COLUMNS = (
    "coverage_dimensions_json",
    "source_knowledge_evidence_json",
)


@dataclass(frozen=True)
class FileFingerprint:
    sha256: str
    size_bytes: int
    modified_ns: int


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    message: str
    recovery: str


@dataclass(frozen=True)
class AlembicCheck:
    table_present: bool
    current_revisions: list[str]
    expected_heads: list[str]


@dataclass(frozen=True)
class CandidateSchemaCheck:
    table_present: bool
    required_columns: list[str]
    missing_columns: list[str]


@dataclass(frozen=True)
class PromptRegistryCheck:
    table_present: bool
    checked_refs: int
    missing_refs: list[str]
    drifted_refs: list[str]


@dataclass(frozen=True)
class PreflightReport:
    ready: bool
    mode: str
    source_path: Path
    inspected_path: Path
    source_before: FileFingerprint
    source_after: FileFingerprint
    source_unchanged: bool
    source_mutation_performed: bool
    alembic: AlembicCheck
    candidate_schema: CandidateSchemaCheck
    prompt_registry: PromptRegistryCheck
    diagnostics: list[Diagnostic]
    safe_next_command: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_path"] = str(self.source_path)
        payload["inspected_path"] = str(self.inspected_path)
        return payload


def discover_expected_heads(repo_root: Path = REPO_ROOT) -> list[str]:
    config = Config(str(repo_root / "backend" / "alembic.ini"))
    config.set_main_option("script_location", str(repo_root / "backend" / "alembic"))
    return sorted(ScriptDirectory.from_config(config).get_heads())


def resolve_database_path(
    *,
    database_path: Path | None = None,
    database_url: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> Path:
    if database_path is not None:
        return database_path.expanduser().resolve()

    configured_url = database_url or os.getenv("DATABASE_URL")
    if configured_url is None:
        return (repo_root / "storage" / "chtest-dev.db").resolve()

    url = make_url(configured_url)
    if url.get_backend_name() != "sqlite":
        raise ValueError("Local database preflight currently supports SQLite URLs only.")
    if not url.database or url.database == ":memory:":
        raise ValueError("Local database preflight requires a file-backed SQLite database.")

    configured_path = Path(url.database).expanduser()
    if not configured_path.is_absolute():
        configured_path = Path.cwd() / configured_path
    return configured_path.resolve()


def run_preflight(
    *,
    database_path: Path,
    repo_root: Path = REPO_ROOT,
    copy_to: Path | None = None,
) -> PreflightReport:
    source_path = database_path.expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"SQLite database does not exist: {source_path}")

    source_before = fingerprint_file(source_path)
    mode = "source_read_only"
    inspected_path = source_path
    if copy_to is not None:
        inspected_path = create_diagnostic_copy(source_path, copy_to)
        mode = "copied_database_diagnostic"

    expected_heads = discover_expected_heads(repo_root)
    diagnostics: list[Diagnostic] = []
    with closing(open_read_only(inspected_path)) as connection:
        table_names = _table_names(connection)
        alembic = _inspect_alembic(connection, table_names, expected_heads, diagnostics)
        candidate_schema = _inspect_candidate_schema(connection, table_names, diagnostics)
        prompt_registry = _inspect_prompt_registry(connection, table_names, repo_root, diagnostics)

    source_after = fingerprint_file(source_path)
    source_unchanged = source_before == source_after
    if not source_unchanged:
        diagnostics.append(
            Diagnostic(
                code="SOURCE_DATABASE_CHANGED_DURING_PREFLIGHT",
                severity="blocker",
                message="The source database fingerprint changed while preflight was running.",
                recovery="Stop writers and rerun preflight before trusting the diagnostic copy.",
            ),
        )

    ready = not any(item.severity == "blocker" for item in diagnostics)
    safe_next_command = _safe_next_command(
        ready=ready,
        mode=mode,
        source_path=source_path,
        inspected_path=inspected_path,
        repo_root=repo_root,
    )
    return PreflightReport(
        ready=ready,
        mode=mode,
        source_path=source_path,
        inspected_path=inspected_path,
        source_before=source_before,
        source_after=source_after,
        source_unchanged=source_unchanged,
        source_mutation_performed=False,
        alembic=alembic,
        candidate_schema=candidate_schema,
        prompt_registry=prompt_registry,
        diagnostics=diagnostics,
        safe_next_command=safe_next_command,
    )


def fingerprint_file(path: Path) -> FileFingerprint:
    stat = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return FileFingerprint(
        sha256=digest.hexdigest(),
        size_bytes=stat.st_size,
        modified_ns=stat.st_mtime_ns,
    )


def open_read_only(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def create_diagnostic_copy(source_path: Path, copy_to: Path) -> Path:
    target_path = copy_to.expanduser().resolve()
    if target_path == source_path:
        raise ValueError("Diagnostic copy path must differ from the source database path.")
    if target_path.exists():
        raise FileExistsError(f"Diagnostic copy already exists; refusing to overwrite: {target_path}")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with (
        closing(open_read_only(source_path)) as source,
        closing(sqlite3.connect(target_path)) as target,
    ):
        source.backup(target)
        target.commit()
    return target_path


def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {str(row["name"]) for row in rows}


def _inspect_alembic(
    connection: sqlite3.Connection,
    table_names: set[str],
    expected_heads: list[str],
    diagnostics: list[Diagnostic],
) -> AlembicCheck:
    table_present = "alembic_version" in table_names
    current_revisions: list[str] = []
    if table_present:
        current_revisions = sorted(
            str(row["version_num"])
            for row in connection.execute("SELECT version_num FROM alembic_version").fetchall()
        )

    if not current_revisions:
        diagnostics.append(
            Diagnostic(
                code="ALEMBIC_VERSION_MISSING",
                severity="blocker",
                message="No Alembic version record exists for this database.",
                recovery="Do not run alembic upgrade on the source. Inspect a copy and establish its baseline first.",
            ),
        )
    elif current_revisions != expected_heads:
        diagnostics.append(
            Diagnostic(
                code="ALEMBIC_REVISION_MISMATCH",
                severity="blocker",
                message=(
                    f"Database revisions {current_revisions} do not match current heads {expected_heads}."
                ),
                recovery="Use a diagnostic copy to audit the schema before choosing a baseline or upgrade path.",
            ),
        )

    return AlembicCheck(
        table_present=table_present,
        current_revisions=current_revisions,
        expected_heads=expected_heads,
    )


def _inspect_candidate_schema(
    connection: sqlite3.Connection,
    table_names: set[str],
    diagnostics: list[Diagnostic],
) -> CandidateSchemaCheck:
    table_present = "generated_case_candidates" in table_names
    present_columns: set[str] = set()
    if table_present:
        present_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info('generated_case_candidates')").fetchall()
        }
    missing_columns = sorted(set(REQUIRED_CANDIDATE_COLUMNS) - present_columns)

    if not table_present:
        diagnostics.append(
            Diagnostic(
                code="CANDIDATE_TABLE_MISSING",
                severity="blocker",
                message="Table generated_case_candidates is missing.",
                recovery="Audit the database baseline on a copy before applying any migration.",
            ),
        )
    elif missing_columns:
        diagnostics.append(
            Diagnostic(
                code="CANDIDATE_COLUMNS_MISSING",
                severity="blocker",
                message=f"GeneratedCaseCandidate is missing current columns: {', '.join(missing_columns)}.",
                recovery="Use a copied database to determine the correct baseline before adding the missing columns.",
            ),
        )

    return CandidateSchemaCheck(
        table_present=table_present,
        required_columns=list(REQUIRED_CANDIDATE_COLUMNS),
        missing_columns=missing_columns,
    )


def _inspect_prompt_registry(
    connection: sqlite3.Connection,
    table_names: set[str],
    repo_root: Path,
    diagnostics: list[Diagnostic],
) -> PromptRegistryCheck:
    parsed_prompts = [
        parse_prompt_file(path)
        for path in discover_builtin_prompt_files(repo_root).values()
    ]
    table_present = "prompt_versions" in table_names
    missing_refs: list[str] = []
    drifted_refs: list[str] = []

    if not table_present:
        diagnostics.append(
            Diagnostic(
                code="PROMPT_VERSION_TABLE_MISSING",
                severity="blocker",
                message="Table prompt_versions is missing.",
                recovery="Audit the database baseline on a copy before starting the application.",
            ),
        )
        return PromptRegistryCheck(
            table_present=False,
            checked_refs=len(parsed_prompts),
            missing_refs=sorted(f"{item.name}:{item.version}" for item in parsed_prompts),
            drifted_refs=[],
        )

    prompt_columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info('prompt_versions')").fetchall()
    }
    required_columns = {"name", "version", "hash", "content"}
    missing_schema_columns = sorted(required_columns - prompt_columns)
    if missing_schema_columns:
        diagnostics.append(
            Diagnostic(
                code="PROMPT_VERSION_SCHEMA_INCOMPLETE",
                severity="blocker",
                message=f"PromptVersion is missing columns: {', '.join(missing_schema_columns)}.",
                recovery="Audit the PromptVersion schema on a copy before starting the application.",
            ),
        )
        return PromptRegistryCheck(
            table_present=True,
            checked_refs=len(parsed_prompts),
            missing_refs=[],
            drifted_refs=[],
        )

    stored_prompts = {
        (str(row["name"]), str(row["version"])): row
        for row in connection.execute(
            "SELECT name, version, hash, content FROM prompt_versions",
        ).fetchall()
    }
    for prompt in parsed_prompts:
        ref = f"{prompt.name}:{prompt.version}"
        stored = stored_prompts.get((prompt.name, prompt.version))
        if stored is None:
            missing_refs.append(ref)
        elif stored["hash"] != prompt.hash or stored["content"] != prompt.content:
            drifted_refs.append(ref)

    if drifted_refs:
        diagnostics.append(
            Diagnostic(
                code="PROMPT_VERSION_CONTENT_DRIFT",
                severity="blocker",
                message=f"Stored PromptVersion content differs from built-in files: {', '.join(drifted_refs)}.",
                recovery="Preserve both versions and resolve the version/content contract on a copied database first.",
            ),
        )
    if missing_refs:
        diagnostics.append(
            Diagnostic(
                code="PROMPT_VERSION_BUILTINS_MISSING",
                severity="warning",
                message=f"Built-in PromptVersion rows are missing: {', '.join(missing_refs)}.",
                recovery="Bootstrap may add missing rows after all blocking schema diagnostics are resolved.",
            ),
        )

    return PromptRegistryCheck(
        table_present=True,
        checked_refs=len(parsed_prompts),
        missing_refs=sorted(missing_refs),
        drifted_refs=sorted(drifted_refs),
    )


def _safe_next_command(
    *,
    ready: bool,
    mode: str,
    source_path: Path,
    inspected_path: Path,
    repo_root: Path,
) -> str:
    if ready and mode == "source_read_only":
        return "Database is ready for local acceptance; no recovery command is required."

    python = _powershell_quote(str(Path(sys.executable).resolve()))
    if mode == "source_read_only":
        suggested_copy = source_path.with_name(f"{source_path.stem}-diagnostic-copy{source_path.suffix}")
        return (
            f"& {python} -m backend.app.db_preflight --database-path "
            f"{_powershell_quote(str(source_path))} --copy-to "
            f"{_powershell_quote(str(suggested_copy))} --json"
        )

    database_url = f"sqlite+pysqlite:///{inspected_path.as_posix()}"
    alembic_ini = repo_root / "backend" / "alembic.ini"
    return (
        f"$env:DATABASE_URL={_powershell_quote(database_url)}; & {python} -m alembic "
        f"-c {_powershell_quote(str(alembic_ini))} current"
    )


def _powershell_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect a local SQLite acceptance database without mutating the source.",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--database-path", type=Path)
    source.add_argument("--database-url")
    parser.add_argument(
        "--copy-to",
        type=Path,
        help="Create a consistent SQLite diagnostic copy at this explicit new path and inspect the copy.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full report as JSON.")
    return parser


def _render_text(report: PreflightReport) -> str:
    lines = [
        f"ready: {str(report.ready).lower()}",
        f"mode: {report.mode}",
        f"source: {report.source_path}",
        f"inspected: {report.inspected_path}",
        f"source_unchanged: {str(report.source_unchanged).lower()}",
    ]
    for diagnostic in report.diagnostics:
        lines.append(f"[{diagnostic.severity}] {diagnostic.code}: {diagnostic.message}")
        lines.append(f"  recovery: {diagnostic.recovery}")
    lines.append(f"safe_next_command: {report.safe_next_command}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        database_path = resolve_database_path(
            database_path=args.database_path,
            database_url=args.database_url,
        )
        report = run_preflight(database_path=database_path, copy_to=args.copy_to)
    except (FileNotFoundError, FileExistsError, ValueError, sqlite3.Error) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False) if args.json else f"error: {exc}")
        return 1

    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(_render_text(report))
    return 0 if report.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
