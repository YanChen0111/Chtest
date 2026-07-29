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
from backend.app.modules.prompt_skill.registry_loader import compute_content_hash
from backend.app.modules.requirements.models import RequirementReview, RiskItem
from backend.app.modules.workflow_control.models import WorkflowHumanDecision, WorkflowStageSnapshot, WorkflowTransitionEvent


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
def api_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[ASGIClient, sessionmaker[Session]]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)
    artifact_root = tmp_path / "artifacts"
    monkeypatch.setenv("CHTEST_MODEL_CONNECTION_PATH", str(tmp_path / "model-connection.json"))

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
                    hash=compute_content_hash("# Prompt"),
                    agent_name="RequirementReviewAgent",
                    content="# Prompt",
                    output_schema_json={"required": ["scores", "issues"]},
                ),
                SkillVersion(
                    name="requirement-review-skill",
                    version="v1",
                    hash=compute_content_hash("# Skill"),
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


def write_model_connection_config(path: Path, *, provider: str, model_name: str) -> None:
    path.write_text(
        json.dumps(
            {
                "provider": provider,
                "model_name": model_name,
                "base_url": "https://gateway.example.test/v1",
                "wire_api": "responses",
                "api_key": "sk-local-secret",
            },
        ),
        encoding="utf-8",
    )


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
        assert session.scalar(
            select(Artifact).where(
                Artifact.owner_entity_id == ai_task.id,
                Artifact.file_path.endswith("/runtime_policy.json"),
            ),
        )
        assert session.scalar(select(RequirementReview).where(RequirementReview.requirement_id == uuid.UUID(requirement["id"])))
        assert len(list(session.scalars(select(RiskItem)))) >= 2


def test_start_requirement_review_uses_saved_model_connection_when_request_omits_model(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    write_model_connection_config(
        tmp_path / "model-connection.json",
        provider="OpenAI Compatible",
        model_name="gpt-live-review",
    )
    observed_task_ids: list[uuid.UUID] = []

    def fake_run_ai_task(session: Session, _store: LocalArtifactStore, job: Any) -> None:
        ai_task = session.get(AITask, job.ai_task_id)
        assert ai_task is not None
        observed_task_ids.append(ai_task.id)
        assert ai_task.model_provider == "OpenAI Compatible"
        assert ai_task.model_name == "gpt-live-review"
        ai_task.status = "succeeded"
        ai_task.output_json = {
            "overall_score": 91,
            "scores": {
                "completeness": 90,
                "clarity": 91,
                "consistency": 92,
                "testability": 90,
                "feasibility": 93,
                "logic": 90,
            },
            "issues": [],
            "clarification_questions": [],
            "test_design_notes": ["Ready for model-backed review."],
            "risk_items": [],
            "used_knowledge": False,
            "used_context_artifact_ids": [],
        }
        session.add(ai_task)
        session.commit()

    monkeypatch.setattr("backend.app.modules.requirements.service.run_ai_task", fake_run_ai_task)

    response = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert observed_task_ids == [uuid.UUID(body["ai_task_id"])]
    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.model_provider == "OpenAI Compatible"
        assert ai_task.model_name == "gpt-live-review"
        review = session.scalar(select(RequirementReview).where(RequirementReview.ai_task_id == ai_task.id))
        assert review is not None
        assert review.overall_score == 91


def test_requirement_review_accepts_clarification_supplement(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    observed_inputs: list[dict[str, Any]] = []

    def fake_run_ai_task(session: Session, _store: LocalArtifactStore, job: Any) -> None:
        ai_task = session.get(AITask, job.ai_task_id)
        assert ai_task is not None
        observed_inputs.append(ai_task.input_json)
        ai_task.status = "succeeded"
        ai_task.output_json = {
            "overall_score": 93,
            "scores": {
                "completeness": 92,
                "clarity": 94,
                "consistency": 93,
                "testability": 95,
                "feasibility": 90,
                "logic": 94,
            },
            "issues": [],
            "clarification_questions": [],
            "test_design_notes": ["Supplement resolved the open discount stacking question."],
            "risk_items": [],
            "used_knowledge": False,
            "used_context_artifact_ids": [],
        }
        session.add(ai_task)
        session.commit()

    monkeypatch.setattr("backend.app.modules.requirements.service.run_ai_task", fake_run_ai_task)

    response = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": False,
            "context_artifact_ids": [],
            "supplement_text": "平台活动可以叠加，但积分不可与优惠券同时使用。",
            "clarification_answers": [
                {
                    "question": "优惠券是否可以与平台活动叠加？",
                    "answer": "可以与平台活动叠加。",
                },
            ],
        },
    )

    assert response.status_code == 202
    assert observed_inputs
    assert observed_inputs[0]["clarification_context"] == {
        "supplement_text": "平台活动可以叠加，但积分不可与优惠券同时使用。",
        "clarification_answers": [
            {
                "question": "优惠券是否可以与平台活动叠加？",
                "answer": "可以与平台活动叠加。",
            },
        ],
    }

    review_response = client.get(f"/api/requirements/{requirement['id']}/review")
    assert review_response.status_code == 200
    assert review_response.json()["overall_score"] == 93


def test_requirement_review_generates_downloadable_requirement_document(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
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
    complete = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/complete-review",
        json_body={"expected_version": review["workflow"]["lock_version"]},
    )
    assert complete.status_code == 200
    approved = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/approve",
        json_body={"expected_version": complete.json()["workflow"]["lock_version"]},
    )
    assert approved.status_code == 200

    response = client.post(
        f"/api/requirements/{requirement['id']}/documents",
        json_body={
            "requirement_review_id": review["id"],
            "version": "v1",
            "status": "confirmed",
        },
    )

    assert response.status_code == 201
    document = response.json()
    assert document["requirement_id"] == requirement["id"]
    assert document["requirement_review_id"] == review["id"]
    assert document["document_number"].startswith("RD-CHECKOUT-SYSTEM-")
    assert document["version"] == "v1"
    assert document["status"] == "confirmed"
    assert document["artifact_id"] == document["id"]
    assert document["download_url"] == f"/api/artifacts/{document['artifact_id']}/download"

    list_response = client.get(f"/api/projects/{requirement['project_id']}/requirement-documents")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed["total"] == 1
    assert listed["items"][0]["document_number"] == document["document_number"]

    download_response = client.get(document["download_url"])
    assert download_response.status_code == 200
    markdown = download_response.body.decode("utf-8")
    assert "# 需求规格说明书" in markdown
    assert document["document_number"] in markdown
    assert "## 4. 功能需求" in markdown
    assert "## 9. 追踪矩阵" in markdown

    with SessionLocal() as session:
        artifact = session.get(Artifact, uuid.UUID(document["artifact_id"]))
        assert artifact is not None
        assert artifact.artifact_type == "requirement_md"
        assert artifact.owner_entity_type == "RequirementReview"
        assert artifact.owner_entity_id == uuid.UUID(review["id"])
        assert artifact.metadata_json["document_number"] == document["document_number"]


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
        assert evidence_artifact.metadata_json["result_count"] == 1
        assert "results" not in evidence_artifact.metadata_json
        assert evidence_artifact.metadata_json["query_text_hash"].startswith("sha256:")

        assert client.artifact_root is not None
        evidence = json.loads((client.artifact_root / evidence_artifact.file_path).read_text())
        assert evidence["retrieval_mode"] == "deterministic_local"
        assert evidence["query_text_hash"].startswith("sha256:")
        assert evidence["query_text_redacted"] == requirement["content"]
        assert evidence["used_context_artifact_ids"] == [context_id]
        assert evidence["result_refs"][0]["context_artifact_id"] == context_id
        assert evidence["result_refs"][0]["score"] >= 1
        assert evidence["result_refs"][0]["matched_term_count"] > 0
        assert "Coupon API Notes" not in json.dumps(evidence)
        assert "Expired coupon checkout" not in json.dumps(evidence)


def test_requirement_review_uses_approved_test_knowledge_cards_without_legacy_adapter(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    context_id = create_context_artifact(
        client,
        requirement["project_id"],
        content="# Coupon Boundary\nExpired coupons cannot be used during checkout.",
    )
    extraction_response = client.post(
        "/api/test-knowledge/cards/extract",
        json_body={
            "project_id": requirement["project_id"],
            "source_artifact_id": context_id,
        },
    )
    assert extraction_response.status_code == 201
    extracted_card = extraction_response.json()["items"][0]
    approval_response = client.request(
        "PATCH",
        f"/api/test-knowledge/cards/{extracted_card['id']}",
        json_body={
            "project_id": requirement["project_id"],
            "status": "approved",
        },
    )
    assert approval_response.status_code == 200

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

    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        retrieval = ai_task.input_json["knowledge_retrieval"]
        assert retrieval["retrieval_mode"] == "test_knowledge_hybrid"
        assert retrieval["result_sources"] == ["test_knowledge_card"]
        assert retrieval["results"][0]["knowledge_card_id"] == extracted_card["id"]
        evidence_artifact = session.get(Artifact, uuid.UUID(ai_task.output_json["retrieval_evidence_artifact_id"]))
        assert evidence_artifact is not None
        assert evidence_artifact.owner_entity_type == "KnowledgeRetrievalRun"
        assert evidence_artifact.owner_entity_id == uuid.UUID(retrieval["knowledge_retrieval_run_id"])
        assert evidence_artifact.metadata_json["created_by_component"] == "KnowledgeRetrievalService"
        assert evidence_artifact.metadata_json["retrieval_mode"] == "keyword"
        assert "results" not in evidence_artifact.metadata_json


def test_requirement_review_does_not_bypass_unsafe_card_through_legacy_adapter(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    context_id = create_context_artifact(
        client,
        requirement["project_id"],
        content="# Coupon Boundary\nExpired coupons cannot be used during checkout.",
    )
    configure_deterministic_adapter(SessionLocal, requirement["project_id"])
    extracted_card = client.post(
        "/api/test-knowledge/cards/extract",
        json_body={
            "project_id": requirement["project_id"],
            "source_artifact_id": context_id,
        },
    ).json()["items"][0]
    approve = client.request(
        "PATCH",
        f"/api/test-knowledge/cards/{extracted_card['id']}",
        json_body={"project_id": requirement["project_id"], "status": "approved"},
    )
    assert approve.status_code == 200
    unsafe = client.request(
        "PATCH",
        f"/api/test-knowledge/cards/{extracted_card['id']}",
        json_body={
            "project_id": requirement["project_id"],
            "status": "unsafe",
            "review_comment": "The governed card content is no longer safe.",
        },
    )
    assert unsafe.status_code == 200

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
    assert response.json()["used_knowledge"] is False
    assert response.json()["used_context_artifact_ids"] == []
    with SessionLocal() as session:
        source_artifact = session.get(Artifact, uuid.UUID(context_id))
        assert source_artifact is not None
        assert source_artifact.metadata_json["safe_to_show"] is True
        assert source_artifact.metadata_json["allowed_for_prompt"] is True


def test_requirement_review_mixed_retrieval_writes_reference_manifest(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    governed_context_id = create_context_artifact(
        client,
        requirement["project_id"],
        title="governed-coupon-rule.md",
        content="# Coupon Rule\nExpired coupons cannot be used during checkout.",
    )
    adapter_context_id = create_context_artifact(
        client,
        requirement["project_id"],
        title="checkout-observability.md",
        content="# Checkout Coupon Logs\nCoupon checkout rejection logs include the validation reason.",
    )
    configure_deterministic_adapter(SessionLocal, requirement["project_id"])
    extracted = client.post(
        "/api/test-knowledge/cards/extract",
        json_body={
            "project_id": requirement["project_id"],
            "source_artifact_id": governed_context_id,
        },
    ).json()["items"]
    for card in extracted:
        approval = client.request(
            "PATCH",
            f"/api/test-knowledge/cards/{card['id']}",
            json_body={"project_id": requirement["project_id"], "status": "approved"},
        )
        assert approval.status_code == 200

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
    assert set(response.json()["used_context_artifact_ids"]) == {
        governed_context_id,
        adapter_context_id,
    }

    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(response.json()["ai_task_id"]))
        assert ai_task is not None
        manifest = session.get(Artifact, uuid.UUID(ai_task.output_json["retrieval_evidence_artifact_id"]))
        assert manifest is not None
        assert manifest.owner_entity_type == "AITask"
        assert manifest.metadata_json["created_by_component"] == "KnowledgeRetrievalReferenceManifest"
        canonical_ids = manifest.metadata_json["canonical_artifact_ids"]
        assert len(canonical_ids) == 1
        canonical = session.get(Artifact, uuid.UUID(canonical_ids[0]))
        assert canonical is not None
        assert canonical.owner_entity_type == "KnowledgeRetrievalRun"
        assert client.artifact_root is not None
        payload = json.loads((client.artifact_root / manifest.file_path).read_text(encoding="utf-8"))
        assert payload["result_refs"][0]["context_artifact_id"] == adapter_context_id
        assert payload["knowledge_evidence_refs"]
        assert payload["canonical_artifact_ids"] == canonical_ids
        assert '"snippet"' not in json.dumps(payload)
        assert "governed-coupon-rule.md" not in json.dumps(payload)
        assert "Coupon checkout rejection logs" not in json.dumps(payload)


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


def test_requirement_review_workflow_is_project_scoped_and_rejects_client_state(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    started = client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={"model_provider": "mock", "model_name": "mock-requirement-review"},
    )
    assert started.status_code == 202
    review = client.get(f"/api/requirements/{requirement['id']}/review").json()

    project_read = client.get(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}",
    )
    assert project_read.status_code == 200
    assert project_read.json()["workflow"]["state"] == "waiting_review"
    cross_project = client.get(f"/api/projects/{uuid.uuid4()}/requirement-reviews/{review['id']}")
    assert cross_project.status_code == 404

    spoofed = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/complete-review",
        json_body={
            "expected_version": review["workflow"]["lock_version"],
            "gate_state": "approved",
            "completed_stages": ["scope", "requirement_review"],
        },
    )
    assert spoofed.status_code == 422


def test_requirement_review_approval_is_consumed_once_and_stale_after_revision(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    assert client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={"model_provider": "mock", "model_name": "mock-requirement-review"},
    ).status_code == 202
    review = client.get(f"/api/requirements/{requirement['id']}/review").json()
    complete = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/complete-review",
        json_body={"expected_version": review["workflow"]["lock_version"]},
    ).json()
    approved = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/approve",
        json_body={"expected_version": complete["workflow"]["lock_version"]},
    ).json()
    old_approval = approved["workflow"]["approval_decision_id"]

    revised_issues = [*approved["issues"], {"severity": "low", "description": "Human clarification"}]
    revised = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/edit",
        json_body={
            "expected_version": approved["workflow"]["lock_version"],
            "issues": revised_issues,
            "clarification_questions": approved["clarification_questions"],
            "test_design_notes": approved["test_design_notes"],
            "risk_items": approved["risk_items"],
        },
    )
    assert revised.status_code == 200
    revised_body = revised.json()
    assert revised_body["workflow"]["state"] == "waiting_review"
    assert revised_body["workflow"]["approval_decision_id"] is None

    stale = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/continue",
        json_body={
            "expected_version": revised_body["workflow"]["lock_version"],
            "approval_decision_id": old_approval,
        },
    )
    assert stale.status_code == 409


def test_requirement_review_reject_regenerate_and_atomic_approve_continue(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)

    rejected_requirement = create_requirement(client)
    client.post(
        f"/api/requirements/{rejected_requirement['id']}/review",
        json_body={"model_provider": "mock", "model_name": "mock-requirement-review"},
    )
    rejected_review = client.get(f"/api/requirements/{rejected_requirement['id']}/review").json()
    rejected = client.post(
        f"/api/projects/{rejected_requirement['project_id']}/requirement-reviews/{rejected_review['id']}/reject",
        json_body={"expected_version": rejected_review["workflow"]["lock_version"], "comment": "Not usable"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["workflow"]["state"] == "rejected"

    created = client.post(
        "/api/requirements",
        json_body={
            "project_id": rejected_requirement["project_id"],
            "title": "Refund review rules",
            "content": "Refund approval must retain its review evidence.",
        },
    )
    assert created.status_code == 201
    requirement = created.json()
    client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={"model_provider": "mock", "model_name": "mock-requirement-review"},
    )
    review = client.get(f"/api/requirements/{requirement['id']}/review").json()
    regenerated = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/regenerate-selected",
        json_body={
            "expected_version": review["workflow"]["lock_version"],
            "comment": "Regenerate selected issue",
            "issues": [*review["issues"], {"severity": "medium", "description": "Regenerated candidate"}],
            "clarification_questions": review["clarification_questions"],
            "test_design_notes": review["test_design_notes"],
            "risk_items": review["risk_items"],
        },
    )
    assert regenerated.status_code == 200
    regenerated_body = regenerated.json()
    assert regenerated_body["workflow"]["state"] == "waiting_review"
    assert regenerated_body["issues"][-1]["description"] == "Regenerated candidate"

    completed = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/complete-review",
        json_body={"expected_version": regenerated_body["workflow"]["lock_version"]},
    ).json()
    advanced = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/approve-and-continue",
        json_body={"expected_version": completed["workflow"]["lock_version"], "comment": "Approved"},
    )
    assert advanced.status_code == 200
    workflow = advanced.json()["workflow"]
    assert workflow["stage"] == "risk_review"
    assert workflow["state"] == "draft"
    replay = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/approve-and-continue",
        json_body={"expected_version": completed["workflow"]["lock_version"], "comment": "Replay"},
    )
    assert replay.status_code == 409

    with SessionLocal() as session:
        approvals = list(
            session.scalars(
                select(WorkflowHumanDecision).where(
                WorkflowHumanDecision.workflow_run_id == uuid.UUID(workflow["run_id"]),
                WorkflowHumanDecision.action == "approve",
                ),
            ),
        )
        assert len(approvals) == 1
        approval = approvals[0]
        assert approval is not None
        consumed = session.scalar(
            select(WorkflowTransitionEvent).where(
                WorkflowTransitionEvent.consumed_approval_decision_id == approval.id,
            ),
        )
        assert consumed is not None


def test_risk_review_preserves_source_snapshot_and_requires_fresh_human_approval(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    assert client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={"model_provider": "mock", "model_name": "mock-requirement-review"},
    ).status_code == 202
    review = client.get(f"/api/requirements/{requirement['id']}/review").json()
    completed = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/complete-review",
        json_body={"expected_version": review["workflow"]["lock_version"]},
    ).json()
    risk_draft_response = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/approve-and-continue",
        json_body={"expected_version": completed["workflow"]["lock_version"], "comment": "Approve requirement"},
    )
    assert risk_draft_response.status_code == 200
    risk_draft = risk_draft_response.json()
    assert risk_draft["workflow"]["stage"] == "risk_review"
    assert risk_draft["workflow"]["state"] == "draft"

    with SessionLocal() as session:
        risk_snapshot = session.get(WorkflowStageSnapshot, uuid.UUID(risk_draft["workflow"]["snapshot_id"]))
        assert risk_snapshot is not None
        source_snapshot = session.get(WorkflowStageSnapshot, risk_snapshot.previous_snapshot_id)
        assert source_snapshot is not None
        assert risk_snapshot.input_payload_json["source_requirement_review_snapshot_id"] == str(source_snapshot.id)
        assert risk_snapshot.input_payload_json["source_requirement_review_snapshot_hash"] == source_snapshot.input_snapshot_hash
        assert risk_snapshot.input_payload_json["risk_items"]

    cross_project = client.get(
        f"/api/projects/{uuid.uuid4()}/requirement-reviews/{review['id']}/risk-review",
    )
    assert cross_project.status_code == 404
    risk_read = client.get(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review",
    )
    assert risk_read.status_code == 200
    assert risk_read.json()["workflow"]["state"] == "draft"

    wrong_stage_action = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/complete-review",
        json_body={"expected_version": risk_draft["workflow"]["lock_version"]},
    )
    assert wrong_stage_action.status_code == 409
    premature_advance = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/approve-and-continue",
        json_body={"expected_version": risk_draft["workflow"]["lock_version"]},
    )
    assert premature_advance.status_code == 409
    unchanged = client.get(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review",
    ).json()
    assert unchanged["workflow"]["lock_version"] == risk_draft["workflow"]["lock_version"]

    submitted = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/submit",
        json_body={"expected_version": risk_draft["workflow"]["lock_version"]},
    ).json()
    assert submitted["workflow"]["state"] == "waiting_review"
    risk_complete = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/complete-review",
        json_body={"expected_version": submitted["workflow"]["lock_version"]},
    ).json()
    old_approved = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/approve",
        json_body={"expected_version": risk_complete["workflow"]["lock_version"]},
    ).json()
    old_approval_id = old_approved["workflow"]["approval_decision_id"]

    edited_risks = [dict(item) for item in old_approved["risk_items"]]
    edited_risks[0]["suggestion"] = "Cover the approved high-risk boundary and recovery evidence."
    edited = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/edit",
        json_body={
            "expected_version": old_approved["workflow"]["lock_version"],
            "comment": "Tighten risk strategy",
            "risk_items": edited_risks,
        },
    )
    assert edited.status_code == 200
    edited_body = edited.json()
    assert edited_body["workflow"]["state"] == "waiting_review"
    assert edited_body["workflow"]["approval_decision_id"] is None
    assert edited_body["risk_items"][0]["suggestion"] == edited_risks[0]["suggestion"]

    stale_continue = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/continue",
        json_body={
            "expected_version": edited_body["workflow"]["lock_version"],
            "approval_decision_id": old_approval_id,
        },
    )
    assert stale_continue.status_code == 409

    completed_again = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/complete-review",
        json_body={"expected_version": edited_body["workflow"]["lock_version"]},
    ).json()
    advanced = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/approve-and-continue",
        json_body={"expected_version": completed_again["workflow"]["lock_version"], "comment": "Approve risks"},
    )
    assert advanced.status_code == 200
    test_plan = advanced.json()
    assert test_plan["workflow"]["stage"] == "test_plan_review"
    assert test_plan["workflow"]["state"] == "draft"
    replay = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/approve-and-continue",
        json_body={"expected_version": completed_again["workflow"]["lock_version"]},
    )
    assert replay.status_code == 409
    assert client.get(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review",
    ).status_code == 409

    with SessionLocal() as session:
        plan_snapshot = session.get(WorkflowStageSnapshot, uuid.UUID(test_plan["workflow"]["snapshot_id"]))
        assert plan_snapshot is not None
        source_risk_snapshot = session.get(WorkflowStageSnapshot, plan_snapshot.previous_snapshot_id)
        assert source_risk_snapshot is not None
        assert plan_snapshot.input_payload_json["source_risk_review_snapshot_id"] == str(source_risk_snapshot.id)
        assert plan_snapshot.input_payload_json["source_risk_review_snapshot_hash"] == source_risk_snapshot.input_snapshot_hash
        assert plan_snapshot.input_payload_json["approved_risk_items"] == edited_risks


def test_test_plan_review_preserves_risk_snapshot_requires_strategy_and_consumes_approval_once(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)
    requirement = create_requirement(client)
    assert client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={"model_provider": "mock", "model_name": "mock-requirement-review"},
    ).status_code == 202
    review = client.get(f"/api/requirements/{requirement['id']}/review").json()
    completed = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/complete-review",
        json_body={"expected_version": review["workflow"]["lock_version"]},
    ).json()
    risk_draft = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/approve-and-continue",
        json_body={"expected_version": completed["workflow"]["lock_version"], "comment": "Approve requirement"},
    ).json()
    risk_submitted = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/submit",
        json_body={"expected_version": risk_draft["workflow"]["lock_version"]},
    ).json()
    risk_completed = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/complete-review",
        json_body={"expected_version": risk_submitted["workflow"]["lock_version"]},
    ).json()
    test_plan_draft = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/risk-review/approve-and-continue",
        json_body={"expected_version": risk_completed["workflow"]["lock_version"], "comment": "Approve risks"},
    ).json()
    assert test_plan_draft["workflow"]["stage"] == "test_plan_review"
    assert test_plan_draft["workflow"]["state"] == "draft"
    submitted = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/submit",
        json_body={"expected_version": test_plan_draft["workflow"]["lock_version"]},
    ).json()
    assert submitted["workflow"]["stage"] == "test_plan_review"
    assert submitted["workflow"]["state"] == "waiting_review"
    assert client.get(
        f"/api/projects/{uuid.uuid4()}/requirement-reviews/{review['id']}/test-plan-review",
    ).status_code == 404
    test_plan_read = client.get(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review",
    )
    assert test_plan_read.status_code == 200
    assert test_plan_read.json()["workflow"]["state"] == "waiting_review"

    completed_plan = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/complete-review",
        json_body={"expected_version": submitted["workflow"]["lock_version"]},
    ).json()
    blocked = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/approve",
        json_body={"expected_version": completed_plan["workflow"]["lock_version"]},
    )
    assert blocked.status_code == 409
    assert blocked.json()["error_code"] == "TEST_PLAN_STRATEGY_REQUIRED"

    edited_plan_items = [
        {
            "title": "Cover coupon boundaries",
            "risk_level": "high",
            "focus": "expired coupon and recovered checkout paths",
        },
    ]
    strategy = "Target the high-risk boundary with a negative checkout regression and recovery assertion."
    edited = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/edit",
        json_body={
            "expected_version": completed_plan["workflow"]["lock_version"],
            "comment": "Add explicit plan strategy",
            "test_strategy": strategy,
            "plan_items": edited_plan_items,
        },
    )
    assert edited.status_code == 200
    edited_body = edited.json()
    assert edited_body["workflow"]["state"] == "waiting_review"
    assert edited_body["workflow"]["approval_decision_id"] is None

    completed_again = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/complete-review",
        json_body={"expected_version": edited_body["workflow"]["lock_version"]},
    ).json()
    old_approved = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/approve",
        json_body={"expected_version": completed_again["workflow"]["lock_version"], "comment": "Approve draft plan"},
    ).json()
    old_approval_id = old_approved["workflow"]["approval_decision_id"]

    revised_strategy = f"{strategy} Also verify audit evidence for the rejected coupon path."
    revised_plan_items = [*edited_plan_items, {"title": "Audit rejected coupon evidence", "risk_level": "medium"}]
    revised = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/edit",
        json_body={
            "expected_version": old_approved["workflow"]["lock_version"],
            "comment": "Add audit evidence focus",
            "test_strategy": revised_strategy,
            "plan_items": revised_plan_items,
        },
    )
    assert revised.status_code == 200
    revised_body = revised.json()
    assert revised_body["workflow"]["state"] == "waiting_review"
    assert revised_body["workflow"]["approval_decision_id"] is None
    stale_continue = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/continue",
        json_body={
            "expected_version": revised_body["workflow"]["lock_version"],
            "approval_decision_id": old_approval_id,
        },
    )
    assert stale_continue.status_code == 409

    completed_final = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/complete-review",
        json_body={"expected_version": revised_body["workflow"]["lock_version"]},
    ).json()
    approved = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/approve-and-continue",
        json_body={"expected_version": completed_final["workflow"]["lock_version"], "comment": "Approve test plan"},
    )
    assert approved.status_code == 200
    approved_body = approved.json()
    assert approved_body["workflow"]["stage"] == "case_review"
    assert approved_body["workflow"]["state"] == "draft"

    replay = client.post(
        f"/api/projects/{requirement['project_id']}/requirement-reviews/{review['id']}/test-plan-review/approve-and-continue",
        json_body={"expected_version": completed_final["workflow"]["lock_version"]},
    )
    assert replay.status_code == 409

    with SessionLocal() as session:
        plan_snapshot = session.get(WorkflowStageSnapshot, uuid.UUID(approved_body["workflow"]["snapshot_id"]))
        assert plan_snapshot is not None
        source_plan_snapshot = session.get(WorkflowStageSnapshot, plan_snapshot.previous_snapshot_id)
        assert source_plan_snapshot is not None
        assert plan_snapshot.input_payload_json["source_test_plan_review_snapshot_id"] == str(source_plan_snapshot.id)
        assert plan_snapshot.input_payload_json["source_test_plan_review_snapshot_hash"] == source_plan_snapshot.input_snapshot_hash
        assert plan_snapshot.input_payload_json["approved_risk_items"]
        assert plan_snapshot.input_payload_json["test_strategy"] == revised_strategy
        assert plan_snapshot.input_payload_json["plan_items"] == revised_plan_items
