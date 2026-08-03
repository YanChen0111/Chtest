from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase as CaseRecord
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.models import Environment, Project, Workspace
from backend.app.modules.projects.router import get_session
from backend.app.modules.reporting.models import Report
from backend.app.modules.requirements.models import Requirement, RiskItem
from backend.app.modules.test_campaigns.models import TestCampaign
from backend.app.modules.workflow_control.models import (
    WorkflowHumanDecision,
    WorkflowStageSnapshot,
    WorkflowTransitionEvent,
)
from backend.app.modules.workflow_control.policy import ApprovalDecision, ControlledStage, WorkflowKind
from backend.app.modules.workflow_control.schemas import HumanApprovalCreate, HumanReviewCreate, WorkflowRunCreate
from backend.app.modules.workflow_control.service import (
    complete_human_review,
    create_workflow_run,
    record_human_approval,
    submit_for_review,
)


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
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
        await app(scope, receive, send)
        assert status_code is not None
        return ASGIResponse(status_code, b"".join(body_chunks))


@pytest.fixture()
def api_client() -> Iterator[tuple[ASGIClient, sessionmaker[Session]]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)

    def override_get_session() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield ASGIClient(), SessionLocal
    app.dependency_overrides.clear()


def _seed_scope_evidence(
    SessionLocal: sessionmaker[Session],
    *,
    approve_plan: bool = True,
) -> dict[str, uuid.UUID]:
    with SessionLocal() as session:
        workspace = Workspace(name="Personal Workspace")
        project = Project(workspace=workspace, name="Checkout")
        other_project = Project(workspace=workspace, name="Billing")
        environment = Environment(project=project, name="staging")
        other_environment = Environment(project=other_project, name="staging")
        requirement = Requirement(
            id=uuid.uuid4(),
            project=project,
            title="Checkout succeeds",
            content="Approved payment completes.",
        )
        risk = RiskItem(
            id=uuid.uuid4(),
            project=project,
            title="Duplicate charge",
            risk_level="high",
            impact="Customer may be charged twice.",
            suggestion="Cover idempotent retry.",
        )
        ai_task = AITask(
            project=project,
            agent_name="CaseGenerationAgent",
            task_type="case_generation",
            prompt_version_id=uuid.uuid4(),
            skill_version_id=uuid.uuid4(),
        )
        generation_task = CaseGenerationTask(
            project=project,
            requirement=requirement,
            ai_task=ai_task,
            target_test_types=["functional"],
        )
        candidate = GeneratedCaseCandidate(
            generation_task=generation_task,
            project=project,
            title="Retry payment safely",
            steps_json=[{"index": 1, "action": "Retry the same payment."}],
            expected_results_json=[{"index": 1, "expected": "Only one charge exists."}],
            covered_requirement_ids_json=[str(requirement.id)],
            covered_risk_ids_json=[str(risk.id)],
            coverage_dimensions_json=[{"key": "business_rule", "claim_ids": ["claim-1"]}],
            generation_reason="Covers the approved retry rule.",
            automation_readiness_json={"status": "ready"},
            quality_assessment_json={"status": "passed"},
            ai_reason="Evidence-backed candidate.",
            status="approved",
        )
        test_case = CaseRecord(
            project=project,
            source_candidate=candidate,
            title=candidate.title,
            steps_json=candidate.steps_json,
            expected_results_json=candidate.expected_results_json,
            review_status="approved",
            status="active",
        )
        session.add_all([project, other_project, environment, other_environment, risk, test_case])
        session.commit()

        plan_run = create_workflow_run(
            session,
            WorkflowRunCreate(
                project_id=project.id,
                workflow_kind=WorkflowKind.REQUIREMENT_TO_EXECUTION,
                subject_ref=f"plan-{uuid.uuid4()}",
                initial_stage=ControlledStage.TEST_PLAN_REVIEW,
                input_payload={
                    "test_strategy": "Prioritize payment idempotency.",
                    "plan_items": [{"risk_id": str(risk.id), "included": True}],
                },
                created_by="Planner",
            ),
        )
        plan_snapshot_id = plan_run.current_snapshot_id
        if approve_plan:
            plan_run = submit_for_review(session, project.id, plan_run.id, expected_version=0)
            plan_run, _ = complete_human_review(
                session,
                project.id,
                plan_run.id,
                expected_version=plan_run.lock_version,
                data=HumanReviewCreate(reviewer="Lead Tester"),
            )
            record_human_approval(
                session,
                project.id,
                plan_run.id,
                expected_version=plan_run.lock_version,
                data=HumanApprovalCreate(reviewer="Lead Tester", decision=ApprovalDecision.APPROVED),
            )
        return {
            "project_id": project.id,
            "other_project_id": other_project.id,
            "environment_id": environment.id,
            "other_environment_id": other_environment.id,
            "requirement_id": requirement.id,
            "risk_id": risk.id,
            "test_case_id": test_case.id,
            "plan_snapshot_id": plan_snapshot_id,
        }


def _campaign_payload(ids: dict[str, uuid.UUID]) -> dict[str, Any]:
    return {
        "name": "Checkout release 2026.08",
        "scope_statement": "Validate checkout payment and retry behavior.",
        "target_environment_id": str(ids["environment_id"]),
        "target_version_ref": "release/2026.08",
        "exit_conditions": ["No open critical defects", "All selected high risks have approved cases"],
        "requirement_ids": [str(ids["requirement_id"])],
        "risk_ids": [str(ids["risk_id"])],
        "test_plan_snapshot_ids": [str(ids["plan_snapshot_id"])],
        "approved_case_ids": [str(ids["test_case_id"])],
        "created_by": "Lead Tester",
    }


def _post_ok(client: ASGIClient, path: str, body: dict[str, Any]) -> dict[str, Any]:
    response = client.post(path, body)
    assert response.status_code in {200, 201}, response.json()
    return response.json()


def test_campaign_scope_uses_real_evidence_and_exact_approval(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    ids = _seed_scope_evidence(SessionLocal)
    base = f"/api/projects/{ids['project_id']}/test-campaigns"
    campaign = _post_ok(client, base, _campaign_payload(ids))

    assert campaign["workflow"]["stage"] == "scope"
    assert campaign["workflow"]["state"] == "draft"
    assert [row["kind"] for row in campaign["coverage_rows"]] == [
        "requirement",
        "risk",
        "test_plan",
        "approved_case",
    ]
    assert {row["coverage_status"] for row in campaign["coverage_rows"]} == {"covered"}
    assert campaign["coverage_rows"][0]["evidence_case_ids"] == [str(ids["test_case_id"])]

    path = f"{base}/{campaign['id']}"
    submitted = _post_ok(
        client,
        f"{path}/submit",
        {"expected_version": campaign["workflow"]["lock_version"]},
    )
    reviewed = _post_ok(
        client,
        f"{path}/complete-review",
        {"expected_version": submitted["workflow"]["lock_version"], "reviewer": "Lead Tester"},
    )
    approved = _post_ok(
        client,
        f"{path}/approve",
        {"expected_version": reviewed["workflow"]["lock_version"], "reviewer": "Lead Tester"},
    )
    approval_id = approved["workflow"]["approval_decision_id"]
    assert approved["workflow"]["can_continue"] is True
    continued = _post_ok(
        client,
        f"{path}/continue",
        {
            "expected_version": approved["workflow"]["lock_version"],
            "approval_decision_id": approval_id,
        },
    )
    assert continued["workflow"]["stage"] == "requirement_review"
    assert continued["workflow"]["state"] == "draft"
    assert continued["workflow"]["can_continue"] is False

    replay = client.post(
        f"{path}/continue",
        {
            "expected_version": continued["workflow"]["lock_version"],
            "approval_decision_id": approval_id,
        },
    )
    assert replay.status_code == 409
    assert replay.json()["error_code"] == "WORKFLOW_STAGE_MISMATCH"

    with SessionLocal() as session:
        campaign_row = session.scalar(select(TestCampaign))
        scope_snapshot = session.scalar(
            select(WorkflowStageSnapshot).where(
                WorkflowStageSnapshot.id == uuid.UUID(campaign["workflow"]["snapshot_id"]),
            ),
        )
        consumed_count = session.scalar(
            select(func.count(WorkflowTransitionEvent.id)).where(
                WorkflowTransitionEvent.consumed_approval_decision_id == uuid.UUID(approval_id),
            ),
        )
        assert campaign_row is not None
        assert scope_snapshot is not None
        assert scope_snapshot.input_payload_json["coverage_rows"] == campaign["coverage_rows"]
        assert consumed_count == 1
        assert session.scalar(select(func.count(TestRun.id))) == 0
        assert session.scalar(select(func.count(Report.id))) == 0


def test_campaign_edit_recomputes_gaps_and_invalidates_old_approval(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    ids = _seed_scope_evidence(SessionLocal, approve_plan=False)
    payload = _campaign_payload(ids)
    payload["approved_case_ids"] = []
    base = f"/api/projects/{ids['project_id']}/test-campaigns"
    campaign = _post_ok(client, base, payload)
    assert [row["coverage_status"] for row in campaign["coverage_rows"]] == ["gap", "gap", "gap"]

    path = f"{base}/{campaign['id']}"
    submitted = _post_ok(client, f"{path}/submit", {"expected_version": 0})
    reviewed = _post_ok(
        client,
        f"{path}/complete-review",
        {"expected_version": submitted["workflow"]["lock_version"], "reviewer": "Reviewer"},
    )
    approved = _post_ok(
        client,
        f"{path}/approve",
        {"expected_version": reviewed["workflow"]["lock_version"], "reviewer": "Reviewer"},
    )
    old_approval_id = approved["workflow"]["approval_decision_id"]

    edit_payload = dict(payload)
    edit_payload.pop("created_by")
    edit_payload.update(
        {
            "expected_version": approved["workflow"]["lock_version"],
            "reviewer": "Reviewer",
            "comment": "Tighten the release exit condition.",
            "exit_conditions": ["All selected risks have approved case evidence"],
        },
    )
    edited = _post_ok(client, f"{path}/edit", edit_payload)
    assert edited["workflow"]["state"] == "draft"
    assert edited["workflow"]["snapshot_iteration"] == 2
    assert edited["workflow"]["approval_decision_id"] is None
    assert edited["workflow"]["snapshot_id"] != campaign["workflow"]["snapshot_id"]

    stale = client.post(
        f"{path}/continue",
        {
            "expected_version": edited["workflow"]["lock_version"],
            "approval_decision_id": old_approval_id,
        },
    )
    assert stale.status_code == 409
    assert stale.json()["error_code"] == "WORKFLOW_APPROVAL_STALE"

    cross_project = client.post(
        f"/api/projects/{ids['other_project_id']}/test-campaigns",
        _campaign_payload(ids),
    )
    assert cross_project.status_code == 404
    assert cross_project.json()["error_code"] == "TEST_CAMPAIGN_ENVIRONMENT_NOT_FOUND"

    with SessionLocal() as session:
        decisions = list(
            session.scalars(
                select(WorkflowHumanDecision).where(
                    WorkflowHumanDecision.id == uuid.UUID(old_approval_id),
                ),
            ),
        )
        snapshots = list(
            session.scalars(
                select(WorkflowStageSnapshot).where(
                    WorkflowStageSnapshot.workflow_run_id == uuid.UUID(edited["workflow"]["run_id"]),
                    WorkflowStageSnapshot.stage == "scope",
                ),
            ),
        )
        assert len(decisions) == 1
        assert len(snapshots) == 2
