from __future__ import annotations

import uuid
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.cases.models import GeneratedCaseCandidate, TestCase
from backend.app.modules.projects.models import Environment, Project
from backend.app.modules.requirements.models import Requirement, RiskItem
from backend.app.modules.test_campaigns.models import TestCampaign
from backend.app.modules.test_campaigns.schemas import (
    TestCampaignAction,
    TestCampaignContinue,
    TestCampaignCreate,
    TestCampaignEdit,
    TestCampaignRead,
    TestCampaignWorkflowRead,
)
from backend.app.modules.workflow_control import service as workflow_service
from backend.app.modules.workflow_control.models import (
    WorkflowHumanDecision,
    WorkflowStageSnapshot,
    WorkflowTransitionEvent,
)
from backend.app.modules.workflow_control.policy import (
    Actor,
    ApprovalDecision,
    ApprovalGrant,
    ControlledStage,
    GateState,
    TransitionAction,
    TransitionPolicyError,
    WorkflowKind,
)
from backend.app.modules.workflow_control.schemas import (
    HumanApprovalCreate,
    HumanReviewCreate,
    WorkflowRevisionCreate,
    WorkflowRunCreate,
)


class TestCampaignError(Exception):
    code = "TEST_CAMPAIGN_ERROR"


class ProjectNotFoundError(TestCampaignError):
    code = "PROJECT_NOT_FOUND"


class EnvironmentNotFoundError(TestCampaignError):
    code = "TEST_CAMPAIGN_ENVIRONMENT_NOT_FOUND"


class TestCampaignNotFoundError(TestCampaignError):
    code = "TEST_CAMPAIGN_NOT_FOUND"


class CampaignEvidenceNotFoundError(TestCampaignError):
    code = "TEST_CAMPAIGN_EVIDENCE_NOT_FOUND"


class CampaignCaseNotApprovedError(TestCampaignError):
    code = "TEST_CAMPAIGN_CASE_NOT_APPROVED"


class CampaignScopeInvalidError(TestCampaignError):
    code = "TEST_CAMPAIGN_SCOPE_INVALID"


def create_test_campaign(
    session: Session,
    project_id: uuid.UUID,
    data: TestCampaignCreate,
) -> TestCampaignRead:
    _require_project(session, project_id)
    _require_environment(session, project_id, data.target_environment_id)
    normalized = _normalized_scope(data)
    coverage_rows = _coverage_rows(session, project_id, normalized)
    campaign = TestCampaign(
        id=uuid.uuid4(),
        project_id=project_id,
        name=normalized["name"],
        scope_statement=normalized["scope_statement"],
        target_environment_id=normalized["target_environment_id"],
        target_version_ref=normalized["target_version_ref"],
        exit_conditions_json=normalized["exit_conditions"],
        requirement_ids_json=normalized["requirement_ids"],
        risk_ids_json=normalized["risk_ids"],
        test_plan_snapshot_ids_json=normalized["test_plan_snapshot_ids"],
        approved_case_ids_json=normalized["approved_case_ids"],
        coverage_rows_json=coverage_rows,
        status="active",
    )
    session.add(campaign)
    workflow_service.create_workflow_run(
        session,
        WorkflowRunCreate(
            project_id=project_id,
            workflow_kind=WorkflowKind.REQUIREMENT_TO_EXECUTION,
            subject_ref=str(campaign.id),
            input_payload=_scope_snapshot_payload(campaign),
            created_by=data.created_by,
            initial_stage=ControlledStage.SCOPE,
        ),
    )
    session.refresh(campaign)
    return _campaign_read(session, campaign)


def list_test_campaigns(session: Session, project_id: uuid.UUID) -> list[TestCampaignRead]:
    _require_project(session, project_id)
    campaigns = list(
        session.scalars(
            select(TestCampaign)
            .where(TestCampaign.project_id == project_id, TestCampaign.status == "active")
            .order_by(TestCampaign.updated_at.desc(), TestCampaign.id.asc()),
        ),
    )
    return [_campaign_read(session, campaign) for campaign in campaigns]


def get_test_campaign(
    session: Session,
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> TestCampaignRead:
    return _campaign_read(session, _campaign(session, project_id, campaign_id))


def edit_test_campaign(
    session: Session,
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignEdit,
) -> TestCampaignRead:
    campaign = _campaign(session, project_id, campaign_id)
    run, _ = _scope_workflow(session, project_id, campaign.id)
    _require_environment(session, project_id, data.target_environment_id)
    normalized = _normalized_scope(data)
    coverage_rows = _coverage_rows(session, project_id, normalized)
    campaign.name = normalized["name"]
    campaign.scope_statement = normalized["scope_statement"]
    campaign.target_environment_id = normalized["target_environment_id"]
    campaign.target_version_ref = normalized["target_version_ref"]
    campaign.exit_conditions_json = normalized["exit_conditions"]
    campaign.requirement_ids_json = normalized["requirement_ids"]
    campaign.risk_ids_json = normalized["risk_ids"]
    campaign.test_plan_snapshot_ids_json = normalized["test_plan_snapshot_ids"]
    campaign.approved_case_ids_json = normalized["approved_case_ids"]
    campaign.coverage_rows_json = coverage_rows
    workflow_service.revise_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=WorkflowRevisionCreate(
            reviewer=data.reviewer,
            comment=data.comment,
            input_payload=_scope_snapshot_payload(campaign),
        ),
    )
    session.refresh(campaign)
    return _campaign_read(session, campaign)


def submit_scope(
    session: Session,
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignAction,
) -> TestCampaignRead:
    campaign = _campaign(session, project_id, campaign_id)
    run, _ = _scope_workflow(session, project_id, campaign.id)
    workflow_service.submit_for_review(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
    )
    return _campaign_read(session, campaign)


def complete_scope_review(
    session: Session,
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignAction,
) -> TestCampaignRead:
    campaign = _campaign(session, project_id, campaign_id)
    run, _ = _scope_workflow(session, project_id, campaign.id)
    workflow_service.complete_human_review(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanReviewCreate(reviewer=data.reviewer, comment=data.comment),
    )
    return _campaign_read(session, campaign)


def decide_scope(
    session: Session,
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignAction,
    *,
    decision: ApprovalDecision,
) -> TestCampaignRead:
    campaign = _campaign(session, project_id, campaign_id)
    run, _ = _scope_workflow(session, project_id, campaign.id)
    workflow_service.record_human_approval(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanApprovalCreate(
            reviewer=data.reviewer,
            comment=data.comment,
            decision=decision,
        ),
    )
    return _campaign_read(session, campaign)


def continue_scope(
    session: Session,
    project_id: uuid.UUID,
    campaign_id: uuid.UUID,
    data: TestCampaignContinue,
) -> TestCampaignRead:
    campaign = _campaign(session, project_id, campaign_id)
    run, snapshot = _scope_workflow(session, project_id, campaign.id)
    workflow_service.advance_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        approval_decision_id=data.approval_decision_id,
        target_stage=ControlledStage.REQUIREMENT_REVIEW,
        next_input_payload={
            "test_campaign_id": str(campaign.id),
            "source_scope_snapshot_id": str(snapshot.id),
            "source_scope_snapshot_hash": snapshot.input_snapshot_hash,
            **_scope_snapshot_payload(campaign),
        },
    )
    return _campaign_read(session, campaign)


def _campaign(session: Session, project_id: uuid.UUID, campaign_id: uuid.UUID) -> TestCampaign:
    campaign = session.scalar(
        select(TestCampaign).where(
            TestCampaign.id == campaign_id,
            TestCampaign.project_id == project_id,
            TestCampaign.status == "active",
        ),
    )
    if campaign is None:
        raise TestCampaignNotFoundError
    return campaign


def _require_project(session: Session, project_id: uuid.UUID) -> None:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError


def _require_environment(session: Session, project_id: uuid.UUID, environment_id: uuid.UUID) -> None:
    environment = session.scalar(
        select(Environment).where(Environment.id == environment_id, Environment.project_id == project_id),
    )
    if environment is None:
        raise EnvironmentNotFoundError


def _scope_workflow(session: Session, project_id: uuid.UUID, campaign_id: uuid.UUID):
    run, snapshot = workflow_service.get_workflow_run_for_subject(
        session,
        project_id,
        workflow_kind=WorkflowKind.REQUIREMENT_TO_EXECUTION,
        subject_ref=str(campaign_id),
    )
    if run.current_stage != ControlledStage.SCOPE.value:
        raise TransitionPolicyError("WORKFLOW_STAGE_MISMATCH")
    return run, snapshot


def _normalized_scope(data: TestCampaignCreate | TestCampaignEdit) -> dict[str, Any]:
    return {
        "name": data.name.strip(),
        "scope_statement": data.scope_statement.strip(),
        "target_environment_id": data.target_environment_id,
        "target_version_ref": data.target_version_ref.strip(),
        "exit_conditions": _normalized_strings(data.exit_conditions),
        "requirement_ids": _normalized_ids(data.requirement_ids),
        "risk_ids": _normalized_ids(data.risk_ids),
        "test_plan_snapshot_ids": _normalized_ids(data.test_plan_snapshot_ids),
        "approved_case_ids": _normalized_ids(data.approved_case_ids),
    }


def _normalized_strings(values: Iterable[str]) -> list[str]:
    normalized = sorted({value.strip() for value in values if value.strip()})
    if not normalized:
        raise CampaignScopeInvalidError
    return normalized


def _normalized_ids(values: Iterable[uuid.UUID]) -> list[str]:
    return sorted({str(value) for value in values})


def _coverage_rows(session: Session, project_id: uuid.UUID, scope: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = _records_by_id(
        session,
        Requirement,
        project_id,
        scope["requirement_ids"],
    )
    risks = _records_by_id(session, RiskItem, project_id, scope["risk_ids"])
    plan_snapshots = _test_plan_snapshots(
        session,
        project_id,
        scope["test_plan_snapshot_ids"],
    )
    cases = _approved_cases(session, project_id, scope["approved_case_ids"])
    case_links = _case_links(session, cases)
    rows: list[dict[str, Any]] = []
    for requirement in requirements:
        evidence = sorted(
            str(case_id)
            for case_id, links in case_links.items()
            if str(requirement.id) in links["requirements"]
        )
        rows.append(
            _coverage_row(
                "requirement",
                requirement.id,
                requirement.title,
                evidence_case_ids=evidence,
                gap_reason=None if evidence else "No selected approved case cites this requirement.",
            ),
        )
    for risk in risks:
        evidence = sorted(
            str(case_id)
            for case_id, links in case_links.items()
            if str(risk.id) in links["risks"]
        )
        rows.append(
            _coverage_row(
                "risk",
                risk.id,
                risk.title,
                evidence_case_ids=evidence,
                gap_reason=None if evidence else "No selected approved case cites this risk.",
            ),
        )
    for snapshot in plan_snapshots:
        approved = _snapshot_has_approval(session, project_id, snapshot)
        strategy = str(snapshot.input_payload_json.get("test_strategy") or "Test plan snapshot")
        rows.append(
            _coverage_row(
                "test_plan",
                snapshot.id,
                strategy,
                evidence_snapshot_id=str(snapshot.id),
                gap_reason=None if approved else "Test plan snapshot has no human approval evidence.",
            ),
        )
    for case in cases:
        rows.append(
            _coverage_row(
                "approved_case",
                case.id,
                case.title,
                evidence_case_ids=[str(case.id)],
            ),
        )
    return rows


def _records_by_id(session: Session, model, project_id: uuid.UUID, ids: list[str]) -> list[Any]:
    if not ids:
        return []
    uuid_ids = [uuid.UUID(value) for value in ids]
    records = list(
        session.scalars(
            select(model)
            .where(model.id.in_(uuid_ids), model.project_id == project_id)
            .order_by(model.id.asc()),
        ),
    )
    if {str(record.id) for record in records} != set(ids):
        raise CampaignEvidenceNotFoundError
    return records


def _test_plan_snapshots(
    session: Session,
    project_id: uuid.UUID,
    ids: list[str],
) -> list[WorkflowStageSnapshot]:
    if not ids:
        return []
    uuid_ids = [uuid.UUID(value) for value in ids]
    snapshots = list(
        session.scalars(
            select(WorkflowStageSnapshot)
            .where(
                WorkflowStageSnapshot.id.in_(uuid_ids),
                WorkflowStageSnapshot.project_id == project_id,
                WorkflowStageSnapshot.stage == ControlledStage.TEST_PLAN_REVIEW.value,
            )
            .order_by(WorkflowStageSnapshot.id.asc()),
        ),
    )
    if {str(snapshot.id) for snapshot in snapshots} != set(ids):
        raise CampaignEvidenceNotFoundError
    return snapshots


def _approved_cases(session: Session, project_id: uuid.UUID, ids: list[str]) -> list[TestCase]:
    if not ids:
        return []
    uuid_ids = [uuid.UUID(value) for value in ids]
    cases = list(
        session.scalars(
            select(TestCase)
            .where(TestCase.id.in_(uuid_ids), TestCase.project_id == project_id)
            .order_by(TestCase.id.asc()),
        ),
    )
    if {str(case.id) for case in cases} != set(ids):
        raise CampaignEvidenceNotFoundError
    if any(
        case.status != "active" or case.review_status not in {"approved", "approved_after_edit"}
        for case in cases
    ):
        raise CampaignCaseNotApprovedError
    return cases


def _case_links(
    session: Session,
    cases: list[TestCase],
) -> dict[uuid.UUID, dict[str, set[str]]]:
    candidate_ids = [case.source_candidate_id for case in cases if case.source_candidate_id is not None]
    project_id = cases[0].project_id if cases else None
    candidates = {
        candidate.id: candidate
        for candidate in session.scalars(
            select(GeneratedCaseCandidate).where(
                GeneratedCaseCandidate.id.in_(candidate_ids),
                GeneratedCaseCandidate.project_id == project_id,
            ),
        )
    } if candidate_ids else {}
    return {
        case.id: {
            "requirements": _string_set(candidates.get(case.source_candidate_id).covered_requirement_ids_json)
            if candidates.get(case.source_candidate_id) is not None
            else set(),
            "risks": _string_set(candidates.get(case.source_candidate_id).covered_risk_ids_json)
            if candidates.get(case.source_candidate_id) is not None
            else set(),
        }
        for case in cases
    }


def _string_set(values: list[Any]) -> set[str]:
    return {str(value) for value in values}


def _snapshot_has_approval(
    session: Session,
    project_id: uuid.UUID,
    snapshot: WorkflowStageSnapshot,
) -> bool:
    return session.scalar(
        select(WorkflowHumanDecision.id).where(
            WorkflowHumanDecision.project_id == project_id,
            WorkflowHumanDecision.workflow_run_id == snapshot.workflow_run_id,
            WorkflowHumanDecision.snapshot_id == snapshot.id,
            WorkflowHumanDecision.stage == ControlledStage.TEST_PLAN_REVIEW.value,
            WorkflowHumanDecision.action == TransitionAction.APPROVE.value,
            WorkflowHumanDecision.decision == ApprovalDecision.APPROVED.value,
        ),
    ) is not None


def _coverage_row(
    kind: str,
    target_id: uuid.UUID,
    label: str,
    *,
    evidence_case_ids: list[str] | None = None,
    evidence_snapshot_id: str | None = None,
    gap_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "target_id": str(target_id),
        "label": label,
        "coverage_status": "gap" if gap_reason else "covered",
        "evidence_case_ids": evidence_case_ids or [],
        "evidence_snapshot_id": evidence_snapshot_id,
        "gap_reason": gap_reason,
    }


def _scope_snapshot_payload(campaign: TestCampaign) -> dict[str, Any]:
    return {
        "test_campaign_id": str(campaign.id),
        "name": campaign.name,
        "scope_statement": campaign.scope_statement,
        "target_environment_id": str(campaign.target_environment_id),
        "target_version_ref": campaign.target_version_ref,
        "exit_conditions": list(campaign.exit_conditions_json),
        "requirement_ids": list(campaign.requirement_ids_json),
        "risk_ids": list(campaign.risk_ids_json),
        "test_plan_snapshot_ids": list(campaign.test_plan_snapshot_ids_json),
        "approved_case_ids": list(campaign.approved_case_ids_json),
        "coverage_rows": list(campaign.coverage_rows_json),
    }


def _campaign_read(session: Session, campaign: TestCampaign) -> TestCampaignRead:
    run, snapshot = workflow_service.get_workflow_run_for_subject(
        session,
        campaign.project_id,
        workflow_kind=WorkflowKind.REQUIREMENT_TO_EXECUTION,
        subject_ref=str(campaign.id),
    )
    approval = _current_approval(session, run)
    can_continue = approval is not None and _approval_is_current(session, run, approval)
    return TestCampaignRead(
        id=campaign.id,
        project_id=campaign.project_id,
        name=campaign.name,
        scope_statement=campaign.scope_statement,
        target_environment_id=campaign.target_environment_id,
        target_version_ref=campaign.target_version_ref,
        exit_conditions=list(campaign.exit_conditions_json),
        requirement_ids=[uuid.UUID(value) for value in campaign.requirement_ids_json],
        risk_ids=[uuid.UUID(value) for value in campaign.risk_ids_json],
        test_plan_snapshot_ids=[uuid.UUID(value) for value in campaign.test_plan_snapshot_ids_json],
        approved_case_ids=[uuid.UUID(value) for value in campaign.approved_case_ids_json],
        coverage_rows=list(campaign.coverage_rows_json),
        status=campaign.status,
        workflow=TestCampaignWorkflowRead(
            run_id=run.id,
            stage=run.current_stage,
            state=run.gate_state,
            lock_version=run.lock_version,
            snapshot_id=snapshot.id,
            snapshot_hash=snapshot.input_snapshot_hash,
            snapshot_iteration=snapshot.stage_iteration,
            approval_decision_id=approval.id if can_continue and approval is not None else None,
            can_continue=can_continue,
        ),
        created_at=campaign.created_at.isoformat(),
        updated_at=campaign.updated_at.isoformat(),
    )


def _current_approval(session: Session, run) -> WorkflowHumanDecision | None:
    return session.scalar(
        select(WorkflowHumanDecision)
        .where(
            WorkflowHumanDecision.project_id == run.project_id,
            WorkflowHumanDecision.workflow_run_id == run.id,
            WorkflowHumanDecision.snapshot_id == run.current_snapshot_id,
            WorkflowHumanDecision.stage == run.current_stage,
            WorkflowHumanDecision.action == TransitionAction.APPROVE.value,
            WorkflowHumanDecision.decision == ApprovalDecision.APPROVED.value,
            WorkflowHumanDecision.allowed_action == TransitionAction.ADVANCE.value,
        )
        .order_by(WorkflowHumanDecision.created_at.desc(), WorkflowHumanDecision.id.desc()),
    )


def _approval_is_current(session: Session, run, decision: WorkflowHumanDecision) -> bool:
    consumed = session.scalar(
        select(WorkflowTransitionEvent.id).where(
            WorkflowTransitionEvent.consumed_approval_decision_id == decision.id,
        ),
    )
    grant = ApprovalGrant(
        workflow_kind=WorkflowKind(run.workflow_kind),
        workflow_ref=str(run.id),
        subject_ref=run.subject_ref,
        stage=ControlledStage(run.current_stage),
        input_snapshot_hash=run.input_snapshot_hash,
        allowed_action=TransitionAction.ADVANCE,
        decision=ApprovalDecision.APPROVED,
        granted_by=decision.reviewer,
        actor=Actor.HUMAN,
    )
    return (
        run.gate_state == GateState.APPROVED.value
        and decision.source_run_version + 1 == run.lock_version
        and decision.grant_fingerprint == grant.fingerprint
        and consumed is None
    )
