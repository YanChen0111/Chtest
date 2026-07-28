from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, select, update
from sqlalchemy.orm import Session

from backend.app.models.base import Base
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.workflow_control.models import (
    WorkflowHumanDecision,
    WorkflowStageSnapshot,
    WorkflowTransitionEvent,
)
from backend.app.modules.workflow_control.policy import (
    ApprovalDecision,
    ControlledStage,
    GateState,
    WorkflowKind,
)
from backend.app.modules.workflow_control.schemas import (
    HumanApprovalCreate,
    HumanReviewCreate,
    WorkflowRevisionCreate,
    WorkflowRunCreate,
)
from backend.app.modules.workflow_control.service import (
    WorkflowApprovalNotFoundError,
    WorkflowApprovalReplayError,
    WorkflowApprovalStaleError,
    WorkflowRunNotFoundError,
    WorkflowSnapshotIntegrityError,
    WorkflowSnapshotInvalidError,
    WorkflowVersionConflictError,
    advance_workflow,
    complete_human_review,
    create_workflow_run,
    get_workflow_run,
    record_human_approval,
    revise_workflow,
    submit_for_review,
)


ROOT = Path(__file__).parents[3]
PROJECT_MIGRATION = ROOT / "alembic/versions/20260626_0001_project_core.py"
WORKFLOW_MIGRATION = ROOT / "alembic/versions/20260728_0019_workflow_control_persistence.py"
ORIGINAL_PAYLOAD = {"requirement": "Expired coupons are rejected"}


def _load_migration(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def _projects(session: Session) -> tuple[Project, Project]:
    workspace = Workspace(name="Personal Workspace")
    first = Project(workspace=workspace, name="Checkout")
    second = Project(workspace=workspace, name="Billing")
    session.add_all([first, second])
    session.commit()
    return first, second


def _create_run(session: Session, project: Project, payload: dict | None = None):
    return create_workflow_run(
        session,
        WorkflowRunCreate(
            project_id=project.id,
            workflow_kind=WorkflowKind.REQUIREMENT_TO_EXECUTION,
            subject_ref="requirement-001",
            input_payload=payload or ORIGINAL_PAYLOAD,
            created_by="tester",
        ),
    )


def _approve_current(session: Session, project: Project, run, *, reviewer: str = "tester"):
    run = submit_for_review(session, project.id, run.id, expected_version=run.lock_version)
    run, _ = complete_human_review(
        session,
        project.id,
        run.id,
        expected_version=run.lock_version,
        data=HumanReviewCreate(reviewer=reviewer),
    )
    return record_human_approval(
        session,
        project.id,
        run.id,
        expected_version=run.lock_version,
        data=HumanApprovalCreate(reviewer=reviewer, decision=ApprovalDecision.APPROVED),
    )


def test_workflow_control_migration_creates_persistence_tables() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    migrations = [
        _load_migration("workflow_project_core", PROJECT_MIGRATION),
        _load_migration("workflow_persistence", WORKFLOW_MIGRATION),
    ]
    with engine.begin() as connection:
        operations = Operations(MigrationContext.configure(connection))
        originals = [migration.op for migration in migrations]
        for migration in migrations:
            migration.op = operations
        try:
            for migration in migrations:
                migration.upgrade()
        finally:
            for migration, original in zip(migrations, originals, strict=True):
                migration.op = original
        inspector = inspect(connection)
        tables = set(inspector.get_table_names())
        run_columns = {column["name"] for column in inspector.get_columns("workflow_runs")}
        decision_columns = {
            column["name"] for column in inspector.get_columns("workflow_human_decisions")
        }
        event_unique = {
            item["name"] for item in inspector.get_unique_constraints("workflow_transition_events")
        }

    assert {
        "workflow_runs",
        "workflow_stage_snapshots",
        "workflow_human_decisions",
        "workflow_transition_events",
    } <= tables
    assert {"project_id", "current_snapshot_id", "lock_version", "status"} <= run_columns
    assert {"snapshot_id", "grant_fingerprint", "source_run_version"} <= decision_columns
    assert "uq_workflow_transition_events_consumed_approval" in event_unique


def test_run_uses_server_hash_authoritative_position_and_project_isolation() -> None:
    with _session() as session:
        project, other_project = _projects(session)
        run = _create_run(session, project)
        snapshot = session.get(WorkflowStageSnapshot, run.current_snapshot_id)

        assert run.current_stage == ControlledStage.SCOPE.value
        assert run.gate_state == GateState.DRAFT.value
        assert run.lock_version == 0
        assert snapshot is not None
        assert snapshot.input_snapshot_hash == run.input_snapshot_hash
        assert snapshot.stage_iteration == 1

        with pytest.raises(WorkflowRunNotFoundError):
            get_workflow_run(session, other_project.id, run.id)

        snapshot.input_payload_json = {"requirement": "changed after approval"}
        with pytest.raises(ValueError, match="WORKFLOW_EVIDENCE_IMMUTABLE"):
            session.commit()
        session.rollback()


def test_human_approval_instance_is_consumed_once_by_versioned_advance() -> None:
    with _session() as session:
        project, other_project = _projects(session)
        run = _create_run(session, project)
        run, approval = _approve_current(session, project, run)

        assert approval.grant_fingerprint is not None
        assert run.gate_state == GateState.APPROVED.value
        assert run.lock_version == 3

        with pytest.raises(WorkflowRunNotFoundError):
            advance_workflow(
                session,
                other_project.id,
                run.id,
                expected_version=3,
                approval_decision_id=approval.id,
                target_stage=ControlledStage.REQUIREMENT_REVIEW,
                next_input_payload={"review": "target snapshot"},
            )

        advanced = advance_workflow(
            session,
            project.id,
            run.id,
            expected_version=3,
            approval_decision_id=approval.id,
            target_stage=ControlledStage.REQUIREMENT_REVIEW,
            next_input_payload={"review": "target snapshot"},
        )
        assert advanced.current_stage == ControlledStage.REQUIREMENT_REVIEW.value
        assert advanced.gate_state == GateState.DRAFT.value
        assert advanced.lock_version == 4
        consumption = session.scalar(
            select(WorkflowTransitionEvent).where(
                WorkflowTransitionEvent.consumed_approval_decision_id == approval.id,
            ),
        )
        assert consumption is not None
        assert consumption.result_run_version == 4

        with pytest.raises(WorkflowApprovalReplayError):
            advance_workflow(
                session,
                project.id,
                run.id,
                expected_version=4,
                approval_decision_id=approval.id,
                target_stage=ControlledStage.RISK_REVIEW,
                next_input_payload={"risk": "forbidden replay"},
            )


def test_rejected_decision_has_no_grant_and_cannot_authorize_advance() -> None:
    with _session() as session:
        project, _ = _projects(session)
        run = _create_run(session, project)
        run = submit_for_review(session, project.id, run.id, expected_version=0)
        run, _ = complete_human_review(
            session,
            project.id,
            run.id,
            expected_version=1,
            data=HumanReviewCreate(reviewer="tester"),
        )
        run, rejection = record_human_approval(
            session,
            project.id,
            run.id,
            expected_version=2,
            data=HumanApprovalCreate(reviewer="tester", decision=ApprovalDecision.REJECTED),
        )

        assert rejection.grant_fingerprint is None
        with pytest.raises(WorkflowApprovalNotFoundError):
            advance_workflow(
                session,
                project.id,
                run.id,
                expected_version=3,
                approval_decision_id=rejection.id,
                target_stage=ControlledStage.REQUIREMENT_REVIEW,
                next_input_payload={"review": "forbidden"},
            )


def test_revision_creates_new_snapshot_and_invalidates_old_approval() -> None:
    with _session() as session:
        project, _ = _projects(session)
        run = _create_run(session, project)
        run, approval = _approve_current(session, project, run)
        old_snapshot_id = run.current_snapshot_id

        revised, snapshot, decision = revise_workflow(
            session,
            project.id,
            run.id,
            expected_version=3,
            data=WorkflowRevisionCreate(
                reviewer="tester",
                comment="Requirement changed",
                input_payload={"requirement": "Rejected with an audit reason"},
            ),
        )

        assert revised.gate_state == GateState.DRAFT.value
        assert revised.current_snapshot_id == snapshot.id != old_snapshot_id
        assert decision.action == "revise"
        with pytest.raises(WorkflowApprovalStaleError):
            advance_workflow(
                session,
                project.id,
                run.id,
                expected_version=4,
                approval_decision_id=approval.id,
                target_stage=ControlledStage.REQUIREMENT_REVIEW,
                next_input_payload={"review": "must not use stale approval"},
            )


def test_same_stage_and_hash_can_be_reapproved_without_reviving_old_decision() -> None:
    with _session() as session:
        project, _ = _projects(session)
        run = _create_run(session, project)
        run, old_approval = _approve_current(session, project, run)
        original_hash = run.input_snapshot_hash

        run, _, _ = revise_workflow(
            session,
            project.id,
            run.id,
            expected_version=3,
            data=WorkflowRevisionCreate(
                reviewer="tester",
                input_payload={"requirement": "Temporary revision"},
            ),
        )
        run = submit_for_review(session, project.id, run.id, expected_version=4)
        run, _ = complete_human_review(
            session,
            project.id,
            run.id,
            expected_version=5,
            data=HumanReviewCreate(reviewer="tester"),
        )
        run, _ = record_human_approval(
            session,
            project.id,
            run.id,
            expected_version=6,
            data=HumanApprovalCreate(reviewer="tester", decision=ApprovalDecision.REJECTED),
        )
        run, restored_snapshot, _ = revise_workflow(
            session,
            project.id,
            run.id,
            expected_version=7,
            data=WorkflowRevisionCreate(reviewer="tester", input_payload=ORIGINAL_PAYLOAD),
        )
        assert restored_snapshot.input_snapshot_hash == original_hash
        assert restored_snapshot.id != old_approval.snapshot_id

        run, new_approval = _approve_current(session, project, run)
        assert new_approval.id != old_approval.id
        assert new_approval.grant_fingerprint == old_approval.grant_fingerprint

        with pytest.raises(WorkflowApprovalStaleError):
            advance_workflow(
                session,
                project.id,
                run.id,
                expected_version=11,
                approval_decision_id=old_approval.id,
                target_stage=ControlledStage.REQUIREMENT_REVIEW,
                next_input_payload={"review": "old decision forbidden"},
            )

        advanced = advance_workflow(
            session,
            project.id,
            run.id,
            expected_version=11,
            approval_decision_id=new_approval.id,
            target_stage=ControlledStage.REQUIREMENT_REVIEW,
            next_input_payload={"review": "new decision accepted"},
        )
        assert advanced.lock_version == 12


def test_stale_version_writes_no_decision_snapshot_or_event() -> None:
    with _session() as session:
        project, _ = _projects(session)
        run = _create_run(session, project)
        run = submit_for_review(session, project.id, run.id, expected_version=0)
        decision_count = session.query(WorkflowHumanDecision).count()
        snapshot_count = session.query(WorkflowStageSnapshot).count()
        event_count = session.query(WorkflowTransitionEvent).count()

        with pytest.raises(WorkflowVersionConflictError):
            complete_human_review(
                session,
                project.id,
                run.id,
                expected_version=0,
                data=HumanReviewCreate(reviewer="tester"),
            )

        assert session.query(WorkflowHumanDecision).count() == decision_count
        assert session.query(WorkflowStageSnapshot).count() == snapshot_count
        assert session.query(WorkflowTransitionEvent).count() == event_count


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"api_key": "must-not-persist"},
        {"nested": {"access_token": "must-not-persist"}},
        {"score": float("nan")},
        {"score": float("inf")},
    ],
)
def test_snapshot_tampering_and_invalid_payloads_fail_closed(invalid_payload: dict) -> None:
    with _session() as session:
        project, _ = _projects(session)
        run = _create_run(session, project)
        session.execute(
            update(WorkflowStageSnapshot)
            .where(WorkflowStageSnapshot.id == run.current_snapshot_id)
            .values(input_snapshot_hash=f"sha256:{'f' * 64}"),
        )
        session.commit()

        with pytest.raises(WorkflowSnapshotIntegrityError):
            submit_for_review(session, project.id, run.id, expected_version=0)

        with pytest.raises(WorkflowSnapshotInvalidError):
            _create_run(session, project, invalid_payload)
