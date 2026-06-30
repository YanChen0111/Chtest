from __future__ import annotations

from pathlib import Path
from typing import Any
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.execution.playwright_runner import (
    PlaywrightRunner,
    PlaywrightRunnerCommandError,
    discover_playwright_artifacts,
    parse_playwright_counts,
)
from backend.app.modules.projects.models import Project, TestCommand, Workspace
from backend.app.modules.projects.router import get_session


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


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


def seed_project(session: Session) -> Project:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    return project


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def json(self) -> Any:
        import json

        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def post(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        import asyncio

        return asyncio.run(self._request("POST", path, json_body))

    async def _request(self, method: str, path: str, json_body: dict[str, Any] | None) -> ASGIResponse:
        import json

        body = json.dumps(json_body).encode("utf-8") if json_body is not None else b""
        status_code: int | None = None
        body_chunks: list[bytes] = []
        request_complete = False

        async def receive() -> dict[str, Any]:
            nonlocal request_complete
            if not request_complete:
                request_complete = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        async def send(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                body_chunks.append(message.get("body", b""))

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": b"",
            "headers": [
                (b"host", b"testserver"),
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }

        await self.asgi_app(scope, receive, send)
        assert status_code is not None
        return ASGIResponse(status_code, b"".join(body_chunks))


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


def test_create_playwright_test_run_from_approved_automation_draft(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_npx = write_fake_npx(tmp_path)
    import backend.app.modules.execution.service as execution_service

    monkeypatch.setattr(execution_service, "PlaywrightRunner", lambda: PlaywrightRunner(npx_executable=str(fake_npx)))
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project = seed_project(session)
            draft = AutomationDraft(
                project_id=project.id,
                ai_task_id=uuid.uuid4(),
                target_framework="playwright",
                title="playwright draft for checkout",
                draft_code="import { test } from '@playwright/test';\ntest('checkout smoke', async () => {});\n",
                draft_language="typescript",
                suggested_file_path="tests/checkout.spec.ts",
                status="approved",
            )
            session.add(draft)
            session.commit()
            draft_id = draft.id
            project_id = project.id

        response = ASGIClient(app).post(
            "/api/test-runs",
            {
                "project_id": str(project_id),
                "automation_draft_id": str(draft_id),
                "runner_mode": "playwright_local",
                "reason": "run approved playwright draft",
            },
        )

        assert response.status_code == 202
        body = response.json()
        assert body["automation_draft_id"] == str(draft_id)
        assert body["runner_mode"] == "playwright_local"
        assert body["status"] == "passed"
        assert body["parsed_result"]["passed"] == 1
        assert body["test_results"][0]["test_name"] == "generated::checkout smoke"
        assert {artifact["artifact_type"] for artifact in body["artifacts"]} >= {
            "runtime_manifest",
            "stdout",
            "stderr",
            "playwright_trace",
            "screenshot",
        }
    finally:
        app.dependency_overrides.clear()


def test_create_playwright_test_run_rejects_unapproved_draft(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_npx = write_fake_npx(tmp_path)
    import backend.app.modules.execution.service as execution_service

    monkeypatch.setattr(execution_service, "PlaywrightRunner", lambda: PlaywrightRunner(npx_executable=str(fake_npx)))
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project = seed_project(session)
            draft = AutomationDraft(
                project_id=project.id,
                ai_task_id=uuid.uuid4(),
                target_framework="playwright",
                title="playwright draft for checkout",
                draft_code="test('checkout smoke', async () => {});\n",
                draft_language="typescript",
                suggested_file_path="tests/checkout.spec.ts",
                status="draft_generated",
            )
            session.add(draft)
            session.commit()
            draft_id = draft.id
            project_id = project.id

        response = ASGIClient(app).post(
            "/api/test-runs",
            {
                "project_id": str(project_id),
                "automation_draft_id": str(draft_id),
                "runner_mode": "playwright_local",
            },
        )

        assert response.status_code == 400
        assert response.json()["error_code"] == "TEST_RUN_INVALID_INPUT"
    finally:
        app.dependency_overrides.clear()


def test_create_playwright_test_run_from_configured_test_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_npx = write_fake_npx(tmp_path)
    import backend.app.modules.execution.service as execution_service

    monkeypatch.setattr(execution_service, "PlaywrightRunner", lambda: PlaywrightRunner(npx_executable=str(fake_npx)))
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project = seed_project(session)
            command = TestCommand(
                project_id=project.id,
                name="playwright smoke",
                command="npx playwright test tests/checkout.spec.ts",
                working_directory=str(tmp_path),
                command_type="playwright",
                status="active",
            )
            session.add(command)
            session.commit()
            command_id = command.id
            project_id = project.id

        response = ASGIClient(app).post(
            "/api/test-runs",
            {
                "project_id": str(project_id),
                "test_command_id": str(command_id),
                "runner_mode": "playwright_local",
                "reason": "run configured playwright command",
            },
        )

        assert response.status_code == 202
        body = response.json()
        assert body["test_command_id"] == str(command_id)
        assert body["automation_draft_id"] is None
        assert body["runner_mode"] == "playwright_local"
        assert body["status"] == "passed"
        assert body["test_results"][0]["test_name"] == "playwright_runner::session"
    finally:
        app.dependency_overrides.clear()
