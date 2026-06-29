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


def create_project(client: ASGIClient) -> dict[str, Any]:
    response = client.post("/api/projects", json_body={"name": "Checkout System"})
    assert response.status_code == 201
    return response.json()


def create_module(
    client: ASGIClient,
    project_id: str,
    name: str,
    parent_id: str | None = None,
) -> dict[str, Any]:
    response = client.post(
        f"/api/projects/{project_id}/modules",
        json_body={"name": name, "parent_id": parent_id, "sort_order": 10},
    )
    assert response.status_code == 201
    return response.json()


def test_create_root_module_derives_level_and_path(api_client: ASGIClient) -> None:
    project = create_project(api_client)

    response = api_client.post(
        f"/api/projects/{project['id']}/modules",
        json_body={"name": "Checkout", "sort_order": 10},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project["id"]
    assert body["parent_id"] is None
    assert body["name"] == "Checkout"
    assert body["level"] == 1
    assert body["path"] == "/Checkout"
    assert body["sort_order"] == 10
    assert body["status"] == "active"


def test_create_child_module_derives_level_and_path(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    root = create_module(api_client, project["id"], "Checkout")

    child = create_module(api_client, project["id"], "Coupon", root["id"])

    assert child["parent_id"] == root["id"]
    assert child["level"] == 2
    assert child["path"] == "/Checkout/Coupon"


def test_list_modules_returns_project_modules_in_tree_order(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    root = create_module(api_client, project["id"], "Checkout")
    child = create_module(api_client, project["id"], "Coupon", root["id"])

    response = api_client.get(f"/api/projects/{project['id']}/modules")

    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body["items"]] == [root["id"], child["id"]]
    assert body["total"] == 2


def test_update_module_renames_path_for_module(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    root = create_module(api_client, project["id"], "Checkout")

    response = api_client.patch(
        f"/api/projects/{project['id']}/modules/{root['id']}",
        json_body={"name": "Order Checkout", "sort_order": 20, "status": "active"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Order Checkout"
    assert body["path"] == "/Order Checkout"
    assert body["sort_order"] == 20


def test_update_parent_module_refreshes_child_paths(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    root = create_module(api_client, project["id"], "Checkout")
    child = create_module(api_client, project["id"], "Coupon", root["id"])

    response = api_client.patch(
        f"/api/projects/{project['id']}/modules/{root['id']}",
        json_body={"name": "Order Checkout"},
    )
    assert response.status_code == 200

    modules = api_client.get(f"/api/projects/{project['id']}/modules").json()["items"]
    child_after_update = next(module for module in modules if module["id"] == child["id"])
    assert child_after_update["path"] == "/Order Checkout/Coupon"


def test_module_tree_rejects_more_than_five_levels(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    parent_id: str | None = None
    for index in range(1, 6):
        module = create_module(api_client, project["id"], f"Level {index}", parent_id)
        parent_id = module["id"]

    response = api_client.post(
        f"/api/projects/{project['id']}/modules",
        json_body={"name": "Too Deep", "parent_id": parent_id},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "MODULE_LEVEL_LIMIT_EXCEEDED"


def test_duplicate_module_name_under_same_parent_returns_conflict(api_client: ASGIClient) -> None:
    project = create_project(api_client)
    create_module(api_client, project["id"], "Checkout")

    response = api_client.post(
        f"/api/projects/{project['id']}/modules",
        json_body={"name": "Checkout"},
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "MODULE_ALREADY_EXISTS"


def test_create_module_rejects_parent_from_other_project(api_client: ASGIClient) -> None:
    first_project = create_project(api_client)
    second_response = api_client.post("/api/projects", json_body={"name": "Inventory System"})
    assert second_response.status_code == 201
    second_project = second_response.json()
    foreign_parent = create_module(api_client, first_project["id"], "Checkout")

    response = api_client.post(
        f"/api/projects/{second_project['id']}/modules",
        json_body={"name": "Coupon", "parent_id": foreign_parent["id"]},
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "MODULE_PARENT_NOT_FOUND"


def test_unknown_project_module_create_returns_contract_error(api_client: ASGIClient) -> None:
    response = api_client.post(
        f"/api/projects/{uuid.uuid4()}/modules",
        json_body={"name": "Checkout"},
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROJECT_NOT_FOUND"
