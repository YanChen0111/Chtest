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
from backend.app.modules.execution import service as execution_service
from backend.app.modules.execution.models import TestRun
from backend.app.modules.execution.pytest_runner import PytestRunnerResult
from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.prompt_skill.registry_loader import compute_content_hash
from backend.app.modules.review_history.models import ReviewHistory
from backend.app.modules.workflow_control.models import WorkflowHumanDecision, WorkflowStageSnapshot


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
                    hash=compute_content_hash("# Requirement Review Prompt"),
                    agent_name="RequirementReviewAgent",
                    content="# Requirement Review Prompt",
                ),
                SkillVersion(
                    name="requirement-review-skill",
                    version="v1",
                    hash=compute_content_hash("# Requirement Review Skill"),
                    applicable_agents=["RequirementReviewAgent"],
                    content="# Requirement Review Skill",
                ),
                PromptVersion(
                    name="case_generation",
                    version="v1",
                    hash=compute_content_hash("# Case Generation Prompt"),
                    agent_name="CaseGenerationAgent",
                    content="# Case Generation Prompt",
                ),
                SkillVersion(
                    name="test-case-generation-skill",
                    version="v1",
                    hash=compute_content_hash("# Case Generation Skill"),
                    applicable_agents=["CaseGenerationAgent"],
                    content="# Case Generation Skill",
                ),
                PromptVersion(
                    name="automation_plan_generation",
                    version="v1",
                    hash=compute_content_hash("# Automation Plan Prompt"),
                    agent_name="AutomationPlanAgent",
                    content="# Automation Plan Prompt",
                ),
                SkillVersion(
                    name="automation-plan-skill",
                    version="v1",
                    hash=compute_content_hash("# Automation Plan Skill"),
                    applicable_agents=["AutomationPlanAgent"],
                    content="# Automation Plan Skill",
                ),
                PromptVersion(
                    name="automation_draft_generation",
                    version="v1",
                    hash=compute_content_hash("# Automation Draft Prompt"),
                    agent_name="AutomationDraftAgent",
                    content="# Automation Draft Prompt",
                ),
                SkillVersion(
                    name="automation-draft-skill",
                    version="v1",
                    hash=compute_content_hash("# Automation Draft Skill"),
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


def create_automation_plan_review_context(client: ASGIClient, SessionLocal: sessionmaker[Session]) -> dict[str, Any]:
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
    assert client.post(
        f"/api/requirements/{requirement['id']}/review",
        {
            "prompt_version": "requirement_review:v1",
            "skill_version": "requirement-review-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-requirement-review",
            "use_knowledge": False,
            "context_artifact_ids": [],
        },
    ).status_code == 202
    review = client.get(f"/api/requirements/{requirement['id']}/review").json()
    requirement_completed = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/complete-review",
        {"expected_version": review["workflow"]["lock_version"]},
    ).json()
    risk_draft = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/approve-and-continue",
        {"expected_version": requirement_completed["workflow"]["lock_version"]},
    ).json()
    risk_submitted = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/risk-review/submit",
        {"expected_version": risk_draft["workflow"]["lock_version"]},
    ).json()
    risk_completed = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/risk-review/complete-review",
        {"expected_version": risk_submitted["workflow"]["lock_version"]},
    ).json()
    test_plan_draft = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/risk-review/approve-and-continue",
        {"expected_version": risk_completed["workflow"]["lock_version"]},
    ).json()
    test_plan_submitted = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/test-plan-review/submit",
        {"expected_version": test_plan_draft["workflow"]["lock_version"]},
    ).json()
    strategy = "Cover coupon validation before automation planning."
    test_plan_edited = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/test-plan-review/edit",
        {
            "expected_version": test_plan_submitted["workflow"]["lock_version"],
            "test_strategy": strategy,
            "plan_items": [{"risk_title": "Expired coupon", "risk_level": "high", "strategy": strategy}],
        },
    ).json()
    test_plan_completed = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/test-plan-review/complete-review",
        {"expected_version": test_plan_edited["workflow"]["lock_version"]},
    ).json()
    case_review_draft = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/test-plan-review/approve-and-continue",
        {"expected_version": test_plan_completed["workflow"]["lock_version"]},
    ).json()
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
    candidates = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates").json()["items"]
    candidate = candidates[0]
    approved_case = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        {"action": "approve", "review_comment": "Ready for automation planning."},
    ).json()
    for rejected_candidate in candidates[1:]:
        assert client.post(
            f"/api/case-review/items/{rejected_candidate['id']}/approve",
            {"action": "reject", "review_comment": "Outside automation scope."},
        ).status_code == 200
    case_submitted = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/submit",
        {"expected_version": case_review_draft["workflow"]["lock_version"]},
    ).json()
    case_edited = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/edit",
        {
            "expected_version": case_submitted["workflow"]["lock_version"],
            "candidate_decisions": [
                {
                    "candidate_id": candidate["id"],
                    "action": "approve",
                    "test_case_id": approved_case["test_case_id"],
                },
            ],
        },
    ).json()
    case_completed = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/complete-review",
        {"expected_version": case_edited["workflow"]["lock_version"]},
    ).json()
    automation_plan_draft = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/approve-and-continue",
        {"expected_version": case_completed["workflow"]["lock_version"]},
    ).json()
    assert automation_plan_draft["workflow"]["stage"] == "automation_plan_review"
    return {
        "project_id": project["id"],
        "requirement_id": requirement["id"],
        "requirement_review_id": review["id"],
        "candidate_id": candidate["id"],
        "test_case_id": approved_case["test_case_id"],
        "automation_plan_workflow": automation_plan_draft,
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


def test_automation_plan_review_workflow_requires_approved_plan_and_consumes_exact_approval(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _artifact_root = api_client
    context = create_automation_plan_review_context(client, SessionLocal)

    workflow_response = client.get(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review",
    )
    assert workflow_response.status_code == 200
    workflow = workflow_response.json()
    assert workflow["workflow"]["state"] == "draft"
    assert workflow["source_case_review_snapshot_id"]
    assert workflow["approved_test_case_ids"] == [context["test_case_id"]]

    plan_response = client.post(
        "/api/automation/plans",
        {
            "project_id": context["project_id"],
            "test_case_id": context["test_case_id"],
            "target_framework": "pytest",
            "use_knowledge": False,
            "context_artifact_ids": [],
            "model_provider": "mock",
            "model_name": "mock-automation-plan",
        },
    )
    assert plan_response.status_code == 202
    plan_body = plan_response.json()

    submitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/submit",
        {"expected_version": workflow["workflow"]["lock_version"]},
    ).json()
    completed = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/complete-review",
        {"expected_version": submitted["workflow"]["lock_version"]},
    ).json()
    blocked = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/approve",
        {"expected_version": completed["workflow"]["lock_version"]},
    )
    assert blocked.status_code == 409
    assert blocked.json()["error_code"] == "AUTOMATION_PLAN_REVIEW_PLAN_APPROVAL_REQUIRED"

    approve_plan = client.post(
        f"/api/automation/plans/{plan_body['id']}/approve",
        {"action": "approve", "review_comment": "Plan is feasible."},
    )
    assert approve_plan.status_code == 200
    edited = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/edit",
        {
            "expected_version": completed["workflow"]["lock_version"],
            "plan_decisions": [{"automation_plan_id": plan_body["id"], "status": "approved"}],
        },
    ).json()
    assert edited["workflow"]["state"] == "waiting_review"
    assert plan_body["id"] in edited["generated_plan_ids"]

    completed_again = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/complete-review",
        {"expected_version": edited["workflow"]["lock_version"]},
    ).json()
    old_approved = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/approve",
        {"expected_version": completed_again["workflow"]["lock_version"]},
    ).json()
    old_approval_id = old_approved["workflow"]["approval_decision_id"]

    revised = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/edit",
        {
            "expected_version": old_approved["workflow"]["lock_version"],
            "plan_decisions": [
                {
                    "automation_plan_id": plan_body["id"],
                    "status": "approved",
                    "review_comment": "Still feasible.",
                },
            ],
        },
    ).json()
    stale = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/continue",
        {
            "expected_version": revised["workflow"]["lock_version"],
            "approval_decision_id": old_approval_id,
        },
    )
    assert stale.status_code == 409

    completed_final = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/complete-review",
        {"expected_version": revised["workflow"]["lock_version"]},
    ).json()
    approved_final = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/approve",
        {"expected_version": completed_final["workflow"]["lock_version"]},
    ).json()
    advanced = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/continue",
        {
            "expected_version": approved_final["workflow"]["lock_version"],
            "approval_decision_id": approved_final["workflow"]["approval_decision_id"],
        },
    )
    assert advanced.status_code == 200
    advanced_body = advanced.json()
    assert advanced_body["workflow"]["stage"] == "automation_draft_review"
    assert advanced_body["workflow"]["state"] == "draft"

    with SessionLocal() as session:
        draft_snapshot = session.get(WorkflowStageSnapshot, uuid.UUID(advanced_body["workflow"]["snapshot_id"]))
        assert draft_snapshot is not None
        source_plan_snapshot = session.get(WorkflowStageSnapshot, draft_snapshot.previous_snapshot_id)
        assert source_plan_snapshot is not None
        payload = draft_snapshot.input_payload_json

    assert payload["source_automation_plan_review_snapshot_id"] == str(source_plan_snapshot.id)
    assert payload["source_automation_plan_review_snapshot_hash"] == source_plan_snapshot.input_snapshot_hash
    assert payload["source_case_review_snapshot_id"]
    assert payload["source_case_review_snapshot_hash"]
    assert payload["approved_automation_plan_ids"] == [plan_body["id"]]
    assert payload["approved_test_case_ids"] == [context["test_case_id"]]


def test_automation_draft_review_workflow_requires_approved_draft_before_execution_approval(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    client, SessionLocal, _artifact_root = api_client
    context = create_automation_plan_review_context(client, SessionLocal)
    workflow = context["automation_plan_workflow"]
    plan_body = client.post(
        "/api/automation/plans",
        {
            "project_id": context["project_id"],
            "test_case_id": context["test_case_id"],
            "target_framework": "pytest",
            "use_knowledge": False,
            "context_artifact_ids": [],
            "model_provider": "mock",
            "model_name": "mock-automation-plan",
        },
    ).json()
    assert client.post(
        f"/api/automation/plans/{plan_body['id']}/approve",
        {"action": "approve", "review_comment": "Plan is feasible."},
    ).status_code == 200
    plan_submitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/submit",
        {"expected_version": workflow["workflow"]["lock_version"]},
    ).json()
    plan_edited = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/edit",
        {
            "expected_version": plan_submitted["workflow"]["lock_version"],
            "plan_decisions": [{"automation_plan_id": plan_body["id"], "status": "approved"}],
        },
    ).json()
    plan_completed = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/complete-review",
        {"expected_version": plan_edited["workflow"]["lock_version"]},
    ).json()
    draft_stage = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/approve-and-continue",
        {"expected_version": plan_completed["workflow"]["lock_version"]},
    ).json()
    assert draft_stage["workflow"]["stage"] == "automation_draft_review"

    draft_body = client.post(
        f"/api/automation/plans/{plan_body['id']}/generate-draft",
        {"model_provider": "mock", "model_name": "mock-automation-draft"},
    ).json()
    draft_workflow = client.get(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review",
    ).json()
    assert draft_workflow["workflow"]["state"] == "draft"
    assert draft_body["automation_draft_id"] in draft_workflow["generated_draft_ids"]

    draft_submitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/submit",
        {"expected_version": draft_workflow["workflow"]["lock_version"]},
    ).json()
    draft_completed = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/complete-review",
        {"expected_version": draft_submitted["workflow"]["lock_version"]},
    ).json()
    blocked = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/approve",
        {"expected_version": draft_completed["workflow"]["lock_version"]},
    )
    assert blocked.status_code == 409
    assert blocked.json()["error_code"] == "AUTOMATION_DRAFT_REVIEW_DRAFT_APPROVAL_REQUIRED"

    assert client.post(
        f"/api/automation/drafts/{draft_body['automation_draft_id']}/approve",
        {"action": "approve", "review_comment": "Draft code is safe to execute."},
    ).status_code == 200
    draft_edited = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/edit",
        {
            "expected_version": draft_completed["workflow"]["lock_version"],
            "draft_decisions": [{"automation_draft_id": draft_body["automation_draft_id"], "status": "approved"}],
        },
    ).json()
    draft_completed_final = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/complete-review",
        {"expected_version": draft_edited["workflow"]["lock_version"]},
    ).json()
    approved_final = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/approve",
        {"expected_version": draft_completed_final["workflow"]["lock_version"]},
    ).json()
    advanced = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/continue",
        {
            "expected_version": approved_final["workflow"]["lock_version"],
            "approval_decision_id": approved_final["workflow"]["approval_decision_id"],
        },
    )
    assert advanced.status_code == 200
    advanced_body = advanced.json()
    assert advanced_body["workflow"]["stage"] == "execution_approval"
    assert advanced_body["workflow"]["state"] == "draft"

    with SessionLocal() as session:
        execution_snapshot = session.get(WorkflowStageSnapshot, uuid.UUID(advanced_body["workflow"]["snapshot_id"]))
        assert execution_snapshot is not None
        source_draft_snapshot = session.get(WorkflowStageSnapshot, execution_snapshot.previous_snapshot_id)
        assert source_draft_snapshot is not None
        payload = execution_snapshot.input_payload_json

    assert payload["source_automation_draft_review_snapshot_id"] == str(source_draft_snapshot.id)
    assert payload["source_automation_draft_review_snapshot_hash"] == source_draft_snapshot.input_snapshot_hash
    assert payload["approved_automation_plan_ids"] == [plan_body["id"]]
    assert payload["approved_automation_draft_ids"] == [draft_body["automation_draft_id"]]


def test_execution_approval_workflow_gates_test_run_and_preserves_draft_snapshot(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, SessionLocal, _artifact_root = api_client
    context = create_automation_plan_review_context(client, SessionLocal)
    workflow = context["automation_plan_workflow"]
    plan_body = client.post(
        "/api/automation/plans",
        {
            "project_id": context["project_id"],
            "test_case_id": context["test_case_id"],
            "target_framework": "pytest",
            "use_knowledge": False,
            "context_artifact_ids": [],
            "model_provider": "mock",
            "model_name": "mock-automation-plan",
        },
    ).json()
    assert client.post(
        f"/api/automation/plans/{plan_body['id']}/approve",
        {"action": "approve", "review_comment": "Plan is feasible."},
    ).status_code == 200
    plan_submitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/submit",
        {"expected_version": workflow["workflow"]["lock_version"]},
    ).json()
    plan_edited = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/edit",
        {
            "expected_version": plan_submitted["workflow"]["lock_version"],
            "plan_decisions": [{"automation_plan_id": plan_body["id"], "status": "approved"}],
        },
    ).json()
    plan_completed = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/complete-review",
        {"expected_version": plan_edited["workflow"]["lock_version"]},
    ).json()
    draft_stage = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-plan-review/approve-and-continue",
        {"expected_version": plan_completed["workflow"]["lock_version"]},
    ).json()
    assert draft_stage["workflow"]["stage"] == "automation_draft_review"

    draft_body = client.post(
        f"/api/automation/plans/{plan_body['id']}/generate-draft",
        {"model_provider": "mock", "model_name": "mock-automation-draft"},
    ).json()
    assert client.post(
        f"/api/automation/drafts/{draft_body['automation_draft_id']}/approve",
        {"action": "approve", "review_comment": "Draft code is safe to execute."},
    ).status_code == 200
    draft_workflow = client.get(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review",
    ).json()
    draft_submitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/submit",
        {"expected_version": draft_workflow["workflow"]["lock_version"]},
    ).json()
    draft_edited = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/edit",
        {
            "expected_version": draft_submitted["workflow"]["lock_version"],
            "draft_decisions": [{"automation_draft_id": draft_body["automation_draft_id"], "status": "approved"}],
        },
    ).json()
    draft_completed = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/complete-review",
        {"expected_version": draft_edited["workflow"]["lock_version"]},
    ).json()
    execution_stage = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/automation-draft-review/approve-and-continue",
        {"expected_version": draft_completed["workflow"]["lock_version"]},
    ).json()
    assert execution_stage["workflow"]["stage"] == "execution_approval"

    blocked_run_response = client.post(
        "/api/test-runs",
        {
            "project_id": context["project_id"],
            "automation_draft_id": draft_body["automation_draft_id"],
            "reason": "AI execution recommendation without human execution approval",
        },
    )
    assert blocked_run_response.status_code == 400
    assert blocked_run_response.json()["error_code"] == "TEST_RUN_INVALID_INPUT"

    execution_workflow = client.get(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval",
    ).json()
    assert execution_workflow["approved_automation_draft_ids"] == [draft_body["automation_draft_id"]]
    assert execution_workflow["source_automation_draft_review_snapshot_id"]
    execution_submitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval/submit",
        {"expected_version": execution_workflow["workflow"]["lock_version"]},
    ).json()
    execution_completed = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval/complete-review",
        {"expected_version": execution_submitted["workflow"]["lock_version"]},
    ).json()
    execution_approved = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval/approve",
        {
            "expected_version": execution_completed["workflow"]["lock_version"],
            "comment": "Approved for controlled local pytest execution.",
        },
    ).json()
    stale_approval_id = execution_approved["workflow"]["approval_decision_id"]
    assert execution_approved["workflow"]["state"] == "approved"
    assert execution_approved["workflow"]["can_execute"] is True

    execution_edited = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval/edit",
        {
            "expected_version": execution_approved["workflow"]["lock_version"],
            "execution_decisions": [
                {
                    "automation_draft_id": draft_body["automation_draft_id"],
                    "status": "approved",
                    "runner_mode": "local_subprocess",
                    "reason": "Human reviewed execution scope.",
                },
            ],
        },
    ).json()
    assert execution_edited["workflow"]["state"] == "draft"
    stale_run_response = client.post(
        "/api/test-runs",
        {
            "project_id": context["project_id"],
            "automation_draft_id": draft_body["automation_draft_id"],
            "execution_approval_decision_id": stale_approval_id,
            "reason": "attempt with stale execution approval",
        },
    )
    assert stale_run_response.status_code == 400
    assert stale_run_response.json()["error_code"] == "TEST_RUN_INVALID_INPUT"

    execution_resubmitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval/submit",
        {"expected_version": execution_edited["workflow"]["lock_version"]},
    ).json()
    execution_recompleted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval/complete-review",
        {"expected_version": execution_resubmitted["workflow"]["lock_version"]},
    ).json()
    execution_reapproved = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval/approve",
        {"expected_version": execution_recompleted["workflow"]["lock_version"]},
    ).json()
    assert execution_reapproved["workflow"]["state"] == "approved"
    assert execution_reapproved["workflow"]["approval_decision_id"]
    assert execution_reapproved["approved_automation_draft_ids"] == [draft_body["automation_draft_id"]]

    with SessionLocal() as session:
        draft = session.get(AutomationDraft, uuid.UUID(draft_body["automation_draft_id"]))
        assert draft is not None
        gate_run, gate_snapshot = execution_service._execution_approval_workflow(
            session,
            uuid.UUID(context["project_id"]),
            uuid.UUID(context["requirement_review_id"]),
        )
        gate_decision = session.get(
            WorkflowHumanDecision,
            uuid.UUID(execution_reapproved["workflow"]["approval_decision_id"]),
        )
        assert gate_run.gate_state == "approved"
        assert gate_run.current_snapshot_id == gate_snapshot.id
        assert str(draft.id) in gate_snapshot.input_payload_json["approved_automation_draft_ids"]
        assert gate_decision is not None
        assert gate_decision.project_id == uuid.UUID(context["project_id"])
        assert gate_decision.workflow_run_id == gate_run.id
        assert gate_decision.snapshot_id == gate_snapshot.id
        assert gate_decision.stage == "execution_approval"
        assert gate_decision.action == "approve"
        assert gate_decision.decision == "approved"
        assert gate_decision.allowed_action == "advance"
        execution_service.validate_automation_draft_approval(draft)
        assert execution_service.automation_draft_quality_gate(draft)["approval_blocking_reasons"] == []
        assert draft.suggested_file_path and not Path(draft.suggested_file_path).is_absolute()

    class SuccessfulPytestRunner:
        def run(self, _command: str, _working_directory: Path, timeout_seconds: int = 600) -> PytestRunnerResult:
            assert timeout_seconds == 600
            return PytestRunnerResult(
                stdout="1 passed in 0.01s",
                stderr="",
                exit_code=0,
                duration_ms=10,
                parsed_result={"total": 1, "passed": 1, "failed": 0, "skipped": 0, "error": 0},
            )

    monkeypatch.setattr(execution_service, "PytestRunner", SuccessfulPytestRunner)
    run_response = client.post(
        "/api/test-runs",
        {
            "project_id": context["project_id"],
            "automation_draft_id": draft_body["automation_draft_id"],
            "execution_approval_decision_id": execution_reapproved["workflow"]["approval_decision_id"],
            "reason": "controlled execution approval",
        },
    )
    assert run_response.status_code == 202
    run_body = run_response.json()
    assert run_body["automation_draft_id"] == draft_body["automation_draft_id"]

    advanced = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-approval/continue",
        {
            "expected_version": execution_reapproved["workflow"]["lock_version"],
            "approval_decision_id": execution_reapproved["workflow"]["approval_decision_id"],
        },
    )
    assert advanced.status_code == 200
    advanced_body = advanced.json()
    assert advanced_body["workflow"]["stage"] == "execution_result_review"

    with SessionLocal() as session:
        result_snapshot = session.get(WorkflowStageSnapshot, uuid.UUID(advanced_body["workflow"]["snapshot_id"]))
        assert result_snapshot is not None
        source_execution_snapshot = session.get(WorkflowStageSnapshot, result_snapshot.previous_snapshot_id)
        assert source_execution_snapshot is not None
        payload = result_snapshot.input_payload_json
        test_run = session.get(TestRun, uuid.UUID(run_body["id"]))

    assert test_run is not None
    assert payload["source_execution_approval_snapshot_id"] == str(source_execution_snapshot.id)
    assert payload["source_execution_approval_snapshot_hash"] == source_execution_snapshot.input_snapshot_hash
    assert payload["source_automation_draft_review_snapshot_id"] == execution_workflow[
        "source_automation_draft_review_snapshot_id"
    ]
    assert payload["source_automation_draft_review_snapshot_hash"] == execution_workflow[
        "source_automation_draft_review_snapshot_hash"
    ]
    assert payload["approved_automation_draft_ids"] == [draft_body["automation_draft_id"]]
    assert run_body["id"] in payload["generated_test_run_ids"]

    result_workflow = client.get(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review",
    ).json()
    assert result_workflow["workflow"]["state"] == "draft"
    assert result_workflow["source_execution_approval_snapshot_id"] == str(source_execution_snapshot.id)
    assert result_workflow["source_execution_approval_snapshot_hash"] == source_execution_snapshot.input_snapshot_hash
    assert result_workflow["generated_test_run_ids"] == [run_body["id"]]
    assert result_workflow["execution_artifact_ids"]

    result_submitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/submit",
        {"expected_version": result_workflow["workflow"]["lock_version"]},
    ).json()
    result_completed = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/complete-review",
        {"expected_version": result_submitted["workflow"]["lock_version"]},
    ).json()
    result_approved = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/approve",
        {"expected_version": result_completed["workflow"]["lock_version"]},
    ).json()
    stale_result_approval_id = result_approved["workflow"]["approval_decision_id"]
    assert result_approved["workflow"]["state"] == "approved"

    result_edited = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/edit",
        {
            "expected_version": result_approved["workflow"]["lock_version"],
            "result_decisions": [
                {
                    "test_run_id": run_body["id"],
                    "status": run_body["status"],
                    "artifact_ids": result_workflow["execution_artifact_ids"],
                    "conclusion": "Execution evidence reviewed by human.",
                },
            ],
        },
    ).json()
    assert result_edited["workflow"]["state"] == "draft"
    stale_continue = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/continue",
        {
            "expected_version": result_edited["workflow"]["lock_version"],
            "approval_decision_id": stale_result_approval_id,
        },
    )
    assert stale_continue.status_code == 409

    result_resubmitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/submit",
        {"expected_version": result_edited["workflow"]["lock_version"]},
    ).json()
    result_recompleted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/complete-review",
        {"expected_version": result_resubmitted["workflow"]["lock_version"]},
    ).json()
    result_reapproved = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/approve",
        {"expected_version": result_recompleted["workflow"]["lock_version"]},
    ).json()
    blocked_failure_analysis = client.post(
        f"/api/test-runs/{run_body['id']}/failure-analysis",
        {"model_provider": "mock", "model_name": "mock-failure-analysis"},
    )
    assert blocked_failure_analysis.status_code == 400
    assert blocked_failure_analysis.json()["error_code"] == "EXECUTION_RESULT_REVIEW_APPROVAL_REQUIRED"

    stale_failure_analysis = client.post(
        f"/api/test-runs/{run_body['id']}/failure-analysis",
        {
            "model_provider": "mock",
            "model_name": "mock-failure-analysis",
            "execution_result_review_decision_id": stale_result_approval_id,
        },
    )
    assert stale_failure_analysis.status_code == 400
    assert stale_failure_analysis.json()["error_code"] == "EXECUTION_RESULT_REVIEW_APPROVAL_REQUIRED"

    allowed_failure_analysis = client.post(
        f"/api/test-runs/{run_body['id']}/failure-analysis",
        {
            "model_provider": "mock",
            "model_name": "mock-failure-analysis",
            "execution_result_review_decision_id": result_reapproved["workflow"]["approval_decision_id"],
        },
    )
    assert allowed_failure_analysis.status_code == 202

    blocked_report = client.post(
        "/api/reports",
        {
            "project_id": context["project_id"],
            "report_type": "automation_execution",
            "related_entity_type": "TestRun",
            "related_entity_id": run_body["id"],
        },
    )
    assert blocked_report.status_code == 400
    assert blocked_report.json()["error_code"] == "EXECUTION_RESULT_REVIEW_APPROVAL_REQUIRED"

    blocked_report_before_stage = client.post(
        "/api/reports",
        {
            "project_id": context["project_id"],
            "report_type": "automation_execution",
            "related_entity_type": "TestRun",
            "related_entity_id": run_body["id"],
            "execution_result_review_decision_id": result_reapproved["workflow"]["approval_decision_id"],
        },
    )
    assert blocked_report_before_stage.status_code == 409
    assert blocked_report_before_stage.json()["error_code"] == "REPORT_REVIEW_WORKFLOW_STAGE_REQUIRED"

    report_stage = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/execution-result-review/continue",
        {
            "expected_version": result_reapproved["workflow"]["lock_version"],
            "approval_decision_id": result_reapproved["workflow"]["approval_decision_id"],
        },
    )
    assert report_stage.status_code == 200
    report_stage_body = report_stage.json()
    assert report_stage_body["workflow"]["stage"] == "report_review"

    with SessionLocal() as session:
        report_snapshot = session.get(WorkflowStageSnapshot, uuid.UUID(report_stage_body["workflow"]["snapshot_id"]))
        assert report_snapshot is not None
        source_result_snapshot = session.get(WorkflowStageSnapshot, report_snapshot.previous_snapshot_id)
        assert source_result_snapshot is not None
        report_payload = report_snapshot.input_payload_json

    assert report_payload["source_execution_result_review_snapshot_id"] == str(source_result_snapshot.id)
    assert report_payload["source_execution_result_review_snapshot_hash"] == source_result_snapshot.input_snapshot_hash
    assert report_payload["source_execution_approval_snapshot_id"] == str(source_execution_snapshot.id)
    assert report_payload["source_execution_approval_snapshot_hash"] == source_execution_snapshot.input_snapshot_hash
    assert report_payload["generated_test_run_ids"] == [run_body["id"]]
    assert set(report_payload["execution_artifact_ids"]) == set(result_workflow["execution_artifact_ids"])

    allowed_report = client.post(
        "/api/reports",
        {
            "project_id": context["project_id"],
            "report_type": "automation_execution",
            "related_entity_type": "TestRun",
            "related_entity_id": run_body["id"],
            "execution_result_review_decision_id": result_reapproved["workflow"]["approval_decision_id"],
        },
    )
    assert allowed_report.status_code == 202
    allowed_report_body = allowed_report.json()
    assert allowed_report_body["status"] == "draft"

    draft_report = client.get(f"/api/reports/{allowed_report_body['report_id']}").json()
    assert draft_report["status"] == "draft"
    assert draft_report["artifact_ids"]

    report_workflow = client.get(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review",
    ).json()
    assert report_workflow["workflow"]["state"] == "draft"
    assert report_workflow["source_execution_result_review_snapshot_id"] == str(source_result_snapshot.id)
    assert report_workflow["source_execution_result_review_snapshot_hash"] == source_result_snapshot.input_snapshot_hash
    assert report_workflow["source_execution_approval_snapshot_id"] == str(source_execution_snapshot.id)
    assert report_workflow["source_execution_approval_snapshot_hash"] == source_execution_snapshot.input_snapshot_hash
    assert report_workflow["generated_test_run_ids"] == [run_body["id"]]
    assert set(report_workflow["execution_artifact_ids"]) == set(result_workflow["execution_artifact_ids"])
    assert report_workflow["generated_report_ids"] == []

    report_submitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/submit",
        {"expected_version": report_workflow["workflow"]["lock_version"]},
    ).json()
    report_completed = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/complete-review",
        {"expected_version": report_submitted["workflow"]["lock_version"]},
    ).json()
    blocked_report_approval = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/approve",
        {"expected_version": report_completed["workflow"]["lock_version"]},
    )
    assert blocked_report_approval.status_code == 409
    assert blocked_report_approval.json()["error_code"] == "REPORT_REVIEW_ARTIFACT_REQUIRED"

    report_edited = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/edit",
        {
            "expected_version": report_completed["workflow"]["lock_version"],
            "report_decisions": [
                {
                    "report_id": allowed_report_body["report_id"],
                    "status": "reviewed_candidate",
                    "artifact_ids": draft_report["artifact_ids"],
                    "conclusion": draft_report["conclusion"],
                },
            ],
        },
    ).json()
    assert report_edited["workflow"]["state"] == "draft"
    assert report_edited["generated_report_ids"] == [allowed_report_body["report_id"]]
    assert set(report_edited["report_artifact_ids"]) == set(draft_report["artifact_ids"])

    report_resubmitted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/submit",
        {"expected_version": report_edited["workflow"]["lock_version"]},
    ).json()
    report_recompleted = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/complete-review",
        {"expected_version": report_resubmitted["workflow"]["lock_version"]},
    ).json()
    report_approved = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/approve",
        {"expected_version": report_recompleted["workflow"]["lock_version"]},
    ).json()
    assert report_approved["workflow"]["state"] == "approved"
    assert report_approved["workflow"]["can_continue"] is True

    published = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/continue",
        {
            "expected_version": report_approved["workflow"]["lock_version"],
            "approval_decision_id": report_approved["workflow"]["approval_decision_id"],
        },
    ).json()
    assert published["workflow"]["published"] is True
    assert published["workflow"]["can_continue"] is False

    ready_report = client.get(f"/api/reports/{allowed_report_body['report_id']}").json()
    assert ready_report["status"] == "ready"

    replay_publish = client.post(
        f"/api/projects/{context['project_id']}/requirement-reviews/{context['requirement_review_id']}/report-review/continue",
        {
            "expected_version": published["workflow"]["lock_version"],
            "approval_decision_id": report_approved["workflow"]["approval_decision_id"],
        },
    )
    assert replay_publish.status_code == 409
    assert replay_publish.json()["error_code"] == "WORKFLOW_APPROVAL_ALREADY_CONSUMED"


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
