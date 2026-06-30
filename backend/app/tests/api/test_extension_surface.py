from __future__ import annotations

import asyncio
import json
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.extension.models import KnowledgeAdapterConfig, ToolDefinition
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

    def put(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("PUT", path, json_body)

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


def create_project(SessionLocal: sessionmaker[Session]) -> Project:
    with SessionLocal() as session:
        workspace = Workspace(name="Personal Workspace")
        project = Project(workspace=workspace, name="Checkout")
        session.add(project)
        session.commit()
        session.refresh(project)
        return project


def test_get_knowledge_adapter_returns_not_configured_shell(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project = create_project(SessionLocal)

    response = client.get(f"/api/projects/{project.id}/knowledge-adapter")

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == str(project.id)
    assert body["adapter_name"] == "default"
    assert body["status"] == "not_configured"
    assert body["provider_type"] == "none"
    assert body["config"] == {}
    assert body["safety_policy"] == {}
    assert body["used_knowledge"] is False


def test_update_knowledge_adapter_persists_stub_without_runtime(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project = create_project(SessionLocal)

    response = client.put(
        f"/api/projects/{project.id}/knowledge-adapter",
        json_body={
            "adapter_name": "default",
            "status": "configured_stub",
            "provider_type": "stub",
            "config": {"display_name": "Future company knowledge adapter"},
            "safety_policy": {"allowed_for_prompt": False},
            "notes": "V1 placeholder only",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "configured_stub"
    assert body["provider_type"] == "stub"
    assert body["config"] == {"display_name": "Future company knowledge adapter"}
    assert body["safety_policy"] == {"allowed_for_prompt": False}
    assert body["used_knowledge"] is False

    with SessionLocal() as session:
        config = session.query(KnowledgeAdapterConfig).filter_by(project_id=project.id).one()
        assert config.status == "configured_stub"
        assert config.provider_type == "stub"
        assert config.config_json == {"display_name": "Future company knowledge adapter"}


def test_update_knowledge_adapter_rejects_runtime_provider_config(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project = create_project(SessionLocal)

    response = client.put(
        f"/api/projects/{project.id}/knowledge-adapter",
        json_body={
            "provider_type": "pinecone",
            "config": {
                "api_key": "sk-live",
                "vector_db_url": "https://example.invalid",
                "embedding_model": "text-embedding",
            },
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "KNOWLEDGE_ADAPTER_RUNTIME_NOT_ALLOWED"

    with SessionLocal() as session:
        assert session.query(KnowledgeAdapterConfig).count() == 0


def test_get_knowledge_base_lists_context_artifacts_and_usage(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project = create_project(SessionLocal)

    with SessionLocal() as session:
        artifact = Artifact(
            project_id=project.id,
            owner_entity_type="Project",
            owner_entity_id=project.id,
            artifact_type="context_markdown",
            file_path=f"projects/{project.id}/context-artifacts/context.md",
            mime_type="text/markdown",
            size_bytes=42,
            sha256="abc123",
            metadata_json={
                "title": "coupon-api-notes.md",
                "source_ref": "manual:coupon-api-notes.md",
                "safe_to_show": True,
                "redaction_applied": False,
                "allowed_for_prompt": True,
            },
        )
        session.add(artifact)
        session.flush()
        ai_task = AITask(
            project_id=project.id,
            agent_name="RequirementReviewAgent",
            task_type="requirement_review",
            prompt_version_id=project.id,
            skill_version_id=project.id,
            status="succeeded",
            context_artifact_ids=[artifact.id],
            output_json={"used_knowledge": False},
        )
        session.add(ai_task)
        session.commit()

    response = client.get(f"/api/projects/{project.id}/knowledge-base")

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == str(project.id)
    assert body["knowledge_adapter"]["status"] == "not_configured"
    assert body["knowledge_adapter"]["used_knowledge"] is False
    assert body["non_goals"] == [
        "no_vector_index",
        "no_embedding",
        "no_reranking",
        "no_external_rag_runtime",
    ]
    assert len(body["context_artifacts"]) == 1
    item = body["context_artifacts"][0]
    assert item["id"]
    assert item["title"] == "coupon-api-notes.md"
    assert item["source_ref"] == "manual:coupon-api-notes.md"
    assert item["mime_type"] == "text/markdown"
    assert item["safe_to_show"] is True
    assert item["redaction_applied"] is False
    assert item["allowed_for_prompt"] is True
    assert item["usage_count"] == 1
    assert item["latest_used_at"] is not None


def test_list_tool_definitions_exposes_mcp_ready_schema_without_runtime(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project = create_project(SessionLocal)

    with SessionLocal() as session:
        tool_definition = ToolDefinition(
            project_id=project.id,
            name="pytest_runner",
            description="Run allowlisted pytest commands",
            tool_type="test_runner",
            input_schema_json={"type": "object"},
            output_schema_json={"type": "object"},
            risk_level="medium",
            approval_required=False,
            command_allowlist_json=["pytest {path}"],
            allowed_working_directories_json=["/workspace"],
            artifact_policy_json={"stdout": True},
            is_mcp_ready=True,
            mcp_metadata_json={"schema_version": "v1", "capability_name": "pytest_runner"},
        )
        mcp_proxy = ToolDefinition(
            project_id=project.id,
            name="future_mcp_proxy",
            description="Future MCP schema intent only",
            tool_type="mcp_proxy",
            input_schema_json={"type": "object"},
            output_schema_json={"type": "object"},
            risk_level="high",
            approval_required=True,
            is_mcp_ready=True,
            mcp_metadata_json={"schema_version": "v1", "capability_name": "future_proxy"},
        )
        session.add_all([tool_definition, mcp_proxy])
        session.commit()

    response = client.get(f"/api/projects/{project.id}/tool-definitions")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    first = body["items"][0]
    assert first["name"] == "future_mcp_proxy"
    assert first["tool_type"] == "mcp_proxy"
    assert first["approval_required"] is True
    assert first["is_mcp_ready"] is True
    assert first["mcp_metadata"] == {"schema_version": "v1", "capability_name": "future_proxy"}
    assert "server_url" not in first["mcp_metadata"]
    second = body["items"][1]
    assert second["name"] == "pytest_runner"
    assert second["command_allowlist"] == ["pytest {path}"]
    assert second["allowed_working_directories"] == ["/workspace"]
    assert second["artifact_policy"] == {"stdout": True}
