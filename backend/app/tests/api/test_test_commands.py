from __future__ import annotations

import asyncio
import json
import os
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


def create_repository(client: ASGIClient, project_id: str, repo_dir: Path) -> dict[str, Any]:
    response = client.post(
        "/api/repositories",
        json_body={"project_id": project_id, "name": "sample-app", "local_path": str(repo_dir)},
    )
    assert response.status_code == 201
    return response.json()


def create_environment(client: ASGIClient, project_id: str) -> dict[str, Any]:
    response = client.post(
        "/api/environments",
        json_body={"project_id": project_id, "name": "local", "variables_json": {"APP_ENV": "test"}},
    )
    assert response.status_code == 201
    return response.json()


def create_test_command_payload(
    project_id: str,
    repository_id: str,
    environment_id: str,
    working_directory: Path,
) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "repository_id": repository_id,
        "environment_id": environment_id,
        "name": "pytest unit",
        "command": "pytest tests/unit -q --junitxml=artifacts/junit.xml",
        "working_directory": str(working_directory),
        "command_type": "pytest",
        "timeout_seconds": 600,
        "parse_junit": True,
        "parse_coverage": False,
    }


@pytest.fixture()
def project_context(api_client: tuple[ASGIClient, Path]) -> tuple[ASGIClient, dict[str, Any]]:
    client, allowlist_root = api_client
    project = create_project(client)
    repo_dir = create_repo_dir(allowlist_root)
    repository = create_repository(client, project["id"], repo_dir)
    environment = create_environment(client, project["id"])
    return client, {
        "project": project,
        "repository": repository,
        "environment": environment,
        "repo_dir": repo_dir,
    }


def test_create_test_command_returns_contract_model(
    project_context: tuple[ASGIClient, dict[str, Any]],
) -> None:
    client, context = project_context

    response = client.post(
        "/api/test-commands",
        json_body=create_test_command_payload(
            context["project"]["id"],
            context["repository"]["id"],
            context["environment"]["id"],
            context["repo_dir"],
        ),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == context["project"]["id"]
    assert body["repository_id"] == context["repository"]["id"]
    assert body["environment_id"] == context["environment"]["id"]
    assert body["command_type"] == "pytest"
    assert body["timeout_seconds"] == 600
    assert body["parse_junit"] is True
    assert body["status"] == "active"


def test_list_and_update_test_command(project_context: tuple[ASGIClient, dict[str, Any]]) -> None:
    client, context = project_context
    created = client.post(
        "/api/test-commands",
        json_body=create_test_command_payload(
            context["project"]["id"],
            context["repository"]["id"],
            context["environment"]["id"],
            context["repo_dir"],
        ),
    ).json()

    update_response = client.patch(
        f"/api/test-commands/{created['id']}",
        json_body={
            "name": "pytest smoke",
            "command": "pytest tests/smoke -q",
            "working_directory": str(context["repo_dir"]),
            "command_type": "pytest",
            "timeout_seconds": 300,
            "parse_junit": False,
            "parse_coverage": False,
            "status": "active",
        },
    )
    list_response = client.get(f"/api/projects/{context['project']['id']}/test-commands")

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "pytest smoke"
    assert update_response.json()["timeout_seconds"] == 300
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == created["id"]
    assert list_response.json()["total"] == 1


def test_validate_test_command_returns_contract_result(
    project_context: tuple[ASGIClient, dict[str, Any]],
) -> None:
    client, context = project_context
    created = client.post(
        "/api/test-commands",
        json_body=create_test_command_payload(
            context["project"]["id"],
            context["repository"]["id"],
            context["environment"]["id"],
            context["repo_dir"],
        ),
    ).json()

    response = client.post(f"/api/test-commands/{created['id']}/validate", json_body={"dry_run": True})

    assert response.status_code == 200
    body = response.json()
    assert body["test_command_id"] == created["id"]
    assert body["valid"] is True
    assert body["allowlist_passed"] is True
    assert body["working_directory_passed"] is True
    assert body["messages"] == []


def test_test_command_rejects_forbidden_shell_operator(
    project_context: tuple[ASGIClient, dict[str, Any]],
) -> None:
    client, context = project_context
    payload = create_test_command_payload(
        context["project"]["id"],
        context["repository"]["id"],
        context["environment"]["id"],
        context["repo_dir"],
    )
    payload["command"] = "pytest tests -q && rm -rf /tmp/example"

    response = client.post("/api/test-commands", json_body=payload)

    assert response.status_code == 422
    assert response.json()["error_code"] == "TEST_COMMAND_NOT_ALLOWED"


def test_test_command_rejects_single_ampersand_and_newline(
    project_context: tuple[ASGIClient, dict[str, Any]],
) -> None:
    client, context = project_context
    for command in ("pytest tests -q & rm -rf /tmp/example", "pytest tests -q\nrm -rf /tmp/example"):
        payload = create_test_command_payload(
            context["project"]["id"],
            context["repository"]["id"],
            context["environment"]["id"],
            context["repo_dir"],
        )
        payload["command"] = command

        response = client.post("/api/test-commands", json_body=payload)

        assert response.status_code == 422
        assert response.json()["error_code"] == "TEST_COMMAND_NOT_ALLOWED"


def test_test_command_rejects_command_outside_allowlist(
    project_context: tuple[ASGIClient, dict[str, Any]],
) -> None:
    client, context = project_context
    payload = create_test_command_payload(
        context["project"]["id"],
        context["repository"]["id"],
        context["environment"]["id"],
        context["repo_dir"],
    )
    payload["command"] = "python manage.py shell"
    payload["command_type"] = "python"

    response = client.post("/api/test-commands", json_body=payload)

    assert response.status_code == 422
    assert response.json()["error_code"] == "TEST_COMMAND_NOT_ALLOWED"


def test_test_command_rejects_playwright_prefix_bypass(
    project_context: tuple[ASGIClient, dict[str, Any]],
) -> None:
    client, context = project_context
    payload = create_test_command_payload(
        context["project"]["id"],
        context["repository"]["id"],
        context["environment"]["id"],
        context["repo_dir"],
    )
    payload["command"] = "npx playwright testmalicious"
    payload["command_type"] = "playwright"

    response = client.post("/api/test-commands", json_body=payload)

    assert response.status_code == 422
    assert response.json()["error_code"] == "TEST_COMMAND_NOT_ALLOWED"


def test_test_command_rejects_working_directory_outside_repository(
    project_context: tuple[ASGIClient, dict[str, Any]],
    tmp_path: Path,
) -> None:
    client, context = project_context
    outside_dir = tmp_path / "outside-workdir"
    outside_dir.mkdir()
    payload = create_test_command_payload(
        context["project"]["id"],
        context["repository"]["id"],
        context["environment"]["id"],
        outside_dir,
    )

    response = client.post("/api/test-commands", json_body=payload)

    assert response.status_code == 422
    assert response.json()["error_code"] == "TEST_COMMAND_NOT_ALLOWED"


def test_test_command_rejects_environment_from_other_project(
    api_client: tuple[ASGIClient, Path],
) -> None:
    client, allowlist_root = api_client
    first_project = create_project(client)
    first_repo_dir = create_repo_dir(allowlist_root, "sample-app")
    first_repository = create_repository(client, first_project["id"], first_repo_dir)
    second_project_response = client.post("/api/projects", json_body={"name": "Inventory System"})
    assert second_project_response.status_code == 201
    second_project = second_project_response.json()
    second_environment = create_environment(client, second_project["id"])
    payload = create_test_command_payload(
        first_project["id"],
        first_repository["id"],
        second_environment["id"],
        first_repo_dir,
    )

    response = client.post("/api/test-commands", json_body=payload)

    assert response.status_code == 422
    assert response.json()["error_code"] == "TEST_COMMAND_NOT_ALLOWED"
