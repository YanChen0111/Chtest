import asyncio
import importlib.util
import json
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.main import app
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.projects.models import Project, Repository, Workspace
from backend.app.modules.projects.router import get_session
from backend.app.modules.review_history.models import ReviewHistory
from backend.app.modules.review_history.service import EvidenceArtifactInvalidError, append_review_history
from backend.app.tests.api.test_cicd_quality_center import seed_project_repository, session_factory


PROJECT_CORE_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260626_0001_project_core.py"
REVIEW_HISTORY_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260701_0006_review_history.py"


def load_migration(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


class ReviewHistoryASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class ReviewHistoryASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def get(self, url: str) -> ReviewHistoryASGIResponse:
        return asyncio.run(self._request("GET", url, None))

    def post(self, url: str, json_body: dict[str, Any]) -> ReviewHistoryASGIResponse:
        return asyncio.run(self._request("POST", url, json_body))

    async def _request(
        self,
        method: str,
        url: str,
        json_body: dict[str, Any] | None,
    ) -> ReviewHistoryASGIResponse:
        parsed = urlsplit(url)
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
            "path": parsed.path,
            "raw_path": parsed.path.encode("utf-8"),
            "query_string": parsed.query.encode("utf-8"),
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
        return ReviewHistoryASGIResponse(status_code, b"".join(body_chunks))


def review_history_client() -> Iterator[tuple[ReviewHistoryASGIClient, sessionmaker[Session]]]:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield ReviewHistoryASGIClient(app), SessionLocal
    finally:
        app.dependency_overrides.clear()


def test_append_review_history_uses_default_user_and_persists_append_only_event() -> None:
    for _, SessionLocal in review_history_client():
        with SessionLocal() as session:
            project, _repository = seed_project_repository(session)
            session.commit()
            project_id = project.id
            entity_id = uuid.uuid4()
            artifact = Artifact(
                project_id=project_id,
                owner_entity_type="UnitTestPatch",
                owner_entity_id=entity_id,
                artifact_type="unit_test_patch",
                file_path="unit_test.patch",
                mime_type="text/x-diff",
                size_bytes=12,
                sha256="abc",
                metadata_json={},
            )
            session.add(artifact)
            session.flush()
            artifact_id = artifact.id

            event = append_review_history(
                session,
                project_id=project_id,
                entity_type="UnitTestPatch",
                entity_id=entity_id,
                related_entity_type="CICDRun",
                related_entity_id=uuid.uuid4(),
                action="approve",
                from_status="awaiting_review",
                to_status="approved",
                comment="Only tests/ is modified",
                evidence_artifact_ids=[artifact_id],
                metadata={"source": "unit-test"},
            )
            session.commit()

        with SessionLocal() as session:
            stored = session.scalar(select(ReviewHistory).where(ReviewHistory.id == event.id))

        assert stored is not None
        assert stored.project_id == project_id
        assert stored.entity_type == "UnitTestPatch"
        assert stored.entity_id == entity_id
        assert stored.related_entity_type == "CICDRun"
        assert stored.action == "approve"
        assert stored.from_status == "awaiting_review"
        assert stored.to_status == "approved"
        assert stored.reviewer == "Default User"
        assert stored.comment == "Only tests/ is modified"
        assert stored.evidence_artifact_ids == [artifact_id]
        assert stored.metadata_json == {"source": "unit-test"}


def test_append_review_history_rejects_missing_or_cross_project_artifacts() -> None:
    for _, SessionLocal in review_history_client():
        with SessionLocal() as session:
            project, _repository = seed_project_repository(session)
            other_workspace = Workspace(name="Other Workspace")
            session.add(other_workspace)
            session.flush()
            other_project = Project(workspace_id=other_workspace.id, name="Other Project")
            session.add(other_project)
            session.flush()
            _other_repository = Repository(
                project_id=other_project.id,
                name="other-app",
                local_path="/Users/yanchen/VscodeProject/other-app",
            )
            session.add(_other_repository)
            session.commit()

            missing_artifact_id = uuid.uuid4()
            try:
                append_review_history(
                    session,
                    project_id=project.id,
                    entity_type="UnitTestPatch",
                    entity_id=uuid.uuid4(),
                    action="approve",
                    evidence_artifact_ids=[missing_artifact_id],
                )
            except EvidenceArtifactInvalidError as exc:
                assert exc.artifact_ids == [missing_artifact_id]
            else:
                raise AssertionError("missing artifact id should be rejected")

            cross_project_artifact = Artifact(
                project_id=other_project.id,
                owner_entity_type="UnitTestPatch",
                owner_entity_id=uuid.uuid4(),
                artifact_type="unit_test_patch",
                file_path="unit_test.patch",
                mime_type="text/x-diff",
                size_bytes=12,
                sha256="def",
                metadata_json={},
            )
            session.add(cross_project_artifact)
            session.flush()

            try:
                append_review_history(
                    session,
                    project_id=project.id,
                    entity_type="UnitTestPatch",
                    entity_id=uuid.uuid4(),
                    action="approve",
                    evidence_artifact_ids=[cross_project_artifact.id],
                )
            except EvidenceArtifactInvalidError as exc:
                assert exc.artifact_ids == [cross_project_artifact.id]
            else:
                raise AssertionError("cross-project artifact id should be rejected")


def test_review_history_migration_creates_contract_table() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    migrations = [
        load_migration("project_core_migration_for_review_history", PROJECT_CORE_MIGRATION_PATH),
        load_migration("review_history_migration", REVIEW_HISTORY_MIGRATION_PATH),
    ]

    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        operations = Operations(context)
        original_ops = [migration.op for migration in migrations]
        for migration in migrations:
            migration.op = operations
        try:
            for migration in migrations:
                migration.upgrade()
        finally:
            for migration, original_op in zip(migrations, original_ops, strict=True):
                migration.op = original_op

        inspector = inspect(connection)
        tables = set(inspector.get_table_names())
        columns = {column["name"] for column in inspector.get_columns("review_history")}

    assert "review_history" in tables
    assert {
        "id",
        "project_id",
        "entity_type",
        "entity_id",
        "related_entity_type",
        "related_entity_id",
        "action",
        "from_status",
        "to_status",
        "reviewer",
        "comment",
        "evidence_artifact_ids",
        "metadata_json",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(columns)


def test_list_review_history_filters_by_entity_and_related_entity() -> None:
    for client, SessionLocal in review_history_client():
        with SessionLocal() as session:
            project, _repository = seed_project_repository(session)
            session.commit()
            project_id = project.id
            patch_id = uuid.uuid4()
            cicd_run_id = uuid.uuid4()
            other_entity_id = uuid.uuid4()

            append_review_history(
                session,
                project_id=project_id,
                entity_type="UnitTestPatch",
                entity_id=patch_id,
                related_entity_type="CICDRun",
                related_entity_id=cicd_run_id,
                action="approve",
                from_status="awaiting_review",
                to_status="approved",
            )
            append_review_history(
                session,
                project_id=project_id,
                entity_type="AutomationDraft",
                entity_id=other_entity_id,
                action="edit",
                from_status="under_review",
                to_status="edited",
                reviewer="Local Reviewer",
            )
            session.commit()

        entity_response = client.get(
            f"/api/review-history?project_id={project_id}&entity_type=UnitTestPatch&entity_id={patch_id}",
        )
        related_response = client.get(
            f"/api/review-history?project_id={project_id}&related_entity_type=CICDRun&related_entity_id={cicd_run_id}",
        )

        assert entity_response.status_code == 200
        assert related_response.status_code == 200
        entity_body = entity_response.json()
        related_body = related_response.json()
        assert entity_body["total"] == 1
        assert related_body["total"] == 1
        item = entity_body["items"][0]
        assert item["entity_type"] == "UnitTestPatch"
        assert item["entity_id"] == str(patch_id)
        assert item["related_entity_type"] == "CICDRun"
        assert item["related_entity_id"] == str(cicd_run_id)
        assert item["reviewer"] == "Default User"
        assert item["created_at"]


def test_review_history_has_no_generic_public_create_endpoint() -> None:
    for client, SessionLocal in review_history_client():
        with SessionLocal() as session:
            project, _repository = seed_project_repository(session)
            session.commit()
            project_id = project.id

        response = client.post(
            "/api/review-history",
            {
                "project_id": str(project_id),
                "entity_type": "UnitTestPatch",
                "entity_id": str(uuid.uuid4()),
                "action": "approve",
            },
        )

        assert response.status_code == 405
