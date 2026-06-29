from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.projects.router import get_session


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
        return self.request("GET", path)

    def post(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("POST", path, json_body)

    def request(self, method: str, path: str, json_body: dict[str, Any] | None = None) -> ASGIResponse:
        return asyncio.run(self._request(method, path, json_body))

    async def _request(
        self,
        method: str,
        path: str,
        json_body: dict[str, Any] | None,
    ) -> ASGIResponse:
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


@pytest.fixture()
def api_client(tmp_path: Path) -> Iterator[tuple[ASGIClient, sessionmaker[Session], Path]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)
    artifact_root = tmp_path / "artifacts"

    def override_get_session() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    def override_get_artifact_store() -> LocalArtifactStore:
        return LocalArtifactStore(root=artifact_root)

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_artifact_store] = override_get_artifact_store

    yield ASGIClient(app), SessionLocal, artifact_root

    app.dependency_overrides.clear()


def create_project(SessionLocal: sessionmaker[Session], name: str = "Checkout") -> Project:
    with SessionLocal() as session:
        workspace = session.query(Workspace).filter_by(name="Personal Workspace").one_or_none()
        if workspace is None:
            workspace = Workspace(name="Personal Workspace")
        project = Project(workspace=workspace, name=name)
        session.add(project)
        session.commit()
        session.refresh(project)
        return project


def test_create_context_artifact_writes_file_and_artifact_row(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, artifact_root = api_client
    project = create_project(SessionLocal)

    response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project.id),
            "title": "coupon-api-notes.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": "# Coupon API Notes\nPOST /api/coupons/validate validates coupons.",
            "source_ref": "manual:coupon-api-notes.md",
            "safe_to_show": False,
        },
    )

    assert response.status_code == 201
    body = response.json()
    artifact_id = uuid.UUID(body["id"])
    assert body["project_id"] == str(project.id)
    assert body["owner_entity_type"] == "Project"
    assert body["owner_entity_id"] == str(project.id)
    assert body["artifact_type"] == "context_markdown"
    assert body["mime_type"] == "text/markdown"
    assert body["file_path"] == f"projects/{project.id}/context-artifacts/{artifact_id}/content.md"
    assert body["sha256"].startswith("sha256:")
    assert body["metadata"]["title"] == "coupon-api-notes.md"
    assert body["metadata"]["source_ref"] == "manual:coupon-api-notes.md"
    assert body["metadata"]["safe_to_show"] is True
    assert body["metadata"]["redaction_applied"] is False
    assert body["metadata"]["allowed_for_prompt"] is True
    assert "content" not in body
    assert (artifact_root / body["file_path"]).read_text() == "# Coupon API Notes\nPOST /api/coupons/validate validates coupons."

    with SessionLocal() as session:
        artifact = session.get(Artifact, artifact_id)
        assert artifact is not None
        assert artifact.owner_entity_type == "Project"
        assert artifact.owner_entity_id == project.id
        assert artifact.sha256 == body["sha256"].removeprefix("sha256:")
        assert artifact.metadata_json["allowed_for_prompt"] is True


def test_list_context_artifacts_returns_only_project_context_items(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _ = api_client
    project = create_project(SessionLocal)
    other_project = create_project(SessionLocal, name="Billing")
    created = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project.id),
            "title": "coupon-api-notes.md",
            "artifact_type": "context_text",
            "mime_type": "text/plain",
            "content": "coupon test notes",
            "source_ref": "manual:coupon-api-notes.md",
        },
    ).json()
    client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(other_project.id),
            "title": "other.md",
            "artifact_type": "context_text",
            "mime_type": "text/plain",
            "content": "other notes",
            "source_ref": "manual:other.md",
        },
    )

    response = client.get(f"/api/projects/{project.id}/context-artifacts")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"] == [
        {
            "id": created["id"],
            "title": "coupon-api-notes.md",
            "artifact_type": "context_text",
            "mime_type": "text/plain",
            "safe_to_show": True,
            "redaction_applied": False,
        },
    ]


def test_context_artifact_rejects_unknown_project(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, _, _ = api_client

    response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(uuid.uuid4()),
            "title": "missing.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": "# Missing",
            "source_ref": "manual:missing.md",
        },
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROJECT_NOT_FOUND"


def test_context_artifact_rejects_disallowed_mime(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _ = api_client
    project = create_project(SessionLocal)

    response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project.id),
            "title": "image.png",
            "artifact_type": "context_markdown",
            "mime_type": "image/png",
            "content": "not allowed",
            "source_ref": "manual:image.png",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "CONTEXT_ARTIFACT_NOT_ALLOWED"


def test_context_artifact_rejects_mismatched_type_and_mime(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _ = api_client
    project = create_project(SessionLocal)

    response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project.id),
            "title": "coupon-api-notes.md",
            "artifact_type": "context_json",
            "mime_type": "text/plain",
            "content": "{}",
            "source_ref": "manual:coupon-api-notes.md",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "CONTEXT_ARTIFACT_NOT_ALLOWED"


def test_context_artifact_rejects_large_content(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _ = api_client
    project = create_project(SessionLocal)

    response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project.id),
            "title": "large.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": "x" * (1024 * 1024 + 1),
            "source_ref": "manual:large.md",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "CONTEXT_ARTIFACT_TOO_LARGE"


def test_context_artifact_rejects_high_risk_secret(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _ = api_client
    project = create_project(SessionLocal)

    response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project.id),
            "title": "secret.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": "Authorization: Bearer sk-test-secret-value",
            "source_ref": "manual:secret.md",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "CONTEXT_ARTIFACT_SECRET_DETECTED"


def test_context_artifact_scans_metadata_for_secrets(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _ = api_client
    project = create_project(SessionLocal)

    response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project.id),
            "title": "user@example.com",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": "# safe note",
            "source_ref": "manual:safe.md",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "CONTEXT_ARTIFACT_SECRET_DETECTED"


def test_context_artifact_metadata_includes_base_artifact_fields(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _ = api_client
    project = create_project(SessionLocal)

    body = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project.id),
            "title": "coupon-api-notes.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": "# safe note",
            "source_ref": "manual:coupon-api-notes.md",
        },
    ).json()

    metadata = body["metadata"]
    assert metadata["created_by_component"] == "ContextArtifactAPI"
    assert metadata["source_entity_type"] == "Project"
    assert metadata["source_entity_id"] == str(project.id)
    assert metadata["description"] == "Context artifact coupon-api-notes.md"
