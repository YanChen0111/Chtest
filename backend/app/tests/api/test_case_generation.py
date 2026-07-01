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
from backend.app.modules.ai_runtime.providers import mock_provider
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase as CaseModel
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


def create_reviewed_requirement(client: ASGIClient, SessionLocal: sessionmaker[Session]) -> tuple[dict[str, Any], dict[str, Any]]:
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
    return requirement, review


def test_start_case_generation_persists_candidates_without_creating_test_cases(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)

    response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": requirement["project_id"],
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

    assert response.status_code == 202
    body = response.json()
    assert body["case_generation_task_id"]
    assert body["ai_task_id"]
    assert body["status"] == "pending"
    assert body["used_knowledge"] is False
    assert body["used_context_artifact_ids"] == []

    candidates_response = client.get(f"/api/case-generation/tasks/{body['case_generation_task_id']}/candidates")
    assert candidates_response.status_code == 200
    candidates = candidates_response.json()
    assert candidates["total"] >= 5
    titles = {candidate["title"] for candidate in candidates["items"]}
    assert "可用优惠券可成功抵扣订单金额" in titles
    first_candidate = next(
        candidate for candidate in candidates["items"] if candidate["title"] == "可用优惠券可成功抵扣订单金额"
    )
    assert first_candidate["priority"] == "P0"
    assert first_candidate["test_type"] == "functional"
    assert first_candidate["steps"]
    assert first_candidate["expected_results"]
    assert first_candidate["requirement_refs"]
    assert first_candidate["ai_reason"]
    assert first_candidate["source_knowledge_evidence_ids"] == []
    assert first_candidate["knowledge_evidence_refs"] == []
    assert first_candidate["covered_risk_ids"] == []
    assert first_candidate["generation_reason"] is None
    assert first_candidate["automation_readiness"] == "unknown"
    assert first_candidate["quality_score"] is None
    assert first_candidate["review_findings"] == []
    assert first_candidate["coverage_gap_notes"] is None
    assert first_candidate["status"] == "generated"

    with SessionLocal() as session:
        generation_task = session.get(CaseGenerationTask, uuid.UUID(body["case_generation_task_id"]))
        assert generation_task is not None
        assert generation_task.status == "succeeded"
        assert generation_task.generated_count == candidates["total"]
        assert generation_task.target_test_types == ["functional", "ui"]
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.task_type == "case_generation"
        assert ai_task.status == "succeeded"
        persisted_candidate = session.scalar(
            select(GeneratedCaseCandidate).where(GeneratedCaseCandidate.generation_task_id == generation_task.id),
        )
        assert persisted_candidate is not None
        assert persisted_candidate.source_knowledge_evidence_ids == []
        assert persisted_candidate.knowledge_evidence_refs_json == []
        assert persisted_candidate.covered_risk_ids == []
        assert persisted_candidate.automation_readiness == "unknown"
        assert persisted_candidate.review_findings_json == []
        assert list(session.scalars(select(CaseModel))) == []


def test_start_case_generation_persists_knowledge_evidence_fields_from_ai_output(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)

    original_success_output = mock_provider.MockLLMProvider._success_output

    def success_output_with_evidence(self, request):
        output = original_success_output(self, request)
        if request.model_name == "mock-case-generator":
            output["cases"][0].update(
                {
                    "source_knowledge_evidence_ids": ["ke-expired-coupon-boundary"],
                    "knowledge_evidence_refs": [
                        {
                            "evidence_id": "ke-expired-coupon-boundary",
                            "knowledge_card_id": "00000000-0000-0000-0000-000000000821",
                            "source_artifact_id": "00000000-0000-0000-0000-000000000371",
                            "snippet": "Expired coupons must be rejected before order submission.",
                            "score": 0.92,
                        },
                    ],
                    "covered_risk_ids": ["00000000-0000-0000-0000-000000000411"],
                    "generation_reason": "Boundary case for expired coupon validation.",
                    "automation_readiness": "suitable_for_playwright",
                    "quality_score": 88,
                    "review_findings": [{"type": "evidence_complete", "severity": "info"}],
                    "coverage_gap_notes": "",
                },
            )
        return output

    monkeypatch.setattr(mock_provider.MockLLMProvider, "_success_output", success_output_with_evidence)

    response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": requirement["project_id"],
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

    assert response.status_code == 202
    generation = response.json()
    candidates_response = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates")

    assert candidates_response.status_code == 200
    candidate = next(
        item
        for item in candidates_response.json()["items"]
        if item["source_knowledge_evidence_ids"] == ["ke-expired-coupon-boundary"]
    )
    assert candidate["source_knowledge_evidence_ids"] == ["ke-expired-coupon-boundary"]
    assert candidate["knowledge_evidence_refs"][0]["knowledge_card_id"] == "00000000-0000-0000-0000-000000000821"
    assert candidate["covered_risk_ids"] == ["00000000-0000-0000-0000-000000000411"]
    assert candidate["generation_reason"] == "Boundary case for expired coupon validation."
    assert candidate["automation_readiness"] == "suitable_for_playwright"
    assert candidate["quality_score"] == 88
    assert candidate["review_findings"] == [{"type": "evidence_complete", "severity": "info"}]
    assert candidate["coverage_gap_notes"] == ""
    assert candidate["status"] == "generated"

    with SessionLocal() as session:
        persisted_candidate = session.scalar(
            select(GeneratedCaseCandidate).where(
                GeneratedCaseCandidate.generation_task_id == uuid.UUID(generation["case_generation_task_id"]),
            ),
        )
        assert persisted_candidate is not None
        assert persisted_candidate.source_knowledge_evidence_ids == ["ke-expired-coupon-boundary"]
        assert persisted_candidate.knowledge_evidence_refs_json[0]["evidence_id"] == "ke-expired-coupon-boundary"
        assert persisted_candidate.covered_risk_ids == [uuid.UUID("00000000-0000-0000-0000-000000000411")]
        assert persisted_candidate.generation_reason == "Boundary case for expired coupon validation."
        assert persisted_candidate.automation_readiness == "suitable_for_playwright"
        assert persisted_candidate.quality_score == 88
        assert persisted_candidate.review_findings_json == [{"type": "evidence_complete", "severity": "info"}]
        assert persisted_candidate.coverage_gap_notes == ""
        assert list(session.scalars(select(CaseModel))) == []


def test_schema_invalid_case_generation_does_not_write_task_or_candidates(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)

    response = client.post(
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
            "mock_mode": "schema_invalid",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "CASE_GENERATION_SCHEMA_INVALID"

    with SessionLocal() as session:
        ai_task = session.scalar(select(AITask).where(AITask.task_type == "case_generation"))
        assert ai_task is not None
        assert ai_task.status == "failed"
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))
        assert llm_log is not None
        assert llm_log.status == "schema_invalid"
        artifacts = list(session.scalars(select(Artifact).where(Artifact.owner_entity_id == ai_task.id)))
        assert any(artifact.artifact_type == "raw_llm_output" for artifact in artifacts)
        assert list(session.scalars(select(CaseGenerationTask))) == []
        assert list(session.scalars(select(GeneratedCaseCandidate))) == []
        assert list(session.scalars(select(CaseModel))) == []


@pytest.mark.parametrize(
    "evidence_patch",
    [
        {"covered_risk_ids": ["not-a-uuid"]},
        {"automation_readiness": "ship_it"},
        {"quality_score": 101},
        {"quality_score": -1},
        {
            "knowledge_evidence_refs": [
                {
                    "evidence_id": "ke-secret",
                    "snippet": "Authorization: Bearer sk-test-secret-value",
                },
            ],
        },
        {"review_findings": [{"type": "raw_provider_payload", "message": "raw_provider_payload"}]},
    ],
)
def test_malformed_generated_case_evidence_output_does_not_write_candidates(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
    evidence_patch: dict[str, Any],
) -> None:
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)

    original_success_output = mock_provider.MockLLMProvider._success_output

    def malformed_success_output(self, request):
        output = original_success_output(self, request)
        if request.model_name == "mock-case-generator":
            output["cases"][0].update(evidence_patch)
        return output

    monkeypatch.setattr(mock_provider.MockLLMProvider, "_success_output", malformed_success_output)

    response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": requirement["project_id"],
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

    assert response.status_code == 422
    assert response.json()["error_code"] == "CASE_GENERATION_SCHEMA_INVALID"

    with SessionLocal() as session:
        ai_task = session.scalar(select(AITask).where(AITask.task_type == "case_generation"))
        assert ai_task is not None
        assert ai_task.status == "failed"
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))
        assert llm_log is not None
        assert llm_log.status == "schema_invalid"
        assert list(session.scalars(select(CaseGenerationTask))) == []
        assert list(session.scalars(select(GeneratedCaseCandidate))) == []
        assert list(session.scalars(select(CaseModel))) == []


def test_unknown_generation_task_candidates_returns_contract_error(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, _ = api_client

    response = client.get(f"/api/case-generation/tasks/{uuid.uuid4()}/candidates")

    assert response.status_code == 404
    assert response.json()["error_code"] == "CASE_GENERATION_TASK_NOT_FOUND"
