from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.execution.newman_runner import (
    NewmanRunner,
    NewmanRunnerCommandError,
    parse_newman_report,
)
from backend.app.modules.projects.models import Project, TestCommand, Workspace
from backend.app.modules.projects.router import get_session


def write_fake_npx(tmp_path: Path, report_name: str = "newman-report.json") -> Path:
    executable = tmp_path / "fake-npx"
    payload = {
        "collection": {"info": {"name": "coupon-api"}},
        "run": {
            "stats": {
                "requests": {"total": 2, "failed": 0},
                "assertions": {"total": 4, "failed": 1},
            },
            "timings": {"completed": 812},
            "executions": [
                {
                    "item": {"name": "Create coupon"},
                    "assertions": [
                        {"assertion": "status is 201", "skipped": False, "error": None},
                        {"assertion": "body has id", "skipped": False, "error": None},
                    ],
                    "request": {"method": "POST", "url": {"raw": "{{baseUrl}}/coupons"}},
                },
                {
                    "item": {"name": "Reject expired coupon"},
                    "assertions": [
                        {"assertion": "status is 400", "skipped": False, "error": None},
                        {
                            "assertion": "message is explicit",
                            "skipped": False,
                            "error": {"message": "expected clear message"},
                        },
                    ],
                    "request": {"method": "POST", "url": {"raw": "{{baseUrl}}/coupons/validate"}},
                },
            ],
        },
    }
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "from pathlib import Path\n"
        f"Path({report_name!r}).write_text({json.dumps(payload)!r}, encoding='utf-8')\n"
        "print('Newman run complete: 3 passed, 1 failed')\n",
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
        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def post(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        import asyncio

        return asyncio.run(self._request("POST", path, json_body))

    async def _request(self, method: str, path: str, json_body: dict[str, Any] | None) -> ASGIResponse:
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


def test_newman_runner_executes_allowlisted_command_and_parses_report(tmp_path: Path) -> None:
    fake_npx = write_fake_npx(tmp_path)
    collection = tmp_path / "collections" / "coupon.postman_collection.json"
    collection.parent.mkdir()
    collection.write_text("{}", encoding="utf-8")
    runner = NewmanRunner(npx_executable=str(fake_npx))

    result = runner.run(
        "npx newman run collections/coupon.postman_collection.json --reporters json --reporter-json-export newman-report.json",
        working_directory=tmp_path,
    )

    assert result.exit_code == 0
    assert "Newman run complete" in result.stdout
    assert result.parsed_result == {
        "total": 4,
        "passed": 3,
        "failed": 1,
        "skipped": 0,
        "error": 0,
        "request_count": 2,
        "assertion_count": 4,
        "collection_name": "coupon-api",
        "duration_ms": 812,
    }
    assert [item.test_name for item in result.test_results] == [
        "coupon-api/Create coupon::status is 201",
        "coupon-api/Create coupon::body has id",
        "coupon-api/Reject expired coupon::status is 400",
        "coupon-api/Reject expired coupon::message is explicit",
    ]
    assert result.test_results[-1].status == "failed"
    assert result.test_results[-1].failure_message == "expected clear message"
    assert result.newman_json_path.name == "newman-report.json"


def test_newman_runner_rejects_forbidden_shell_operator(tmp_path: Path) -> None:
    fake_npx = write_fake_npx(tmp_path)
    runner = NewmanRunner(npx_executable=str(fake_npx))

    with pytest.raises(NewmanRunnerCommandError):
        runner.run("npx newman run collection.json && rm -rf /tmp/example", working_directory=tmp_path)


def test_parse_newman_report_counts_skipped_assertions() -> None:
    parsed, results = parse_newman_report(
        {
            "collection": {"info": {"name": "coupon-api"}},
            "run": {
                "stats": {
                    "requests": {"total": 1, "failed": 0},
                    "assertions": {"total": 2, "failed": 0},
                },
                "executions": [
                    {
                        "item": {"name": "List coupons"},
                        "assertions": [
                            {"assertion": "status is 200", "skipped": False, "error": None},
                            {"assertion": "optional cache header", "skipped": True, "error": None},
                        ],
                        "request": {"method": "GET", "url": {"raw": "{{baseUrl}}/coupons"}},
                    },
                ],
            },
        },
    )

    assert parsed["total"] == 2
    assert parsed["passed"] == 1
    assert parsed["skipped"] == 1
    assert results[1].status == "skipped"


def test_create_newman_test_run_from_configured_test_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_npx = write_fake_npx(tmp_path)
    collection = tmp_path / "collections" / "coupon.postman_collection.json"
    collection.parent.mkdir()
    collection.write_text("{}", encoding="utf-8")
    import backend.app.modules.execution.service as execution_service

    monkeypatch.setattr(execution_service, "NewmanRunner", lambda: NewmanRunner(npx_executable=str(fake_npx)))
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
                name="newman coupon api",
                command=(
                    "npx newman run collections/coupon.postman_collection.json "
                    "--reporters json --reporter-json-export newman-report.json"
                ),
                working_directory=str(tmp_path),
                command_type="newman",
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
                "runner_mode": "newman_local",
                "reason": "run configured newman command",
            },
        )

        assert response.status_code == 202
        body = response.json()
        assert body["test_command_id"] == str(command_id)
        assert body["automation_draft_id"] is None
        assert body["runner_mode"] == "newman_local"
        assert body["status"] == "failed"
        assert body["parsed_result"]["request_count"] == 2
        assert body["parsed_result"]["assertion_count"] == 4
        assert body["test_results"][-1]["status"] == "failed"
        assert body["test_results"][-1]["metadata"]["source"] == "newman_runner"
        artifacts_by_type = {artifact["artifact_type"]: artifact for artifact in body["artifacts"]}
        assert set(artifacts_by_type) >= {
            "runtime_manifest",
            "stdout",
            "stderr",
            "newman_json",
            "parsed_output",
        }
        assert artifacts_by_type["parsed_output"]["mime_type"] == "application/json"
    finally:
        app.dependency_overrides.clear()
