from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.projects.models import Environment, Project, Workspace
from backend.app.modules.projects.router import get_session
from backend.app.modules.requirements.models import Requirement, RequirementReview
from backend.app.modules.test_campaigns.models import TestCampaign
from backend.app.modules.workflow_control.models import (
    WorkflowHumanDecision,
    WorkflowRun,
    WorkflowStageSnapshot,
    WorkflowTransitionEvent,
)
from backend.app.modules.workflow_control.policy import (
    Actor,
    ApprovalDecision,
    ControlledStage,
    GateState,
    TransitionAction,
    WorkflowKind,
)
from backend.app.modules.workflow_control.schemas import (
    HumanApprovalCreate,
    HumanReviewCreate,
    WorkflowRunCreate,
)
from backend.app.modules.workflow_control.service import (
    create_workflow_run,
    complete_human_review,
    list_workflow_queue,
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
        return asyncio.run(self._get(path))

    async def _get(self, path: str) -> ASGIResponse:
        status_code: int | None = None
        body_chunks: list[bytes] = []
        request_complete = False

        async def receive() -> dict[str, Any]:
            nonlocal request_complete
            if not request_complete:
                request_complete = True
                return {"type": "http.request", "body": b"", "more_body": False}
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
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": b"",
            "headers": [(b"host", b"testserver")],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }
        await app(scope, receive, send)
        assert status_code is not None
        return ASGIResponse(status_code, b"".join(body_chunks))


def _session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def _projects(session: Session) -> tuple[Project, Project]:
    workspace = Workspace(name="Personal Workspace")
    project = Project(workspace=workspace, name="Checkout")
    other_project = Project(workspace=workspace, name="Billing")
    session.add_all([project, other_project])
    session.commit()
    return project, other_project


def _create_run(
    session: Session,
    project: Project,
    *,
    subject_ref: str,
    stage: ControlledStage = ControlledStage.REQUIREMENT_REVIEW,
):
    return create_workflow_run(
        session,
        WorkflowRunCreate(
            project_id=project.id,
            workflow_kind=WorkflowKind.REQUIREMENT_TO_EXECUTION,
            subject_ref=subject_ref,
            initial_stage=stage,
            input_payload={"subject_ref": subject_ref},
            created_by="queue-test",
        ),
    )


def _campaign(session: Session, project: Project, *, status: str = "active") -> TestCampaign:
    environment = Environment(project_id=project.id, name=f"env-{uuid.uuid4()}", variables_json={})
    session.add(environment)
    session.flush()
    campaign = TestCampaign(
        project_id=project.id,
        name="Queue campaign",
        scope_statement="Restore this exact campaign.",
        target_environment_id=environment.id,
        target_version_ref="release/2026.08",
        exit_conditions_json=["No open critical defects"],
        requirement_ids_json=[],
        risk_ids_json=[],
        test_plan_snapshot_ids_json=[],
        approved_case_ids_json=[],
        coverage_rows_json=[],
        status=status,
    )
    session.add(campaign)
    session.flush()
    return campaign


def _requirement_review(
    session: Session,
    project: Project,
    *,
    requirement_status: str = "active",
) -> tuple[Requirement, RequirementReview]:
    task = AITask(
        project_id=project.id,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
        model_provider="mock",
        model_name="mock-requirement-review",
        status="succeeded",
        input_json={},
        output_json={},
        token_usage_json={},
        context_artifact_ids=[],
    )
    requirement = Requirement(
        project_id=project.id,
        title="Queue requirement",
        content="Restore this exact requirement review.",
        source_type="manual",
        source_ref="REQ-QUEUE-1",
        status=requirement_status,
    )
    review = RequirementReview(
        requirement=requirement,
        ai_task=task,
        overall_score=80,
        issues_json=[],
        clarification_questions_json=[],
        test_design_notes_json=[],
        status="reviewed",
    )
    session.add_all([task, requirement, review])
    session.flush()
    return requirement, review


def test_workflow_queue_routes_only_exact_same_project_scope_campaign() -> None:
    with _session() as session:
        project, other_project = _projects(session)
        campaign = _campaign(session, project)
        other_campaign = _campaign(session, other_project)
        inactive_campaign = _campaign(session, project, status="archived")

        valid = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(campaign.id), stage=ControlledStage.SCOPE).id,
            expected_version=0,
        )
        cross_project = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(other_campaign.id), stage=ControlledStage.SCOPE).id,
            expected_version=0,
        )
        inactive = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(inactive_campaign.id), stage=ControlledStage.SCOPE).id,
            expected_version=0,
        )
        missing = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(uuid.uuid4()), stage=ControlledStage.SCOPE).id,
            expected_version=0,
        )
        malformed = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref="not-a-campaign-id", stage=ControlledStage.SCOPE).id,
            expected_version=0,
        )
        wrong_stage = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(campaign.id)).id,
            expected_version=0,
        )

        by_id = {item["id"]: item for item in list_workflow_queue(session, project.id)}
        campaign_id = campaign.id
        valid_id = valid.id
        cross_project_id = cross_project.id
        inactive_id = inactive.id
        missing_id = missing.id
        malformed_id = malformed.id
        wrong_stage_id = wrong_stage.id

    assert by_id[valid_id]["route_path"] == f"/campaigns/scope?campaign_id={campaign_id}"
    assert by_id[cross_project_id]["route_path"] is None
    assert by_id[inactive_id]["route_path"] is None
    assert by_id[missing_id]["route_path"] is None
    assert by_id[malformed_id]["route_path"] is None
    assert by_id[wrong_stage_id]["route_path"] is None


def test_workflow_queue_routes_only_exact_same_project_requirement_review() -> None:
    with _session() as session:
        project, other_project = _projects(session)
        requirement, review = _requirement_review(session, project)
        _, other_review = _requirement_review(session, other_project)
        _, inactive_review = _requirement_review(session, project, requirement_status="archived")

        valid = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(review.id)).id,
            expected_version=0,
        )
        cross_project = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(other_review.id)).id,
            expected_version=0,
        )
        inactive = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(inactive_review.id)).id,
            expected_version=0,
        )
        missing = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref=str(uuid.uuid4())).id,
            expected_version=0,
        )
        malformed = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref="not-a-review-id").id,
            expected_version=0,
        )
        wrong_stage = submit_for_review(
            session,
            project.id,
            _create_run(
                session,
                project,
                subject_ref=str(review.id),
                stage=ControlledStage.RISK_REVIEW,
            ).id,
            expected_version=0,
        )

        by_id = {item["id"]: item for item in list_workflow_queue(session, project.id)}
        expected_route = (
            f"/requirements/review?requirement_id={requirement.id}"
            f"&requirement_review_id={review.id}&workflow_run_id={valid.id}"
        )
        valid_id = valid.id
        cross_project_id = cross_project.id
        inactive_id = inactive.id
        missing_id = missing.id
        malformed_id = malformed.id
        wrong_stage_id = wrong_stage.id

    assert by_id[valid_id]["route_path"] == expected_route
    assert by_id[cross_project_id]["route_path"] is None
    assert by_id[inactive_id]["route_path"] is None
    assert by_id[missing_id]["route_path"] is None
    assert by_id[malformed_id]["route_path"] is None
    assert by_id[wrong_stage_id]["route_path"] is None


def test_workflow_queue_groups_only_actionable_project_runs() -> None:
    with _session() as session:
        project, other_project = _projects(session)
        waiting_review = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref="waiting-review").id,
            expected_version=0,
        )
        waiting_approval = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref="waiting-approval").id,
            expected_version=0,
        )
        waiting_approval, _ = complete_human_review(
            session,
            project.id,
            waiting_approval.id,
            expected_version=waiting_approval.lock_version,
            data=HumanReviewCreate(reviewer="tester"),
        )
        continuable = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref="continuable").id,
            expected_version=0,
        )
        continuable, _ = complete_human_review(
            session,
            project.id,
            continuable.id,
            expected_version=continuable.lock_version,
            data=HumanReviewCreate(reviewer="tester"),
        )
        continuable, approval = record_human_approval(
            session,
            project.id,
            continuable.id,
            expected_version=continuable.lock_version,
            data=HumanApprovalCreate(reviewer="tester", decision=ApprovalDecision.APPROVED),
        )
        stale = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref="stale-approval").id,
            expected_version=0,
        )
        stale, _ = complete_human_review(
            session,
            project.id,
            stale.id,
            expected_version=stale.lock_version,
            data=HumanReviewCreate(reviewer="tester"),
        )
        stale, _ = record_human_approval(
            session,
            project.id,
            stale.id,
            expected_version=stale.lock_version,
            data=HumanApprovalCreate(reviewer="tester", decision=ApprovalDecision.APPROVED),
        )
        stale.lock_version += 1
        session.add(stale)
        rejected = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref="rejected").id,
            expected_version=0,
        )
        rejected, _ = complete_human_review(
            session,
            project.id,
            rejected.id,
            expected_version=rejected.lock_version,
            data=HumanReviewCreate(reviewer="tester"),
        )
        record_human_approval(
            session,
            project.id,
            rejected.id,
            expected_version=rejected.lock_version,
            data=HumanApprovalCreate(reviewer="tester", decision=ApprovalDecision.REJECTED),
        )
        inactive = submit_for_review(
            session,
            project.id,
            _create_run(session, project, subject_ref="inactive").id,
            expected_version=0,
        )
        inactive.status = "completed"
        session.add(inactive)
        other_waiting = submit_for_review(
            session,
            other_project.id,
            _create_run(session, other_project, subject_ref="other-project").id,
            expected_version=0,
        )
        other_waiting_id = other_waiting.id
        consumed_terminal = submit_for_review(
            session,
            project.id,
            _create_run(
                session,
                project,
                subject_ref="consumed-terminal",
                stage=ControlledStage.REPORT_REVIEW,
            ).id,
            expected_version=0,
        )
        consumed_terminal, _ = complete_human_review(
            session,
            project.id,
            consumed_terminal.id,
            expected_version=consumed_terminal.lock_version,
            data=HumanReviewCreate(reviewer="tester"),
        )
        consumed_terminal, consumed_approval = record_human_approval(
            session,
            project.id,
            consumed_terminal.id,
            expected_version=consumed_terminal.lock_version,
            data=HumanApprovalCreate(reviewer="tester", decision=ApprovalDecision.APPROVED),
        )
        session.add(
            WorkflowTransitionEvent(
                project_id=project.id,
                workflow_run_id=consumed_terminal.id,
                actor=Actor.SYSTEM.value,
                action=TransitionAction.ADVANCE.value,
                from_stage=ControlledStage.REPORT_REVIEW.value,
                from_state=GateState.APPROVED.value,
                to_stage=ControlledStage.REPORT_REVIEW.value,
                to_state=GateState.APPROVED.value,
                source_snapshot_id=consumed_terminal.current_snapshot_id,
                target_snapshot_id=consumed_terminal.current_snapshot_id,
                consumed_approval_decision_id=consumed_approval.id,
                grant_fingerprint=consumed_approval.grant_fingerprint,
                source_run_version=consumed_terminal.lock_version,
                result_run_version=consumed_terminal.lock_version + 1,
            ),
        )
        session.commit()

        items = list_workflow_queue(session, project.id)
        counts_before = (
            session.query(WorkflowRun).count(),
            session.query(WorkflowStageSnapshot).count(),
            session.query(WorkflowHumanDecision).count(),
            session.query(WorkflowTransitionEvent).count(),
        )

        def override_get_session():
            yield session

        app.dependency_overrides[get_session] = override_get_session
        try:
            first_response = ASGIClient().get(f"/api/projects/{project.id}/workflow-runs")
            second_response = ASGIClient().get(f"/api/projects/{project.id}/workflow-runs")
            missing_project_response = ASGIClient().get(f"/api/projects/{uuid.uuid4()}/workflow-runs")
        finally:
            app.dependency_overrides.clear()

        counts_after = (
            session.query(WorkflowRun).count(),
            session.query(WorkflowStageSnapshot).count(),
            session.query(WorkflowHumanDecision).count(),
            session.query(WorkflowTransitionEvent).count(),
        )
        waiting_review_snapshot_id = waiting_review.current_snapshot_id
        waiting_approval_version = waiting_approval.lock_version
        approval_id = approval.id
        project_id = project.id

    by_subject = {item["subject_ref"]: item for item in items}
    assert set(by_subject) == {"waiting-review", "waiting-approval", "continuable"}
    assert by_subject["waiting-review"]["bucket"] == "waiting_review"
    assert by_subject["waiting-approval"]["bucket"] == "waiting_approval"
    assert by_subject["continuable"]["bucket"] == "can_continue"
    assert by_subject["continuable"]["can_continue"] is True
    assert by_subject["continuable"]["approval_decision_id"] == approval_id
    assert by_subject["continuable"]["route_path"] is None
    assert by_subject["waiting-review"]["current_snapshot_id"] == waiting_review_snapshot_id
    assert by_subject["waiting-approval"]["lock_version"] == waiting_approval_version
    assert other_waiting_id not in {item["id"] for item in items}
    assert first_response.status_code == 200
    assert first_response.json() == second_response.json()
    assert first_response.json()["project_id"] == str(project_id)
    assert [item["subject_ref"] for item in first_response.json()["items"]] == [
        "waiting-review",
        "waiting-approval",
        "continuable",
    ]
    assert counts_after == counts_before
    assert missing_project_response.status_code == 404
    assert missing_project_response.json()["error_code"] == "WORKFLOW_PROJECT_NOT_FOUND"
