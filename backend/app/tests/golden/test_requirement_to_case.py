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
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase as CaseModel
from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.prompt_skill.registry_loader import compute_content_hash
from backend.app.modules.requirements.models import RequirementReview, RiskItem


GOLDEN_REQUIREMENT_CONTENT = (
    "# 优惠券结算规则\n\n"
    "用户在提交订单时，可以选择一张可用优惠券。优惠券不可与积分同时使用。"
    "过期优惠券不可使用。优惠券金额不能超过订单应付金额。"
    "提交订单后，系统需要展示优惠后的最终支付金额。"
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


def candidate_by_title(candidates: list[dict[str, Any]], title: str) -> dict[str, Any]:
    return next(candidate for candidate in candidates if candidate["title"] == title)


def golden_review_plan(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if len(candidates) < 5:
        raise AssertionError("Golden case generation must provide at least five review candidates.")
    edited = candidates[2]
    return {
        candidates[0]["title"]: {"action": "approve", "review_comment": "Primary workflow is complete."},
        candidates[1]["title"]: {"action": "approve", "review_comment": "High-risk path is reviewable."},
        edited["title"]: {
            "action": "approve_after_edit",
            "review_comment": "Add deterministic reviewed input data.",
            "edited_case": {
                "title": edited["title"],
                "priority": edited["priority"],
                "test_type": edited["test_type"],
                "precondition": edited["precondition"],
                "steps": edited["steps"],
                "expected_results": edited["expected_results"],
                "input_data": {"reviewed_fixture": True},
                "tags": ["reviewed", "boundary"],
            },
        },
        candidates[3]["title"]: {
            "action": "needs_optimization",
            "review_comment": "Expected behavior needs clarification.",
        },
        candidates[4]["title"]: {"action": "approve", "review_comment": "Observable result is testable."},
    }


def test_golden_requirement_flows_to_reviewed_test_cases(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    seed_prompt_skill(SessionLocal)

    project_response = client.post("/api/projects", json_body={"name": "Checkout System"})
    assert project_response.status_code == 201
    project = project_response.json()
    module_response = client.post(
        f"/api/projects/{project['id']}/modules",
        json_body={"name": "订单结算", "sort_order": 10},
    )
    assert module_response.status_code == 201
    module = module_response.json()

    requirement_response = client.post(
        "/api/requirements",
        json_body={
            "project_id": project["id"],
            "module_id": module["id"],
            "title": "优惠券结算规则",
            "content": GOLDEN_REQUIREMENT_CONTENT,
            "source_type": "manual",
            "source_ref": "REQ-COUPON-001",
        },
    )
    assert requirement_response.status_code == 201
    requirement = requirement_response.json()

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
    review_response = client.get(f"/api/requirements/{requirement['id']}/review")
    assert review_response.status_code == 200
    review = review_response.json()
    assert review["overall_score"] == 82
    assert review["scores"].keys() >= {"completeness", "clarity", "consistency", "testability", "feasibility", "logic"}
    assert len(review["risk_items"]) >= 2

    generation_response = client.post(
        "/api/case-generation/tasks",
        json_body={
            "project_id": project["id"],
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
    assert generation_response.status_code == 202
    generation = generation_response.json()

    candidates_response = client.get(f"/api/case-generation/tasks/{generation['case_generation_task_id']}/candidates")
    assert candidates_response.status_code == 200
    candidates_body = candidates_response.json()
    candidates = candidates_body["items"]
    assert candidates_body["total"] >= 5
    for candidate in candidates:
        assert candidate["steps"]
        assert candidate["expected_results"]
        assert candidate["requirement_refs"]
        assert candidate["ai_reason"]

    review_plan = golden_review_plan(candidates)

    review_results = []
    for title, payload in review_plan.items():
        candidate = candidate_by_title(candidates, title)
        response = client.post(f"/api/case-review/items/{candidate['id']}/approve", json_body=payload)
        assert response.status_code == 200
        review_results.append(response.json())

    with SessionLocal() as session:
        persisted_review = session.scalar(select(RequirementReview).where(RequirementReview.id == uuid.UUID(review["id"])))
        assert persisted_review is not None
        assert persisted_review.overall_score == 82
        assert all(
            score > 0
            for score in (
                persisted_review.completeness_score,
                persisted_review.clarity_score,
                persisted_review.consistency_score,
                persisted_review.testability_score,
                persisted_review.feasibility_score,
                persisted_review.logic_score,
            )
        )
        assert len(list(session.scalars(select(RiskItem).where(RiskItem.requirement_review_id == persisted_review.id)))) >= 2

        generation_task = session.get(CaseGenerationTask, uuid.UUID(generation["case_generation_task_id"]))
        assert generation_task is not None
        assert generation_task.generated_count >= 5
        persisted_candidates = list(
            session.scalars(
                select(GeneratedCaseCandidate).where(GeneratedCaseCandidate.generation_task_id == generation_task.id),
            ),
        )
        assert len(persisted_candidates) >= 5
        test_cases = list(session.scalars(select(CaseModel)))
        assert len(test_cases) == 4

        approved_count = sum(1 for candidate in persisted_candidates if candidate.status == "approved")
        edited_count = sum(1 for candidate in persisted_candidates if candidate.status == "approved_after_edit")
        optimization_count = sum(1 for candidate in persisted_candidates if candidate.status == "needs_optimization")
        reviewed_count = approved_count + edited_count + optimization_count
        acceptance_rate = (approved_count + edited_count) / generation_task.generated_count

        assert approved_count == 3
        assert edited_count == 1
        assert optimization_count == 1
        assert reviewed_count >= 4
        assert acceptance_rate >= 0.8

        edited_case = next(test_case for test_case in test_cases if test_case.review_status == "approved_after_edit")
        assert edited_case.input_data_json == {"reviewed_fixture": True}
        assert edited_case.steps_json

    statuses = {result["status"] for result in review_results}
    assert statuses == {"approved", "approved_after_edit", "needs_optimization"}
