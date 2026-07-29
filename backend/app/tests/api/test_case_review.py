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
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.cases.models import GeneratedCaseCandidate, TestCase as CaseModel
from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.prompt_skill.registry_loader import compute_content_hash
from backend.app.modules.review_history.models import ReviewHistory
from backend.app.modules.workflow_control.models import WorkflowStageSnapshot


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
            ],
        )
        session.commit()


def create_candidate(client: ASGIClient, SessionLocal: sessionmaker[Session]) -> dict[str, Any]:
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
    generation = client.post(
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
    ).json()
    candidates = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates").json()
    return candidates["items"][0]


def test_approve_candidate_creates_test_case(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    candidate = create_candidate(client, SessionLocal)

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "approve", "review_comment": "Looks good."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_id"] == candidate["id"]
    assert body["status"] == "approved"
    assert body["test_case_id"]

    with SessionLocal() as session:
        refreshed_candidate = session.get(GeneratedCaseCandidate, uuid.UUID(candidate["id"]))
        test_case = session.get(CaseModel, uuid.UUID(body["test_case_id"]))
        assert refreshed_candidate is not None
        assert test_case is not None
        assert refreshed_candidate.status == "approved"
        assert refreshed_candidate.review_comment == "Looks good."
        assert test_case.source_candidate_id == refreshed_candidate.id
        assert test_case.title == refreshed_candidate.title
        assert test_case.review_status == "approved"
        history = session.scalar(select(ReviewHistory).where(ReviewHistory.entity_id == refreshed_candidate.id))
        assert history is not None
        assert history.project_id == refreshed_candidate.project_id
        assert history.entity_type == "GeneratedCaseCandidate"
        assert history.action == "approve"
        assert history.from_status == "generated"
        assert history.to_status == "approved"
        assert history.reviewer == "Default User"
        assert history.comment == "Looks good."


def test_approve_after_edit_creates_test_case_from_edited_case(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    candidate = create_candidate(client, SessionLocal)

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={
            "action": "approve_after_edit",
            "edited_case": {
                "title": "Expired coupon cannot submit order",
                "priority": "P0",
                "test_type": "functional",
                "precondition": "User has an expired coupon.",
                "steps": ["Prepare expired coupon", "Open checkout", "Select expired coupon", "Submit order"],
                "expected_results": ["Submit is blocked", "Expired coupon message is shown"],
                "input_data": {"coupon_state": "expired"},
                "tags": ["coupon", "regression"],
            },
            "review_comment": "Added test data preparation.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved_after_edit"

    with SessionLocal() as session:
        test_case = session.get(CaseModel, uuid.UUID(body["test_case_id"]))
        assert test_case is not None
        assert test_case.title == "Expired coupon cannot submit order"
        assert test_case.steps_json[0] == "Prepare expired coupon"
        assert test_case.input_data_json == {"coupon_state": "expired"}
        assert test_case.tags == ["coupon", "regression"]
        assert test_case.review_status == "approved_after_edit"


def test_reject_candidate_does_not_create_test_case(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    candidate = create_candidate(client, SessionLocal)

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "reject", "review_comment": "Too vague."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["test_case_id"] is None

    with SessionLocal() as session:
        refreshed_candidate = session.get(GeneratedCaseCandidate, uuid.UUID(candidate["id"]))
        assert refreshed_candidate is not None
        assert refreshed_candidate.status == "rejected"
        assert refreshed_candidate.review_comment == "Too vague."
        assert list(session.scalars(select(CaseModel))) == []
        history = session.scalar(select(ReviewHistory).where(ReviewHistory.entity_id == refreshed_candidate.id))
        assert history is not None
        assert history.action == "reject"
        assert history.from_status == "generated"
        assert history.to_status == "rejected"
        assert history.comment == "Too vague."


def test_needs_optimization_marks_candidate_without_creating_test_case(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    candidate = create_candidate(client, SessionLocal)

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "needs_optimization", "review_comment": "Need better boundary coverage."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_optimization"
    assert body["test_case_id"] is None

    with SessionLocal() as session:
        refreshed_candidate = session.get(GeneratedCaseCandidate, uuid.UUID(candidate["id"]))
        assert refreshed_candidate is not None
        assert refreshed_candidate.status == "needs_optimization"
        assert list(session.scalars(select(CaseModel))) == []


def test_final_candidate_status_cannot_be_reviewed_again(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, _ = api_client
    candidate = create_candidate(client, _)
    first = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "reject", "review_comment": "No."},
    )
    assert first.status_code == 200

    response = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "approve"},
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "CASE_CANDIDATE_ALREADY_FINAL"


def test_case_review_workflow_requires_existing_candidate_review_and_consumes_exact_approval(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
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
    assert client.post(
        f"/api/requirements/{requirement['id']}/review",
        json_body={
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
        json_body={"expected_version": review["workflow"]["lock_version"]},
    ).json()
    risk_draft = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/approve-and-continue",
        json_body={"expected_version": requirement_completed["workflow"]["lock_version"]},
    ).json()
    risk_submitted = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/risk-review/submit",
        json_body={"expected_version": risk_draft["workflow"]["lock_version"]},
    ).json()
    risk_completed = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/risk-review/complete-review",
        json_body={"expected_version": risk_submitted["workflow"]["lock_version"]},
    ).json()
    test_plan_draft = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/risk-review/approve-and-continue",
        json_body={"expected_version": risk_completed["workflow"]["lock_version"]},
    ).json()
    test_plan_submitted = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/test-plan-review/submit",
        json_body={"expected_version": test_plan_draft["workflow"]["lock_version"]},
    ).json()
    strategy = "Cover high-risk coupon validation before generating formal cases."
    test_plan_edited = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/test-plan-review/edit",
        json_body={
            "expected_version": test_plan_submitted["workflow"]["lock_version"],
            "test_strategy": strategy,
            "plan_items": [{"risk_title": "Coupon validation", "risk_level": "high", "strategy": strategy}],
        },
    ).json()
    test_plan_completed = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/test-plan-review/complete-review",
        json_body={"expected_version": test_plan_edited["workflow"]["lock_version"]},
    ).json()
    case_review_draft = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/test-plan-review/approve-and-continue",
        json_body={"expected_version": test_plan_completed["workflow"]["lock_version"]},
    ).json()
    assert case_review_draft["workflow"]["stage"] == "case_review"
    assert case_review_draft["workflow"]["state"] == "draft"

    generation = client.post(
        "/api/case-generation/tasks",
        json_body={
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
    candidates = client.get(
        f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates",
    ).json()["items"]
    candidate = candidates[0]

    case_review = client.get(f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review")
    assert case_review.status_code == 200
    assert case_review.json()["workflow"]["state"] == "draft"
    assert client.get(f"/api/projects/{uuid.uuid4()}/requirement-reviews/{review['id']}/case-review").status_code == 404

    submitted = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/submit",
        json_body={"expected_version": case_review.json()["workflow"]["lock_version"]},
    ).json()
    completed = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/complete-review",
        json_body={"expected_version": submitted["workflow"]["lock_version"]},
    ).json()
    blocked = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/approve",
        json_body={"expected_version": completed["workflow"]["lock_version"]},
    )
    assert blocked.status_code == 409
    assert blocked.json()["error_code"] == "CASE_REVIEW_CANDIDATE_APPROVAL_REQUIRED"

    approved_case = client.post(
        f"/api/case-review/items/{candidate['id']}/approve",
        json_body={"action": "approve", "review_comment": "Promote this candidate."},
    ).json()
    for rejected_candidate in candidates[1:]:
        rejected = client.post(
            f"/api/case-review/items/{rejected_candidate['id']}/approve",
            json_body={"action": "reject", "review_comment": "Outside this review scope."},
        )
        assert rejected.status_code == 200
    edited_response = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/edit",
        json_body={
            "expected_version": completed["workflow"]["lock_version"],
            "candidate_decisions": [{"candidate_id": candidate["id"], "action": "approve"}],
        },
    )
    assert edited_response.status_code == 200, edited_response.json()
    edited = edited_response.json()
    assert edited["workflow"]["state"] == "waiting_review"
    assert edited["workflow"]["approval_decision_id"] is None
    assert candidate["id"] in edited["generated_candidate_ids"]

    completed_again = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/complete-review",
        json_body={"expected_version": edited["workflow"]["lock_version"]},
    ).json()
    old_approved = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/approve",
        json_body={"expected_version": completed_again["workflow"]["lock_version"]},
    ).json()
    old_approval_id = old_approved["workflow"]["approval_decision_id"]
    revised = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/edit",
        json_body={
            "expected_version": old_approved["workflow"]["lock_version"],
            "candidate_decisions": [
                {
                    "candidate_id": candidate["id"],
                    "action": "approve",
                    "test_case_id": approved_case["test_case_id"],
                },
            ],
        },
    ).json()
    stale = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/continue",
        json_body={
            "expected_version": revised["workflow"]["lock_version"],
            "approval_decision_id": old_approval_id,
        },
    )
    assert stale.status_code == 409

    completed_final = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/complete-review",
        json_body={"expected_version": revised["workflow"]["lock_version"]},
    ).json()
    approved_final = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/approve",
        json_body={"expected_version": completed_final["workflow"]["lock_version"]},
    ).json()
    advanced = client.post(
        f"/api/projects/{project['id']}/requirement-reviews/{review['id']}/case-review/continue",
        json_body={
            "expected_version": approved_final["workflow"]["lock_version"],
            "approval_decision_id": approved_final["workflow"]["approval_decision_id"],
        },
    )
    assert advanced.status_code == 200
    advanced_body = advanced.json()
    assert advanced_body["workflow"]["stage"] == "automation_plan_review"
    assert advanced_body["workflow"]["state"] == "draft"

    with SessionLocal() as session:
        automation_snapshot = session.get(WorkflowStageSnapshot, uuid.UUID(advanced_body["workflow"]["snapshot_id"]))
        assert automation_snapshot is not None
        source_case_snapshot = session.get(WorkflowStageSnapshot, automation_snapshot.previous_snapshot_id)
        assert source_case_snapshot is not None
        assert automation_snapshot.input_payload_json["source_case_review_snapshot_id"] == str(source_case_snapshot.id)
        assert automation_snapshot.input_payload_json["source_case_review_snapshot_hash"] == source_case_snapshot.input_snapshot_hash
        assert automation_snapshot.input_payload_json["source_test_plan_review_snapshot_id"]
        assert automation_snapshot.input_payload_json["approved_candidate_ids"] == [candidate["id"]]
        assert automation_snapshot.input_payload_json["approved_test_case_ids"] == [approved_case["test_case_id"]]
