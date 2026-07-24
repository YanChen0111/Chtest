from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum


_SNAPSHOT_HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


class Actor(StrEnum):
    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system"


class WorkflowKind(StrEnum):
    REQUIREMENT_TO_EXECUTION = "requirement_to_execution"
    CICD_PATCH = "cicd_patch"


class ControlledStage(StrEnum):
    SCOPE = "scope"
    REQUIREMENT_REVIEW = "requirement_review"
    RISK_REVIEW = "risk_review"
    TEST_PLAN_REVIEW = "test_plan_review"
    CASE_REVIEW = "case_review"
    AUTOMATION_PLAN_REVIEW = "automation_plan_review"
    AUTOMATION_DRAFT_REVIEW = "automation_draft_review"
    EXECUTION_APPROVAL = "execution_approval"
    EXECUTION_RESULT_REVIEW = "execution_result_review"
    REPORT_REVIEW = "report_review"
    CHANGE_SCOPE = "change_scope"
    UNIT_TEST_PATCH_REVIEW = "unit_test_patch_review"
    PATCH_APPLY_APPROVAL = "patch_apply_approval"
    REGRESSION_PLAN_REVIEW = "regression_plan_review"
    QUALITY_GATE_REVIEW = "quality_gate_review"


WORKFLOW_STAGE_SEQUENCES: dict[WorkflowKind, tuple[ControlledStage, ...]] = {
    WorkflowKind.REQUIREMENT_TO_EXECUTION: (
        ControlledStage.SCOPE,
        ControlledStage.REQUIREMENT_REVIEW,
        ControlledStage.RISK_REVIEW,
        ControlledStage.TEST_PLAN_REVIEW,
        ControlledStage.CASE_REVIEW,
        ControlledStage.AUTOMATION_PLAN_REVIEW,
        ControlledStage.AUTOMATION_DRAFT_REVIEW,
        ControlledStage.EXECUTION_APPROVAL,
        ControlledStage.EXECUTION_RESULT_REVIEW,
        ControlledStage.REPORT_REVIEW,
    ),
    WorkflowKind.CICD_PATCH: (
        ControlledStage.CHANGE_SCOPE,
        ControlledStage.UNIT_TEST_PATCH_REVIEW,
        ControlledStage.PATCH_APPLY_APPROVAL,
        ControlledStage.REGRESSION_PLAN_REVIEW,
        ControlledStage.QUALITY_GATE_REVIEW,
    ),
}


class GateState(StrEnum):
    DRAFT = "draft"
    WAITING_REVIEW = "waiting_review"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class TransitionAction(StrEnum):
    SUBMIT_FOR_REVIEW = "submit_for_review"
    COMPLETE_REVIEW = "complete_review"
    APPROVE = "approve"
    ADVANCE = "advance"
    REJECT = "reject"
    REVISE = "revise"
    BACK = "back"


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class TransitionPolicyError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class WorkflowPosition:
    workflow_kind: WorkflowKind
    workflow_ref: str
    subject_ref: str
    stage: ControlledStage
    state: GateState
    input_snapshot_hash: str
    completed_stages: tuple[ControlledStage, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.workflow_kind, WorkflowKind):
            raise ValueError("workflow_kind must be a WorkflowKind")
        if not isinstance(self.stage, ControlledStage):
            raise ValueError("stage must be a ControlledStage")
        if not isinstance(self.state, GateState):
            raise ValueError("state must be a GateState")
        if any(not isinstance(stage, ControlledStage) for stage in self.completed_stages):
            raise ValueError("completed_stages must contain ControlledStage values")
        _require_ref(self.workflow_ref, "workflow_ref")
        _require_ref(self.subject_ref, "subject_ref")
        _require_snapshot_hash(self.input_snapshot_hash)
        sequence = WORKFLOW_STAGE_SEQUENCES[self.workflow_kind]
        if self.stage not in sequence:
            raise ValueError("stage does not belong to workflow_kind")
        stage_index = sequence.index(self.stage)
        if self.completed_stages != sequence[:stage_index]:
            raise ValueError("completed_stages must be the exact workflow prefix")


@dataclass(frozen=True)
class ApprovalGrant:
    workflow_kind: WorkflowKind
    workflow_ref: str
    subject_ref: str
    stage: ControlledStage
    input_snapshot_hash: str
    allowed_action: TransitionAction
    decision: ApprovalDecision
    granted_by: str
    actor: Actor = Actor.HUMAN

    def __post_init__(self) -> None:
        if not isinstance(self.workflow_kind, WorkflowKind):
            raise ValueError("workflow_kind must be a WorkflowKind")
        if not isinstance(self.stage, ControlledStage):
            raise ValueError("stage must be a ControlledStage")
        if self.stage not in WORKFLOW_STAGE_SEQUENCES[self.workflow_kind]:
            raise ValueError("stage does not belong to workflow_kind")
        if not isinstance(self.allowed_action, TransitionAction):
            raise ValueError("allowed_action must be a TransitionAction")
        if not isinstance(self.decision, ApprovalDecision):
            raise ValueError("decision must be an ApprovalDecision")
        if not isinstance(self.actor, Actor):
            raise ValueError("actor must be an Actor")
        _require_ref(self.workflow_ref, "workflow_ref")
        _require_ref(self.subject_ref, "subject_ref")
        _require_ref(self.granted_by, "granted_by")
        _require_snapshot_hash(self.input_snapshot_hash)
        if self.allowed_action is not TransitionAction.ADVANCE:
            raise ValueError("ApprovalGrant may authorize only advance")

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            [
                self.workflow_kind.value,
                self.workflow_ref,
                self.subject_ref,
                self.stage.value,
                self.input_snapshot_hash,
                self.allowed_action.value,
                self.decision.value,
                self.granted_by,
                self.actor.value,
            ],
            ensure_ascii=True,
            separators=(",", ":"),
        )
        return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def apply_transition(
    position: WorkflowPosition,
    *,
    action: TransitionAction,
    actor: Actor,
    approval: ApprovalGrant | None = None,
    target_stage: ControlledStage | None = None,
    new_input_snapshot_hash: str | None = None,
) -> WorkflowPosition:
    if actor is Actor.AI and action is not TransitionAction.SUBMIT_FOR_REVIEW:
        raise TransitionPolicyError("AI_ACTOR_CANNOT_CONTROL_WORKFLOW")

    if action is TransitionAction.SUBMIT_FOR_REVIEW:
        if actor not in {Actor.AI, Actor.SYSTEM}:
            raise TransitionPolicyError("AI_OR_SYSTEM_ACTOR_REQUIRED")
        _require_state(position, GateState.DRAFT)
        _reject_extra_transition_input(target_stage, new_input_snapshot_hash, approval)
        return _replace_state(position, GateState.WAITING_REVIEW)

    if action is TransitionAction.ADVANCE:
        if actor is not Actor.SYSTEM:
            raise TransitionPolicyError("SYSTEM_ACTOR_REQUIRED")
        _require_state(position, GateState.APPROVED)
        _require_valid_approval(position, approval)
        expected = _adjacent_stage(position, direction=1)
        if target_stage is not expected:
            raise TransitionPolicyError("STAGE_SKIP_OR_INVALID_TARGET")
        snapshot_hash = _require_changed_snapshot(position, new_input_snapshot_hash)
        return WorkflowPosition(
            workflow_kind=position.workflow_kind,
            workflow_ref=position.workflow_ref,
            subject_ref=position.subject_ref,
            stage=expected,
            state=GateState.DRAFT,
            input_snapshot_hash=snapshot_hash,
            completed_stages=position.completed_stages + (position.stage,),
        )

    if actor is not Actor.HUMAN:
        raise TransitionPolicyError("HUMAN_ACTOR_REQUIRED")

    if action is TransitionAction.COMPLETE_REVIEW:
        _require_state(position, GateState.WAITING_REVIEW)
        _reject_extra_transition_input(target_stage, new_input_snapshot_hash, approval)
        return _replace_state(position, GateState.WAITING_APPROVAL)

    if action is TransitionAction.APPROVE:
        _require_state(position, GateState.WAITING_APPROVAL)
        if target_stage is not None or new_input_snapshot_hash is not None:
            raise TransitionPolicyError("INVALID_TRANSITION_INPUT")
        _require_valid_approval(position, approval)
        return _replace_state(position, GateState.APPROVED)

    if action is TransitionAction.REJECT:
        if position.state not in {GateState.WAITING_REVIEW, GateState.WAITING_APPROVAL}:
            raise TransitionPolicyError("INVALID_GATE_STATE")
        _reject_extra_transition_input(target_stage, new_input_snapshot_hash, approval)
        return _replace_state(position, GateState.REJECTED)

    if action is TransitionAction.REVISE:
        if position.state not in {
            GateState.WAITING_REVIEW,
            GateState.WAITING_APPROVAL,
            GateState.APPROVED,
            GateState.REJECTED,
        }:
            raise TransitionPolicyError("INVALID_GATE_STATE")
        if target_stage is not None or approval is not None:
            raise TransitionPolicyError("INVALID_TRANSITION_INPUT")
        snapshot_hash = _require_changed_snapshot(position, new_input_snapshot_hash)
        return _replace_position(position, state=GateState.DRAFT, snapshot_hash=snapshot_hash)

    if action is TransitionAction.BACK:
        if approval is not None:
            raise TransitionPolicyError("INVALID_TRANSITION_INPUT")
        expected = _adjacent_stage(position, direction=-1)
        if target_stage is not expected:
            raise TransitionPolicyError("STAGE_SKIP_OR_INVALID_TARGET")
        snapshot_hash = _require_changed_snapshot(position, new_input_snapshot_hash)
        target_index = WORKFLOW_STAGE_SEQUENCES[position.workflow_kind].index(expected)
        return WorkflowPosition(
            workflow_kind=position.workflow_kind,
            workflow_ref=position.workflow_ref,
            subject_ref=position.subject_ref,
            stage=expected,
            state=GateState.DRAFT,
            input_snapshot_hash=snapshot_hash,
            completed_stages=position.completed_stages[:target_index],
        )

    raise TransitionPolicyError("UNKNOWN_TRANSITION_ACTION")


def _require_state(position: WorkflowPosition, expected: GateState) -> None:
    if position.state is not expected:
        raise TransitionPolicyError("INVALID_GATE_STATE")


def _require_valid_approval(
    position: WorkflowPosition,
    approval: ApprovalGrant | None,
) -> None:
    if approval is None:
        raise TransitionPolicyError("APPROVAL_REQUIRED")
    if approval.actor is not Actor.HUMAN:
        raise TransitionPolicyError("HUMAN_APPROVAL_REQUIRED")
    if approval.decision is not ApprovalDecision.APPROVED:
        raise TransitionPolicyError("APPROVAL_DECISION_REJECTED")
    if approval.allowed_action is not TransitionAction.ADVANCE:
        raise TransitionPolicyError("APPROVAL_ACTION_MISMATCH")
    if approval.workflow_kind is not position.workflow_kind:
        raise TransitionPolicyError("APPROVAL_WORKFLOW_KIND_MISMATCH")
    if approval.workflow_ref != position.workflow_ref:
        raise TransitionPolicyError("APPROVAL_WORKFLOW_MISMATCH")
    if approval.subject_ref != position.subject_ref:
        raise TransitionPolicyError("APPROVAL_SUBJECT_MISMATCH")
    if approval.stage is not position.stage:
        raise TransitionPolicyError("APPROVAL_STAGE_MISMATCH")
    if approval.input_snapshot_hash != position.input_snapshot_hash:
        raise TransitionPolicyError("APPROVAL_SNAPSHOT_MISMATCH")


def _adjacent_stage(position: WorkflowPosition, *, direction: int) -> ControlledStage:
    sequence = WORKFLOW_STAGE_SEQUENCES[position.workflow_kind]
    index = sequence.index(position.stage) + direction
    if index < 0 or index >= len(sequence):
        raise TransitionPolicyError("NO_ADJACENT_STAGE")
    return sequence[index]


def _require_changed_snapshot(
    position: WorkflowPosition,
    new_input_snapshot_hash: str | None,
) -> str:
    if new_input_snapshot_hash is None:
        raise TransitionPolicyError("NEW_INPUT_SNAPSHOT_REQUIRED")
    try:
        _require_snapshot_hash(new_input_snapshot_hash)
    except ValueError as exc:
        raise TransitionPolicyError("INVALID_INPUT_SNAPSHOT_HASH") from exc
    if new_input_snapshot_hash == position.input_snapshot_hash:
        raise TransitionPolicyError("INPUT_SNAPSHOT_MUST_CHANGE")
    return new_input_snapshot_hash


def _replace_state(position: WorkflowPosition, state: GateState) -> WorkflowPosition:
    return _replace_position(position, state=state, snapshot_hash=position.input_snapshot_hash)


def _replace_position(
    position: WorkflowPosition,
    *,
    state: GateState,
    snapshot_hash: str,
) -> WorkflowPosition:
    return WorkflowPosition(
        workflow_kind=position.workflow_kind,
        workflow_ref=position.workflow_ref,
        subject_ref=position.subject_ref,
        stage=position.stage,
        state=state,
        input_snapshot_hash=snapshot_hash,
        completed_stages=position.completed_stages,
    )


def _reject_extra_transition_input(
    target_stage: ControlledStage | None,
    new_input_snapshot_hash: str | None,
    approval: ApprovalGrant | None,
) -> None:
    if target_stage is not None or new_input_snapshot_hash is not None or approval is not None:
        raise TransitionPolicyError("INVALID_TRANSITION_INPUT")


def _require_ref(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _require_snapshot_hash(value: str) -> None:
    if not _SNAPSHOT_HASH_PATTERN.fullmatch(value):
        raise ValueError("input_snapshot_hash must be canonical sha256:<lowercase-hex>")
