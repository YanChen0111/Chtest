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
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.projects.models import Project, Workspace
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

    def request(self, method: str, path: str) -> ASGIResponse:
        return asyncio.run(self._request(method, path))

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


def create_completed_ai_task(SessionLocal: sessionmaker[Session]) -> tuple[Project, AITask]:
    with SessionLocal() as session:
        project_id = uuid.uuid4()
        ai_task_id = uuid.uuid4()
        project = Project(id=project_id, workspace=Workspace(name="Personal Workspace"), name="Checkout")
        ai_task = AITask(
            id=ai_task_id,
            project=project,
            agent_name="RequirementReviewAgent",
            task_type="requirement_review",
            prompt_version_id=uuid.uuid4(),
            skill_version_id=uuid.uuid4(),
            model_name="mock-requirement-review",
            status="succeeded",
            output_json={"overall_score": 82, "used_knowledge": False},
            token_usage_json={"prompt_tokens": 128, "completion_tokens": 256},
            context_artifact_ids=[uuid.UUID("00000000-0000-0000-0000-000000000371")],
        )
        raw_artifact = Artifact(
            project=project,
            owner_entity_type="AITask",
            owner_entity_id=ai_task_id,
            artifact_type="raw_llm_output",
            file_path=f"projects/{project_id}/ai-tasks/{ai_task_id}/raw_output.json",
            mime_type="application/json",
            sha256="a" * 64,
            metadata_json={"safe_to_show": False, "redaction_applied": False},
        )
        parsed_artifact = Artifact(
            project=project,
            owner_entity_type="AITask",
            owner_entity_id=ai_task_id,
            artifact_type="parsed_output",
            file_path=f"projects/{project_id}/ai-tasks/{ai_task_id}/parsed_output.json",
            mime_type="application/json",
            sha256="b" * 64,
            metadata_json={"safe_to_show": True, "redaction_applied": False},
        )
        context_manifest_artifact = Artifact(
            project=project,
            owner_entity_type="AITask",
            owner_entity_id=ai_task_id,
            artifact_type="input_json",
            file_path=f"projects/{project_id}/ai-tasks/{ai_task_id}/context_manifest.json",
            mime_type="application/json",
            sha256="c" * 64,
            metadata_json={"safe_to_show": True, "redaction_applied": False},
        )
        llm_call = LLMCallLog(
            project=project,
            ai_task=ai_task,
            prompt_version_id=ai_task.prompt_version_id,
            skill_version_id=ai_task.skill_version_id,
            provider="mock",
            model_name="mock-requirement-review",
            status="succeeded",
            response_artifact=raw_artifact,
            parsed_artifact=parsed_artifact,
            token_usage_json={"prompt_tokens": 128, "completion_tokens": 256},
            input_summary_json={"task_type": "requirement_review"},
            output_summary_json={"overall_score": 82},
        )
        session.add_all([ai_task, raw_artifact, parsed_artifact, context_manifest_artifact, llm_call])
        session.commit()
        session.refresh(project)
        session.refresh(ai_task)
        return project, ai_task


def test_get_ai_task_returns_status_artifacts_and_llm_calls(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project, ai_task = create_completed_ai_task(SessionLocal)

    response = client.get(f"/api/ai-tasks/{ai_task.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(ai_task.id)
    assert body["project_id"] == str(project.id)
    assert body["agent_name"] == "RequirementReviewAgent"
    assert body["task_type"] == "requirement_review"
    assert body["status"] == "succeeded"
    assert body["model_provider"] == "mock"
    assert body["model_name"] == "mock-requirement-review"
    assert body["token_usage"] == {"prompt_tokens": 128, "completion_tokens": 256}
    assert body["used_knowledge"] is False
    assert body["context_artifact_ids"] == ["00000000-0000-0000-0000-000000000371"]
    assert body["used_context_artifact_ids"] == ["00000000-0000-0000-0000-000000000371"]
    assert body["context_manifest_artifact_id"]
    assert {artifact["artifact_type"] for artifact in body["artifacts"]} == {
        "raw_llm_output",
        "parsed_output",
        "input_json",
    }
    assert "content" not in body["artifacts"][0]
    assert body["llm_call_logs"][0]["status"] == "succeeded"
    assert body["llm_call_logs"][0]["response_artifact_id"]


def test_list_project_ai_tasks_returns_recent_task_summaries(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project, ai_task = create_completed_ai_task(SessionLocal)

    response = client.get(f"/api/projects/{project.id}/ai-tasks")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == str(ai_task.id)
    assert body["items"][0]["status"] == "succeeded"
    assert body["items"][0]["context_artifact_ids"] == ["00000000-0000-0000-0000-000000000371"]


def test_list_unknown_project_ai_tasks_returns_contract_error(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client

    response = client.get(f"/api/projects/{uuid.uuid4()}/ai-tasks")

    assert response.status_code == 404
    assert response.json()["error_code"] == "PROJECT_NOT_FOUND"


def test_unknown_ai_task_returns_contract_error(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _ = api_client

    response = client.get(f"/api/ai-tasks/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "AI_TASK_NOT_FOUND"
