from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.modules.execution.playwright_runner import (
    PlaywrightRunner,
    PlaywrightRunnerCommandError,
    discover_playwright_artifacts,
    parse_playwright_counts,
)


def write_fake_npx(tmp_path: Path) -> Path:
    executable = tmp_path / "fake-npx"
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "Path('playwright-report').mkdir(exist_ok=True)\n"
        "Path('playwright-report/trace.zip').write_bytes(b'trace')\n"
        "Path('playwright-report/screenshot.png').write_bytes(b'png')\n"
        "print('1 passed (42ms)')\n",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | 0o111)
    return executable


def test_playwright_runner_executes_allowlisted_command(tmp_path: Path) -> None:
    fake_npx = write_fake_npx(tmp_path)
    runner = PlaywrightRunner(npx_executable=str(fake_npx))

    result = runner.run("npx playwright test tests/checkout.spec.ts", working_directory=tmp_path)

    assert result.exit_code == 0
    assert result.duration_ms >= 0
    assert "1 passed" in result.stdout
    assert result.stderr == ""
    assert result.parsed_result["total"] == 1
    assert result.parsed_result["passed"] == 1
    assert {artifact.artifact_type for artifact in result.artifacts} == {"playwright_trace", "screenshot"}
    assert {artifact.mime_type for artifact in result.artifacts} == {"application/zip", "image/png"}


def test_playwright_runner_rejects_forbidden_shell_operator(tmp_path: Path) -> None:
    fake_npx = write_fake_npx(tmp_path)
    runner = PlaywrightRunner(npx_executable=str(fake_npx))

    with pytest.raises(PlaywrightRunnerCommandError):
        runner.run("npx playwright test && rm -rf /tmp/example", working_directory=tmp_path)


def test_playwright_runner_rejects_non_playwright_command(tmp_path: Path) -> None:
    fake_npx = write_fake_npx(tmp_path)
    runner = PlaywrightRunner(npx_executable=str(fake_npx))

    with pytest.raises(PlaywrightRunnerCommandError):
        runner.run("pytest tests -q", working_directory=tmp_path)


def test_parse_playwright_counts_reads_failures_and_skips() -> None:
    parsed = parse_playwright_counts("2 passed 1 failed 3 skipped")

    assert parsed == {"total": 6, "passed": 2, "failed": 1, "skipped": 3, "error": 0}


def test_discover_playwright_artifacts_returns_trace_and_screenshot(tmp_path: Path) -> None:
    report_dir = tmp_path / "playwright-report"
    report_dir.mkdir()
    (report_dir / "trace.zip").write_bytes(b"trace")
    (report_dir / "checkout.png").write_bytes(b"png")
    (report_dir / "notes.txt").write_text("ignored", encoding="utf-8")

    artifacts = discover_playwright_artifacts(tmp_path)

    assert [artifact.artifact_type for artifact in artifacts] == ["playwright_trace", "screenshot"]
    assert [artifact.file_path for artifact in artifacts] == [
        "playwright-report/trace.zip",
        "playwright-report/checkout.png",
    ]
