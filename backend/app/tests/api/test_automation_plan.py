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
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.automation.models import AutomationDraft, AutomationPlan
from backend.app.modules.cases.models import GeneratedCaseCandidate
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.review_history.models import ReviewHistory


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

    def put(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("PUT", path, json_body)

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
def api_client(tmp_path: Path) -> Iterator[tuple[ASGIClient, sessionmaker[Session], Path]]:
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

    yield ASGIClient(app), SessionLocal, artifact_root

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
                PromptVersion(
                    name="automation_plan_generation",
                    version="v1",
                    hash="sha256:" + "e" * 64,
                    agent_name="AutomationPlanAgent",
                    content="# Automation Plan Prompt",
                ),
                SkillVersion(
                    name="automation-plan-skill",
                    version="v1",
                    hash="sha256:" + "f" * 64,
                    applicable_agents=["AutomationPlanAgent"],
                    content="# Automation Plan Skill",
                ),
                PromptVersion(
                    name="automation_draft_generation",
                    version="v1",
                    hash="sha256:" + "1" * 64,
                    agent_name="AutomationDraftAgent",
                    content="# Automation Draft Prompt",
                ),
                SkillVersion(
                    name="automation-draft-skill",
                    version="v1",
                    hash="sha256:" + "2" * 64,
                    applicable_agents=["AutomationDraftAgent"],
                    content="# Automation Draft Skill",
                ),
            ],
        )
        session.commit()


def create_approved_test_case(client: ASGIClient, SessionLocal: sessionmaker[Session]) -> dict[str, Any]:
    seed_prompt_skill(SessionLocal)
    project = client.post("/api/projects", {"name": "Checkout System"}).json()
    requirement = client.post(
        "/api/requirements",
        {
            "project_id": project["id"],
            "title": "Coupon checkout rules",
            "content": "Expired coupons cannot be used at checkout.",
        },
    ).json()
    review_start = client.post(
        f"/api/requirements/{requirement['id']}/review",
        {
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
        {
            "project_id": project["id"],
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
    ).json()
    candidates = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates").json()
    candidate = candidates["items"][0]
    review_response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        {
            "action": "approve_after_edit",
            "edited_case": {
                "title": "Expired coupon cannot submit order",
                "priority": "P0",
                "test_type": "functional",
                "precondition": "User has an expired coupon.",
                "steps": ["Prepare expired coupon", "Open checkout", "Select expired coupon", "Submit order"],
                "expected_results": ["Submit is blocked", "Expired coupon message is shown"],
                "input_data": {"coupon_state": "expired"},
                "tags": ["coupon", "checkout"],
            },
            "review_comment": "Ready for automation planning.",
        },
    )
    assert review_response.status_code == 200
    body = review_response.json()
    return {
        "project_id": project["id"],
        "requirement_id": requirement["id"],
        "requirement_review_id": review["id"],
        "candidate_id": candidate["id"],
        "test_case_id": body["test_case_id"],
    }


def enable_local_knowledge(client: ASGIClient, project_id: str) -> None:
    response = client.put(
        f"/api/projects/{project_id}/knowledge-adapter",
        {
            "adapter_name": "default",
            "status": "configured_stub",
            "provider_type": "deterministic_local",
            "config": {"match_mode": "keyword_overlap", "max_results": 5, "max_snippet_chars": 320, "min_score": 1},
            "safety_policy": {"same_project_only": True, "require_allowed_for_prompt": True},
            "notes": "Deterministic local retrieval for tests.",
        },
    )
    assert response.status_code == 200


def create_context_artifact(client: ASGIClient, project_id: str) -> str:
    response = client.post(
        "/api/context-artifacts",
        {
            "project_id": project_id,
            "title": "coupon-api-notes.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": "# Coupon API\nExpired coupon checkout submissions must be blocked.",
            "source_ref": "manual:coupon-api-notes.md",
        },
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_automation_plan_requires_approval_before_draft_and_execution(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, artifact_root = api_client
    context = create_approved_test_case(client, SessionLocal)
    enable_local_knowledge(client, context["project_id"])
    context_artifact_id = create_context_artifact(client, context["project_id"])
    knowledge_card_id = str(uuid.uuid4())
    with SessionLocal() as session:
        candidate = session.get(GeneratedCaseCandidate, uuid.UUID(context["candidate_id"]))
        assert candidate is not None
        candidate.source_knowledge_evidence_json = [
            {
                "evidence_id": str(uuid.uuid4()),
                "knowledge_card_id": knowledge_card_id,
                "source_artifact_id": context_artifact_id,
                "knowledge_type": "BoundaryCondition",
                "title": "Expired coupon boundary",
                "snippet": "Expired coupons cannot be used during checkout.",
                "score": 10,
                "matched_terms": ["expired", "coupon"],
                "retrieval_reason": "case_generation_inherited_evidence",
                "safe_to_show": True,
                "allowed_for_prompt": True,
                "status": "approved",
            },
        ]
        session.add(candidate)
        session.commit()

    plan_response = client.post(
        "/api/automation/plans",
        {
            "project_id": context["project_id"],
            "test_case_id": context["test_case_id"],
            "target_framework": "pytest",
            "use_knowledge": True,
            "context_artifact_ids": [context_artifact_id],
            "model_provider": "mock",
            "model_name": "mock-automation-plan",
        },
    )

    assert plan_response.status_code == 202
    plan_body = plan_response.json()
    assert plan_body["status"] == "plan_generated"
    assert plan_body["test_case_id"] == context["test_case_id"]
    assert plan_body["requirement_id"] == context["requirement_id"]
    assert plan_body["requirement_review_id"] == context["requirement_review_id"]
    assert plan_body["source_candidate_id"] == context["candidate_id"]
    assert plan_body["used_context_artifact_ids"] == [context_artifact_id]
    assert plan_body["knowledge_retrieval_artifact_id"]
    assert all(
        item.get("knowledge_card_id") != knowledge_card_id
        for item in plan_body["plan"]["knowledge_evidence"]
    )
    assert any(
        item.get("context_artifact_id") == context_artifact_id
        for item in plan_body["plan"]["knowledge_evidence"]
    )
    assert "Prepare precondition" in plan_body["execution_steps"][0]

    blocked_draft_response = client.post(
        f"/api/automation/plans/{plan_body['id']}/generate-draft",
        {"model_provider": "mock", "model_name": "mock-automation-draft"},
    )
    assert blocked_draft_response.status_code == 409
    assert blocked_draft_response.json()["error_code"] == "AUTOMATION_PLAN_NOT_APPROVED"

    approve_plan_response = client.post(
        f"/api/automation/plans/{plan_body['id']}/approve",
        {"action": "approve", "review_comment": "Plan is feasible."},
    )
    assert approve_plan_response.status_code == 200
    assert approve_plan_response.json()["status"] == "approved"

    draft_response = client.post(
        f"/api/automation/plans/{plan_body['id']}/generate-draft",
        {"model_provider": "mock", "model_name": "mock-automation-draft"},
    )
    assert draft_response.status_code == 202
    draft_body = draft_response.json()
    assert draft_body["status"] == "draft_generated"

    draft_detail = client.get(f"/api/automation/drafts/{draft_body['automation_draft_id']}").json()
    assert draft_detail["automation_plan_id"] == plan_body["id"]
    assert "Generated from an approved AutomationPlan" in draft_detail["execution_notes"]
    assert "AutomationPlan:" in draft_detail["draft_code"]

    blocked_run_response = client.post(
        "/api/test-runs",
        {
            "project_id": context["project_id"],
            "automation_draft_id": draft_body["automation_draft_id"],
            "reason": "run unapproved draft",
        },
    )
    assert blocked_run_response.status_code == 400
    assert blocked_run_response.json()["error_code"] == "TEST_RUN_INVALID_INPUT"

    approve_draft_response = client.post(
        f"/api/automation/drafts/{draft_body['automation_draft_id']}/approve",
        {"action": "approve", "review_comment": "Draft code is safe to execute."},
    )
    assert approve_draft_response.status_code == 200
    assert approve_draft_response.json()["status"] == "approved"

    run_response = client.post(
        "/api/test-runs",
        {
            "project_id": context["project_id"],
            "automation_draft_id": draft_body["automation_draft_id"],
            "reason": "run approved draft",
        },
    )
    assert run_response.status_code == 400
    assert run_response.json()["error_code"] == "TEST_RUN_INVALID_INPUT"

    with SessionLocal() as session:
        plan = session.get(AutomationPlan, uuid.UUID(plan_body["id"]))
        draft = session.get(AutomationDraft, uuid.UUID(draft_body["automation_draft_id"]))
        retrieval_artifact = session.get(Artifact, uuid.UUID(plan_body["knowledge_retrieval_artifact_id"]))
        plan_task = session.get(AITask, uuid.UUID(plan_body["ai_task_id"]))
        test_run = session.scalar(select(TestRun).where(TestRun.automation_draft_id == draft.id))
        history = {
            (item.entity_type, item.action, item.from_status, item.to_status)
            for item in session.scalars(select(ReviewHistory))
            if item.entity_type in {"AutomationPlan", "AutomationDraft"}
        }

    assert plan is not None
    assert draft is not None
    assert retrieval_artifact is not None
    assert plan_task is not None
    assert test_run is None
    assert plan.status == "draft_generated"
    assert draft.status == "approved"
    assert draft.automation_plan_id == plan.id
    assert retrieval_artifact.artifact_type == "knowledge_retrieval"
    assert retrieval_artifact.owner_entity_type == "AITask"
    assert retrieval_artifact.metadata_json["created_by_component"] == "DeterministicKnowledgeAdapter"
    assert "results" not in retrieval_artifact.metadata_json
    assert (artifact_root / retrieval_artifact.file_path).exists()
    assert plan_task.input_json["knowledge_retrieval"]["used_knowledge"] is True
    assert all(
        result.get("knowledge_card_id") != knowledge_card_id
        for result in plan_task.input_json["knowledge_retrieval"]["results"]
    )
    assert any(
        result.get("context_artifact_id") == context_artifact_id
        for result in plan_task.input_json["knowledge_retrieval"]["results"]
    )
    assert ("AutomationPlan", "approve", "plan_generated", "approved") in history
    assert ("AutomationPlan", "generate_draft", "approved", "draft_generated") in history
    assert ("AutomationDraft", "approve", "draft_generated", "approved") in history


def test_automation_plan_rejects_unsourced_test_case(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _artifact_root = api_client
    context = create_approved_test_case(client, SessionLocal)
    with SessionLocal() as session:
        from backend.app.modules.cases.models import TestCase

        source_case = session.get(TestCase, uuid.UUID(context["test_case_id"]))
        assert source_case is not None
        unsourced_case = TestCase(
            project_id=source_case.project_id,
            title="Manual unsourced case",
            priority="P1",
            test_type="functional",
            precondition=None,
            steps_json=["Open checkout"],
            expected_results_json=["Checkout opens"],
            input_data_json={},
            tags=["manual"],
            source_type="manual",
            review_status="approved",
            status="active",
        )
        session.add(unsourced_case)
        session.commit()
        project_id = source_case.project_id
        test_case_id = unsourced_case.id

    response = client.post(
        "/api/automation/plans",
        {
            "project_id": str(project_id),
            "test_case_id": str(test_case_id),
            "target_framework": "pytest",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "AUTOMATION_PLAN_SOURCE_NOT_APPROVED"
