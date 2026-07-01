from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.projects.router import get_session
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.modules.reporting.schemas import FailureAnalysisRead as AnalysisRead
from backend.app.modules.reporting.schemas import ReportRead as ExecutionReportRead


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def get(self, path: str) -> ASGIResponse:
        return asyncio.run(self._request("GET", path, None))

    def post(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
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


def seed_project_task_and_run(session: Session) -> tuple[Project, AITask, TestRun, TestResult, Artifact]:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    ai_task = AITask(
        project_id=project.id,
        agent_name="FailureAnalysisAgent",
        task_type="failure_analysis",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
        model_provider="mock",
        model_name="mock-failure-analysis",
        status="succeeded",
        input_json={},
        output_json={},
    )
    test_run = TestRun(
        project_id=project.id,
        name="pytest failed run",
        command="pytest tests/test_coupon.py -q",
        working_directory="/Users/yanchen/VscodeProject/sample-app",
        status="failed",
        exit_code=1,
        parsed_result_json={"total": 1, "passed": 0, "failed": 1, "skipped": 0, "error": 0},
    )
    session.add_all([ai_task, test_run])
    session.flush()
    artifact = Artifact(
        project_id=project.id,
        owner_entity_type="TestRun",
        owner_entity_id=test_run.id,
        artifact_type="stderr",
        file_path=f"test-runs/{test_run.id}/stderr.log",
        mime_type="text/plain",
        size_bytes=32,
        sha256="sha256:stderr",
        metadata_json={"source": "pytest"},
    )
    session.add(artifact)
    session.flush()
    result = TestResult(
        project_id=project.id,
        test_run_id=test_run.id,
        test_name="tests/test_coupon.py::test_expired_coupon",
        test_file="tests/test_coupon.py",
        status="failed",
        failure_message="fixture coupon_client not found",
        failure_artifact_ids=[artifact.id],
        metadata_json={"classname": "tests.test_coupon"},
    )
    session.add(result)
    session.flush()
    return project, ai_task, test_run, result, artifact


def seed_failed_run_without_evidence(session: Session) -> tuple[Project, TestRun]:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    test_run = TestRun(
        project_id=project.id,
        name="pytest failed run without evidence",
        command="pytest tests/test_coupon.py -q",
        working_directory="/Users/yanchen/VscodeProject/sample-app",
        status="failed",
        exit_code=1,
        parsed_result_json={},
    )
    session.add(test_run)
    session.flush()
    return project, test_run


def test_failure_analysis_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, ai_task, test_run, test_result, artifact = seed_project_task_and_run(session)
        analysis = FailureAnalysis(
            project_id=project.id,
            test_run_id=test_run.id,
            test_result_id=test_result.id,
            ai_task_id=ai_task.id,
            classification="test_script_issue",
            confidence=0.82,
            evidence_artifact_ids=[artifact.id],
            summary="Fixture lookup failed before business assertion.",
            root_cause="coupon_client fixture is missing.",
            suggested_actions_json=["Add fixture coupon_client"],
        )
        session.add(analysis)
        session.commit()
        persisted = session.scalar(select(FailureAnalysis).where(FailureAnalysis.id == analysis.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.test_run_id == test_run.id
    assert persisted.test_result_id == test_result.id
    assert persisted.ai_task_id == ai_task.id
    assert persisted.classification == "test_script_issue"
    assert float(persisted.confidence) == 0.82
    assert persisted.evidence_artifact_ids == [artifact.id]
    assert persisted.suggested_actions_json == ["Add fixture coupon_client"]
    assert persisted.status == "draft"


def test_report_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, _ai_task, test_run, _test_result, artifact = seed_project_task_and_run(session)
        report = Report(
            project_id=project.id,
            report_type="automation_execution",
            title="Automation execution report",
            related_entity_type="TestRun",
            related_entity_id=test_run.id,
            status="ready",
            conclusion="failed",
            summary="1 pytest test failed.",
            metrics_json={"total": 1, "failed": 1},
            artifact_ids=[artifact.id],
        )
        session.add(report)
        session.commit()
        persisted = session.scalar(select(Report).where(Report.id == report.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.report_type == "automation_execution"
    assert persisted.related_entity_type == "TestRun"
    assert persisted.related_entity_id == test_run.id
    assert persisted.status == "ready"
    assert persisted.conclusion == "failed"
    assert persisted.metrics_json["failed"] == 1
    assert persisted.artifact_ids == [artifact.id]


def test_failure_analysis_read_schema_uses_contract_field_names() -> None:
    analysis_id = uuid.uuid4()
    project_id = uuid.uuid4()
    test_run_id = uuid.uuid4()
    ai_task_id = uuid.uuid4()
    artifact_id = uuid.uuid4()

    read = AnalysisRead(
        id=analysis_id,
        project_id=project_id,
        test_run_id=test_run_id,
        test_result_id=None,
        ai_task_id=ai_task_id,
        classification="insufficient_evidence",
        confidence=0.0,
        evidence_artifact_ids=[artifact_id],
        summary="Not enough evidence.",
        root_cause=None,
        suggested_actions=["Attach stdout and stderr artifacts"],
        status="draft",
    )

    body = read.model_dump(mode="json")
    assert body["id"] == str(analysis_id)
    assert body["classification"] == "insufficient_evidence"
    assert body["evidence_artifact_ids"] == [str(artifact_id)]
    assert body["suggested_actions"] == ["Attach stdout and stderr artifacts"]


def test_report_read_schema_embeds_evidence_manifest() -> None:
    report_id = uuid.uuid4()
    project_id = uuid.uuid4()
    run_id = uuid.uuid4()
    artifact_id = uuid.uuid4()

    read = ExecutionReportRead(
        id=report_id,
        project_id=project_id,
        report_type="automation_execution",
        title="Automation execution report",
        related_entity_type="TestRun",
        related_entity_id=run_id,
        status="ready",
        conclusion="passed",
        summary="1 test passed.",
        metrics={"total": 1, "passed": 1},
        artifact_ids=[artifact_id],
        evidence_manifest={
            "report_id": str(report_id),
            "conclusion": "passed",
            "evidence": [{"artifact_id": str(artifact_id), "required": True}],
            "missing_evidence": [],
        },
        artifacts=[],
    )

    body = read.model_dump(mode="json")
    assert body["id"] == str(report_id)
    assert body["related_entity_id"] == str(run_id)
    assert body["metrics"]["passed"] == 1
    assert body["artifact_ids"] == [str(artifact_id)]
    assert body["evidence_manifest"]["missing_evidence"] == []


def test_create_failure_analysis_api_classifies_from_test_run_evidence() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            _project, _ai_task, test_run, _result, artifact = seed_project_task_and_run(session)
            session.commit()
            test_run_id = test_run.id
            artifact_id = artifact.id

        client = ASGIClient(app)
        response = client.post(
            f"/api/test-runs/{test_run_id}/failure-analysis",
            {"model_provider": "mock", "model_name": "mock-failure-analysis"},
        )

        assert response.status_code == 202
        created = response.json()
        assert created["status"] == "draft"

        get_response = client.get(f"/api/test-runs/{test_run_id}/failure-analysis")
        assert get_response.status_code == 200
        body = get_response.json()
        assert body["id"] == created["failure_analysis_id"]
        assert body["ai_task_id"] == created["ai_task_id"]
        assert body["classification"] == "test_script_issue"
        assert body["confidence"] == 0.82
        assert body["evidence_artifact_ids"] == [str(artifact_id)]
        assert body["root_cause"] == "fixture coupon_client not found"
        assert body["suggested_actions"] == ["Add or fix the missing test fixture before rerunning the suite."]

        with SessionLocal() as session:
            ai_task = session.get(AITask, uuid.UUID(created["ai_task_id"]))
            assert ai_task is not None
            assert ai_task.task_type == "failure_analysis"
            assert ai_task.status == "succeeded"
            assert ai_task.output_json["classification"] == "test_script_issue"
            assert session.scalar(select(Report)) is None
    finally:
        app.dependency_overrides.clear()


def test_create_failure_analysis_api_returns_insufficient_evidence_without_artifacts_or_results() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            _project, test_run = seed_failed_run_without_evidence(session)
            session.commit()
            test_run_id = test_run.id

        client = ASGIClient(app)
        response = client.post(f"/api/test-runs/{test_run_id}/failure-analysis", {})

        assert response.status_code == 202
        get_response = client.get(f"/api/test-runs/{test_run_id}/failure-analysis")
        assert get_response.status_code == 200
        body = get_response.json()
        assert body["classification"] == "insufficient_evidence"
        assert body["confidence"] == 0.0
        assert body["evidence_artifact_ids"] == []
        assert body["root_cause"] is None
        assert body["suggested_actions"] == ["Attach stdout, stderr, and failed TestResult evidence before analysis."]
    finally:
        app.dependency_overrides.clear()


def test_create_automation_execution_report_api_writes_evidence_artifacts() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project, _ai_task, test_run, _result, artifact = seed_project_task_and_run(session)
            session.commit()
            project_id = project.id
            test_run_id = test_run.id
            artifact_id = artifact.id

        client = ASGIClient(app)
        response = client.post(
            "/api/reports",
            {
                "project_id": str(project_id),
                "report_type": "automation_execution",
                "related_entity_type": "TestRun",
                "related_entity_id": str(test_run_id),
            },
        )

        assert response.status_code == 202
        created = response.json()
        assert created["status"] == "ready"
        assert created["evidence_manifest_artifact_id"] is not None

        get_response = client.get(f"/api/reports/{created['report_id']}")
        assert get_response.status_code == 200
        body = get_response.json()
        assert body["id"] == created["report_id"]
        assert body["report_type"] == "automation_execution"
        assert body["related_entity_type"] == "TestRun"
        assert body["related_entity_id"] == str(test_run_id)
        assert body["status"] == "ready"
        assert body["conclusion"] == "failed"
        assert body["metrics"]["failed"] == 1
        assert str(artifact_id) in body["evidence_manifest"]["evidence"][0]["artifact_id"]
        assert body["evidence_manifest"]["missing_evidence"] == []
        artifact_types = {artifact["artifact_type"] for artifact in body["artifacts"]}
        assert artifact_types == {"report_md", "report_json"}
        manifest = next(
            artifact
            for artifact in body["artifacts"]
            if artifact["id"] == created["evidence_manifest_artifact_id"]
        )
        assert manifest["metadata_json"]["manifest_kind"] == "evidence_manifest"
    finally:
        app.dependency_overrides.clear()


def test_create_automation_execution_report_api_does_not_pass_without_evidence() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project, test_run = seed_failed_run_without_evidence(session)
            test_run.parsed_result_json = {"total": 1, "passed": 1, "failed": 0, "skipped": 0, "error": 0}
            test_run.status = "passed"
            test_run.exit_code = 0
            session.add(test_run)
            session.commit()
            project_id = project.id
            test_run_id = test_run.id

        client = ASGIClient(app)
        response = client.post(
            "/api/reports",
            {
                "project_id": str(project_id),
                "report_type": "automation_execution",
                "related_entity_type": "TestRun",
                "related_entity_id": str(test_run_id),
            },
        )

        assert response.status_code == 202
        body = client.get(f"/api/reports/{response.json()['report_id']}").json()
        assert body["conclusion"] == "insufficient_evidence"
        assert body["metrics"]["passed"] == 1
        assert body["evidence_manifest"]["missing_evidence"] == ["execution_artifact"]
    finally:
        app.dependency_overrides.clear()
