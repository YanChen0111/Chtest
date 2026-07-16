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
        return asyncio.run(self._request("GET", path))

    async def _request(self, method: str, path: str) -> ASGIResponse:
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
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": b"",
            "headers": [(b"host", b"testserver")],
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


def seed_prompt_and_skill_versions(SessionLocal: sessionmaker[Session]) -> tuple[PromptVersion, SkillVersion]:
    with SessionLocal() as session:
        prompt = PromptVersion(
            name="requirement_review",
            version="v1",
            hash="sha256:" + "a" * 64,
            agent_name="RequirementReviewAgent",
            content="# Prompt: requirement_review v1",
            input_schema_json={"type": "object", "required": ["requirement"]},
            output_schema_json={"type": "object", "required": ["scores"]},
        )
        skill = SkillVersion(
            name="requirement-review-skill",
            version="v1",
            hash="sha256:" + "b" * 64,
            applicable_agents=["RequirementReviewAgent"],
            content="# Skill: requirement-review-skill v1",
            quality_gates_json=["All six dimensions must be present."],
            forbidden_actions_json=["Do not claim external RAG evidence."],
            tool_permissions_json=["No execution tools."],
        )
        session.add_all([prompt, skill])
        session.commit()
        session.refresh(prompt)
        session.refresh(skill)
        return prompt, skill


def test_list_prompt_versions_returns_trace_fields(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    prompt, _ = seed_prompt_and_skill_versions(SessionLocal)

    response = client.get("/api/prompt-versions")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == str(prompt.id)
    assert body["items"][0]["name"] == "requirement_review"
    assert body["items"][0]["version"] == "v1"
    assert body["items"][0]["hash"] == "sha256:" + "a" * 64
    assert body["items"][0]["agent_name"] == "RequirementReviewAgent"
    assert body["items"][0]["status"] == "active"
    assert body["items"][0]["input_schema_json"]["required"] == ["requirement"]
    assert body["items"][0]["output_schema_json"]["required"] == ["scores"]


def test_get_prompt_version_returns_content_and_schema_metadata(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    prompt, _ = seed_prompt_and_skill_versions(SessionLocal)

    response = client.get(f"/api/prompt-versions/{prompt.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(prompt.id)
    assert body["content"] == "# Prompt: requirement_review v1"
    assert body["input_schema_json"]["type"] == "object"
    assert body["output_schema_json"]["type"] == "object"


def test_list_skill_versions_returns_agent_and_gate_metadata(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    _, skill = seed_prompt_and_skill_versions(SessionLocal)

    response = client.get("/api/skill-versions")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == str(skill.id)
    assert body["items"][0]["name"] == "requirement-review-skill"
    assert body["items"][0]["version"] == "v1"
    assert body["items"][0]["hash"] == "sha256:" + "b" * 64
    assert body["items"][0]["applicable_agents"] == ["RequirementReviewAgent"]
    assert body["items"][0]["quality_gates_json"] == ["All six dimensions must be present."]
    assert body["items"][0]["forbidden_actions_json"] == ["Do not claim external RAG evidence."]
    assert body["items"][0]["tool_permissions_json"] == ["No execution tools."]


def test_get_skill_version_returns_content_and_gate_metadata(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    _, skill = seed_prompt_and_skill_versions(SessionLocal)

    response = client.get(f"/api/skill-versions/{skill.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(skill.id)
    assert body["content"] == "# Skill: requirement-review-skill v1"
    assert body["applicable_agents"] == ["RequirementReviewAgent"]


def test_unknown_prompt_or_skill_version_returns_contract_error(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client

    prompt_response = client.get(f"/api/prompt-versions/{uuid.uuid4()}")
    skill_response = client.get(f"/api/skill-versions/{uuid.uuid4()}")

    assert prompt_response.status_code == 404
    assert prompt_response.json()["error_code"] == "PROMPT_VERSION_NOT_FOUND"
    assert skill_response.status_code == 404
    assert skill_response.json()["error_code"] == "SKILL_VERSION_NOT_FOUND"
