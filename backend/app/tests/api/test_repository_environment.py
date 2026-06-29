from __future__ import annotations

import asyncio
import json
import os
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
def api_client(tmp_path: Path) -> Iterator[tuple[ASGIClient, Path]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)

    allowlist_root = tmp_path / "repos"
    allowlist_root.mkdir()
    previous_allowlist = os.environ.get("CHTEST_REPOSITORY_ALLOWLIST_ROOTS")
    os.environ["CHTEST_REPOSITORY_ALLOWLIST_ROOTS"] = str(allowlist_root)

    def override_get_session() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    yield ASGIClient(app), allowlist_root

    app.dependency_overrides.clear()
    if previous_allowlist is None:
        os.environ.pop("CHTEST_REPOSITORY_ALLOWLIST_ROOTS", None)
    else:
        os.environ["CHTEST_REPOSITORY_ALLOWLIST_ROOTS"] = previous_allowlist


def create_project(client: ASGIClient) -> dict[str, Any]:
    response = client.post("/api/projects", json_body={"name": "Checkout System"})
    assert response.status_code == 201
    return response.json()


def create_repo_dir(allowlist_root: Path, name: str = "sample-app") -> Path:
    repo_dir = allowlist_root / name
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()
    return repo_dir


def test_create_repository_requires_existing_allowlisted_path(
    api_client: tuple[ASGIClient, Path],
) -> None:
    client, allowlist_root = api_client
    project = create_project(client)
    repo_dir = create_repo_dir(allowlist_root)

    response = client.post(
        "/api/repositories",
        json_body={
            "project_id": project["id"],
            "name": "sample-app",
            "local_path": str(repo_dir),
            "default_base_branch": "main",
            "language_hint": "python",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project["id"]
    assert body["name"] == "sample-app"
    assert body["local_path"] == str(repo_dir.resolve())
    assert body["default_base_branch"] == "main"
    assert body["language_hint"] == "python"
    assert body["status"] == "active"


def test_list_repositories_returns_project_repositories(api_client: tuple[ASGIClient, Path]) -> None:
    client, allowlist_root = api_client
    project = create_project(client)
    repo_dir = create_repo_dir(allowlist_root)
    created = client.post(
        "/api/repositories",
        json_body={"project_id": project["id"], "name": "sample-app", "local_path": str(repo_dir)},
    ).json()

    response = client.get(f"/api/projects/{project['id']}/repositories")

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["id"] == created["id"]
    assert body["total"] == 1


def test_update_repository_revalidates_local_path(api_client: tuple[ASGIClient, Path]) -> None:
    client, allowlist_root = api_client
    project = create_project(client)
    first_repo_dir = create_repo_dir(allowlist_root, "sample-app")
    second_repo_dir = create_repo_dir(allowlist_root, "sample-app-v2")
    created = client.post(
        "/api/repositories",
        json_body={"project_id": project["id"], "name": "sample-app", "local_path": str(first_repo_dir)},
    ).json()

    response = client.patch(
        f"/api/repositories/{created['id']}",
        json_body={
            "name": "sample-app-v2",
            "local_path": str(second_repo_dir),
            "default_base_branch": "develop",
            "language_hint": "javascript",
            "status": "active",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "sample-app-v2"
    assert body["local_path"] == str(second_repo_dir.resolve())
    assert body["default_base_branch"] == "develop"
    assert body["language_hint"] == "javascript"


def test_repository_path_outside_allowlist_returns_contract_error(
    api_client: tuple[ASGIClient, Path],
    tmp_path: Path,
) -> None:
    client, _ = api_client
    project = create_project(client)
    outside_repo = tmp_path / "outside"
    outside_repo.mkdir()

    response = client.post(
        "/api/repositories",
        json_body={"project_id": project["id"], "name": "outside", "local_path": str(outside_repo)},
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "REPOSITORY_PATH_NOT_ALLOWED"


def test_repository_path_must_exist(api_client: tuple[ASGIClient, Path]) -> None:
    client, allowlist_root = api_client
    project = create_project(client)

    response = client.post(
        "/api/repositories",
        json_body={
            "project_id": project["id"],
            "name": "missing",
            "local_path": str(allowlist_root / "missing"),
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "REPOSITORY_PATH_NOT_ALLOWED"


def test_create_environment_returns_contract_model(api_client: tuple[ASGIClient, Path]) -> None:
    client, _ = api_client
    project = create_project(client)

    response = client.post(
        "/api/environments",
        json_body={
            "project_id": project["id"],
            "name": "local",
            "variables_json": {"APP_ENV": "test", "BASE_URL": "http://127.0.0.1:8000"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project["id"]
    assert body["name"] == "local"
    assert body["variables_json"] == {"APP_ENV": "test", "BASE_URL": "http://127.0.0.1:8000"}
    assert body["status"] == "active"


def test_create_environment_rejects_raw_secret_values(api_client: tuple[ASGIClient, Path]) -> None:
    client, _ = api_client
    project = create_project(client)

    response = client.post(
        "/api/environments",
        json_body={
            "project_id": project["id"],
            "name": "local",
            "variables_json": {"API_TOKEN": "plain-token-value"},
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "ENVIRONMENT_SECRET_NOT_ALLOWED"


def test_list_and_update_environment(api_client: tuple[ASGIClient, Path]) -> None:
    client, _ = api_client
    project = create_project(client)
    created = client.post(
        "/api/environments",
        json_body={"project_id": project["id"], "name": "local", "variables_json": {"APP_ENV": "test"}},
    ).json()

    update_response = client.patch(
        f"/api/environments/{created['id']}",
        json_body={
            "name": "dev",
            "variables_json": {"APP_ENV": "dev"},
            "status": "active",
        },
    )
    list_response = client.get(f"/api/projects/{project['id']}/environments")

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "dev"
    assert update_response.json()["variables_json"] == {"APP_ENV": "dev"}
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == created["id"]
    assert list_response.json()["total"] == 1


def test_update_environment_allows_secret_reference(api_client: tuple[ASGIClient, Path]) -> None:
    client, _ = api_client
    project = create_project(client)
    created = client.post(
        "/api/environments",
        json_body={"project_id": project["id"], "name": "local", "variables_json": {"APP_ENV": "test"}},
    ).json()

    response = client.patch(
        f"/api/environments/{created['id']}",
        json_body={"variables_json": {"API_TOKEN": "ref:local/api-token"}},
    )

    assert response.status_code == 200
    assert response.json()["variables_json"] == {"API_TOKEN": "ref:local/api-token"}


def test_unknown_project_repository_create_returns_contract_error(
    api_client: tuple[ASGIClient, Path],
) -> None:
    client, allowlist_root = api_client
    repo_dir = create_repo_dir(allowlist_root)

    response = client.post(
        "/api/repositories",
        json_body={"project_id": str(uuid.uuid4()), "name": "sample-app", "local_path": str(repo_dir)},
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROJECT_NOT_FOUND"
