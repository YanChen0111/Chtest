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
            "decision_table_acknowledged": True,
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
    first_candidate = next(candidate for candidate in candidates["items"] if candidate["title"].startswith("Main workflow:"))
    assert first_candidate["priority"] == "P0"
    assert first_candidate["test_type"] == "functional"
    assert first_candidate["steps"]
    assert first_candidate["expected_results"]
    assert first_candidate["requirement_refs"]
    assert first_candidate["coverage_dimensions"]
    assert any(dimension["key"] == "positive" for dimension in first_candidate["coverage_dimensions"])
    assert first_candidate["covered_requirement_ids"]
    assert first_candidate["case_type"] == "functional"
    assert first_candidate["generation_reason"] == first_candidate["ai_reason"]
    assert first_candidate["automation_readiness"]["status"] == "ready_for_review"
    assert first_candidate["quality_assessment"]["agent"] == "CaseReviewAgent"
    assert first_candidate["ai_reason"]
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
        assert ai_task.input_json["decision_table_acknowledged"] is True
        assert any(dimension["key"] == "boundary" for dimension in ai_task.input_json["decision_table_dimensions"])
        assert session.scalar(select(GeneratedCaseCandidate).where(GeneratedCaseCandidate.generation_task_id == generation_task.id))
        assert list(session.scalars(select(CaseModel))) == []


def test_case_generation_marks_wrong_domain_mock_output_failed(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, SessionLocal = api_client

    def fake_run_ai_task(session: Session, _store: LocalArtifactStore, job: Any) -> None:
        ai_task = session.get(AITask, job.ai_task_id)
        assert ai_task is not None
        ai_task.status = "succeeded"
        ai_task.output_json = {
            "cases": [
                {
                    "title": "Expired coupon cannot be used at checkout",
                    "priority": "P0",
                    "test_type": "functional",
                    "precondition": "A customer owns an expired coupon.",
                    "steps": ["Open checkout", "Select the expired coupon"],
                    "expected_results": ["Coupon selection is rejected."],
                    "requirement_refs": ["REQ-COUPON-001"],
                    "coverage_dimensions": [{"key": "negative", "evidence": "Expired coupon rejection."}],
                    "ai_reason": "Cover coupon expiration behavior.",
                },
            ],
            "used_knowledge": False,
            "used_context_artifact_ids": [],
        }
        session.add(ai_task)
        session.commit()

    monkeypatch.setattr("backend.app.modules.cases.service.run_ai_task", fake_run_ai_task)
    seed_prompt_skill(SessionLocal)
    project = client.post("/api/projects", json_body={"name": "Charging System"}).json()
    requirement = client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "title": "预约充电规则与权限",
            "content": "用户 App 支持预约充电、重复预约、最多 2 个预约任务、插枪状态和电流条件判断。",
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
            "decision_table_acknowledged": True,
            "context_artifact_ids": [],
        },
    )

    assert response.status_code == 202
    body = response.json()
    task_response = client.get(f"/api/case-generation/tasks/{body['case_generation_task_id']}")
    assert task_response.status_code == 200
    task_body = task_response.json()
    assert task_body["status"] == "failed"
    assert task_body["error_code"] == "CASE_GENERATION_DOMAIN_MISMATCH"
    candidates_response = client.get(f"/api/case-generation/tasks/{body['case_generation_task_id']}/candidates")
    assert candidates_response.status_code == 200
    assert candidates_response.json()["total"] == 0


def test_start_case_generation_uses_saved_model_connection_when_request_omits_model(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)
    write_model_connection_config(
        tmp_path / "model-connection.json",
        provider="OpenAI Compatible",
        model_name="gpt-live-cases",
    )
    observed_task_ids: list[uuid.UUID] = []

    def fake_run_ai_task(session: Session, _store: LocalArtifactStore, job: Any) -> None:
        ai_task = session.get(AITask, job.ai_task_id)
        assert ai_task is not None
        observed_task_ids.append(ai_task.id)
        assert ai_task.model_provider == "OpenAI Compatible"
        assert ai_task.model_name == "gpt-live-cases"
        assert ai_task.input_json["decision_table_acknowledged"] is True
        ai_task.status = "succeeded"
        ai_task.output_json = {
            "cases": [
                {
                    "title": "Model-backed checkout coupon happy path",
                    "priority": "P1",
                    "test_type": "functional",
                    "precondition": "A valid coupon exists.",
                    "steps": ["Open checkout", "Apply coupon", "Submit order"],
                    "expected_results": ["Order is submitted with the discounted amount."],
                    "requirement_refs": [str(requirement["id"])],
                    "risk_refs": [],
                    "input_data": {},
                    "tags": ["coupon"],
                    "coverage_dimensions": [
                        {
                            "key": "positive",
                            "evidence": "Valid coupon can be applied during checkout.",
                        },
                    ],
                    "ai_reason": "Covers the primary configured-model generation path.",
                },
            ],
            "used_knowledge": False,
            "used_context_artifact_ids": [],
        }
        session.add(ai_task)
        session.commit()

    monkeypatch.setattr("backend.app.modules.cases.service.run_ai_task", fake_run_ai_task)

    response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": requirement["project_id"],
            "requirement_id": requirement["id"],
            "requirement_review_id": review["id"],
            "target_test_types": ["functional"],
            "prompt_version": "case_generation:v1",
            "skill_version": "test-case-generation-skill:v1",
            "use_knowledge": False,
            "decision_table_acknowledged": True,
            "context_artifact_ids": [],
        },
    )

    assert response.status_code == 202
    body = response.json()
    candidates_response = client.get(f"/api/case-generation/tasks/{body['case_generation_task_id']}/candidates")
    assert candidates_response.status_code == 200
    candidates = candidates_response.json()
    assert candidates["items"][0]["coverage_dimensions"] == [
        {
            "key": "positive",
            "label": "主流程",
            "evidence": "Valid coupon can be applied during checkout.",
            "source": "model",
        },
    ]
    assert observed_task_ids == [uuid.UUID(body["ai_task_id"])]
    with SessionLocal() as session:
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert ai_task is not None
        assert ai_task.model_provider == "OpenAI Compatible"
        assert ai_task.model_name == "gpt-live-cases"
        generation_task = session.get(CaseGenerationTask, uuid.UUID(body["case_generation_task_id"]))
        assert generation_task is not None
        assert generation_task.generated_count == 1
        candidate = session.scalar(select(GeneratedCaseCandidate).where(GeneratedCaseCandidate.generation_task_id == generation_task.id))
        assert candidate is not None
        assert candidate.coverage_dimensions_json[0]["source"] == "model"
        assert candidate.covered_requirement_ids_json == [str(requirement["id"])]
        assert candidate.case_type == "functional"
        assert candidate.generation_reason == candidate.ai_reason


def test_start_case_generation_can_use_requirement_document_artifact(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)
    document_response = client.post(
        f"/api/requirements/{requirement['id']}/documents",
        json_body={
            "requirement_review_id": review["id"],
            "version": "v1",
            "status": "confirmed",
        },
    )
    assert document_response.status_code == 201
    document = document_response.json()
    observed_inputs: list[dict[str, Any]] = []

    def fake_run_ai_task(session: Session, _store: LocalArtifactStore, job: Any) -> None:
        ai_task = session.get(AITask, job.ai_task_id)
        assert ai_task is not None
        observed_inputs.append(ai_task.input_json)
        ai_task.status = "succeeded"
        ai_task.output_json = {
            "cases": [
                {
                    "title": "Document-backed coupon case",
                    "priority": "P1",
                    "test_type": "functional",
                    "precondition": "Requirement document is confirmed.",
                    "steps": ["Read requirement document", "Design checkout coupon case"],
                    "expected_results": ["Case traces back to the requirement document."],
                    "requirement_refs": [document["document_number"]],
                    "risk_refs": [],
                    "input_data": {},
                    "tags": ["requirement-document"],
                    "coverage_dimensions": [
                        {
                            "key": "positive",
                            "evidence": "Requirement document is used as the case source.",
                        },
                    ],
                    "ai_reason": "Uses the generated requirement specification as source of truth.",
                },
            ],
            "used_knowledge": False,
            "used_context_artifact_ids": [],
        }
        session.add(ai_task)
        session.commit()

    monkeypatch.setattr("backend.app.modules.cases.service.run_ai_task", fake_run_ai_task)

    response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": requirement["project_id"],
            "requirement_id": requirement["id"],
            "requirement_review_id": review["id"],
            "requirement_document_artifact_id": document["artifact_id"],
            "target_test_types": ["functional"],
            "prompt_version": "case_generation:v1",
            "skill_version": "test-case-generation-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-case-generator",
            "use_knowledge": False,
            "decision_table_acknowledged": True,
            "context_artifact_ids": [],
        },
    )

    assert response.status_code == 202
    assert observed_inputs
    assert observed_inputs[0]["decision_table_acknowledged"] is True
    requirement_document = observed_inputs[0]["requirement_document"]
    assert requirement_document["artifact_id"] == document["artifact_id"]
    assert requirement_document["document_number"] == document["document_number"]
    assert "# 需求规格说明书" in requirement_document["content"]
    assert "## 9. 追踪矩阵" in requirement_document["content"]


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
            "decision_table_acknowledged": True,
            "context_artifact_ids": [],
            "mock_mode": "schema_invalid",
        },
    )

    assert response.status_code == 202
    body = response.json()
    task_response = client.get(f"/api/case-generation/tasks/{body['case_generation_task_id']}")
    assert task_response.status_code == 200
    task_body = task_response.json()
    assert task_body["status"] == "failed"
    assert task_body["error_code"] == "MOCK_SCHEMA_INVALID"

    with SessionLocal() as session:
        ai_task = session.scalar(select(AITask).where(AITask.task_type == "case_generation"))
        assert ai_task is not None
        assert ai_task.status == "failed"
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))
        assert llm_log is not None
        assert llm_log.status == "schema_invalid"
        artifacts = list(session.scalars(select(Artifact).where(Artifact.owner_entity_id == ai_task.id)))
        assert any(artifact.artifact_type == "raw_llm_output" for artifact in artifacts)
        generation_task = session.get(CaseGenerationTask, uuid.UUID(body["case_generation_task_id"]))
        assert generation_task is not None
        assert generation_task.status == "failed"
        assert list(session.scalars(select(GeneratedCaseCandidate))) == []
        assert list(session.scalars(select(CaseModel))) == []


def test_case_generation_requires_decision_table_acknowledgement(
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
        },
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "CASE_GENERATION_DECISION_TABLE_REQUIRED"
    with SessionLocal() as session:
        assert list(session.scalars(select(AITask).where(AITask.task_type == "case_generation"))) == []
        assert list(session.scalars(select(CaseGenerationTask))) == []
        assert list(session.scalars(select(GeneratedCaseCandidate))) == []


def test_case_generation_rejects_invalid_coverage_dimensions(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)

    def fake_run_ai_task(session: Session, _store: LocalArtifactStore, job: Any) -> None:
        ai_task = session.get(AITask, job.ai_task_id)
        assert ai_task is not None
        ai_task.status = "succeeded"
        ai_task.output_json = {
            "cases": [
                {
                    "title": "Model-backed checkout coupon case with invalid coverage",
                    "priority": "P1",
                    "test_type": "functional",
                    "precondition": "A valid coupon exists.",
                    "steps": ["Open checkout", "Apply coupon", "Submit order"],
                    "expected_results": ["Order is submitted with the discounted amount."],
                    "requirement_refs": [str(requirement["id"])],
                    "risk_refs": [],
                    "input_data": {},
                    "tags": ["coupon"],
                    "coverage_dimensions": [{"key": "unknown", "evidence": "Not an allowed coverage key."}],
                    "ai_reason": "Covers a schema-invalid coverage dimension path.",
                },
            ],
            "used_knowledge": False,
            "used_context_artifact_ids": [],
        }
        session.add(ai_task)
        session.commit()

    monkeypatch.setattr("backend.app.modules.cases.service.run_ai_task", fake_run_ai_task)

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
            "decision_table_acknowledged": True,
            "context_artifact_ids": [],
        },
    )

    assert response.status_code == 202
    body = response.json()
    task_body = client.get(f"/api/case-generation/tasks/{body['case_generation_task_id']}").json()
    assert task_body["status"] == "failed"
    assert task_body["error_code"] == "CASE_GENERATION_SCHEMA_INVALID"
    with SessionLocal() as session:
        assert list(session.scalars(select(GeneratedCaseCandidate))) == []


def test_case_generation_rejects_model_fabricated_knowledge_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, SessionLocal = api_client
    requirement, review = create_reviewed_requirement(client, SessionLocal)

    def fake_run_ai_task(session: Session, _store: LocalArtifactStore, job: Any) -> None:
        ai_task = session.get(AITask, job.ai_task_id)
        assert ai_task is not None
        ai_task.status = "succeeded"
        ai_task.output_json = {
            "cases": [
                {
                    "title": "Checkout coupon case with fabricated evidence",
                    "priority": "P1",
                    "test_type": "functional",
                    "precondition": "A coupon exists.",
                    "steps": ["Open checkout", "Apply coupon"],
                    "expected_results": ["Checkout validates the coupon."],
                    "requirement_refs": [str(requirement["id"])],
                    "risk_refs": [],
                    "source_knowledge_evidence": [
                        {
                            "evidence_id": str(uuid.uuid4()),
                            "knowledge_card_id": str(uuid.uuid4()),
                            "snippet": "Fabricated provider evidence.",
                            "score": 999,
                        },
                    ],
                    "coverage_dimensions": [
                        {"key": "positive", "evidence": "Coupon checkout path."},
                    ],
                    "ai_reason": "Exercises the checkout requirement.",
                },
            ],
            "used_knowledge": True,
            "used_context_artifact_ids": [],
        }
        session.add(ai_task)
        session.commit()

    monkeypatch.setattr("backend.app.modules.cases.service.run_ai_task", fake_run_ai_task)

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
            "decision_table_acknowledged": True,
            "context_artifact_ids": [],
        },
    )

    assert response.status_code == 202
    task_body = client.get(f"/api/case-generation/tasks/{response.json()['case_generation_task_id']}").json()
    assert task_body["status"] == "failed"
    assert task_body["error_code"] == "CASE_GENERATION_SCHEMA_INVALID"
    with SessionLocal() as session:
        assert list(session.scalars(select(GeneratedCaseCandidate))) == []


def test_unknown_generation_task_candidates_returns_contract_error(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, _ = api_client

    response = client.get(f"/api/case-generation/tasks/{uuid.uuid4()}/candidates")

    assert response.status_code == 404
    assert response.json()["error_code"] == "CASE_GENERATION_TASK_NOT_FOUND"
