from __future__ import annotations

import re
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.modules.projects.service import has_forbidden_shell_operator, is_command_allowlisted


class PlaywrightRunnerCommandError(ValueError):
    pass


@dataclass(frozen=True)
class PlaywrightArtifactCandidate:
    artifact_type: str
    file_path: str
    mime_type: str


@dataclass(frozen=True)
class PlaywrightRunnerResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    parsed_result: dict[str, Any]
    artifacts: list[PlaywrightArtifactCandidate]


class PlaywrightRunner:
    def __init__(self, npx_executable: str = "npx") -> None:
        self.npx_executable = npx_executable

    def run(self, command: str, working_directory: str | Path, timeout_seconds: int = 600) -> PlaywrightRunnerResult:
        validate_playwright_command(command)
        workdir = Path(working_directory).expanduser().resolve()
        if not workdir.exists() or not workdir.is_dir():
            raise PlaywrightRunnerCommandError("Working directory must exist.")

        argv = normalize_playwright_argv(command, self.npx_executable)
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
        return PlaywrightRunnerResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            duration_ms=duration_ms,
            parsed_result=parse_playwright_counts(completed.stdout, completed.stderr),
            artifacts=discover_playwright_artifacts(workdir),
        )


def validate_playwright_command(command: str) -> None:
    if has_forbidden_shell_operator(command) or not is_command_allowlisted(command, "playwright"):
        raise PlaywrightRunnerCommandError("Command is outside the Playwright allowlist.")


def normalize_playwright_argv(command: str, npx_executable: str) -> list[str]:
    parts = shlex.split(command)
    if parts[:3] != ["npx", "playwright", "test"]:
        raise PlaywrightRunnerCommandError("Command must start with npx playwright test.")
    return [npx_executable, "playwright", "test", *parts[3:]]


def parse_playwright_counts(stdout: str, stderr: str = "") -> dict[str, Any]:
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


def discover_playwright_artifacts(working_directory: Path) -> list[PlaywrightArtifactCandidate]:
    candidates: list[PlaywrightArtifactCandidate] = []
    for trace in sorted(working_directory.rglob("*.zip")):
        if "trace" in trace.name.lower() or "trace" in str(trace.parent).lower():
            candidates.append(
                PlaywrightArtifactCandidate(
                    artifact_type="playwright_trace",
                    file_path=trace.relative_to(working_directory).as_posix(),
                    mime_type="application/zip",
                ),
            )
    for screenshot in sorted(working_directory.rglob("*.png")):
        candidates.append(
            PlaywrightArtifactCandidate(
                artifact_type="screenshot",
                file_path=screenshot.relative_to(working_directory).as_posix(),
                mime_type="image/png",
            ),
        )
    return candidates
