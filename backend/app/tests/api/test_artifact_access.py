from __future__ import annotations

import asyncio
import hashlib
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
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.projects.router import get_session


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes, headers: dict[str, str]) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def get(self, path: str) -> ASGIResponse:
        return asyncio.run(self._request("GET", path))

    async def _request(self, method: str, path: str) -> ASGIResponse:
        status_code: int | None = None
        body_chunks: list[bytes] = []
        headers: dict[str, str] = {}
        request_complete = False

        async def receive() -> dict[str, Any]:
            nonlocal request_complete
            if not request_complete:
                request_complete = True
                return {"type": "http.request", "body": b"", "more_body": False}
            return {"type": "http.disconnect"}

        async def send(message: dict[str, Any]) -> None:
            nonlocal status_code, headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = {key.decode("latin-1").lower(): value.decode("latin-1") for key, value in message["headers"]}
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
            "headers": [(b"host", b"testserver")],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }

        await self.asgi_app(scope, receive, send)
        assert status_code is not None
        return ASGIResponse(status_code, b"".join(body_chunks), headers)


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


def seed_project(session: Session) -> Project:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    return project


def create_artifact(
    SessionLocal: sessionmaker[Session],
    artifact_root: Path,
    *,
    file_path: str = "projects/demo/test-runs/run-1/stdout.log",
    content: bytes = b"pytest output\n",
    mime_type: str = "text/plain",
    metadata_json: dict[str, Any] | None = None,
) -> uuid.UUID:
    destination = artifact_root / file_path
    destination.parent.mkdir(parents=True)
    destination.write_bytes(content)
    with SessionLocal() as session:
        project = seed_project(session)
        artifact = Artifact(
            project_id=project.id,
            owner_entity_type="TestRun",
            owner_entity_id=uuid.uuid4(),
            artifact_type="stdout",
            file_path=file_path,
            mime_type=mime_type,
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            metadata_json=metadata_json or {"created_by_component": "test"},
        )
        session.add(artifact)
        session.commit()
        return artifact.id


def test_download_local_artifact_returns_recorded_content_and_headers(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, artifact_root = api_client
    artifact_id = create_artifact(
        SessionLocal,
        artifact_root,
        file_path="projects/demo/test-runs/run-1/stdout.log",
        content=b"hello artifact\n",
        mime_type="text/plain",
    )

    response = client.get(f"/api/artifacts/{artifact_id}/download")

    assert response.status_code == 200
    assert response.body == b"hello artifact\n"
    assert response.headers["content-type"].startswith("text/plain")
    assert 'filename="stdout.log"' in response.headers["content-disposition"]


def test_download_missing_artifact_returns_contract_error(api_client: tuple[ASGIClient, sessionmaker[Session], Path]) -> None:
    client, _, _ = api_client

    response = client.get(f"/api/artifacts/{uuid.uuid4()}/download")

    assert response.status_code == 404
    assert response.json()["error_code"] == "ARTIFACT_NOT_FOUND"


def test_download_rejects_unsafe_artifact_path(api_client: tuple[ASGIClient, sessionmaker[Session], Path]) -> None:
    client, SessionLocal, _ = api_client
    with SessionLocal() as session:
        project = seed_project(session)
        artifact = Artifact(
            project_id=project.id,
            owner_entity_type="TestRun",
            owner_entity_id=uuid.uuid4(),
            artifact_type="stdout",
            file_path="../outside.log",
            mime_type="text/plain",
            size_bytes=1,
            sha256=hashlib.sha256(b"x").hexdigest(),
            metadata_json={"created_by_component": "test"},
        )
        session.add(artifact)
        session.commit()
        artifact_id = artifact.id

    response = client.get(f"/api/artifacts/{artifact_id}/download")

    assert response.status_code == 400
    assert response.json()["error_code"] == "ARTIFACT_PATH_UNSAFE"


def test_download_rejects_external_artifact_reference(api_client: tuple[ASGIClient, sessionmaker[Session], Path]) -> None:
    client, SessionLocal, _ = api_client
    with SessionLocal() as session:
        project = seed_project(session)
        artifact = Artifact(
            project_id=project.id,
            owner_entity_type="CICDRun",
            owner_entity_id=uuid.uuid4(),
            artifact_type="ci_run_metadata",
            file_path="https://example.invalid/artifacts/1",
            mime_type="application/json",
            size_bytes=0,
            sha256="",
            metadata_json={"external_url": "https://example.invalid/artifacts/1"},
        )
        session.add(artifact)
        session.commit()
        artifact_id = artifact.id

    response = client.get(f"/api/artifacts/{artifact_id}/download")

    assert response.status_code == 422
    assert response.json()["error_code"] == "ARTIFACT_NOT_LOCAL"
