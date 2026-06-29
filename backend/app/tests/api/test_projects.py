from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.projects.models import (
    Environment,
    Module,
    Project,
    Repository,
    TestCommand,
    Workspace,
)
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

    def patch(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("PATCH", path, json_body)

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
def api_client() -> Iterator[tuple[ASGIClient, sessionmaker[Session]]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)

    def override_get_session() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    yield ASGIClient(app), SessionLocal

    app.dependency_overrides.clear()


def test_create_project_returns_contract_read_model(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/projects",
        json_body={
            "name": "Checkout System",
            "description": "personal testing project",
            "default_language": "python",
            "default_test_type": "functional",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["name"] == "Checkout System"
    assert body["description"] == "personal testing project"
    assert body["default_language"] == "python"
    assert body["default_test_type"] == "functional"
    assert body["status"] == "active"
    assert body["created_at"]


def test_get_project_returns_created_project(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client
    created = client.post("/api/projects", json_body={"name": "Checkout System"}).json()

    response = client.get(f"/api/projects/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Checkout System"


def test_update_project_patches_allowed_project_fields(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client
    created = client.post("/api/projects", json_body={"name": "Checkout System"}).json()

    response = client.patch(
        f"/api/projects/{created['id']}",
        json_body={
            "name": "Checkout Platform",
            "description": "updated project description",
            "default_language": "javascript",
            "default_test_type": "api",
            "status": "active",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["name"] == "Checkout Platform"
    assert body["description"] == "updated project description"
    assert body["default_language"] == "javascript"
    assert body["default_test_type"] == "api"
    assert body["status"] == "active"


def test_project_settings_bootstrap_returns_related_context(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    created = client.post("/api/projects", json_body={"name": "Checkout System"}).json()
    project_id = uuid.UUID(created["id"])

    with SessionLocal() as session:
        project = session.get(Project, project_id)
        assert project is not None
        module = Module(
            project=project,
            name="Coupon",
            level=1,
            path="/coupon",
            sort_order=10,
        )
        repository = Repository(
            project=project,
            name="sample-checkout",
            local_path="/Users/yanchen/VscodeProject/sample-checkout",
            default_base_branch="main",
            language_hint="python",
        )
        environment = Environment(
            project=project,
            name="local",
            variables_json={"BASE_URL": "http://localhost:8000"},
        )
        test_command = TestCommand(
            project=project,
            repository=repository,
            environment=environment,
            name="pytest unit",
            command="pytest tests -q --junitxml=artifacts/junit.xml",
            working_directory="/Users/yanchen/VscodeProject/sample-checkout",
            command_type="pytest",
        )
        session.add_all([module, repository, environment, test_command])
        session.commit()

    response = client.get(f"/api/projects/{created['id']}/settings")

    assert response.status_code == 200
    body = response.json()
    assert body["project"]["id"] == created["id"]
    assert body["modules"][0]["path"] == "/coupon"
    assert body["repositories"][0]["name"] == "sample-checkout"
    assert body["environments"][0]["variables_json"] == {"BASE_URL": "http://localhost:8000"}
    assert body["test_commands"][0]["name"] == "pytest unit"
    assert body["tool_definitions"] == []


def test_unknown_project_returns_contract_error(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client

    response = client.get(f"/api/projects/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROJECT_NOT_FOUND"


def test_invalid_project_id_returns_contract_error(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client

    response = client.get("/api/projects/not-a-uuid")

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert body["message"] == "Request validation failed."
    assert "errors" in body["details"]


def test_duplicate_project_name_returns_contract_error(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client
    first = client.post("/api/projects", json_body={"name": "Checkout System"})
    assert first.status_code == 201

    response = client.post("/api/projects", json_body={"name": "Checkout System"})

    assert response.status_code == 409
    assert response.json()["error_code"] == "PROJECT_ALREADY_EXISTS"
