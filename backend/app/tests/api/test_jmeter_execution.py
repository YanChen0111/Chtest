from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.execution.jmeter_runner import JMeterRunnerCommandError, parse_jmeter_jtl
from backend.app.modules.projects.models import Project, TestCommand, Workspace
from backend.app.modules.projects.router import get_session


JTL_CSV = """timeStamp,elapsed,label,responseCode,responseMessage,threadName,success,bytes,grpThreads,allThreads,Latency,IdleTime,Connect
1719820800000,120,GET /coupons,200,OK,Thread Group 1-1,true,512,1,1,80,0,12
1719820800200,240,POST /coupons,500,Internal Server Error,Thread Group 1-1,false,256,1,1,180,0,24
1719820800600,90,GET /health,200,OK,Thread Group 1-1,true,128,1,1,50,0,6
"""


JTL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testResults version="1.2">
  <httpSample t="120" lt="80" ts="1719820800000" s="true" lb="GET /coupons" rc="200" rm="OK" by="512" />
  <httpSample t="240" lt="180" ts="1719820800200" s="false" lb="POST /coupons" rc="500" rm="Internal Server Error" by="256" />
</testResults>
"""


def test_parse_jmeter_jtl_csv_summarizes_sampler_counts(tmp_path: Path) -> None:
    jtl_path = tmp_path / "results.jtl"
    jtl_path.write_text(JTL_CSV, encoding="utf-8")

    parsed, results = parse_jmeter_jtl(jtl_path)

    assert parsed == {
        "total": 3,
        "passed": 2,
        "failed": 1,
        "skipped": 0,
        "error": 0,
        "sampler_count": 3,
        "assertion_count": 3,
        "duration_ms": 450,
        "average_latency_ms": 103,
    }
    assert [item.test_name for item in results] == [
        "jmeter/GET /coupons",
        "jmeter/POST /coupons",
        "jmeter/GET /health",
    ]
    assert results[1].status == "failed"
    assert results[1].failure_message == "500 Internal Server Error"
    assert results[1].metadata["response_code"] == "500"
    assert results[1].metadata["latency_ms"] == 180


def test_parse_jmeter_jtl_xml_summarizes_sampler_counts(tmp_path: Path) -> None:
    jtl_path = tmp_path / "results.xml"
    jtl_path.write_text(JTL_XML, encoding="utf-8")

    parsed, results = parse_jmeter_jtl(jtl_path)

    assert parsed["total"] == 2
    assert parsed["passed"] == 1
    assert parsed["failed"] == 1
    assert parsed["duration_ms"] == 360
    assert parsed["average_latency_ms"] == 130
    assert results[0].test_name == "jmeter/GET /coupons"
    assert results[1].failure_message == "500 Internal Server Error"


def test_parse_jmeter_jtl_rejects_missing_or_empty_results(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.jtl"
    empty_path = tmp_path / "empty.jtl"
    empty_path.write_text("", encoding="utf-8")

    with pytest.raises(JMeterRunnerCommandError, match="JMeter JTL file was not produced"):
        parse_jmeter_jtl(missing_path)

    with pytest.raises(JMeterRunnerCommandError, match="JMeter JTL file contains no sampler results"):
        parse_jmeter_jtl(empty_path)


def write_fake_jmeter(tmp_path: Path) -> Path:
    executable = tmp_path / "fake-jmeter"
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "Path('results.jtl').write_text("
        + repr(JTL_CSV)
        + ", encoding='utf-8')\n"
        "print('JMeter run complete: 2 passed, 1 failed')\n",
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
        import json

        return asyncio.run(self._request("POST", path, json.dumps(json_body).encode("utf-8")))

    async def _request(self, method: str, path: str, body: bytes) -> ASGIResponse:
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


def test_create_jmeter_test_run_from_configured_test_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_jmeter = write_fake_jmeter(tmp_path)
    plan = tmp_path / "plans" / "coupon.jmx"
    plan.parent.mkdir()
    plan.write_text("<jmeterTestPlan />", encoding="utf-8")
    import backend.app.modules.execution.service as execution_service
    from backend.app.modules.execution.jmeter_runner import JMeterRunner

    monkeypatch.setattr(execution_service, "JMeterRunner", lambda: JMeterRunner(jmeter_executable=str(fake_jmeter)))
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
                name="jmeter coupon smoke",
                command="jmeter -n -t plans/coupon.jmx -l results.jtl",
                working_directory=str(tmp_path),
                command_type="jmeter",
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
                "runner_mode": "jmeter_local",
                "reason": "run configured jmeter command",
            },
        )

        assert response.status_code == 202
        body = response.json()
        assert body["test_command_id"] == str(command_id)
        assert body["runner_mode"] == "jmeter_local"
        assert body["status"] == "failed"
        assert body["parsed_result"]["sampler_count"] == 3
        assert body["parsed_result"]["failed"] == 1
        assert body["test_results"][1]["status"] == "failed"
        assert body["test_results"][1]["metadata"]["source"] == "jmeter_runner"
        artifacts_by_type = {artifact["artifact_type"]: artifact for artifact in body["artifacts"]}
        assert set(artifacts_by_type) >= {"runtime_manifest", "stdout", "stderr", "jmeter_jtl", "parsed_output"}
        assert artifacts_by_type["jmeter_jtl"]["mime_type"] == "text/csv"
    finally:
        app.dependency_overrides.clear()


def test_create_jmeter_test_run_rejects_forbidden_shell_operator(tmp_path: Path) -> None:
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
                name="unsafe jmeter",
                command="jmeter -n -t plans/coupon.jmx -l results.jtl && rm -rf /tmp/example",
                working_directory=str(tmp_path),
                command_type="jmeter",
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
                "runner_mode": "jmeter_local",
                "reason": "run unsafe jmeter command",
            },
        )

        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()
