from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.extension.models import KnowledgeAdapterConfig
from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion


FIXTURE_PATH = Path("docs/fixtures/08-deterministic-knowledge-retrieval-golden.md")
GOLDEN_REQUIREMENT_CONTENT = (
    "# Coupon checkout API requirement\n\n"
    "When checkout validates a coupon, the API must reject expired coupon codes "
    "before payment submit and explain the coupon failure to the shopper."
)
GOLDEN_COUPON_API_CONTENT = (
    "# Coupon API Notes\n\n"
    "Expired coupon validation blocks checkout before payment submit. The "
    "coupon API returns COUPON_EXPIRED and the shopper sees a clear coupon "
    "failure message."
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
        self.artifact_root: Path | None = None

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

    client = ASGIClient(app)
    client.artifact_root = artifact_root

    yield client, SessionLocal

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
                    output_schema_json={"required": ["scores", "issues"]},
                ),
                SkillVersion(
                    name="requirement-review-skill",
                    version="v1",
                    hash="sha256:" + "b" * 64,
                    applicable_agents=["RequirementReviewAgent"],
                    content="# Requirement Review Skill",
                ),
            ],
        )
        session.commit()


def configure_deterministic_adapter(SessionLocal: sessionmaker[Session], project_id: str) -> None:
    with SessionLocal() as session:
        session.add(
            KnowledgeAdapterConfig(
                project_id=uuid.UUID(project_id),
                adapter_name="default",
                status="configured_stub",
                provider_type="deterministic_local",
                config_json={"match_mode": "keyword_overlap", "max_results": 5, "max_snippet_chars": 320},
            ),
        )
        session.commit()


def test_golden_deterministic_retrieval_improves_requirement_review_context(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    assert FIXTURE_PATH.exists()

    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)

    project_response = client.post("/api/projects", json_body={"name": "Checkout System"})
    assert project_response.status_code == 201
    project = project_response.json()

    requirement_response = client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "title": "Coupon checkout API rejects expired coupons",
            "content": GOLDEN_REQUIREMENT_CONTENT,
            "source_type": "manual",
            "source_ref": "REQ-COUPON-RETRIEVAL-001",
        },
    )
    assert requirement_response.status_code == 201
    requirement = requirement_response.json()

    context_response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": project["id"],
            "title": "coupon-api-notes.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": GOLDEN_COUPON_API_CONTENT,
            "source_ref": "manual:coupon-api-notes.md",
        },
    )
    assert context_response.status_code == 201
    context_id = context_response.json()["id"]
    configure_deterministic_adapter(SessionLocal, project["id"])

    review_start = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": True,
            "context_artifact_ids": [],
        },
    )
    assert review_start.status_code == 202
    review_start_body = review_start.json()
    assert review_start_body["used_knowledge"] is True
    assert review_start_body["used_context_artifact_ids"] == [context_id]

    review_response = client.get(f"/api/requirements/{requirement['id']}/review")
    assert review_response.status_code == 200
    review = review_response.json()
    assert review["status"] == "reviewed"
    assert review["used_knowledge"] is True
    assert review["used_context_artifact_ids"] == [context_id]

    with SessionLocal() as session:
        context_artifact = session.get(Artifact, uuid.UUID(context_id))
        assert context_artifact is not None
        assert context_artifact.artifact_type == "context_markdown"
        assert context_artifact.metadata_json["safe_to_show"] is True
        assert context_artifact.metadata_json["allowed_for_prompt"] is True
        assert context_artifact.metadata_json["source_ref"] == "manual:coupon-api-notes.md"

        ai_task = session.get(AITask, uuid.UUID(review_start_body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.status == "succeeded"
        assert ai_task.context_artifact_ids == [uuid.UUID(context_id)]
        assert ai_task.output_json["used_knowledge"] is True
        assert ai_task.output_json["used_context_artifact_ids"] == [context_id]
        evidence_artifact_id = uuid.UUID(ai_task.output_json["retrieval_evidence_artifact_id"])
        evidence_artifact = session.get(Artifact, evidence_artifact_id)
        assert evidence_artifact is not None
        assert evidence_artifact.owner_entity_type == "AITask"
        assert evidence_artifact.owner_entity_id == ai_task.id
        assert evidence_artifact.artifact_type == "knowledge_retrieval"
        assert evidence_artifact.mime_type == "application/json"
        assert evidence_artifact.metadata_json["created_by_component"] == "DeterministicKnowledgeAdapter"
        assert evidence_artifact.metadata_json["retrieval_mode"] == "deterministic_local"
        assert evidence_artifact.metadata_json["used_context_artifact_ids"] == [context_id]
        assert evidence_artifact.metadata_json["safe_to_show"] is True
        assert evidence_artifact.metadata_json["redaction_applied"] is False

        forbidden_tables = {
            "rag_indexes",
            "embeddings",
            "mcp_servers",
            "tenants",
            "roles",
            "permissions",
        }
        assert forbidden_tables.isdisjoint(inspect(session.bind).get_table_names())
        assert list(
            session.scalars(
                select(Artifact).where(
                    Artifact.project_id == uuid.UUID(project["id"]),
                    Artifact.artifact_type.in_(["embedding", "vector_index", "mcp_runtime"]),
                ),
            ),
        ) == []

    assert client.artifact_root is not None
    evidence = json.loads((client.artifact_root / evidence_artifact.file_path).read_text())
    assert evidence["retrieval_mode"] == "deterministic_local"
    assert evidence["query_text"] == GOLDEN_REQUIREMENT_CONTENT
    assert evidence["used_knowledge"] is True
    assert evidence["used_context_artifact_ids"] == [context_id]
    assert {"coupon", "checkout", "api", "expired"}.issubset(set(evidence["query_terms"]))
    assert evidence["results"][0]["context_artifact_id"] == context_id
    assert evidence["results"][0]["title"] == "coupon-api-notes.md"
    assert evidence["results"][0]["source_ref"] == "manual:coupon-api-notes.md"
    assert evidence["results"][0]["score"] >= 4
    assert {"coupon", "checkout", "api", "expired"}.issubset(set(evidence["results"][0]["matched_terms"]))
    assert "Expired coupon validation" in evidence["results"][0]["snippet"]
    assert evidence["results"][0]["sha256"].startswith("sha256:")
    assert evidence["results"][0]["allowed_for_prompt"] is True
    assert evidence["results"][0]["redaction_applied"] is False

    knowledge_response = client.get(f"/api/projects/{project['id']}/knowledge-base")
    assert knowledge_response.status_code == 200
    knowledge = knowledge_response.json()
    assert knowledge["knowledge_adapter"]["used_knowledge"] is True
    assert knowledge["knowledge_adapter"]["retrieval_mode"] == "deterministic_local"
    context_row = next(item for item in knowledge["context_artifacts"] if item["id"] == context_id)
    assert context_row["retrieved_count"] == 1
    assert context_row["latest_retrieved_at"]
    assert context_row["usage_count"] == 1
    assert context_row["latest_used_at"]

    assert len(knowledge["latest_retrievals"]) == 1
    latest = knowledge["latest_retrievals"][0]
    assert latest["ai_task_id"] == review_start_body["ai_task_id"]
    assert latest["retrieval_evidence_artifact_id"] == str(evidence_artifact.id)
    assert latest["query_terms"] == evidence["query_terms"]
    assert latest["used_context_artifact_ids"] == [context_id]
    assert latest["snippet_count"] == 1
    assert latest["results"][0]["context_artifact_id"] == context_id
    assert latest["results"][0]["score"] >= 4
    assert {"coupon", "checkout", "api", "expired"}.issubset(set(latest["results"][0]["matched_terms"]))
    assert "Expired coupon validation" in latest["results"][0]["snippet"]
