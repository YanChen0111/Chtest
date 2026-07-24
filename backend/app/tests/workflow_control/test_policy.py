from __future__ import annotations

from dataclasses import replace

import pytest

from backend.app.modules.workflow_control.policy import (
    Actor,
    ApprovalDecision,
    ApprovalGrant,
    ControlledStage,
    GateState,
    TransitionAction,
    TransitionPolicyError,
    WorkflowKind,
    WorkflowPosition,
    apply_transition,
)


HASH_V1 = f"sha256:{'1' * 64}"
HASH_V2 = f"sha256:{'2' * 64}"


def _position(
    state: GateState,
    *,
    workflow_kind: WorkflowKind = WorkflowKind.REQUIREMENT_TO_EXECUTION,
    stage: ControlledStage = ControlledStage.SCOPE,
    completed_stages: tuple[ControlledStage, ...] = (),
    snapshot_hash: str = HASH_V1,
) -> WorkflowPosition:
    return WorkflowPosition(
        workflow_kind=workflow_kind,
        workflow_ref="workflow-1",
        subject_ref="requirement-1",
        stage=stage,
        state=state,
        input_snapshot_hash=snapshot_hash,
        completed_stages=completed_stages,
    )


def _approval(
    position: WorkflowPosition,
    **changes: object,
) -> ApprovalGrant:
    values = {
        "workflow_kind": position.workflow_kind,
        "workflow_ref": position.workflow_ref,
        "subject_ref": position.subject_ref,
        "stage": position.stage,
        "input_snapshot_hash": position.input_snapshot_hash,
        "allowed_action": TransitionAction.ADVANCE,
        "decision": ApprovalDecision.APPROVED,
        "granted_by": "local-reviewer",
        "actor": Actor.HUMAN,
    }
    values.update(changes)
    return ApprovalGrant(**values)  # type: ignore[arg-type]


def _approve(position: WorkflowPosition) -> tuple[WorkflowPosition, ApprovalGrant]:
    waiting_review = apply_transition(
        position,
        action=TransitionAction.SUBMIT_FOR_REVIEW,
        actor=Actor.AI,
    )
    waiting_approval = apply_transition(
        waiting_review,
        action=TransitionAction.COMPLETE_REVIEW,
        actor=Actor.HUMAN,
    )
    approval = _approval(waiting_approval)
    approved = apply_transition(
        waiting_approval,
        action=TransitionAction.APPROVE,
        actor=Actor.HUMAN,
        approval=approval,
    )
    return approved, approval


def test_human_approval_and_system_advance_create_a_new_stage_snapshot() -> None:
    approved, approval = _approve(_position(GateState.DRAFT))

    advanced = apply_transition(
        approved,
        action=TransitionAction.ADVANCE,
        actor=Actor.SYSTEM,
        approval=approval,
        target_stage=ControlledStage.REQUIREMENT_REVIEW,
        new_input_snapshot_hash=HASH_V2,
    )

    assert advanced == _position(
        GateState.DRAFT,
        stage=ControlledStage.REQUIREMENT_REVIEW,
        completed_stages=(ControlledStage.SCOPE,),
        snapshot_hash=HASH_V2,
    )
    assert approval.fingerprint.startswith("sha256:")
    assert len(approval.fingerprint) == 71


@pytest.mark.parametrize(
    "action",
    [
        TransitionAction.COMPLETE_REVIEW,
        TransitionAction.APPROVE,
        TransitionAction.ADVANCE,
        TransitionAction.REJECT,
        TransitionAction.REVISE,
        TransitionAction.BACK,
    ],
)
def test_ai_actor_cannot_control_or_advance_workflow(action: TransitionAction) -> None:
    with pytest.raises(TransitionPolicyError, match="AI_ACTOR_CANNOT_CONTROL_WORKFLOW"):
        apply_transition(
            _position(GateState.APPROVED),
            action=action,
            actor=Actor.AI,
            target_stage=ControlledStage.REQUIREMENT_REVIEW,
            new_input_snapshot_hash=HASH_V2,
        )


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        ({"actor": Actor.AI}, "HUMAN_APPROVAL_REQUIRED"),
        ({"decision": ApprovalDecision.REJECTED}, "APPROVAL_DECISION_REJECTED"),
        (
            {
                "workflow_kind": WorkflowKind.CICD_PATCH,
                "stage": ControlledStage.CHANGE_SCOPE,
            },
            "APPROVAL_WORKFLOW_KIND_MISMATCH",
        ),
        ({"workflow_ref": "workflow-2"}, "APPROVAL_WORKFLOW_MISMATCH"),
        ({"subject_ref": "requirement-2"}, "APPROVAL_SUBJECT_MISMATCH"),
        ({"stage": ControlledStage.REQUIREMENT_REVIEW}, "APPROVAL_STAGE_MISMATCH"),
        ({"input_snapshot_hash": HASH_V2}, "APPROVAL_SNAPSHOT_MISMATCH"),
    ],
)
def test_approval_grant_scope_mismatches_fail_closed(
    changes: dict[str, object],
    code: str,
) -> None:
    position = _position(GateState.WAITING_APPROVAL)
    with pytest.raises(TransitionPolicyError, match=code):
        apply_transition(
            position,
            action=TransitionAction.APPROVE,
            actor=Actor.HUMAN,
            approval=_approval(position, **changes),
        )


def test_changed_input_hash_invalidates_prior_approval() -> None:
    position = _position(GateState.WAITING_APPROVAL, snapshot_hash=HASH_V2)
    old_position = replace(position, input_snapshot_hash=HASH_V1)

    with pytest.raises(TransitionPolicyError, match="APPROVAL_SNAPSHOT_MISMATCH"):
        apply_transition(
            position,
            action=TransitionAction.APPROVE,
            actor=Actor.HUMAN,
            approval=_approval(old_position),
        )


def test_approval_fingerprint_uses_unambiguous_canonical_encoding() -> None:
    position = _position(GateState.WAITING_APPROVAL)
    first = _approval(
        replace(position, workflow_ref="a\x1fb", subject_ref="c"),
    )
    second = _approval(
        replace(position, workflow_ref="a", subject_ref="b\x1fc"),
    )

    assert first.fingerprint != second.fingerprint


@pytest.mark.parametrize(
    "action",
    [
        TransitionAction.COMPLETE_REVIEW,
        TransitionAction.APPROVE,
        TransitionAction.REJECT,
        TransitionAction.REVISE,
        TransitionAction.BACK,
    ],
)
def test_system_actor_cannot_perform_human_review_actions(action: TransitionAction) -> None:
    with pytest.raises(TransitionPolicyError, match="HUMAN_ACTOR_REQUIRED"):
        apply_transition(
            _position(GateState.WAITING_REVIEW),
            action=action,
            actor=Actor.SYSTEM,
        )


def test_human_cannot_submit_and_missing_approval_fails_closed() -> None:
    with pytest.raises(TransitionPolicyError, match="AI_OR_SYSTEM_ACTOR_REQUIRED"):
        apply_transition(
            _position(GateState.DRAFT),
            action=TransitionAction.SUBMIT_FOR_REVIEW,
            actor=Actor.HUMAN,
        )

    with pytest.raises(TransitionPolicyError, match="APPROVAL_REQUIRED"):
        apply_transition(
            _position(GateState.WAITING_APPROVAL),
            action=TransitionAction.APPROVE,
            actor=Actor.HUMAN,
        )


def test_invalid_runtime_enum_and_grant_capability_fail_at_boundary() -> None:
    with pytest.raises(ValueError, match="workflow_kind must be"):
        replace(_position(GateState.DRAFT), workflow_kind="unknown")

    with pytest.raises(ValueError, match="authorize only advance"):
        _approval(
            _position(GateState.WAITING_APPROVAL),
            allowed_action=TransitionAction.APPROVE,
        )


def test_missing_gates_stage_skips_and_non_system_advance_fail_closed() -> None:
    approved, approval = _approve(_position(GateState.DRAFT))

    with pytest.raises(TransitionPolicyError, match="SYSTEM_ACTOR_REQUIRED"):
        apply_transition(
            approved,
            action=TransitionAction.ADVANCE,
            actor=Actor.HUMAN,
            approval=approval,
            target_stage=ControlledStage.REQUIREMENT_REVIEW,
            new_input_snapshot_hash=HASH_V2,
        )

    with pytest.raises(TransitionPolicyError, match="STAGE_SKIP_OR_INVALID_TARGET"):
        apply_transition(
            approved,
            action=TransitionAction.ADVANCE,
            actor=Actor.SYSTEM,
            approval=approval,
            target_stage=ControlledStage.RISK_REVIEW,
            new_input_snapshot_hash=HASH_V2,
        )

    with pytest.raises(TransitionPolicyError, match="INVALID_GATE_STATE"):
        apply_transition(
            _position(GateState.WAITING_REVIEW),
            action=TransitionAction.ADVANCE,
            actor=Actor.SYSTEM,
            approval=_approval(_position(GateState.WAITING_REVIEW)),
            target_stage=ControlledStage.REQUIREMENT_REVIEW,
            new_input_snapshot_hash=HASH_V2,
        )


def test_reject_revise_and_back_require_human_and_a_new_snapshot() -> None:
    rejected = apply_transition(
        _position(GateState.WAITING_APPROVAL),
        action=TransitionAction.REJECT,
        actor=Actor.HUMAN,
    )
    revised = apply_transition(
        rejected,
        action=TransitionAction.REVISE,
        actor=Actor.HUMAN,
        new_input_snapshot_hash=HASH_V2,
    )
    requirement_position = _position(
        GateState.APPROVED,
        stage=ControlledStage.REQUIREMENT_REVIEW,
        completed_stages=(ControlledStage.SCOPE,),
    )
    backed = apply_transition(
        requirement_position,
        action=TransitionAction.BACK,
        actor=Actor.HUMAN,
        target_stage=ControlledStage.SCOPE,
        new_input_snapshot_hash=HASH_V2,
    )

    assert revised.state is GateState.DRAFT
    assert revised.input_snapshot_hash == HASH_V2
    assert backed == _position(GateState.DRAFT, snapshot_hash=HASH_V2)

    with pytest.raises(TransitionPolicyError, match="INPUT_SNAPSHOT_MUST_CHANGE"):
        apply_transition(
            rejected,
            action=TransitionAction.REVISE,
            actor=Actor.HUMAN,
            new_input_snapshot_hash=HASH_V1,
        )


def test_workflow_prefix_and_snapshot_hash_are_validated_at_boundary() -> None:
    with pytest.raises(ValueError, match="exact workflow prefix"):
        _position(
            GateState.DRAFT,
            stage=ControlledStage.RISK_REVIEW,
            completed_stages=(ControlledStage.SCOPE,),
        )

    with pytest.raises(ValueError, match="canonical sha256"):
        _position(GateState.DRAFT, snapshot_hash="sha256:not-a-digest")


def test_automation_plan_and_draft_are_separate_human_gates() -> None:
    plan_position = _position(
        GateState.DRAFT,
        stage=ControlledStage.AUTOMATION_PLAN_REVIEW,
        completed_stages=(
            ControlledStage.SCOPE,
            ControlledStage.REQUIREMENT_REVIEW,
            ControlledStage.RISK_REVIEW,
            ControlledStage.TEST_PLAN_REVIEW,
            ControlledStage.CASE_REVIEW,
        ),
    )
    approved_plan, plan_approval = _approve(plan_position)
    draft_position = apply_transition(
        approved_plan,
        action=TransitionAction.ADVANCE,
        actor=Actor.SYSTEM,
        approval=plan_approval,
        target_stage=ControlledStage.AUTOMATION_DRAFT_REVIEW,
        new_input_snapshot_hash=HASH_V2,
    )

    assert draft_position.state is GateState.DRAFT
    with pytest.raises(TransitionPolicyError, match="INVALID_GATE_STATE"):
        apply_transition(
            draft_position,
            action=TransitionAction.ADVANCE,
            actor=Actor.SYSTEM,
            approval=plan_approval,
            target_stage=ControlledStage.EXECUTION_APPROVAL,
            new_input_snapshot_hash=HASH_V1,
        )


def test_cicd_patch_workflow_cannot_skip_patch_review_or_apply_approval() -> None:
    scope = _position(
        GateState.DRAFT,
        workflow_kind=WorkflowKind.CICD_PATCH,
        stage=ControlledStage.CHANGE_SCOPE,
    )
    approved_scope, approval = _approve(scope)
    patch_review = apply_transition(
        approved_scope,
        action=TransitionAction.ADVANCE,
        actor=Actor.SYSTEM,
        approval=approval,
        target_stage=ControlledStage.UNIT_TEST_PATCH_REVIEW,
        new_input_snapshot_hash=HASH_V2,
    )

    assert patch_review.completed_stages == (ControlledStage.CHANGE_SCOPE,)
    with pytest.raises(TransitionPolicyError, match="INVALID_GATE_STATE"):
        apply_transition(
            patch_review,
            action=TransitionAction.ADVANCE,
            actor=Actor.SYSTEM,
            approval=approval,
            target_stage=ControlledStage.PATCH_APPLY_APPROVAL,
            new_input_snapshot_hash=HASH_V1,
        )


def test_terminal_stage_cannot_advance() -> None:
    position = _position(
        GateState.APPROVED,
        stage=ControlledStage.REPORT_REVIEW,
        completed_stages=(
            ControlledStage.SCOPE,
            ControlledStage.REQUIREMENT_REVIEW,
            ControlledStage.RISK_REVIEW,
            ControlledStage.TEST_PLAN_REVIEW,
            ControlledStage.CASE_REVIEW,
            ControlledStage.AUTOMATION_PLAN_REVIEW,
            ControlledStage.AUTOMATION_DRAFT_REVIEW,
            ControlledStage.EXECUTION_APPROVAL,
            ControlledStage.EXECUTION_RESULT_REVIEW,
        ),
    )
    with pytest.raises(TransitionPolicyError, match="NO_ADJACENT_STAGE"):
        apply_transition(
            position,
            action=TransitionAction.ADVANCE,
            actor=Actor.SYSTEM,
            approval=_approval(position),
            target_stage=ControlledStage.REPORT_REVIEW,
            new_input_snapshot_hash=HASH_V2,
        )
