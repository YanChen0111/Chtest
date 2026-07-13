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
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.knowledge.models import (
    TestKnowledgeCard as TestKnowledgeCardModel,
    TestKnowledgeEmbeddingIndex,
)
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

    def patch(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("PATCH", path, json_body)

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


def seed_case_generation_prompt_skill(SessionLocal: sessionmaker[Session]) -> None:
    with SessionLocal() as session:
        session.add_all(
            [
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


def create_project_context_and_requirement(client: ASGIClient) -> tuple[str, str, str]:
    project = client.post("/api/projects", {"name": "Checkout System"}).json()
    artifact = client.post(
        "/api/context-artifacts",
        {
            "project_id": project["id"],
            "title": "coupon-api-notes.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": (
                "# Coupon API\n"
                "POST /api/coupons/validate validates checkout coupons.\n"
                "Expired coupons cannot be used during checkout.\n"
                "Coupon amount cannot exceed payable order amount."
            ),
            "source_ref": "manual:coupon-api-notes.md",
        },
    ).json()
    requirement = client.post(
        "/api/requirements",
        {
            "project_id": project["id"],
            "title": "Coupon checkout rules",
            "content": "Expired coupon cannot be used and coupon amount cannot exceed order amount.",
        },
    ).json()
    return project["id"], artifact["id"], requirement["id"]


def approve_cards(client: ASGIClient, project_id: str, cards: list[dict[str, Any]]) -> None:
    for card in cards:
        response = client.patch(
            f"/api/test-knowledge/cards/{card['id']}",
            {"project_id": project_id, "status": "approved"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "approved"


def test_extract_test_knowledge_cards_from_context_artifact(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project_id, artifact_id, _requirement_id = create_project_context_and_requirement(client)

    response = client.post(
        "/api/test-knowledge/cards/extract",
        {"project_id": project_id, "source_artifact_id": artifact_id},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["created_count"] >= 2
    assert body["skipped_count"] == 0
    assert {item["knowledge_type"] for item in body["items"]} >= {"APIContract", "BoundaryCondition"}

    list_response = client.get(f"/api/projects/{project_id}/test-knowledge/cards")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == body["created_count"]

    duplicate_response = client.post(
        "/api/test-knowledge/cards/extract",
        {"project_id": project_id, "source_artifact_id": artifact_id},
    )
    assert duplicate_response.status_code == 201
    assert duplicate_response.json()["created_count"] == 0
    assert duplicate_response.json()["skipped_count"] == body["created_count"]

    with SessionLocal() as session:
        cards = list(session.scalars(select(TestKnowledgeCardModel)))
        assert len(cards) == body["created_count"]
        assert all(card.allowed_for_prompt for card in cards)


def test_retrieve_test_knowledge_card_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _SessionLocal = api_client
    project_id, artifact_id, _requirement_id = create_project_context_and_requirement(client)
    extract_response = client.post(
        "/api/test-knowledge/cards/extract",
        {"project_id": project_id, "source_artifact_id": artifact_id},
    )
    assert extract_response.status_code == 201

    response = client.post(
        "/api/test-knowledge/cards/retrieve",
        {"project_id": project_id, "query_text": "expired coupon checkout", "limit": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query_text"] == "expired coupon checkout"
    assert body["total"] >= 1
    first = body["items"][0]
    assert first["source_artifact_id"] == artifact_id
    assert first["knowledge_card_id"]
    assert first["score"] >= 1
    assert "expired" in first["matched_terms"]
    assert first["allowed_for_prompt"] is True
    assert first["status"] == "extracted"

    approved_only_response = client.post(
        "/api/test-knowledge/cards/retrieve",
        {"project_id": project_id, "query_text": "expired coupon checkout", "limit": 3, "approved_only": True},
    )
    assert approved_only_response.status_code == 200
    assert approved_only_response.json()["total"] == 0

    approve_cards(client, project_id, extract_response.json()["items"])
    approved_response = client.post(
        "/api/test-knowledge/cards/retrieve",
        {"project_id": project_id, "query_text": "expired coupon checkout", "limit": 3, "approved_only": True},
    )
    assert approved_response.status_code == 200
    assert approved_response.json()["total"] >= 1
    assert approved_response.json()["items"][0]["status"] == "approved"


def test_extract_all_test_knowledge_cards_from_prompt_eligible_context(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, _SessionLocal = api_client
    project_id, artifact_id, _requirement_id = create_project_context_and_requirement(client)

    response = client.post(
        "/api/test-knowledge/cards/extract-batch",
        {"project_id": project_id},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["source_artifact_ids"] == [artifact_id]
    assert body["created_count"] >= 2
    assert body["skipped_count"] == 0


def test_rebuild_test_knowledge_embedding_index_and_hybrid_retrieval(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    project_id, artifact_id, _requirement_id = create_project_context_and_requirement(client)
    extract_response = client.post(
        "/api/test-knowledge/cards/extract",
        {"project_id": project_id, "source_artifact_id": artifact_id},
    )
    assert extract_response.status_code == 201
    created_count = extract_response.json()["created_count"]

    rebuild_response = client.post(
        "/api/test-knowledge/index/rebuild",
        {"project_id": project_id, "embedding_dim": 64},
    )

    assert rebuild_response.status_code == 201
    rebuild = rebuild_response.json()
    assert rebuild["indexed_count"] == created_count
    assert rebuild["skipped_count"] == 0
    assert rebuild["embedding_model"] == "deterministic-hashing-v1"
    assert rebuild["items"][0]["knowledge_card_id"]
    assert rebuild["items"][0]["embedding_provider"] == "deterministic_local"

    second_rebuild_response = client.post(
        "/api/test-knowledge/index/rebuild",
        {"project_id": project_id, "embedding_dim": 64},
    )
    assert second_rebuild_response.status_code == 201
    assert second_rebuild_response.json()["skipped_count"] == created_count

    index_response = client.get(f"/api/projects/{project_id}/test-knowledge/index")
    assert index_response.status_code == 200
    index_body = index_response.json()
    assert index_body["indexed_count"] == created_count
    assert index_body["embedding_models"] == ["deterministic-hashing-v1"]

    retrieval_response = client.post(
        "/api/test-knowledge/cards/retrieve",
        {"project_id": project_id, "query_text": "POST coupons validate checkout", "limit": 3},
    )
    assert retrieval_response.status_code == 200
    retrieval = retrieval_response.json()
    assert retrieval["total"] >= 1
    assert any("semantic_score" in item for item in retrieval["items"])
    assert any(item["retrieval_reason"] == "deterministic_hybrid_keyword_vector" for item in retrieval["items"])

    graph_response = client.get(f"/api/projects/{project_id}/test-knowledge/graph")
    assert graph_response.status_code == 200
    graph = graph_response.json()
    assert graph["coverage"]["embedding_indexed_card_count"] == created_count
    assert graph["coverage"]["vector_index_coverage_ratio"] == 1
    assert any(node["node_type"] == "embedding_index" for node in graph["nodes"])
    assert any(edge["edge_type"] == "indexes_knowledge_card" for edge in graph["edges"])

    first_card_id = extract_response.json()["items"][0]["id"]
    archive_response = client.patch(
        f"/api/test-knowledge/cards/{first_card_id}",
        {"project_id": project_id, "status": "archived"},
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["allowed_for_prompt"] is False

    with SessionLocal() as session:
        archived_index = session.scalar(
            select(TestKnowledgeEmbeddingIndex).where(
                TestKnowledgeEmbeddingIndex.knowledge_card_id == uuid.UUID(first_card_id),
            ),
        )
        assert archived_index is not None
        assert archived_index.status == "stale"
        assert archived_index.metadata_json["stale_reason"] == "knowledge_card_no_longer_prompt_eligible"

    stale_index_response = client.get(f"/api/projects/{project_id}/test-knowledge/index")
    assert stale_index_response.status_code == 200
    assert stale_index_response.json()["indexed_count"] == created_count - 1

    stale_graph_response = client.get(f"/api/projects/{project_id}/test-knowledge/graph")
    assert stale_graph_response.status_code == 200
    stale_graph = stale_graph_response.json()
    assert stale_graph["coverage"]["embedding_index_count"] == created_count
    assert stale_graph["coverage"]["embedding_indexed_card_count"] == created_count - 1


def test_case_generation_uses_test_knowledge_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_case_generation_prompt_skill(SessionLocal)
    project_id, artifact_id, requirement_id = create_project_context_and_requirement(client)
    extract_response = client.post(
        "/api/test-knowledge/cards/extract",
        {"project_id": project_id, "source_artifact_id": artifact_id},
    )
    assert extract_response.status_code == 201
    approve_cards(client, project_id, extract_response.json()["items"])

    generation_response = client.post(
        "/api/case-generation/tasks",
        {
            "project_id": project_id,
            "requirement_id": requirement_id,
            "requirement_review_id": None,
            "target_test_types": ["functional"],
            "prompt_version": "case_generation:v1",
            "skill_version": "test-case-generation-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-case-generator",
            "use_knowledge": True,
            "decision_table_acknowledged": True,
            "context_artifact_ids": [],
        },
    )

    assert generation_response.status_code == 202
    generation = generation_response.json()
    assert generation["used_knowledge"] is True
    assert generation["used_context_artifact_ids"] == [artifact_id]

    candidates = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates").json()
    first_candidate = candidates["items"][0]
    assert first_candidate["source_knowledge_evidence"]
    assert first_candidate["source_knowledge_evidence"][0]["source_artifact_id"] == artifact_id
    assert first_candidate["source_knowledge_evidence"][0]["knowledge_card_id"]

    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(generation["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.input_json["knowledge_evidence"]
        assert ai_task.output_json["used_knowledge"] is True

    graph_response = client.get(f"/api/projects/{project_id}/test-knowledge/graph")
    assert graph_response.status_code == 200
    graph = graph_response.json()
    assert graph["coverage"]["approved_card_count"] >= 1
    assert graph["coverage"]["covered_knowledge_card_count"] >= 1
    assert graph["coverage"]["knowledge_coverage_ratio"] > 0
    assert any(node["node_type"] == "knowledge_card" for node in graph["nodes"])
    assert any(edge["edge_type"] == "uses_knowledge_card" for edge in graph["edges"])
