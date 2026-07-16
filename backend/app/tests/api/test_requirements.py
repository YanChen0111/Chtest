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
def api_client() -> Iterator[ASGIClient]:
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

    yield ASGIClient(app)

    app.dependency_overrides.clear()


def create_project(client: ASGIClient, name: str = "Checkout System") -> dict[str, Any]:
    response = client.post("/api/projects", json_body={"name": name})
    assert response.status_code == 201
    return response.json()


def create_module(client: ASGIClient, project_id: str, name: str = "Checkout") -> dict[str, Any]:
    response = client.post(
        f"/api/projects/{project_id}/modules",
        json_body={"name": name, "sort_order": 10},
    )
    assert response.status_code == 201
    return response.json()


def test_create_requirement_returns_contract_read_model(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    module = create_module(api_client, project["id"])

    response = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "module_id": module["id"],
            "title": "Coupon checkout rules",
            "content": "User can select one available coupon during checkout.",
            "source_type": "manual",
            "source_ref": "REQ-COUPON-001",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["project_id"] == project["id"]
    assert body["module_id"] == module["id"]
    assert body["title"] == "Coupon checkout rules"
    assert body["content"] == "User can select one available coupon during checkout."
    assert body["source_type"] == "manual"
    assert body["source_ref"] == "REQ-COUPON-001"
    assert body["status"] == "active"
    assert body["created_at"]
    assert body["updated_at"]


def test_get_requirement_returns_created_requirement(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    created = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "title": "Coupon checkout rules",
            "content": "Coupon cannot be used with points.",
        },
    ).json()

    response = api_client.get(f"/api/requirements/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Coupon checkout rules"
    assert response.json()["source_type"] == "manual"


def test_list_requirements_returns_project_requirements_in_created_order(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    first = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "title": "First requirement",
            "content": "First content.",
        },
    ).json()
    second = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "title": "Second requirement",
            "content": "Second content.",
        },
    ).json()

    response = api_client.get(f"/api/projects/{project['id']}/requirements")

    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body["items"]] == [first["id"], second["id"]]
    assert body["total"] == 2


def test_list_requirements_does_not_return_other_project_requirements(api_client: ASGIClient) -> None:
    first_project = create_project(api_client)
    second_project = create_project(api_client, "Inventory System")
    included = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": first_project["id"],
            "title": "Checkout requirement",
            "content": "Checkout content.",
        },
    ).json()
    other = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": second_project["id"],
            "title": "Inventory requirement",
            "content": "Inventory content.",
        },
    ).json()

    response = api_client.get(f"/api/projects/{first_project['id']}/requirements")

    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body["items"]] == [included["id"]]
    assert other["id"] not in [item["id"] for item in body["items"]]
    assert body["total"] == 1


def test_create_requirement_rejects_unknown_project(api_client: ASGIClient) -> None:
    response = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": str(uuid.uuid4()),
            "title": "Coupon checkout rules",
            "content": "Coupon cannot be used with points.",
        },
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROJECT_NOT_FOUND"


def test_create_requirement_rejects_non_manual_source_type(api_client: ASGIClient) -> None:
    project = create_project(api_client)

    response = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "title": "Imported requirement",
            "content": "Imported content.",
            "source_type": "import",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"


def test_create_requirement_rejects_module_from_other_project(api_client: ASGIClient) -> None:
    first_project = create_project(api_client)
    second_project = create_project(api_client, "Inventory System")
    foreign_module = create_module(api_client, first_project["id"])

    response = api_client.post(
        "/api/requirements",
        json_body={
            "project_id": second_project["id"],
            "module_id": foreign_module["id"],
            "title": "Coupon checkout rules",
            "content": "Coupon cannot be used with points.",
        },
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "MODULE_NOT_FOUND"


def test_unknown_requirement_returns_contract_error(api_client: ASGIClient) -> None:
    response = api_client.get(f"/api/requirements/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "REQUIREMENT_NOT_FOUND"


def test_unknown_project_requirement_list_returns_contract_error(api_client: ASGIClient) -> None:
    response = api_client.get(f"/api/projects/{uuid.uuid4()}/requirements")

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROJECT_NOT_FOUND"
