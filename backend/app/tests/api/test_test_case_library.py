from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Iterator
from typing import Any
from urllib.parse import urlsplit

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.cases.models import GeneratedCaseCandidate, TestCase as CaseModel
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.projects.router import get_session
from backend.app.modules.requirements.models import Requirement


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
        return asyncio.run(self._request("GET", path))

    async def _request(self, method: str, path: str) -> ASGIResponse:
        parsed = urlsplit(path)
        status_code: int | None = None
        body_chunks: list[bytes] = []
        request_complete = False

        async def receive() -> dict[str, Any]:
            nonlocal request_complete
            if not request_complete:
                request_complete = True
                return {"type": "http.request", "body": b"", "more_body": False}
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
            "headers": [(b"host", b"testserver"), (b"accept", b"application/json")],
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


def seed_library_records(SessionLocal: sessionmaker[Session]) -> dict[str, uuid.UUID]:
    with SessionLocal() as session:
        workspace = Workspace(name="Personal Workspace")
        session.add(workspace)
        session.flush()
        project = Project(workspace_id=workspace.id, name="Checkout System")
        other_project = Project(workspace_id=workspace.id, name="Billing System")
        session.add_all([project, other_project])
        session.flush()
        requirement = Requirement(
            project_id=project.id,
            title="Coupon checkout rules",
            content="Expired coupons cannot be used.",
        )
        session.add(requirement)
        session.flush()
        approved_candidate = GeneratedCaseCandidate(
            generation_task_id=uuid.uuid4(),
            project_id=project.id,
            module_id=None,
            title="Expired coupon cannot submit order",
            priority="P0",
            test_type="functional",
            precondition="User has an expired coupon",
            steps_json=["Prepare expired coupon", "Open checkout", "Submit order"],
            expected_results_json=["Submit is blocked", "Expired coupon message is shown"],
            input_data_json={"coupon_state": "expired"},
            tags=["coupon", "boundary"],
            requirement_refs_json=["Expired coupons cannot be used"],
            risk_refs_json=[],
            ai_reason="Covers expiration boundary",
            status="approved_after_edit",
        )
        generated_candidate = GeneratedCaseCandidate(
            generation_task_id=uuid.uuid4(),
            project_id=project.id,
            module_id=None,
            title="Generated only candidate",
            priority="P2",
            test_type="ui",
            precondition=None,
            steps_json=["Draft step"],
            expected_results_json=["Draft expected"],
            input_data_json={},
            tags=[],
            requirement_refs_json=[],
            risk_refs_json=[],
            ai_reason="Not reviewed",
            status="generated",
        )
        session.add_all([approved_candidate, generated_candidate])
        session.flush()
        session.add_all(
            [
                CaseModel(
                    project_id=project.id,
                    module_id=None,
                    source_candidate_id=approved_candidate.id,
                    title="Expired coupon cannot submit order",
                    priority="P0",
                    test_type="functional",
                    precondition="User has an expired coupon",
                    steps_json=["Prepare expired coupon", "Open checkout", "Submit order"],
                    expected_results_json=["Submit is blocked", "Expired coupon message is shown"],
                    input_data_json={"coupon_state": "expired"},
                    tags=["coupon", "boundary"],
                    source_type="ai",
                    review_status="approved_after_edit",
                    status="active",
                ),
                CaseModel(
                    project_id=project.id,
                    module_id=None,
                    source_candidate_id=None,
                    title="Available coupon discounts payable amount",
                    priority="P1",
                    test_type="ui",
                    precondition="User has a valid coupon",
                    steps_json=["Open checkout", "Select coupon", "Submit order"],
                    expected_results_json=["Final payable amount is discounted"],
                    input_data_json={"coupon_state": "valid"},
                    tags=["coupon", "ui"],
                    source_type="ai",
                    review_status="approved",
                    status="active",
                ),
                CaseModel(
                    project_id=other_project.id,
                    module_id=None,
                    source_candidate_id=None,
                    title="Other project case",
                    priority="P0",
                    test_type="functional",
                    precondition=None,
                    steps_json=["Other step"],
                    expected_results_json=["Other expected"],
                    input_data_json={},
                    tags=[],
                    source_type="ai",
                    review_status="approved",
                    status="active",
                ),
            ],
        )
        session.commit()
        return {"project_id": project.id, "other_project_id": other_project.id}


def test_list_test_cases_returns_reviewed_cases_for_project(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    ids = seed_library_records(SessionLocal)

    response = client.get(f"/api/test-cases?project_id={ids['project_id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    titles = [item["title"] for item in body["items"]]
    repeat_response = client.get(f"/api/test-cases?project_id={ids['project_id']}")
    assert repeat_response.status_code == 200
    assert [item["title"] for item in repeat_response.json()["items"]] == titles
    expired_case = next(item for item in body["items"] if item["title"] == "Expired coupon cannot submit order")
    assert expired_case["source_candidate_id"]
    assert expired_case["priority"] == "P0"
    assert expired_case["test_type"] == "functional"
    assert expired_case["steps"] == ["Prepare expired coupon", "Open checkout", "Submit order"]
    assert expired_case["expected_results"] == ["Submit is blocked", "Expired coupon message is shown"]
    assert expired_case["input_data"] == {"coupon_state": "expired"}
    assert expired_case["tags"] == ["coupon", "boundary"]
    assert expired_case["review_status"] == "approved_after_edit"
    assert "Generated only candidate" not in titles


def test_list_test_cases_supports_type_priority_and_keyword_filters(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    ids = seed_library_records(SessionLocal)

    response = client.get(f"/api/test-cases?project_id={ids['project_id']}&test_type=ui&priority=P1&keyword=payable")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Available coupon discounts payable amount"

    tag_response = client.get(f"/api/test-cases?project_id={ids['project_id']}&keyword=boundary")
    assert tag_response.status_code == 200
    tag_body = tag_response.json()
    assert tag_body["total"] == 1
    assert tag_body["items"][0]["title"] == "Expired coupon cannot submit order"


def test_list_test_cases_requires_project_id(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    seed_library_records(SessionLocal)

    response = client.get("/api/test-cases")

    assert response.status_code == 422
