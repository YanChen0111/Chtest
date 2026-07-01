from __future__ import annotations

import asyncio
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.projects.router import get_session
from backend.app.tests.golden.test_requirement_to_case import candidate_by_title, seed_prompt_skill
from backend.app.tests.golden.test_requirement_to_case_metrics import golden_review_plan


GOLDEN_REQUIREMENT_CONTENT = (
    "# 优惠券结算规则\n\n"
    "用户在提交订单时，可以选择一张可用优惠券。优惠券不可与积分同时使用。"
    "过期优惠券不可使用。优惠券金额不能超过订单应付金额。"
    "提交订单后，系统需要展示优惠后的最终支付金额。"
)


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def get(self, path: str, query: dict[str, str] | None = None) -> ASGIResponse:
        if query:
            separator = "&" if "?" in path else "?"
            path = f"{path}{separator}{urlencode(query)}"
        return self.request("GET", path)

    def patch(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("PATCH", path, json_body)

    def post(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("POST", path, json_body)

    def request(self, method: str, path: str, json_body: dict[str, Any] | None = None) -> ASGIResponse:
        return asyncio.run(self._request(method, path, json_body))

    async def _request(self, method: str, path: str, json_body: dict[str, Any] | None) -> ASGIResponse:
        parsed = urlsplit(path)
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
        return ASGIResponse(status_code, b"".join(body_chunks))


@pytest.fixture()
def api_client(tmp_path: Path) -> Iterator[tuple[ASGIClient, sessionmaker[Session]]]:
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

    yield ASGIClient(app), SessionLocal

    app.dependency_overrides.clear()


def test_golden_reviewed_cases_are_visible_in_test_case_library(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project, library = create_reviewed_golden_cases(client, SessionLocal)

    assert library["total"] == 4

    expired_case = next(item for item in library["items"] if item["title"] == "过期优惠券不可用于结算")
    assert expired_case["review_status"] == "approved_after_edit"
    assert expired_case["steps"][0] == "准备已过期优惠券"
    assert expired_case["input_data"] == {"coupon_state": "expired"}

    keyword_response = client.get("/api/test-cases", query={"project_id": project["id"], "keyword": "最终支付金额"})
    assert keyword_response.status_code == 200
    keyword_body = keyword_response.json()
    assert keyword_body["total"] == 1
    assert keyword_body["items"][0]["title"] == "提交订单后展示优惠后的最终支付金额"


def create_reviewed_golden_cases(client: ASGIClient, SessionLocal: sessionmaker[Session]) -> tuple[dict[str, Any], dict[str, Any]]:
    seed_prompt_skill(SessionLocal)

    project_response = client.post("/api/projects", json_body={"name": "Checkout System"})
    assert project_response.status_code == 201
    project = project_response.json()
    module_response = client.post(
        f"/api/projects/{project['id']}/modules",
        json_body={"name": "订单结算", "sort_order": 10},
    )
    assert module_response.status_code == 201
    module = module_response.json()

    requirement_response = client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "module_id": module["id"],
            "title": "优惠券结算规则",
            "content": GOLDEN_REQUIREMENT_CONTENT,
            "source_type": "manual",
            "source_ref": "REQ-COUPON-001",
        },
    )
    assert requirement_response.status_code == 201
    requirement = requirement_response.json()

    review_start = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    )
    assert review_start.status_code == 202
    review_response = client.get(f"/api/requirements/{requirement['id']}/review")
    assert review_response.status_code == 200
    review = review_response.json()

    generation_response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": project["id"],
            "requirement_id": requirement["id"],
            "requirement_review_id": review["id"],
            "target_test_types": ["functional", "ui"],
            "prompt_version": "case_generation:v1",
            "skill_version": "test-case-generation-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-case-generator",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    )
    assert generation_response.status_code == 202
    generation = generation_response.json()

    candidates_response = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates")
    assert candidates_response.status_code == 200
    candidates = candidates_response.json()["items"]
    for title, payload in golden_review_plan().items():
        candidate = candidate_by_title(candidates, title)
        response = client.post(f"/api/case-review/items/{candidate['id']}/approve", json_body=payload)
        assert response.status_code == 200

    library_response = client.get("/api/test-cases", query={"project_id": project["id"]})
    assert library_response.status_code == 200
    library = library_response.json()
    return project, library
