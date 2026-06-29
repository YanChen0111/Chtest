from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.cases.models import GeneratedCaseCandidate, TestCase as CaseModel
from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion


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

    async def _request(self, method: str, path: str, json_body: dict[str, Any] | None) -> ASGIResponse:
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


def seed_prompt_skill(SessionLocal: sessionmaker[Session]) -> None:
    with SessionLocal() as session:
        session.add_all(
            [
                PromptVersion(
                    name="requirement_review",
                    version="v1",
                    hash="sha256:" + "a" * 64,
                    agent_name="RequirementReviewAgent",
                    content="# Requirement Review Prompt",
                ),
                SkillVersion(
                    name="requirement-review-skill",
                    version="v1",
                    hash="sha256:" + "b" * 64,
                    applicable_agents=["RequirementReviewAgent"],
                    content="# Requirement Review Skill",
                ),
                PromptVersion(
                    name="case_generation",
                    version="v1",
                    hash="sha256:" + "c" * 64,
                    agent_name="CaseGenerationAgent",
                    content="# Case Generation Prompt",
                ),
                SkillVersion(
                    name="test-case-generation-skill",
                    version="v1",
                    hash="sha256:" + "d" * 64,
                    applicable_agents=["CaseGenerationAgent"],
                    content="# Case Generation Skill",
                ),
            ],
        )
        session.commit()


def create_candidate(client: ASGIClient, SessionLocal: sessionmaker[Session]) -> dict[str, Any]:
    seed_prompt_skill(SessionLocal)
    project = client.post("/api/projects", json_body={"name": "Checkout System"}).json()
    requirement = client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "title": "Coupon checkout rules",
            "content": "Coupon cannot be used with points. Expired coupons cannot be used.",
        },
    ).json()
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
    review = client.get(f"/api/requirements/{requirement['id']}/review").json()
    generation = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": requirement["project_id"],
            "requirement_id": requirement["id"],
            "requirement_review_id": review["id"],
            "target_test_types": ["functional"],
            "prompt_version": "case_generation:v1",
            "skill_version": "test-case-generation-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-case-generator",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    ).json()
    candidates = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates").json()
    return candidates["items"][0]


def test_approve_candidate_creates_test_case(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    candidate = create_candidate(client, SessionLocal)

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "approve", "review_comment": "Looks good."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_id"] == candidate["id"]
    assert body["status"] == "approved"
    assert body["test_case_id"]

    with SessionLocal() as session:
        refreshed_candidate = session.get(GeneratedCaseCandidate, uuid.UUID(candidate["id"]))
        test_case = session.get(CaseModel, uuid.UUID(body["test_case_id"]))
        assert refreshed_candidate is not None
        assert test_case is not None
        assert refreshed_candidate.status == "approved"
        assert refreshed_candidate.review_comment == "Looks good."
        assert test_case.source_candidate_id == refreshed_candidate.id
        assert test_case.title == refreshed_candidate.title
        assert test_case.review_status == "approved"


def test_approve_after_edit_creates_test_case_from_edited_case(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    candidate = create_candidate(client, SessionLocal)

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={
            "action": "approve_after_edit",
            "edited_case": {
                "title": "Expired coupon cannot submit order",
                "priority": "P0",
                "test_type": "functional",
                "precondition": "User has an expired coupon.",
                "steps": ["Prepare expired coupon", "Open checkout", "Select expired coupon", "Submit order"],
                "expected_results": ["Submit is blocked", "Expired coupon message is shown"],
                "input_data": {"coupon_state": "expired"},
                "tags": ["coupon", "regression"],
            },
            "review_comment": "Added test data preparation.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved_after_edit"

    with SessionLocal() as session:
        test_case = session.get(CaseModel, uuid.UUID(body["test_case_id"]))
        assert test_case is not None
        assert test_case.title == "Expired coupon cannot submit order"
        assert test_case.steps_json[0] == "Prepare expired coupon"
        assert test_case.input_data_json == {"coupon_state": "expired"}
        assert test_case.tags == ["coupon", "regression"]
        assert test_case.review_status == "approved_after_edit"


def test_reject_candidate_does_not_create_test_case(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    candidate = create_candidate(client, SessionLocal)

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "reject", "review_comment": "Too vague."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["test_case_id"] is None

    with SessionLocal() as session:
        refreshed_candidate = session.get(GeneratedCaseCandidate, uuid.UUID(candidate["id"]))
        assert refreshed_candidate is not None
        assert refreshed_candidate.status == "rejected"
        assert refreshed_candidate.review_comment == "Too vague."
        assert list(session.scalars(select(CaseModel))) == []


def test_needs_optimization_marks_candidate_without_creating_test_case(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    candidate = create_candidate(client, SessionLocal)

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "needs_optimization", "review_comment": "Need better boundary coverage."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_optimization"
    assert body["test_case_id"] is None

    with SessionLocal() as session:
        refreshed_candidate = session.get(GeneratedCaseCandidate, uuid.UUID(candidate["id"]))
        assert refreshed_candidate is not None
        assert refreshed_candidate.status == "needs_optimization"
        assert list(session.scalars(select(CaseModel))) == []


def test_final_candidate_status_cannot_be_reviewed_again(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, _ = api_client
    candidate = create_candidate(client, _)
    first = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "reject", "review_comment": "No."},
    )
    assert first.status_code == 200

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "approve"},
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "CASE_CANDIDATE_ALREADY_FINAL"
