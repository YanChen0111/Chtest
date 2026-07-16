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
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import CICDChangedFile, CICDRun
from backend.app.modules.cicd.schemas import (
    CICDChangedFileRead,
    CICDRunCreateRequest,
    CICDRunListRead,
    CICDRunRead,
)
from backend.app.modules.cicd.service import parse_local_diff
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.models import Project, Repository, Workspace
from backend.app.modules.projects.router import get_session
from backend.app.modules.reporting.models import Report


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


def seed_project_repository(session: Session) -> tuple[Project, Repository]:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    repository = Repository(
        project_id=project.id,
        name="sample-app",
        local_path="/Users/yanchen/VscodeProject/sample-app",
        default_base_branch="main",
        language_hint="python",
    )
    session.add(repository)
    session.flush()
    return project, repository


def test_cicd_run_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, repository = seed_project_repository(session)
        cicd_run = CICDRun(
            project_id=project.id,
            repository_id=repository.id,
            source_type="local_diff",
            trigger_type="manual",
            provider="local",
            pipeline_name="local diff check",
            base_ref="main",
            head_ref="HEAD",
            summary="Coupon amount boundary change",
            overall_risk="medium",
        )
        session.add(cicd_run)
        session.commit()
        persisted = session.scalar(select(CICDRun).where(CICDRun.id == cicd_run.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.repository_id == repository.id
    assert persisted.source_type == "local_diff"
    assert persisted.trigger_type == "manual"
    assert persisted.provider == "local"
    assert persisted.pipeline_name == "local diff check"
    assert persisted.base_ref == "main"
    assert persisted.head_ref == "HEAD"
    assert persisted.summary == "Coupon amount boundary change"
    assert persisted.overall_risk == "medium"
    assert persisted.quality_gate_status == "pending"
    assert persisted.status == "created"


def test_cicd_changed_file_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, repository = seed_project_repository(session)
        cicd_run = CICDRun(project_id=project.id, repository_id=repository.id)
        session.add(cicd_run)
        session.flush()
        changed_file = CICDChangedFile(
            cicd_run_id=cicd_run.id,
            path="app/coupon.py",
            old_path=None,
            change_type="modified",
            language="python",
            file_role="source",
            risk_level="medium",
            risk_reasons_json=["source file changed"],
            lines_added=12,
            lines_deleted=4,
        )
        session.add(changed_file)
        session.commit()
        persisted = session.scalar(select(CICDChangedFile).where(CICDChangedFile.id == changed_file.id))

    assert persisted is not None
    assert persisted.cicd_run_id == cicd_run.id
    assert persisted.path == "app/coupon.py"
    assert persisted.old_path is None
    assert persisted.change_type == "modified"
    assert persisted.language == "python"
    assert persisted.file_role == "source"
    assert persisted.risk_level == "medium"
    assert persisted.risk_reasons_json == ["source file changed"]
    assert persisted.lines_added == 12
    assert persisted.lines_deleted == 4


def test_cicd_run_create_request_defaults_to_local_first_contract() -> None:
    project_id = uuid.uuid4()
    repository_id = uuid.uuid4()

    request = CICDRunCreateRequest(
        project_id=project_id,
        repository_id=repository_id,
        base_ref="main",
        head_ref="HEAD",
    )

    assert request.project_id == project_id
    assert request.repository_id == repository_id
    assert request.source_type == "local_diff"
    assert request.trigger_type == "manual"
    assert request.provider == "local"
    assert request.diff_text is None


def test_cicd_run_read_schema_embeds_changed_files() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()
    repository_id = uuid.uuid4()
    changed_file_id = uuid.uuid4()

    read = CICDRunRead(
        id=run_id,
        project_id=project_id,
        repository_id=repository_id,
        source_type="local_diff",
        trigger_type="manual",
        provider="local",
        pipeline_name=None,
        base_ref="main",
        head_ref="HEAD",
        summary="Coupon amount boundary change",
        overall_risk="medium",
        quality_gate_status="pending",
        status="created",
        changed_files=[
            CICDChangedFileRead(
                id=changed_file_id,
                cicd_run_id=run_id,
                path="app/coupon.py",
                old_path=None,
                change_type="modified",
                language="python",
                file_role="source",
                risk_level="medium",
                risk_reasons=["source file changed"],
                lines_added=12,
                lines_deleted=4,
            ),
        ],
        analysis_artifacts=[],
    )
    listed = CICDRunListRead(items=[read], total=1)

    body = listed.model_dump(mode="json")
    assert body["items"][0]["id"] == str(run_id)
    assert body["items"][0]["repository_id"] == str(repository_id)
    assert body["items"][0]["changed_files"][0]["path"] == "app/coupon.py"
    assert body["items"][0]["changed_files"][0]["risk_reasons"] == ["source file changed"]


def test_parse_local_diff_returns_changed_file_evidence() -> None:
    diff_text = """diff --git a/app/coupon.py b/app/coupon.py
index 1111111..2222222 100644
--- a/app/coupon.py
+++ b/app/coupon.py
@@ -1,2 +1,5 @@
-old line
+new line
+another line
diff --git a/tests/test_coupon.py b/tests/test_coupon.py
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/tests/test_coupon.py
@@ -0,0 +1,3 @@
+def test_coupon():
+    assert True
diff --git a/docs/coupon.md b/docs/coupon.md
deleted file mode 100644
index 4444444..0000000
--- a/docs/coupon.md
+++ /dev/null
@@ -1,2 +0,0 @@
-old docs
diff --git a/package.json b/package.json
similarity index 92%
rename from package.json
rename to package-renamed.json
--- a/package.json
+++ b/package-renamed.json
@@ -1 +1 @@
-{"scripts":{}}
+{"scripts":{"test":"vitest"}}
"""

    parsed = parse_local_diff(diff_text)
    manifest = {"changed_files": [item.to_manifest_item() for item in parsed]}

    assert [item.path for item in parsed] == [
        "app/coupon.py",
        "tests/test_coupon.py",
        "docs/coupon.md",
        "package-renamed.json",
    ]
    assert [item.change_type for item in parsed] == ["modified", "added", "deleted", "renamed"]
    assert [item.file_role for item in parsed] == ["source", "test", "docs", "build"]
    assert parsed[0].language == "python"
    assert parsed[0].lines_added == 2
    assert parsed[0].lines_deleted == 1
    assert parsed[0].risk_level == "medium"
    assert parsed[1].risk_level == "low"
    assert parsed[2].risk_level == "low"
    assert parsed[3].old_path == "package.json"
    assert parsed[3].risk_level == "medium"
    assert manifest["changed_files"][0]["risk_reasons"]


def test_create_list_get_cicd_run_api_persists_local_diff_changed_files() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project, repository = seed_project_repository(session)
            session.commit()
            project_id = project.id
            repository_id = repository.id

        client = ASGIClient(app)
        response = client.post(
            "/api/cicd/runs",
            {
                "project_id": str(project_id),
                "repository_id": str(repository_id),
                "source_type": "local_diff",
                "base_ref": "main",
                "head_ref": "HEAD",
                "diff_text": "diff --git a/app/coupon.py b/app/coupon.py\n--- a/app/coupon.py\n+++ b/app/coupon.py\n@@ -1 +1,2 @@\n-old\n+new\n",
            },
        )

        assert response.status_code == 202
        created = response.json()
        assert created["status"] == "created"

        list_response = client.get("/api/cicd/runs")
        assert list_response.status_code == 200
        listed = list_response.json()
        assert listed["total"] == 1
        assert listed["items"][0]["id"] == created["cicd_run_id"]
        assert listed["items"][0]["changed_files"][0]["path"] == "app/coupon.py"

        get_response = client.get(f"/api/cicd/runs/{created['cicd_run_id']}")
        assert get_response.status_code == 200
        body = get_response.json()
        assert body["project_id"] == str(project_id)
        assert body["repository_id"] == str(repository_id)
        assert body["source_type"] == "local_diff"
        assert body["trigger_type"] == "manual"
        assert body["provider"] == "local"
        assert body["quality_gate_status"] == "pending"
        assert body["status"] == "created"
        assert body["changed_files"][0]["file_role"] == "source"
        assert body["changed_files"][0]["risk_level"] == "medium"

        with SessionLocal() as session:
            run = session.get(CICDRun, uuid.UUID(created["cicd_run_id"]))
            changed_files = list(session.scalars(select(CICDChangedFile).where(CICDChangedFile.cicd_run_id == run.id)))
            artifacts = list(
                session.scalars(
                    select(Artifact).where(
                        Artifact.owner_entity_type == "CICDRun",
                        Artifact.owner_entity_id == run.id,
                    ),
                ),
            )
            assert session.scalar(select(AutomationDraft)) is None
            assert session.scalar(select(TestRun)) is None
            assert session.scalar(select(Report)) is None

        assert run is not None
        assert len(changed_files) == 1
        assert {artifact.artifact_type for artifact in artifacts} == {"diff_patch", "changed_files"}
    finally:
        app.dependency_overrides.clear()


def test_analyze_cicd_run_api_writes_mock_risk_analysis_evidence() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project, repository = seed_project_repository(session)
            session.commit()
            project_id = project.id
            repository_id = repository.id

        client = ASGIClient(app)
        create_response = client.post(
            "/api/cicd/runs",
            {
                "project_id": str(project_id),
                "repository_id": str(repository_id),
                "source_type": "local_diff",
                "base_ref": "main",
                "head_ref": "HEAD",
                "diff_text": "diff --git a/app/coupon.py b/app/coupon.py\n--- a/app/coupon.py\n+++ b/app/coupon.py\n@@ -1 +1,2 @@\n-old\n+new\n",
            },
        )
        cicd_run_id = create_response.json()["cicd_run_id"]

        analyze_response = client.post(
            f"/api/cicd/runs/{cicd_run_id}/analyze",
            {
                "prompt_version": "cicd_change_analysis:v1",
                "skill_version": "regression-selection-skill:v1",
                "model_provider": "mock",
                "model_name": "mock-cicd-analysis",
            },
        )

        assert analyze_response.status_code == 202
        analyzed = analyze_response.json()
        assert analyzed["cicd_run_id"] == cicd_run_id
        assert analyzed["status"] == "analyzed"
        assert analyzed["ai_task_id"] is not None
        assert analyzed["risk_analysis_artifact_id"] is not None

        get_response = client.get(f"/api/cicd/runs/{cicd_run_id}")
        assert get_response.status_code == 200
        body = get_response.json()
        assert body["status"] == "analyzed"
        assert body["overall_risk"] == "medium"
        assert body["analysis_artifacts"][0]["artifact_type"] == "risk_analysis"

        with SessionLocal() as session:
            ai_task = session.get(AITask, uuid.UUID(analyzed["ai_task_id"]))
            run = session.get(CICDRun, uuid.UUID(cicd_run_id))
            risk_artifact = session.get(Artifact, uuid.UUID(analyzed["risk_analysis_artifact_id"]))
            assert session.scalar(select(AutomationDraft)) is None
            assert session.scalar(select(TestRun)) is None
            assert session.scalar(select(Report)) is None

        assert ai_task is not None
        assert ai_task.task_type == "cicd_change_analysis"
        assert ai_task.status == "succeeded"
        assert ai_task.output_json["overall_risk"] == "medium"
        assert run is not None
        assert run.status == "analyzed"
        assert risk_artifact is not None
        assert risk_artifact.owner_entity_type == "CICDRun"
        assert risk_artifact.metadata_json["overall_risk"] == "medium"
        assert risk_artifact.metadata_json["changed_file_count"] == 1
    finally:
        app.dependency_overrides.clear()
