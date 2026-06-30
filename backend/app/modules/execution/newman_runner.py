from __future__ import annotations

import json
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.modules.projects.service import has_forbidden_shell_operator, is_command_allowlisted


class NewmanRunnerCommandError(ValueError):
    pass


@dataclass(frozen=True)
class NewmanTestResultCandidate:
    test_name: str
    test_file: str | None
    status: str
    duration_ms: int | None
    failure_message: str | None
    metadata: dict[str, Any]


@dataclass(frozen=True)
class NewmanRunnerResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    parsed_result: dict[str, Any]
    test_results: list[NewmanTestResultCandidate]
    newman_json_path: Path


class NewmanRunner:
    def __init__(self, npx_executable: str = "npx") -> None:
        self.npx_executable = npx_executable

    def run(self, command: str, working_directory: str | Path, timeout_seconds: int = 600) -> NewmanRunnerResult:
        validate_newman_command(command)
        workdir = Path(working_directory).expanduser().resolve()
        if not workdir.exists() or not workdir.is_dir():
            raise NewmanRunnerCommandError("Working directory must exist.")

        argv = normalize_newman_argv(command, self.npx_executable)
        report_path = newman_report_path(command, workdir)
        start = time.monotonic()
        completed = subprocess.run(
            argv,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        duration_ms = int((time.monotonic() - start) * 1000)
        if not report_path.exists():
            raise NewmanRunnerCommandError("Newman JSON report was not produced.")

        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise NewmanRunnerCommandError("Newman JSON report is invalid.") from exc
        parsed_result, test_results = parse_newman_report(report)
        return NewmanRunnerResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            parsed_result=parsed_result,
            test_results=test_results,
            newman_json_path=report_path,
        )


def validate_newman_command(command: str) -> None:
    if has_forbidden_shell_operator(command) or not is_command_allowlisted(command, "newman"):
        raise NewmanRunnerCommandError("Command is outside the Newman allowlist.")


def normalize_newman_argv(command: str, npx_executable: str) -> list[str]:
    parts = shlex.split(command)
    if parts[:3] != ["npx", "newman", "run"]:
        raise NewmanRunnerCommandError("Command must start with npx newman run.")
    return [npx_executable, "newman", "run", *parts[3:]]


def newman_report_path(command: str, working_directory: Path) -> Path:
    parts = shlex.split(command)
    if "--reporter-json-export" in parts:
        index = parts.index("--reporter-json-export")
        if index + 1 >= len(parts):
            raise NewmanRunnerCommandError("Missing --reporter-json-export path.")
        candidate = Path(parts[index + 1])
    else:
        candidate = Path("newman-report.json")
    if candidate.is_absolute() or ".." in candidate.parts:
        raise NewmanRunnerCommandError("Newman JSON report path must stay under the working directory.")
    return working_directory / candidate


def parse_newman_report(report: dict[str, Any]) -> tuple[dict[str, Any], list[NewmanTestResultCandidate]]:
    collection_name = str(report.get("collection", {}).get("info", {}).get("name") or "newman_collection")
    run = report.get("run", {})
    executions = run.get("executions") or []
    results: list[NewmanTestResultCandidate] = []
    passed = 0
    failed = 0
    skipped = 0
    error = 0

    for execution in executions:
        item = execution.get("item") or {}
        request = execution.get("request") or {}
        request_name = str(item.get("name") or "request")
        method = str(request.get("method") or "")
        raw_url = safe_url_template(request.get("url"))
        for assertion in execution.get("assertions") or []:
            assertion_name = str(assertion.get("assertion") or "assertion")
            skipped_assertion = bool(assertion.get("skipped"))
            assertion_error = assertion.get("error")
            if skipped_assertion:
                status = "skipped"
                skipped += 1
                failure_message = None
            elif assertion_error:
                status = "failed"
                failed += 1
                failure_message = str(assertion_error.get("message") or assertion_error)
            else:
                status = "passed"
                passed += 1
                failure_message = None
            results.append(
                NewmanTestResultCandidate(
                    test_name=f"{collection_name}/{request_name}::{assertion_name}",
                    test_file=None,
                    status=status,
                    duration_ms=None,
                    failure_message=failure_message,
                    metadata={
                        "source": "newman_runner",
                        "collection_name": collection_name,
                        "request_name": request_name,
                        "assertion_name": assertion_name,
                        "method": method,
                        "url_template": raw_url,
                    },
                ),
            )

    total = passed + failed + skipped + error
    stats = run.get("stats") or {}
    request_count = int((stats.get("requests") or {}).get("total") or len(executions))
    assertion_count = int((stats.get("assertions") or {}).get("total") or total)
    parsed_result = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "error": error,
        "request_count": request_count,
        "assertion_count": assertion_count,
        "collection_name": collection_name,
        "duration_ms": int((run.get("timings") or {}).get("completed") or 0),
    }
    return parsed_result, results


def safe_url_template(url: Any) -> str:
    if isinstance(url, dict):
        raw = str(url.get("raw") or "")
    else:
        raw = str(url or "")
    for marker in ("token=", "api_key=", "password="):
        if marker in raw.lower():
            return "<redacted>"
    return raw
