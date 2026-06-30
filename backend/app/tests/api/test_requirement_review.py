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
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.extension.models import KnowledgeAdapterConfig
from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.requirements.models import RequirementReview, RiskItem


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
                    content="# Prompt",
                    output_schema_json={"required": ["scores", "issues"]},
                ),
                SkillVersion(
                    name="requirement-review-skill",
                    version="v1",
                    hash="sha256:" + "b" * 64,
                    applicable_agents=["RequirementReviewAgent"],
                    content="# Skill",
                ),
            ],
        )
        session.commit()


def create_requirement(client: ASGIClient) -> dict[str, Any]:
    project = client.post("/api/projects", json_body={"name": "Checkout System"}).json()
    response = client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "title": "Coupon checkout rules",
            "content": "Coupon cannot be used with points. Expired coupons cannot be used.",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_context_artifact(
    client: ASGIClient,
    project_id: str,
    *,
    title: str = "coupon-api-notes.md",
    content: str = "# Coupon API Notes\nCoupons are validated before order submit.",
) -> str:
    response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": project_id,
            "title": title,
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": content,
            "source_ref": f"manual:{title}",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


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


def test_start_requirement_review_persists_review_risks_and_ai_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    context_id = create_context_artifact(client, requirement["project_id"])

    response = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": False,
            "context_artifact_ids": [context_id],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["requirement_id"] == requirement["id"]
    assert body["status"] == "pending"
    assert body["next_poll_url"] == f"/api/ai-tasks/{body['ai_task_id']}"
    assert body["used_knowledge"] is False
    assert body["used_context_artifact_ids"] == [context_id]

    review_response = client.get(f"/api/requirements/{requirement['id']}/review")
    assert review_response.status_code == 200
    review = review_response.json()
    assert review["requirement_id"] == requirement["id"]
    assert review["overall_score"] == 82
    assert review["scores"]["clarity"] == 85
    assert review["issues"]
    assert review["clarification_questions"]
    assert len(review["risk_items"]) >= 2
    assert review["risk_items"][0]["risk_level"] == "high"
    assert review["used_context_artifact_ids"] == [context_id]
    assert review["context_manifest_artifact_id"]
    assert review["status"] == "reviewed"

    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.agent_name == "RequirementReviewAgent"
        assert ai_task.task_type == "requirement_review"
        assert ai_task.status == "succeeded"
        assert ai_task.context_artifact_ids == [uuid.UUID(context_id)]
        assert session.scalar(select(RequirementReview).where(RequirementReview.requirement_id == uuid.UUID(requirement["id"])))
        assert len(list(session.scalars(select(RiskItem)))) >= 2


def test_requirement_review_attaches_deterministic_retrieval_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    context_id = create_context_artifact(client, requirement["project_id"])
    configure_deterministic_adapter(SessionLocal, requirement["project_id"])

    response = client.post(
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

    assert response.status_code == 202
    body = response.json()
    assert body["used_knowledge"] is True
    assert body["used_context_artifact_ids"] == [context_id]

    review_response = client.get(f"/api/requirements/{requirement['id']}/review")
    assert review_response.status_code == 200
    review = review_response.json()
    assert review["used_knowledge"] is True
    assert review["used_context_artifact_ids"] == [context_id]

    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.output_json["used_knowledge"] is True
        assert ai_task.output_json["used_context_artifact_ids"] == [context_id]
        evidence_artifact_id = uuid.UUID(ai_task.output_json["retrieval_evidence_artifact_id"])
        evidence_artifact = session.get(Artifact, evidence_artifact_id)
        assert evidence_artifact is not None
        assert evidence_artifact.owner_entity_type == "AITask"
        assert evidence_artifact.owner_entity_id == ai_task.id
        assert evidence_artifact.artifact_type == "knowledge_retrieval"
        assert evidence_artifact.mime_type == "application/json"
        assert (
            evidence_artifact.file_path
            == f"projects/{ai_task.project_id}/ai-tasks/{ai_task.id}/knowledge_retrieval.json"
        )
        assert ai_task.output_json["retrieval_evidence_artifact_id"] == str(evidence_artifact.id)
        assert evidence_artifact.metadata_json["created_by_component"] == "DeterministicKnowledgeAdapter"
        assert evidence_artifact.metadata_json["source_entity_type"] == "AITask"
        assert evidence_artifact.metadata_json["source_entity_id"] == str(ai_task.id)
        assert evidence_artifact.metadata_json["safe_to_show"] is True
        assert evidence_artifact.metadata_json["redaction_applied"] is False
        assert evidence_artifact.metadata_json["retrieval_mode"] == "deterministic_local"
        assert evidence_artifact.metadata_json["used_context_artifact_ids"] == [context_id]

        assert client.artifact_root is not None
        evidence = json.loads((client.artifact_root / evidence_artifact.file_path).read_text())
        assert evidence["retrieval_mode"] == "deterministic_local"
        assert evidence["query_text"] == requirement["content"]
        assert "coupon" in evidence["query_terms"]
        assert evidence["used_knowledge"] is True
        assert evidence["used_context_artifact_ids"] == [context_id]
        assert evidence["results"][0]["context_artifact_id"] == context_id
        assert evidence["results"][0]["title"] == "coupon-api-notes.md"
        assert evidence["results"][0]["source_ref"] == "manual:coupon-api-notes.md"
        assert evidence["results"][0]["score"] >= 1
        assert "coupon" in evidence["results"][0]["matched_terms"]
        assert "Coupon API Notes" in evidence["results"][0]["snippet"]
        assert evidence["results"][0]["sha256"].startswith("sha256:")
        assert evidence["results"][0]["allowed_for_prompt"] is True
        assert evidence["results"][0]["redaction_applied"] is False


def test_requirement_review_merges_explicit_and_retrieved_context_ids(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    explicit_id = create_context_artifact(
        client,
        requirement["project_id"],
        title="shipping-note.md",
        content="# Shipping Note\nShipping cutoff is 18:00.",
    )
    retrieved_id = create_context_artifact(client, requirement["project_id"])
    configure_deterministic_adapter(SessionLocal, requirement["project_id"])

    response = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": True,
            "context_artifact_ids": [explicit_id],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["used_knowledge"] is True
    assert body["used_context_artifact_ids"] == [explicit_id, retrieved_id]

    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.context_artifact_ids == [uuid.UUID(explicit_id), uuid.UUID(retrieved_id)]
        assert ai_task.output_json["used_context_artifact_ids"] == [explicit_id, retrieved_id]
        evidence_artifact = session.get(Artifact, uuid.UUID(ai_task.output_json["retrieval_evidence_artifact_id"]))
        assert evidence_artifact is not None
        assert evidence_artifact.metadata_json["used_context_artifact_ids"] == [retrieved_id]


def test_requirement_review_does_not_retrieve_when_use_knowledge_false(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    context_id = create_context_artifact(client, requirement["project_id"])
    configure_deterministic_adapter(SessionLocal, requirement["project_id"])

    response = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": False,
            "context_artifact_ids": [context_id],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["used_knowledge"] is False
    assert body["used_context_artifact_ids"] == [context_id]

    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.context_artifact_ids == [uuid.UUID(context_id)]
        assert ai_task.output_json["used_knowledge"] is False
        assert ai_task.output_json["used_context_artifact_ids"] == [context_id]
        assert "retrieval_evidence_artifact_id" not in ai_task.output_json
        retrieval_artifacts = list(
            session.scalars(
                select(Artifact).where(
                    Artifact.owner_entity_id == ai_task.id,
                    Artifact.artifact_type == "knowledge_retrieval",
                ),
            ),
        )
        assert retrieval_artifacts == []


def test_requirement_review_keeps_used_knowledge_false_when_adapter_not_configured(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    create_context_artifact(client, requirement["project_id"])

    response = client.post(
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

    assert response.status_code == 202
    body = response.json()
    assert body["used_knowledge"] is False
    assert body["used_context_artifact_ids"] == []

    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.output_json["used_knowledge"] is False
        assert ai_task.output_json["used_context_artifact_ids"] == []
        retrieval_artifacts = list(
            session.scalars(
                select(Artifact).where(
                    Artifact.owner_entity_id == ai_task.id,
                    Artifact.artifact_type == "knowledge_retrieval",
                ),
            ),
        )
        assert retrieval_artifacts == []


def test_schema_invalid_review_does_not_write_business_tables(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)

    response = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": False,
            "context_artifact_ids": [],
            "mock_mode": "schema_invalid",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "REQUIREMENT_REVIEW_SCHEMA_INVALID"

    with SessionLocal() as session:
        ai_task = session.scalar(select(AITask).where(AITask.task_type == "requirement_review"))
        assert ai_task is not None
        assert ai_task.status == "failed"
        assert ai_task.error_json is not None
        assert ai_task.error_json["error_code"] == "MOCK_SCHEMA_INVALID"
        artifacts = list(session.scalars(select(Artifact).where(Artifact.owner_entity_id == ai_task.id)))
        assert any(artifact.artifact_type == "raw_llm_output" for artifact in artifacts)
        assert session.scalar(select(RequirementReview)) is None
        assert list(session.scalars(select(RiskItem))) == []


def test_start_review_rejects_unknown_context_artifact(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)

    response = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": False,
            "context_artifact_ids": [str(uuid.uuid4())],
        },
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "CONTEXT_ARTIFACT_NOT_FOUND"


def test_malformed_review_output_does_not_write_business_tables(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)

    from backend.app.modules.ai_runtime.providers.mock_provider import MockLLMProvider

    original_success_output = MockLLMProvider._success_output

    def malformed_success_output(self, request):
        output = original_success_output(self, request)
        output["scores"]["clarity"] = 999
        output["risk_items"] = [{"title": "missing suggestion", "risk_level": "high"}]
        return output

    monkeypatch.setattr(MockLLMProvider, "_success_output", malformed_success_output)

    response = client.post(
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

    assert response.status_code == 422
    assert response.json()["error_code"] == "REQUIREMENT_REVIEW_SCHEMA_INVALID"

    with SessionLocal() as session:
        ai_task = session.scalar(select(AITask).where(AITask.task_type == "requirement_review"))
        assert ai_task is not None
        assert ai_task.status == "failed"
        assert ai_task.error_json is not None
        assert ai_task.error_json["error_code"] == "REQUIREMENT_REVIEW_SCHEMA_INVALID"
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))
        assert llm_log is not None
        assert llm_log.status == "schema_invalid"
        assert llm_log.error_json is not None
        assert llm_log.error_json["error_code"] == "REQUIREMENT_REVIEW_SCHEMA_INVALID"
        assert session.scalar(select(RequirementReview)) is None
        assert list(session.scalars(select(RiskItem))) == []


def test_get_review_for_unknown_requirement_returns_contract_error(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, _ = api_client

    response = client.get(f"/api/requirements/{uuid.uuid4()}/review")

    assert response.status_code == 404
    assert response.json()["error_code"] == "REQUIREMENT_NOT_FOUND"


def test_get_missing_review_returns_contract_error(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, _ = api_client
    requirement = create_requirement(client)

    response = client.get(f"/api/requirements/{requirement['id']}/review")

    assert response.status_code == 404
    assert response.json()["error_code"] == "REQUIREMENT_REVIEW_NOT_FOUND"
