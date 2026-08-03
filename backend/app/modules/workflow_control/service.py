from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.modules.projects.models import Project
from backend.app.modules.workflow_control.models import (
    WorkflowHumanDecision,
    WorkflowRun,
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
    WorkflowKind,
    WorkflowPosition,
    WORKFLOW_STAGE_SEQUENCES,
    apply_transition,
)
from backend.app.modules.workflow_control.schemas import (
    HumanApprovalCreate,
    HumanReviewCreate,
    WorkflowRevisionCreate,
    WorkflowRunCreate,
)


MAX_SNAPSHOT_BYTES = 1_048_576
FORBIDDEN_SNAPSHOT_KEYS = {
    "api_key",
    "authorization",
    "cookie",
    "password",
    "secret",
    "token",
}


class WorkflowPersistenceError(Exception):
    code = "WORKFLOW_PERSISTENCE_ERROR"


class ProjectNotFoundError(WorkflowPersistenceError):
    code = "WORKFLOW_PROJECT_NOT_FOUND"


class WorkflowRunNotFoundError(WorkflowPersistenceError):
    code = "WORKFLOW_RUN_NOT_FOUND"


class WorkflowConflictError(WorkflowPersistenceError):
    code = "WORKFLOW_CONFLICT"


class WorkflowVersionConflictError(WorkflowPersistenceError):
    code = "WORKFLOW_CONCURRENT_MODIFICATION"


class WorkflowApprovalNotFoundError(WorkflowPersistenceError):
    code = "WORKFLOW_APPROVAL_NOT_FOUND"


class WorkflowApprovalReplayError(WorkflowPersistenceError):
    code = "WORKFLOW_APPROVAL_ALREADY_CONSUMED"


class WorkflowApprovalStaleError(WorkflowPersistenceError):
    code = "WORKFLOW_APPROVAL_STALE"


class WorkflowSnapshotInvalidError(WorkflowPersistenceError):
    code = "WORKFLOW_SNAPSHOT_INVALID"


class WorkflowSnapshotIntegrityError(WorkflowPersistenceError):
    code = "WORKFLOW_SNAPSHOT_INTEGRITY_FAILED"


def canonical_snapshot_hash(stage: ControlledStage, payload: dict[str, Any]) -> str:
    _reject_forbidden_snapshot_keys(payload)
    try:
        canonical = json.dumps(
            {"stage": stage.value, "payload": payload},
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise WorkflowSnapshotInvalidError from exc
    encoded = canonical.encode("utf-8")
    if len(encoded) > MAX_SNAPSHOT_BYTES:
        raise WorkflowSnapshotInvalidError
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def create_workflow_run(session: Session, data: WorkflowRunCreate) -> WorkflowRun:
    if session.get(Project, data.project_id) is None:
        raise ProjectNotFoundError
    sequence = WORKFLOW_STAGE_SEQUENCES[data.workflow_kind]
    stage = data.initial_stage or sequence[0]
    if stage not in sequence:
        raise WorkflowSnapshotInvalidError
    stage_index = sequence.index(stage)
    completed_stages = tuple(data.completed_stages or sequence[:stage_index])
    if completed_stages != sequence[:stage_index]:
        raise WorkflowSnapshotInvalidError
    snapshot_hash = canonical_snapshot_hash(stage, data.input_payload)
    run_id = uuid.uuid4()
    snapshot_id = uuid.uuid4()
    run = WorkflowRun(
        id=run_id,
        project_id=data.project_id,
        workflow_kind=data.workflow_kind.value,
        subject_ref=data.subject_ref,
        current_stage=stage.value,
        gate_state=GateState.DRAFT.value,
        input_snapshot_hash=snapshot_hash,
        current_snapshot_id=snapshot_id,
        completed_stages_json=[item.value for item in completed_stages],
        lock_version=0,
        status="active",
    )
    snapshot = WorkflowStageSnapshot(
        id=snapshot_id,
        project_id=data.project_id,
        workflow_run_id=run_id,
        stage=stage.value,
        stage_iteration=1,
        input_snapshot_hash=snapshot_hash,
        input_payload_json=data.input_payload,
        previous_snapshot_id=None,
        created_by_actor=Actor.HUMAN.value,
        created_by_label=data.created_by,
    )
    session.add_all([run, snapshot])
    _commit(session, WorkflowConflictError)
    session.refresh(run)
    return run


def get_workflow_run(session: Session, project_id: uuid.UUID, run_id: uuid.UUID) -> WorkflowRun:
    run = session.scalar(
        select(WorkflowRun).where(WorkflowRun.id == run_id, WorkflowRun.project_id == project_id),
    )
    if run is None:
        raise WorkflowRunNotFoundError
    return run


def get_workflow_run_authoritative(
    session: Session,
    project_id: uuid.UUID,
    run_id: uuid.UUID,
) -> tuple[WorkflowRun, WorkflowStageSnapshot]:
    run = get_workflow_run(session, project_id, run_id)
    return _authoritative_position(session, project_id, run_id, run.lock_version)


def get_workflow_run_for_subject(
    session: Session,
    project_id: uuid.UUID,
    *,
    workflow_kind: WorkflowKind,
    subject_ref: str,
) -> tuple[WorkflowRun, WorkflowStageSnapshot]:
    run = session.scalar(
        select(WorkflowRun)
        .where(
            WorkflowRun.project_id == project_id,
            WorkflowRun.workflow_kind == workflow_kind.value,
            WorkflowRun.subject_ref == subject_ref,
            WorkflowRun.status == "active",
        )
        .order_by(WorkflowRun.created_at.desc(), WorkflowRun.id.desc()),
    )
    if run is None:
        raise WorkflowRunNotFoundError
    return _authoritative_position(session, project_id, run.id, run.lock_version)


WORKFLOW_QUEUE_BUCKETS = ("waiting_review", "waiting_approval", "can_continue")

def list_workflow_queue(session: Session, project_id: uuid.UUID) -> list[dict[str, Any]]:
    """Return read-only WorkflowRun queue items for the AI Workbench."""
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    runs = list(
        session.scalars(
            select(WorkflowRun)
            .where(
                WorkflowRun.project_id == project_id,
                WorkflowRun.status == "active",
                WorkflowRun.gate_state.in_(
                    [GateState.WAITING_REVIEW.value, GateState.WAITING_APPROVAL.value, GateState.APPROVED.value],
                ),
            )
            .order_by(
                WorkflowRun.gate_state.asc(),
                WorkflowRun.current_stage.asc(),
                WorkflowRun.updated_at.desc(),
                WorkflowRun.id.asc(),
            ),
        ),
    )
    items: list[dict[str, Any]] = []
    for run in runs:
        approval = _latest_current_approval(session, run)
        can_continue = (
            run.gate_state == GateState.APPROVED.value
            and approval is not None
            and approval.source_run_version + 1 == run.lock_version
            and approval.grant_fingerprint
            == _grant(run, approval.reviewer, ApprovalDecision.APPROVED).fingerprint
            and not _approval_consumed(session, approval)
        )
        bucket = _queue_bucket(run, can_continue=can_continue)
        if bucket is None:
            continue
        stage = ControlledStage(run.current_stage)
        items.append(
            {
                "id": run.id,
                "project_id": run.project_id,
                "workflow_kind": WorkflowKind(run.workflow_kind),
                "subject_ref": run.subject_ref,
                "current_stage": stage,
                "gate_state": run.gate_state,
                "bucket": bucket,
                "lock_version": run.lock_version,
                "current_snapshot_id": run.current_snapshot_id,
                "input_snapshot_hash": run.input_snapshot_hash,
                "approval_decision_id": approval.id if can_continue and approval is not None else None,
                "can_continue": can_continue,
                # A route is exposed only after its page can restore this exact run.
                "route_path": None,
                "created_at": run.created_at.isoformat(),
                "updated_at": run.updated_at.isoformat(),
            },
        )
    order = {bucket: index for index, bucket in enumerate(WORKFLOW_QUEUE_BUCKETS)}
    return sorted(
        items,
        key=lambda item: (
            order[item["bucket"]],
            str(item["current_stage"]),
            item["updated_at"],
            str(item["id"]),
        ),
    )


def submit_for_review(
    session: Session,
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    expected_version: int,
) -> WorkflowRun:
    run, snapshot = _authoritative_position(session, project_id, run_id, expected_version)
    position = apply_transition(
        _position(run),
        action=TransitionAction.SUBMIT_FOR_REVIEW,
        actor=Actor.AI,
    )
    return _persist_transition(
        session,
        run,
        snapshot,
        position,
        expected_version=expected_version,
        actor=Actor.AI,
        action=TransitionAction.SUBMIT_FOR_REVIEW,
    )


def complete_human_review(
    session: Session,
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    expected_version: int,
    data: HumanReviewCreate,
) -> tuple[WorkflowRun, WorkflowHumanDecision]:
    run, snapshot = _authoritative_position(session, project_id, run_id, expected_version)
    position = apply_transition(
        _position(run),
        action=TransitionAction.COMPLETE_REVIEW,
        actor=Actor.HUMAN,
    )
    decision = _decision(
        run,
        snapshot,
        action=TransitionAction.COMPLETE_REVIEW,
        decision="reviewed",
        reviewer=data.reviewer,
        comment=data.comment,
        source_run_version=expected_version,
    )
    session.add(decision)
    session.flush()
    updated = _persist_transition(
        session,
        run,
        snapshot,
        position,
        expected_version=expected_version,
        actor=Actor.HUMAN,
        action=TransitionAction.COMPLETE_REVIEW,
        human_decision=decision,
    )
    session.refresh(decision)
    return updated, decision


def record_human_approval(
    session: Session,
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    expected_version: int,
    data: HumanApprovalCreate,
) -> tuple[WorkflowRun, WorkflowHumanDecision]:
    run, snapshot = _authoritative_position(session, project_id, run_id, expected_version)
    approved = data.decision is ApprovalDecision.APPROVED
    action = TransitionAction.APPROVE if approved else TransitionAction.REJECT
    grant = _grant(run, data.reviewer, data.decision) if approved else None
    position = apply_transition(
        _position(run),
        action=action,
        actor=Actor.HUMAN,
        approval=grant,
    )
    decision = _decision(
        run,
        snapshot,
        action=action,
        decision=data.decision.value,
        reviewer=data.reviewer,
        comment=data.comment,
        source_run_version=expected_version,
        allowed_action=TransitionAction.ADVANCE if approved else None,
        grant_fingerprint=grant.fingerprint if grant else None,
    )
    session.add(decision)
    session.flush()
    updated = _persist_transition(
        session,
        run,
        snapshot,
        position,
        expected_version=expected_version,
        actor=Actor.HUMAN,
        action=action,
        human_decision=decision,
        grant_fingerprint=grant.fingerprint if grant else None,
    )
    session.refresh(decision)
    return updated, decision


def revise_workflow(
    session: Session,
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    expected_version: int,
    data: WorkflowRevisionCreate,
) -> tuple[WorkflowRun, WorkflowStageSnapshot, WorkflowHumanDecision]:
    run, source_snapshot = _authoritative_position(session, project_id, run_id, expected_version)
    stage = ControlledStage(run.current_stage)
    snapshot_hash = canonical_snapshot_hash(stage, data.input_payload)
    position = apply_transition(
        _position(run),
        action=TransitionAction.REVISE,
        actor=Actor.HUMAN,
        new_input_snapshot_hash=snapshot_hash,
    )
    target_snapshot = _new_snapshot(
        session,
        run,
        source_snapshot,
        stage=stage,
        snapshot_hash=snapshot_hash,
        payload=data.input_payload,
        actor=Actor.HUMAN,
        label=data.reviewer,
    )
    decision = _decision(
        run,
        source_snapshot,
        action=TransitionAction.REVISE,
        decision="revised",
        reviewer=data.reviewer,
        comment=data.comment,
        source_run_version=expected_version,
    )
    session.add_all([target_snapshot, decision])
    session.flush()
    updated = _persist_transition(
        session,
        run,
        source_snapshot,
        position,
        expected_version=expected_version,
        actor=Actor.HUMAN,
        action=TransitionAction.REVISE,
        target_snapshot=target_snapshot,
        human_decision=decision,
    )
    session.refresh(target_snapshot)
    session.refresh(decision)
    return updated, target_snapshot, decision


def advance_workflow(
    session: Session,
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    expected_version: int,
    approval_decision_id: uuid.UUID,
    target_stage: ControlledStage,
    next_input_payload: dict[str, Any],
    created_by: str = "system",
) -> WorkflowRun:
    run, source_snapshot = _authoritative_position(session, project_id, run_id, expected_version)
    decision = session.scalar(
        select(WorkflowHumanDecision).where(
            WorkflowHumanDecision.id == approval_decision_id,
            WorkflowHumanDecision.project_id == project_id,
            WorkflowHumanDecision.workflow_run_id == run_id,
        ),
    )
    if decision is None or decision.action != TransitionAction.APPROVE.value:
        raise WorkflowApprovalNotFoundError
    consumed = session.scalar(
        select(WorkflowTransitionEvent.id).where(
            WorkflowTransitionEvent.consumed_approval_decision_id == decision.id,
        ),
    )
    if consumed is not None:
        raise WorkflowApprovalReplayError
    if (
        decision.snapshot_id != run.current_snapshot_id
        or decision.stage != run.current_stage
        or decision.source_run_version + 1 != run.lock_version
        or decision.decision != ApprovalDecision.APPROVED.value
        or decision.allowed_action != TransitionAction.ADVANCE.value
    ):
        raise WorkflowApprovalStaleError
    grant = _grant(run, decision.reviewer, ApprovalDecision.APPROVED)
    if decision.grant_fingerprint != grant.fingerprint:
        raise WorkflowApprovalStaleError

    next_hash = canonical_snapshot_hash(target_stage, next_input_payload)
    position = apply_transition(
        _position(run),
        action=TransitionAction.ADVANCE,
        actor=Actor.SYSTEM,
        approval=grant,
        target_stage=target_stage,
        new_input_snapshot_hash=next_hash,
    )
    target_snapshot = _new_snapshot(
        session,
        run,
        source_snapshot,
        stage=target_stage,
        snapshot_hash=next_hash,
        payload=next_input_payload,
        actor=Actor.SYSTEM,
        label=created_by,
    )
    session.add(target_snapshot)
    session.flush()
    return _persist_transition(
        session,
        run,
        source_snapshot,
        position,
        expected_version=expected_version,
        actor=Actor.SYSTEM,
        action=TransitionAction.ADVANCE,
        target_snapshot=target_snapshot,
        consumed_approval=decision,
        grant_fingerprint=grant.fingerprint,
    )


def approve_and_advance_workflow(
    session: Session,
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    *,
    expected_version: int,
    data: HumanReviewCreate,
    target_stage: ControlledStage,
    next_input_payload: dict[str, Any],
    created_by: str = "system",
) -> tuple[WorkflowRun, WorkflowHumanDecision]:
    """Approve the current snapshot and consume that approval atomically."""
    run, source_snapshot = _authoritative_position(session, project_id, run_id, expected_version)
    grant = _grant(run, data.reviewer, ApprovalDecision.APPROVED)
    approved_position = apply_transition(
        _position(run),
        action=TransitionAction.APPROVE,
        actor=Actor.HUMAN,
        approval=grant,
    )
    next_hash = canonical_snapshot_hash(target_stage, next_input_payload)
    advanced_position = apply_transition(
        approved_position,
        action=TransitionAction.ADVANCE,
        actor=Actor.SYSTEM,
        approval=grant,
        target_stage=target_stage,
        new_input_snapshot_hash=next_hash,
    )
    decision = _decision(
        run,
        source_snapshot,
        action=TransitionAction.APPROVE,
        decision=ApprovalDecision.APPROVED.value,
        reviewer=data.reviewer,
        comment=data.comment,
        source_run_version=expected_version,
        allowed_action=TransitionAction.ADVANCE,
        grant_fingerprint=grant.fingerprint,
    )
    target_snapshot = _new_snapshot(
        session,
        run,
        source_snapshot,
        stage=target_stage,
        snapshot_hash=next_hash,
        payload=next_input_payload,
        actor=Actor.SYSTEM,
        label=created_by,
    )
    session.add_all([decision, target_snapshot])
    session.flush()

    result = session.execute(
        update(WorkflowRun)
        .where(
            WorkflowRun.id == run.id,
            WorkflowRun.project_id == run.project_id,
            WorkflowRun.lock_version == expected_version,
            WorkflowRun.current_stage == run.current_stage,
            WorkflowRun.gate_state == run.gate_state,
            WorkflowRun.current_snapshot_id == run.current_snapshot_id,
        )
        .values(
            current_stage=advanced_position.stage.value,
            gate_state=advanced_position.state.value,
            input_snapshot_hash=advanced_position.input_snapshot_hash,
            current_snapshot_id=target_snapshot.id,
            completed_stages_json=[stage.value for stage in advanced_position.completed_stages],
            lock_version=expected_version + 2,
        )
        .execution_options(synchronize_session=False),
    )
    if result.rowcount != 1:
        session.rollback()
        raise WorkflowVersionConflictError

    approval_event = WorkflowTransitionEvent(
        project_id=run.project_id,
        workflow_run_id=run.id,
        actor=Actor.HUMAN.value,
        action=TransitionAction.APPROVE.value,
        from_stage=run.current_stage,
        from_state=run.gate_state,
        to_stage=approved_position.stage.value,
        to_state=approved_position.state.value,
        source_snapshot_id=source_snapshot.id,
        target_snapshot_id=source_snapshot.id,
        human_decision_id=decision.id,
        grant_fingerprint=grant.fingerprint,
        source_run_version=expected_version,
        result_run_version=expected_version + 1,
    )
    advance_event = WorkflowTransitionEvent(
        project_id=run.project_id,
        workflow_run_id=run.id,
        actor=Actor.SYSTEM.value,
        action=TransitionAction.ADVANCE.value,
        from_stage=approved_position.stage.value,
        from_state=approved_position.state.value,
        to_stage=advanced_position.stage.value,
        to_state=advanced_position.state.value,
        source_snapshot_id=source_snapshot.id,
        target_snapshot_id=target_snapshot.id,
        consumed_approval_decision_id=decision.id,
        grant_fingerprint=grant.fingerprint,
        source_run_version=expected_version + 1,
        result_run_version=expected_version + 2,
    )
    session.add_all([approval_event, advance_event])
    _commit(session, WorkflowConflictError)
    session.expire(run)
    session.refresh(decision)
    return get_workflow_run(session, project_id, run_id), decision


def _authoritative_position(
    session: Session,
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    expected_version: int,
) -> tuple[WorkflowRun, WorkflowStageSnapshot]:
    run = get_workflow_run(session, project_id, run_id)
    if run.lock_version != expected_version:
        raise WorkflowVersionConflictError
    snapshot = session.scalar(
        select(WorkflowStageSnapshot).where(
            WorkflowStageSnapshot.id == run.current_snapshot_id,
            WorkflowStageSnapshot.project_id == project_id,
            WorkflowStageSnapshot.workflow_run_id == run_id,
        ),
    )
    if snapshot is None:
        raise WorkflowSnapshotIntegrityError
    expected_hash = canonical_snapshot_hash(ControlledStage(snapshot.stage), snapshot.input_payload_json)
    if (
        snapshot.stage != run.current_stage
        or snapshot.input_snapshot_hash != expected_hash
        or run.input_snapshot_hash != expected_hash
    ):
        raise WorkflowSnapshotIntegrityError
    return run, snapshot


def _persist_transition(
    session: Session,
    run: WorkflowRun,
    source_snapshot: WorkflowStageSnapshot,
    position: WorkflowPosition,
    *,
    expected_version: int,
    actor: Actor,
    action: TransitionAction,
    target_snapshot: WorkflowStageSnapshot | None = None,
    human_decision: WorkflowHumanDecision | None = None,
    consumed_approval: WorkflowHumanDecision | None = None,
    grant_fingerprint: str | None = None,
) -> WorkflowRun:
    target_snapshot_id = target_snapshot.id if target_snapshot else source_snapshot.id
    result = session.execute(
        update(WorkflowRun)
        .where(
            WorkflowRun.id == run.id,
            WorkflowRun.project_id == run.project_id,
            WorkflowRun.lock_version == expected_version,
            WorkflowRun.current_stage == run.current_stage,
            WorkflowRun.gate_state == run.gate_state,
            WorkflowRun.current_snapshot_id == run.current_snapshot_id,
        )
        .values(
            current_stage=position.stage.value,
            gate_state=position.state.value,
            input_snapshot_hash=position.input_snapshot_hash,
            current_snapshot_id=target_snapshot_id,
            completed_stages_json=[stage.value for stage in position.completed_stages],
            lock_version=expected_version + 1,
        )
        .execution_options(synchronize_session=False),
    )
    if result.rowcount != 1:
        session.rollback()
        raise WorkflowVersionConflictError
    event = WorkflowTransitionEvent(
        project_id=run.project_id,
        workflow_run_id=run.id,
        actor=actor.value,
        action=action.value,
        from_stage=run.current_stage,
        from_state=run.gate_state,
        to_stage=position.stage.value,
        to_state=position.state.value,
        source_snapshot_id=source_snapshot.id,
        target_snapshot_id=target_snapshot_id,
        human_decision_id=human_decision.id if human_decision else None,
        consumed_approval_decision_id=consumed_approval.id if consumed_approval else None,
        grant_fingerprint=grant_fingerprint,
        source_run_version=expected_version,
        result_run_version=expected_version + 1,
    )
    session.add(event)
    _commit(session, WorkflowConflictError)
    # API sessions intentionally keep objects after commit; expire the prior
    # identity so callers always receive the authoritative CAS result.
    session.expire(run)
    return get_workflow_run(session, run.project_id, run.id)


def _new_snapshot(
    session: Session,
    run: WorkflowRun,
    source_snapshot: WorkflowStageSnapshot,
    *,
    stage: ControlledStage,
    snapshot_hash: str,
    payload: dict[str, Any],
    actor: Actor,
    label: str,
) -> WorkflowStageSnapshot:
    iteration = session.scalar(
        select(func.max(WorkflowStageSnapshot.stage_iteration)).where(
            WorkflowStageSnapshot.workflow_run_id == run.id,
            WorkflowStageSnapshot.stage == stage.value,
        ),
    )
    return WorkflowStageSnapshot(
        project_id=run.project_id,
        workflow_run_id=run.id,
        stage=stage.value,
        stage_iteration=(iteration or 0) + 1,
        input_snapshot_hash=snapshot_hash,
        input_payload_json=payload,
        previous_snapshot_id=source_snapshot.id,
        created_by_actor=actor.value,
        created_by_label=label,
    )


def _position(run: WorkflowRun) -> WorkflowPosition:
    return WorkflowPosition(
        workflow_kind=WorkflowKind(run.workflow_kind),
        workflow_ref=str(run.id),
        subject_ref=run.subject_ref,
        stage=ControlledStage(run.current_stage),
        state=GateState(run.gate_state),
        input_snapshot_hash=run.input_snapshot_hash,
        completed_stages=tuple(ControlledStage(stage) for stage in run.completed_stages_json),
    )


def _latest_current_approval(session: Session, run: WorkflowRun) -> WorkflowHumanDecision | None:
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


def _approval_consumed(session: Session, decision: WorkflowHumanDecision) -> bool:
    consumed = session.scalar(
        select(WorkflowTransitionEvent.id).where(
            WorkflowTransitionEvent.project_id == decision.project_id,
            WorkflowTransitionEvent.workflow_run_id == decision.workflow_run_id,
            WorkflowTransitionEvent.consumed_approval_decision_id == decision.id,
        ),
    )
    return consumed is not None


def _queue_bucket(run: WorkflowRun, *, can_continue: bool) -> str | None:
    if run.gate_state == GateState.WAITING_REVIEW.value:
        return "waiting_review"
    if run.gate_state == GateState.WAITING_APPROVAL.value:
        return "waiting_approval"
    if can_continue:
        return "can_continue"
    return None


def _grant(
    run: WorkflowRun,
    reviewer: str,
    decision: ApprovalDecision,
) -> ApprovalGrant:
    return ApprovalGrant(
        workflow_kind=WorkflowKind(run.workflow_kind),
        workflow_ref=str(run.id),
        subject_ref=run.subject_ref,
        stage=ControlledStage(run.current_stage),
        input_snapshot_hash=run.input_snapshot_hash,
        allowed_action=TransitionAction.ADVANCE,
        decision=decision,
        granted_by=reviewer,
    )


def _decision(
    run: WorkflowRun,
    snapshot: WorkflowStageSnapshot,
    *,
    action: TransitionAction,
    decision: str,
    reviewer: str,
    comment: str | None,
    source_run_version: int,
    allowed_action: TransitionAction | None = None,
    grant_fingerprint: str | None = None,
) -> WorkflowHumanDecision:
    return WorkflowHumanDecision(
        project_id=run.project_id,
        workflow_run_id=run.id,
        snapshot_id=snapshot.id,
        stage=run.current_stage,
        action=action.value,
        decision=decision,
        allowed_action=allowed_action.value if allowed_action else None,
        reviewer=reviewer,
        comment=comment,
        grant_fingerprint=grant_fingerprint,
        source_run_version=source_run_version,
    )


def _reject_forbidden_snapshot_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = str(key).strip().lower().replace("-", "_")
            if (
                normalized_key in FORBIDDEN_SNAPSHOT_KEYS
                or normalized_key.endswith(("_password", "_secret", "_token", "_api_key"))
            ):
                raise WorkflowSnapshotInvalidError
            _reject_forbidden_snapshot_keys(item)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_snapshot_keys(item)


def _commit(session: Session, error_type: type[WorkflowPersistenceError]) -> None:
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise error_type from exc
