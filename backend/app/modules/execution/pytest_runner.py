from __future__ import annotations

import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.modules.projects.service import has_forbidden_shell_operator, is_command_allowlisted


class PytestRunnerCommandError(ValueError):
    pass


@dataclass(frozen=True)
class PytestRunnerResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    parsed_result: dict[str, Any]


class PytestRunner:
    def __init__(self, python_executable: str = sys.executable) -> None:
        self.python_executable = python_executable

    def run(self, command: str, working_directory: str | Path, timeout_seconds: int = 600) -> PytestRunnerResult:
        validate_pytest_command(command)
        workdir = Path(working_directory).expanduser().resolve()
        if not workdir.exists() or not workdir.is_dir():
            raise PytestRunnerCommandError("Working directory must exist.")

        argv = normalize_pytest_argv(command, self.python_executable)
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
        return PytestRunnerResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            parsed_result=parse_pytest_counts(completed.stdout, completed.stderr),
        )


def validate_pytest_command(command: str) -> None:
    if has_forbidden_shell_operator(command) or not is_command_allowlisted(command, "pytest"):
        raise PytestRunnerCommandError("Command is outside the pytest allowlist.")


def normalize_pytest_argv(command: str, python_executable: str) -> list[str]:
    parts = shlex.split(command)
    if not parts or parts[0] != "pytest":
        raise PytestRunnerCommandError("Command must start with pytest.")
    return [python_executable, "-m", "pytest", *parts[1:]]


def parse_pytest_counts(stdout: str, stderr: str = "") -> dict[str, Any]:
    text = f"{stdout}\n{stderr}"
    counts = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "error": 0}
    for key, pattern in (
        ("passed", r"(\d+)\s+passed"),
        ("failed", r"(\d+)\s+failed"),
        ("skipped", r"(\d+)\s+skipped"),
        ("error", r"(\d+)\s+errors?"),
    ):
        match = re.search(pattern, text)
        if match:
            counts[key] = int(match.group(1))
    counts["total"] = counts["passed"] + counts["failed"] + counts["skipped"] + counts["error"]
    return counts
