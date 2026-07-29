from __future__ import annotations

import hashlib
import json
import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service as ai_runtime_service
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.model_config import resolve_model_identity
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.ai_runtime.providers.base import ProviderArtifactPayload
from backend.app.modules.automation.models import AutomationDraft, AutomationPlan
from backend.app.modules.automation.schemas import (
    AutomationDraftApproveRequest,
    AutomationDraftCreateRequest,
    AutomationDraftEditRequest,
    AutomationDraftReviewWorkflowActionRequest,
    AutomationDraftReviewWorkflowContinueRequest,
    AutomationDraftReviewWorkflowEditRequest,
    AutomationDraftReviewWorkflowRead,
    AutomationPlanApproveRequest,
    AutomationPlanCreateRequest,
    AutomationPlanReviewWorkflowActionRequest,
    AutomationPlanReviewWorkflowContinueRequest,
    AutomationPlanReviewWorkflowEditRequest,
    AutomationPlanReviewWorkflowRead,
    AutomationPlanUpdateRequest,
)
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase
from backend.app.modules.cases.service import case_domain_aligned, extract_domain_terms
from backend.app.modules.extension import service as extension_service
from backend.app.modules.knowledge import service as knowledge_service
from backend.app.modules.projects.models import Project
from backend.app.modules.prompt_skill import service as prompt_skill_service
from backend.app.modules.requirements.models import Requirement, RequirementReview
from backend.app.modules.review_history.service import append_review_history
from backend.app.modules.workflow_control import service as workflow_service
from backend.app.modules.workflow_control.models import WorkflowHumanDecision
from backend.app.modules.workflow_control.policy import ApprovalDecision, ControlledStage, GateState, TransitionAction, WorkflowKind
from backend.app.modules.workflow_control.schemas import HumanApprovalCreate, HumanReviewCreate, WorkflowRevisionCreate
from backend.app.workers.enqueue import FakeAIQueue, enqueue_ai_task
from backend.app.workers.handlers.ai_task_handler import run_ai_task


class ProjectNotFoundError(Exception):
    pass


class TestCaseNotFoundError(Exception):
    pass


class RequirementNotFoundError(Exception):
    pass


class AutomationDraftInvalidInputError(Exception):
    pass


class AutomationDraftGenerationFailedError(Exception):
    pass


class AutomationDraftSchemaInvalidError(Exception):
    pass


class AutomationDraftQualityGateError(Exception):
    pass


class AutomationDraftNotFoundError(Exception):
    pass


class AutomationDraftInvalidActionError(Exception):
    pass


class AutomationPlanNotFoundError(Exception):
    pass


class AutomationPlanInvalidInputError(Exception):
    pass


class AutomationPlanInvalidActionError(Exception):
    pass


class AutomationPlanNotApprovedError(Exception):
    pass


class AutomationPlanSourceNotApprovedError(Exception):
    pass


class AutomationPlanReviewWorkflowStageError(Exception):
    code = "WORKFLOW_STAGE_MISMATCH"


class AutomationPlanReviewGateError(Exception):
    code = "AUTOMATION_PLAN_REVIEW_PLAN_APPROVAL_REQUIRED"


class AutomationDraftReviewWorkflowStageError(Exception):
    code = "WORKFLOW_STAGE_MISMATCH"


class AutomationDraftReviewGateError(Exception):
    code = "AUTOMATION_DRAFT_REVIEW_DRAFT_APPROVAL_REQUIRED"


WorkflowPersistenceError = workflow_service.WorkflowPersistenceError


class ContextArtifactNotFoundError(Exception):
    pass


APPROVED_CASE_STATUSES = {"approved", "approved_after_edit"}
AUTOMATION_RELEVANT_SEMANTIC_SCORE = 0.18
GENERIC_KNOWLEDGE_TERMS = {
    "api",
    "app",
    "boundary",
    "case",
    "data",
    "flow",
    "page",
    "rule",
    "scenario",
    "system",
    "test",
    "ui",
    "user",
    "功能",
    "场景",
    "数据",
    "测试",
    "系统",
    "用户",
    "页面",
}
DEMO_ADAPTER_PATTERN = re.compile(
    r"\b(?:fake|stub|demo)[A-Za-z0-9_]*(?:adapter|client|driver|service|app|page|fixture|repository|factory)\b"
    r"|\b(?:make|build|get|create)_(?:fake|stub|demo)_[A-Za-z0-9_]*"
    r"(?:adapter|client|driver|service|app|page|fixture|repository|factory)\b",
    re.IGNORECASE,
)
LIMITED_EVIDENCE_PATTERN = re.compile(
    r"\b(?:fake|stub|demo|mock|double|placeholder|assert\s+True)\b",
    re.IGNORECASE,
)


def create_automation_plan(
    session: Session,
    store: LocalArtifactStore,
    data: AutomationPlanCreateRequest,
) -> AutomationPlan:
    project = session.get(Project, data.project_id)
    if project is None:
        raise ProjectNotFoundError
    test_case = session.get(TestCase, data.test_case_id)
    if test_case is None or test_case.project_id != data.project_id:
        raise TestCaseNotFoundError
    if test_case.review_status not in APPROVED_CASE_STATUSES or test_case.status != "active":
        raise AutomationPlanSourceNotApprovedError
    if test_case.source_candidate_id is None:
        raise AutomationPlanSourceNotApprovedError
    candidate = session.get(GeneratedCaseCandidate, test_case.source_candidate_id)
    if candidate is None or candidate.project_id != data.project_id:
        raise AutomationPlanSourceNotApprovedError
    generation_task = session.get(CaseGenerationTask, candidate.generation_task_id)
    if generation_task is None or generation_task.project_id != data.project_id:
        raise AutomationPlanSourceNotApprovedError
    validate_context_artifacts(session, data.project_id, data.context_artifact_ids)

    prompt = prompt_skill_service.get_active_prompt_version_by_ref(session, data.prompt_version)
    skill = prompt_skill_service.get_active_skill_version_by_ref(session, data.skill_version)
    retrieval_payload, used_context_artifact_ids = retrieve_automation_plan_knowledge(
        session,
        store,
        project_id=data.project_id,
        test_case=test_case,
        candidate=candidate,
        use_knowledge=data.use_knowledge,
    )
    plan_payload = build_plan_payload(test_case, data.target_framework, retrieval_payload)
    model_provider, model_name = resolve_model_identity(
        model_provider=data.model_provider,
        model_name=data.model_name,
        default_provider="mock",
        default_model_name="mock-automation-plan",
    )
    ai_task = AITask(
        project_id=data.project_id,
        agent_name="AutomationPlanAgent",
        task_type="automation_plan_generation",
        prompt_version_id=prompt.id,
        skill_version_id=skill.id,
        model_provider=model_provider,
        model_name=model_name,
        status="succeeded",
        input_json={
            "test_case_id": str(test_case.id),
            "source_candidate_id": str(candidate.id),
            "requirement_id": str(generation_task.requirement_id),
            "requirement_review_id": str(generation_task.requirement_review_id)
            if generation_task.requirement_review_id is not None
            else None,
            "target_framework": data.target_framework,
            "use_knowledge": data.use_knowledge,
            "context_artifact_ids": [str(context_id) for context_id in data.context_artifact_ids],
            "knowledge_retrieval": retrieval_payload,
        },
        output_json={
            "plan_title": plan_payload["title"],
            "used_knowledge": bool(retrieval_payload),
            "used_context_artifact_ids": [str(context_id) for context_id in used_context_artifact_ids],
        },
        context_artifact_ids=data.context_artifact_ids,
    )
    session.add(ai_task)
    session.flush()
    knowledge_service.link_retrieval_run_to_ai_task(
        session,
        project_id=data.project_id,
        retrieval_payload=retrieval_payload,
        ai_task_id=ai_task.id,
    )

    retrieval_artifact = None
    if retrieval_payload is not None:
        retrieval_artifact = attach_plan_retrieval_evidence_artifact(
            session,
            store,
            ai_task,
            retrieval_payload,
            used_context_artifact_ids,
        )

    plan = AutomationPlan(
        project_id=data.project_id,
        test_case_id=test_case.id,
        requirement_id=generation_task.requirement_id,
        requirement_review_id=generation_task.requirement_review_id,
        source_candidate_id=candidate.id,
        ai_task_id=ai_task.id,
        knowledge_retrieval_artifact_id=retrieval_artifact.id if retrieval_artifact is not None else None,
        target_framework=data.target_framework,
        title=plan_payload["title"],
        plan_json=plan_payload["plan"],
        execution_steps_json=plan_payload["execution_steps"],
        test_data_json=plan_payload["test_data"],
        dependency_notes=plan_payload["dependency_notes"],
        risk_notes=plan_payload["risk_notes"],
        used_context_artifact_ids=used_context_artifact_ids,
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def get_automation_plan(session: Session, plan_id: uuid.UUID) -> AutomationPlan:
    plan = session.get(AutomationPlan, plan_id)
    if plan is None:
        raise AutomationPlanNotFoundError
    return plan


def edit_automation_plan(session: Session, plan_id: uuid.UUID, data: AutomationPlanUpdateRequest) -> AutomationPlan:
    plan = get_automation_plan(session, plan_id)
    if plan.status not in {"plan_generated", "edited"}:
        raise AutomationPlanInvalidActionError
    from_status = plan.status
    if data.title is not None:
        plan.title = data.title
    if data.execution_steps is not None:
        plan.execution_steps_json = list(data.execution_steps)
    if data.test_data is not None:
        plan.test_data_json = dict(data.test_data)
    if data.dependency_notes is not None:
        plan.dependency_notes = data.dependency_notes
    if data.risk_notes is not None:
        plan.risk_notes = data.risk_notes
    plan.review_comment = data.review_comment
    plan.status = "edited"
    session.add(plan)
    append_review_history(
        session,
        project_id=plan.project_id,
        entity_type="AutomationPlan",
        entity_id=plan.id,
        action="edit",
        from_status=from_status,
        to_status=plan.status,
        comment=data.review_comment,
    )
    session.commit()
    session.refresh(plan)
    return plan


def approve_automation_plan(
    session: Session,
    plan_id: uuid.UUID,
    data: AutomationPlanApproveRequest,
) -> AutomationPlan:
    plan = get_automation_plan(session, plan_id)
    if data.action != "approve" or plan.status not in {"plan_generated", "edited"}:
        raise AutomationPlanInvalidActionError
    from_status = plan.status
    plan.status = "approved"
    plan.review_comment = data.review_comment
    session.add(plan)
    append_review_history(
        session,
        project_id=plan.project_id,
        entity_type="AutomationPlan",
        entity_id=plan.id,
        action="approve",
        from_status=from_status,
        to_status=plan.status,
        comment=data.review_comment,
    )
    session.commit()
    session.refresh(plan)
    return plan


def get_automation_plan_review_workflow_detail(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
) -> AutomationPlanReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    return _automation_plan_review_workflow_read(session, project_id, review.id, run, snapshot)


def submit_automation_plan_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationPlanReviewWorkflowActionRequest,
) -> AutomationPlanReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, _ = _automation_plan_review_workflow(session, project_id, review.id)
    workflow_service.submit_for_review(session, project_id, run.id, expected_version=data.expected_version)
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    return _automation_plan_review_workflow_read(session, project_id, review.id, run, snapshot)


def complete_automation_plan_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationPlanReviewWorkflowActionRequest,
) -> AutomationPlanReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, _ = _automation_plan_review_workflow(session, project_id, review.id)
    workflow_service.complete_human_review(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanReviewCreate(reviewer=data.reviewer, comment=data.comment),
    )
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    return _automation_plan_review_workflow_read(session, project_id, review.id, run, snapshot)


def edit_automation_plan_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationPlanReviewWorkflowEditRequest,
) -> AutomationPlanReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    payload = dict(snapshot.input_payload_json)
    payload["plan_decisions"] = _json_safe(data.plan_decisions)
    payload["generated_plan_ids"] = [
        str(plan_id) for plan_id in _automation_plan_ids_for_requirement_review(session, project_id, review.id, payload)
    ]
    revised_run, _, _ = workflow_service.revise_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=WorkflowRevisionCreate(
            reviewer=data.reviewer,
            comment=data.comment,
            input_payload=payload,
        ),
    )
    workflow_service.submit_for_review(
        session,
        project_id,
        revised_run.id,
        expected_version=revised_run.lock_version,
    )
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    return _automation_plan_review_workflow_read(session, project_id, review.id, run, snapshot)


def decide_automation_plan_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationPlanReviewWorkflowActionRequest,
    *,
    decision: ApprovalDecision,
) -> AutomationPlanReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    if decision is ApprovalDecision.APPROVED:
        _require_approved_automation_plan(session, project_id, snapshot.input_payload_json)
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
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    return _automation_plan_review_workflow_read(session, project_id, review.id, run, snapshot)


def continue_automation_plan_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationPlanReviewWorkflowContinueRequest,
) -> AutomationPlanReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    _require_approved_automation_plan(session, project_id, snapshot.input_payload_json)
    workflow_service.advance_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        approval_decision_id=data.approval_decision_id,
        target_stage=ControlledStage.AUTOMATION_DRAFT_REVIEW,
        next_input_payload=_automation_draft_review_input_payload(session, project_id, snapshot),
    )
    run, snapshot = _review_workflow(session, project_id, review.id)
    return _automation_plan_review_workflow_read(session, project_id, review.id, run, snapshot)


def approve_and_continue_automation_plan_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationPlanReviewWorkflowActionRequest,
) -> AutomationPlanReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_plan_review_workflow(session, project_id, review.id)
    _require_approved_automation_plan(session, project_id, snapshot.input_payload_json)
    workflow_service.approve_and_advance_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanReviewCreate(reviewer=data.reviewer, comment=data.comment),
        target_stage=ControlledStage.AUTOMATION_DRAFT_REVIEW,
        next_input_payload=_automation_draft_review_input_payload(session, project_id, snapshot),
    )
    run, snapshot = _review_workflow(session, project_id, review.id)
    return _automation_plan_review_workflow_read(session, project_id, review.id, run, snapshot)


def get_automation_draft_review_workflow_detail(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
) -> AutomationDraftReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    return _automation_draft_review_workflow_read(session, project_id, review.id, run, snapshot)


def submit_automation_draft_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationDraftReviewWorkflowActionRequest,
) -> AutomationDraftReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, _ = _automation_draft_review_workflow(session, project_id, review.id)
    workflow_service.submit_for_review(session, project_id, run.id, expected_version=data.expected_version)
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    return _automation_draft_review_workflow_read(session, project_id, review.id, run, snapshot)


def complete_automation_draft_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationDraftReviewWorkflowActionRequest,
) -> AutomationDraftReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, _ = _automation_draft_review_workflow(session, project_id, review.id)
    workflow_service.complete_human_review(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanReviewCreate(reviewer=data.reviewer, comment=data.comment),
    )
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    return _automation_draft_review_workflow_read(session, project_id, review.id, run, snapshot)


def edit_automation_draft_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationDraftReviewWorkflowEditRequest,
) -> AutomationDraftReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    payload = dict(snapshot.input_payload_json)
    payload["draft_decisions"] = _json_safe(data.draft_decisions)
    payload["generated_draft_ids"] = [
        str(draft_id) for draft_id in _automation_draft_ids_for_requirement_review(session, project_id, payload)
    ]
    revised_run, _, _ = workflow_service.revise_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=WorkflowRevisionCreate(reviewer=data.reviewer, comment=data.comment, input_payload=payload),
    )
    workflow_service.submit_for_review(session, project_id, revised_run.id, expected_version=revised_run.lock_version)
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    return _automation_draft_review_workflow_read(session, project_id, review.id, run, snapshot)


def decide_automation_draft_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationDraftReviewWorkflowActionRequest,
    *,
    decision: ApprovalDecision,
) -> AutomationDraftReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    if decision is ApprovalDecision.APPROVED:
        _require_approved_automation_draft(session, project_id, snapshot.input_payload_json)
    workflow_service.record_human_approval(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanApprovalCreate(reviewer=data.reviewer, comment=data.comment, decision=decision),
    )
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    return _automation_draft_review_workflow_read(session, project_id, review.id, run, snapshot)


def continue_automation_draft_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationDraftReviewWorkflowContinueRequest,
) -> AutomationDraftReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    _require_approved_automation_draft(session, project_id, snapshot.input_payload_json)
    workflow_service.advance_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        approval_decision_id=data.approval_decision_id,
        target_stage=ControlledStage.EXECUTION_APPROVAL,
        next_input_payload=_execution_approval_input_payload(session, project_id, snapshot),
    )
    run, snapshot = _review_workflow(session, project_id, review.id)
    return _automation_draft_review_workflow_read(session, project_id, review.id, run, snapshot)


def approve_and_continue_automation_draft_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: AutomationDraftReviewWorkflowActionRequest,
) -> AutomationDraftReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _automation_draft_review_workflow(session, project_id, review.id)
    _require_approved_automation_draft(session, project_id, snapshot.input_payload_json)
    workflow_service.approve_and_advance_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanReviewCreate(reviewer=data.reviewer, comment=data.comment),
        target_stage=ControlledStage.EXECUTION_APPROVAL,
        next_input_payload=_execution_approval_input_payload(session, project_id, snapshot),
    )
    run, snapshot = _review_workflow(session, project_id, review.id)
    return _automation_draft_review_workflow_read(session, project_id, review.id, run, snapshot)


def create_automation_draft(
    session: Session,
    store: LocalArtifactStore,
    data: AutomationDraftCreateRequest,
) -> tuple[AutomationDraft, AITask]:
    project = session.get(Project, data.project_id)
    if project is None:
        raise ProjectNotFoundError
    automation_plan = None
    test_case_id = data.test_case_id
    requirement_id = data.requirement_id
    target_framework = data.target_framework
    if data.automation_plan_id is not None:
        automation_plan = session.get(AutomationPlan, data.automation_plan_id)
        if automation_plan is None or automation_plan.project_id != data.project_id:
            raise AutomationPlanNotFoundError
        if automation_plan.status != "approved":
            raise AutomationPlanNotApprovedError
        if test_case_id is not None and test_case_id != automation_plan.test_case_id:
            raise AutomationDraftInvalidInputError
        if requirement_id is not None and requirement_id != automation_plan.requirement_id:
            raise AutomationDraftInvalidInputError
        test_case_id = automation_plan.test_case_id
        requirement_id = automation_plan.requirement_id
        target_framework = automation_plan.target_framework

    test_case = None
    if test_case_id is not None:
        test_case = session.get(TestCase, test_case_id)
        if test_case is None or test_case.project_id != data.project_id:
            raise TestCaseNotFoundError
    requirement = None
    if requirement_id is not None:
        requirement = session.get(Requirement, requirement_id)
        if requirement is None or requirement.project_id != data.project_id:
            raise RequirementNotFoundError
    if test_case is None and requirement is None:
        raise AutomationDraftInvalidInputError

    prompt = prompt_skill_service.get_active_prompt_version_by_ref(session, data.prompt_version)
    skill = prompt_skill_service.get_active_skill_version_by_ref(session, data.skill_version)
    source_title = test_case.title if test_case is not None else requirement.title
    model_provider, model_name = resolve_model_identity(
        model_provider=data.model_provider,
        model_name=data.model_name,
        default_provider="mock",
        default_model_name="mock-automation-draft",
    )
    ai_task = AITask(
        project_id=data.project_id,
        agent_name="AutomationDraftAgent",
        task_type="automation_draft_generation",
        prompt_version_id=prompt.id,
        skill_version_id=skill.id,
        model_provider=model_provider,
        model_name=model_name,
        status="created",
        input_json={
            "automation_plan_id": str(automation_plan.id) if automation_plan is not None else None,
            "automation_plan": automation_plan_prompt_summary(automation_plan) if automation_plan is not None else None,
            "test_case_id": str(test_case_id) if test_case_id is not None else None,
            "test_case": test_case_prompt_summary(test_case) if test_case is not None else None,
            "requirement_id": str(requirement_id) if requirement_id is not None else None,
            "requirement": requirement_prompt_summary(requirement) if requirement is not None else None,
            "target_framework": target_framework,
            "source_title": source_title,
        },
    )
    session.add(ai_task)
    session.commit()
    session.refresh(ai_task)

    queue = FakeAIQueue()
    job = enqueue_ai_task(session, queue, ai_task.id)
    run_ai_task(session, store, job)
    session.refresh(ai_task)

    if ai_task.status != "succeeded":
        raise AutomationDraftGenerationFailedError

    try:
        validate_automation_draft_output(ai_task.output_json, target_framework)
    except AutomationDraftSchemaInvalidError:
        mark_automation_draft_schema_invalid(session, ai_task)
        raise

    draft_payload = automation_draft_payload_from_output(
        ai_task.output_json,
        source_title=source_title,
        target_framework=target_framework,
        automation_plan=automation_plan,
    )

    draft = AutomationDraft(
        project_id=data.project_id,
        test_case_id=test_case_id,
        requirement_id=requirement_id,
        ai_task_id=ai_task.id,
        automation_plan_id=automation_plan.id if automation_plan is not None else None,
        target_framework=target_framework,
        title=draft_payload["title"],
        draft_code=draft_payload["draft_code"],
        draft_language=draft_payload["draft_language"],
        suggested_file_path=draft_payload["suggested_file_path"],
        execution_notes=draft_payload["execution_notes"],
        risk_notes=draft_payload["risk_notes"],
    )
    session.add(draft)
    if automation_plan is not None:
        from_status = automation_plan.status
        automation_plan.status = "draft_generated"
        session.add(automation_plan)
        append_review_history(
            session,
            project_id=automation_plan.project_id,
            entity_type="AutomationPlan",
            entity_id=automation_plan.id,
            related_entity_type="AutomationDraft",
            related_entity_id=draft.id,
            action="generate_draft",
            from_status=from_status,
            to_status=automation_plan.status,
            comment="Generated AutomationDraft from approved AutomationPlan.",
        )
    session.commit()
    session.refresh(draft)
    session.refresh(ai_task)
    return draft, ai_task


def get_automation_draft(session: Session, draft_id: uuid.UUID) -> AutomationDraft:
    draft = session.get(AutomationDraft, draft_id)
    if draft is None:
        raise AutomationDraftNotFoundError
    return draft


def edit_automation_draft(session: Session, draft_id: uuid.UUID, data: AutomationDraftEditRequest) -> AutomationDraft:
    draft = get_automation_draft(session, draft_id)
    if draft.status == "approved":
        raise AutomationDraftInvalidActionError
    from_status = draft.status
    draft.draft_code = data.draft_code
    draft.suggested_file_path = data.suggested_file_path
    draft.execution_notes = data.execution_notes
    draft.risk_notes = data.risk_notes
    draft.review_comment = data.review_comment
    draft.status = "edited"
    session.add(draft)
    append_review_history(
        session,
        project_id=draft.project_id,
        entity_type="AutomationDraft",
        entity_id=draft.id,
        action="edit",
        from_status=from_status,
        to_status=draft.status,
        comment=data.review_comment,
    )
    session.commit()
    session.refresh(draft)
    return draft


def approve_automation_draft(session: Session, draft_id: uuid.UUID, data: AutomationDraftApproveRequest) -> AutomationDraft:
    draft = get_automation_draft(session, draft_id)
    if data.action != "approve" or draft.status not in {"draft_generated", "edited"}:
        raise AutomationDraftInvalidActionError
    validate_automation_draft_approval(draft)
    from_status = draft.status
    draft.status = "approved"
    draft.review_comment = data.review_comment
    session.add(draft)
    append_review_history(
        session,
        project_id=draft.project_id,
        entity_type="AutomationDraft",
        entity_id=draft.id,
        action="approve",
        from_status=from_status,
        to_status=draft.status,
        comment=data.review_comment,
    )
    session.commit()
    session.refresh(draft)
    return draft


def _review_workflow(session: Session, project_id: uuid.UUID, requirement_review_id: uuid.UUID):
    return workflow_service.get_workflow_run_for_subject(
        session,
        project_id,
        workflow_kind=WorkflowKind.REQUIREMENT_TO_EXECUTION,
        subject_ref=str(requirement_review_id),
    )


def _automation_plan_review_workflow(session: Session, project_id: uuid.UUID, requirement_review_id: uuid.UUID):
    run, snapshot = _review_workflow(session, project_id, requirement_review_id)
    if run.current_stage != ControlledStage.AUTOMATION_PLAN_REVIEW.value:
        raise AutomationPlanReviewWorkflowStageError
    return run, snapshot


def _automation_draft_review_workflow(session: Session, project_id: uuid.UUID, requirement_review_id: uuid.UUID):
    run, snapshot = _review_workflow(session, project_id, requirement_review_id)
    if run.current_stage != ControlledStage.AUTOMATION_DRAFT_REVIEW.value:
        raise AutomationDraftReviewWorkflowStageError
    return run, snapshot


def _require_requirement_review_in_project(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
) -> RequirementReview:
    row = session.execute(
        select(RequirementReview, Requirement)
        .join(Requirement, Requirement.id == RequirementReview.requirement_id)
        .where(RequirementReview.id == requirement_review_id, Requirement.project_id == project_id),
    ).one_or_none()
    if row is None:
        raise AutomationPlanReviewWorkflowStageError
    return row[0]


def _automation_plan_review_workflow_read(
    session: Session,
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    run,
    snapshot,
) -> AutomationPlanReviewWorkflowRead:
    payload = snapshot.input_payload_json
    latest_approval = session.scalar(
        select(WorkflowHumanDecision)
        .where(
            WorkflowHumanDecision.project_id == run.project_id,
            WorkflowHumanDecision.workflow_run_id == run.id,
            WorkflowHumanDecision.snapshot_id == run.current_snapshot_id,
            WorkflowHumanDecision.action == TransitionAction.APPROVE.value,
            WorkflowHumanDecision.decision == ApprovalDecision.APPROVED.value,
        )
        .order_by(WorkflowHumanDecision.created_at.desc(), WorkflowHumanDecision.id.desc()),
    )
    plan_ids = _automation_plan_ids_for_requirement_review(session, project_id, review_id, payload)
    return AutomationPlanReviewWorkflowRead(
        project_id=project_id,
        requirement_review_id=review_id,
        workflow={
            "run_id": str(run.id),
            "stage": run.current_stage,
            "state": run.gate_state,
            "lock_version": run.lock_version,
            "snapshot_id": str(run.current_snapshot_id),
            "approval_decision_id": str(latest_approval.id) if latest_approval else None,
            "can_submit": run.gate_state == GateState.DRAFT.value,
            "can_complete_review": run.gate_state == GateState.WAITING_REVIEW.value,
            "can_edit": run.gate_state in {
                GateState.WAITING_REVIEW.value,
                GateState.WAITING_APPROVAL.value,
                GateState.APPROVED.value,
                GateState.REJECTED.value,
            },
            "can_approve": run.gate_state == GateState.WAITING_APPROVAL.value,
            "can_continue": run.gate_state == GateState.APPROVED.value and latest_approval is not None,
        },
        source_case_review_snapshot_id=payload.get("source_case_review_snapshot_id"),
        source_case_review_snapshot_hash=payload.get("source_case_review_snapshot_hash"),
        source_test_plan_review_snapshot_id=payload.get("source_test_plan_review_snapshot_id"),
        source_test_plan_review_snapshot_hash=payload.get("source_test_plan_review_snapshot_hash"),
        approved_candidate_ids=list(payload.get("approved_candidate_ids", [])),
        approved_test_case_ids=list(payload.get("approved_test_case_ids", [])),
        generated_plan_ids=plan_ids,
        plan_decisions=_automation_plan_decisions_for_ids(session, project_id, plan_ids),
    )


def _automation_plan_ids_for_requirement_review(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    payload: dict,
) -> list[uuid.UUID]:
    approved_test_case_ids = [
        uuid.UUID(str(test_case_id))
        for test_case_id in payload.get("approved_test_case_ids", [])
        if str(test_case_id)
    ]
    if not approved_test_case_ids:
        return []
    rows = session.scalars(
        select(AutomationPlan.id)
        .where(
            AutomationPlan.project_id == project_id,
            AutomationPlan.requirement_review_id == requirement_review_id,
            AutomationPlan.test_case_id.in_(approved_test_case_ids),
        )
        .order_by(AutomationPlan.created_at.asc(), AutomationPlan.id.asc()),
    )
    return list(rows)


def _automation_plan_decisions_for_ids(
    session: Session,
    project_id: uuid.UUID,
    plan_ids: list[uuid.UUID],
) -> list[dict[str, object]]:
    if not plan_ids:
        return []
    plans = list(
        session.scalars(
            select(AutomationPlan)
            .where(
                AutomationPlan.project_id == project_id,
                AutomationPlan.id.in_(plan_ids),
            )
            .order_by(AutomationPlan.created_at.asc(), AutomationPlan.id.asc()),
        ),
    )
    return [
        {
            "automation_plan_id": str(plan.id),
            "test_case_id": str(plan.test_case_id),
            "status": plan.status,
            "target_framework": plan.target_framework,
            "review_comment": plan.review_comment,
        }
        for plan in plans
    ]


def _require_approved_automation_plan(session: Session, project_id: uuid.UUID, payload: dict) -> None:
    review_id = uuid.UUID(str(payload.get("requirement_review_id")))
    plan_ids = _automation_plan_ids_for_requirement_review(session, project_id, review_id, payload)
    if not plan_ids:
        raise AutomationPlanReviewGateError
    approved_plan_id = session.scalar(
        select(AutomationPlan.id)
        .where(
            AutomationPlan.project_id == project_id,
            AutomationPlan.id.in_(plan_ids),
            AutomationPlan.status == "approved",
        )
        .limit(1),
    )
    if approved_plan_id is None:
        raise AutomationPlanReviewGateError


def _automation_draft_review_input_payload(session: Session, project_id: uuid.UUID, source_snapshot) -> dict[str, object]:
    payload = source_snapshot.input_payload_json
    review_id = uuid.UUID(str(payload.get("requirement_review_id")))
    plan_ids = _automation_plan_ids_for_requirement_review(session, project_id, review_id, payload)
    approved_plan_ids = list(
        session.scalars(
            select(AutomationPlan.id)
            .where(
                AutomationPlan.project_id == project_id,
                AutomationPlan.id.in_(plan_ids),
                AutomationPlan.status == "approved",
            )
            .order_by(AutomationPlan.created_at.asc(), AutomationPlan.id.asc()),
        ),
    )
    approved_test_case_ids = list(
        session.scalars(
            select(AutomationPlan.test_case_id)
            .where(
                AutomationPlan.project_id == project_id,
                AutomationPlan.id.in_(approved_plan_ids),
            )
            .order_by(AutomationPlan.created_at.asc(), AutomationPlan.id.asc()),
        ),
    )
    return {
        "requirement_id": payload.get("requirement_id"),
        "requirement_review_id": payload.get("requirement_review_id"),
        "source_automation_plan_review_snapshot_id": str(source_snapshot.id),
        "source_automation_plan_review_snapshot_hash": source_snapshot.input_snapshot_hash,
        "source_case_review_snapshot_id": payload.get("source_case_review_snapshot_id"),
        "source_case_review_snapshot_hash": payload.get("source_case_review_snapshot_hash"),
        "source_test_plan_review_snapshot_id": payload.get("source_test_plan_review_snapshot_id"),
        "source_test_plan_review_snapshot_hash": payload.get("source_test_plan_review_snapshot_hash"),
        "approved_candidate_ids": list(payload.get("approved_candidate_ids", [])),
        "approved_test_case_ids": [str(test_case_id) for test_case_id in approved_test_case_ids],
        "approved_automation_plan_ids": [str(plan_id) for plan_id in approved_plan_ids],
        "plan_decisions": _automation_plan_decisions_for_ids(session, project_id, plan_ids),
    }


def _automation_draft_review_workflow_read(
    session: Session,
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    run,
    snapshot,
) -> AutomationDraftReviewWorkflowRead:
    payload = snapshot.input_payload_json
    latest_approval = session.scalar(
        select(WorkflowHumanDecision)
        .where(
            WorkflowHumanDecision.project_id == run.project_id,
            WorkflowHumanDecision.workflow_run_id == run.id,
            WorkflowHumanDecision.snapshot_id == run.current_snapshot_id,
            WorkflowHumanDecision.action == TransitionAction.APPROVE.value,
            WorkflowHumanDecision.decision == ApprovalDecision.APPROVED.value,
        )
        .order_by(WorkflowHumanDecision.created_at.desc(), WorkflowHumanDecision.id.desc()),
    )
    draft_ids = _automation_draft_ids_for_requirement_review(session, project_id, payload)
    return AutomationDraftReviewWorkflowRead(
        project_id=project_id,
        requirement_review_id=review_id,
        workflow={
            "run_id": str(run.id),
            "stage": run.current_stage,
            "state": run.gate_state,
            "lock_version": run.lock_version,
            "snapshot_id": str(run.current_snapshot_id),
            "approval_decision_id": str(latest_approval.id) if latest_approval else None,
            "can_submit": run.gate_state == GateState.DRAFT.value,
            "can_complete_review": run.gate_state == GateState.WAITING_REVIEW.value,
            "can_edit": run.gate_state in {
                GateState.WAITING_REVIEW.value,
                GateState.WAITING_APPROVAL.value,
                GateState.APPROVED.value,
                GateState.REJECTED.value,
            },
            "can_approve": run.gate_state == GateState.WAITING_APPROVAL.value,
            "can_continue": run.gate_state == GateState.APPROVED.value and latest_approval is not None,
        },
        source_automation_plan_review_snapshot_id=payload.get("source_automation_plan_review_snapshot_id"),
        source_automation_plan_review_snapshot_hash=payload.get("source_automation_plan_review_snapshot_hash"),
        source_case_review_snapshot_id=payload.get("source_case_review_snapshot_id"),
        source_case_review_snapshot_hash=payload.get("source_case_review_snapshot_hash"),
        approved_automation_plan_ids=list(payload.get("approved_automation_plan_ids", [])),
        approved_test_case_ids=list(payload.get("approved_test_case_ids", [])),
        generated_draft_ids=draft_ids,
        draft_decisions=_automation_draft_decisions_for_ids(session, project_id, draft_ids),
    )


def _automation_draft_ids_for_requirement_review(
    session: Session,
    project_id: uuid.UUID,
    payload: dict,
) -> list[uuid.UUID]:
    approved_plan_ids = [
        uuid.UUID(str(plan_id))
        for plan_id in payload.get("approved_automation_plan_ids", [])
        if str(plan_id)
    ]
    if not approved_plan_ids:
        return []
    rows = session.scalars(
        select(AutomationDraft.id)
        .where(
            AutomationDraft.project_id == project_id,
            AutomationDraft.automation_plan_id.in_(approved_plan_ids),
        )
        .order_by(AutomationDraft.created_at.asc(), AutomationDraft.id.asc()),
    )
    return list(rows)


def _automation_draft_decisions_for_ids(
    session: Session,
    project_id: uuid.UUID,
    draft_ids: list[uuid.UUID],
) -> list[dict[str, object]]:
    if not draft_ids:
        return []
    drafts = list(
        session.scalars(
            select(AutomationDraft)
            .where(AutomationDraft.project_id == project_id, AutomationDraft.id.in_(draft_ids))
            .order_by(AutomationDraft.created_at.asc(), AutomationDraft.id.asc()),
        ),
    )
    return [
        {
            "automation_draft_id": str(draft.id),
            "automation_plan_id": str(draft.automation_plan_id) if draft.automation_plan_id else None,
            "test_case_id": str(draft.test_case_id) if draft.test_case_id else None,
            "status": draft.status,
            "target_framework": draft.target_framework,
            "review_comment": draft.review_comment,
        }
        for draft in drafts
    ]


def _require_approved_automation_draft(session: Session, project_id: uuid.UUID, payload: dict) -> None:
    draft_ids = _automation_draft_ids_for_requirement_review(session, project_id, payload)
    if not draft_ids:
        raise AutomationDraftReviewGateError
    approved_draft_id = session.scalar(
        select(AutomationDraft.id)
        .where(
            AutomationDraft.project_id == project_id,
            AutomationDraft.id.in_(draft_ids),
            AutomationDraft.status == "approved",
        )
        .limit(1),
    )
    if approved_draft_id is None:
        raise AutomationDraftReviewGateError


def _execution_approval_input_payload(session: Session, project_id: uuid.UUID, source_snapshot) -> dict[str, object]:
    payload = source_snapshot.input_payload_json
    draft_ids = _automation_draft_ids_for_requirement_review(session, project_id, payload)
    approved_draft_ids = list(
        session.scalars(
            select(AutomationDraft.id)
            .where(
                AutomationDraft.project_id == project_id,
                AutomationDraft.id.in_(draft_ids),
                AutomationDraft.status == "approved",
            )
            .order_by(AutomationDraft.created_at.asc(), AutomationDraft.id.asc()),
        ),
    )
    return {
        "requirement_id": payload.get("requirement_id"),
        "requirement_review_id": payload.get("requirement_review_id"),
        "source_automation_draft_review_snapshot_id": str(source_snapshot.id),
        "source_automation_draft_review_snapshot_hash": source_snapshot.input_snapshot_hash,
        "source_automation_plan_review_snapshot_id": payload.get("source_automation_plan_review_snapshot_id"),
        "source_automation_plan_review_snapshot_hash": payload.get("source_automation_plan_review_snapshot_hash"),
        "source_case_review_snapshot_id": payload.get("source_case_review_snapshot_id"),
        "source_case_review_snapshot_hash": payload.get("source_case_review_snapshot_hash"),
        "approved_automation_plan_ids": list(payload.get("approved_automation_plan_ids", [])),
        "approved_test_case_ids": list(payload.get("approved_test_case_ids", [])),
        "approved_automation_draft_ids": [str(draft_id) for draft_id in approved_draft_ids],
        "draft_decisions": _automation_draft_decisions_for_ids(session, project_id, draft_ids),
    }


def _json_safe(value):
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def validate_automation_draft_approval(draft: AutomationDraft) -> None:
    if automation_draft_approval_blocking_reasons(draft):
        raise AutomationDraftQualityGateError


def automation_draft_quality_gate(draft: AutomationDraft) -> dict[str, object]:
    blocking_reasons = automation_draft_approval_blocking_reasons(draft)
    evidence_warnings = automation_draft_evidence_warnings(draft)
    if blocking_reasons:
        status = "blocked"
        evidence_level = "blocked"
    elif evidence_warnings:
        status = "needs_real_evidence_review"
        evidence_level = "demo_or_unverified"
    else:
        status = "ready_for_approval"
        evidence_level = "reviewed_candidate"
    return {
        "status": status,
        "execution_evidence_level": evidence_level,
        "approval_blocking_reasons": blocking_reasons,
        "evidence_warnings": evidence_warnings,
    }


def automation_draft_approval_blocking_reasons(draft: AutomationDraft) -> list[str]:
    code = (draft.draft_code or "").strip()
    reasons: list[str] = []
    if not code:
        reasons.append("Draft code is required.")
        return reasons
    if draft.target_framework == "pytest" and not re.search(r"\bdef\s+test_[a-zA-Z0-9_]*\s*\(", code):
        reasons.append("Pytest draft must define at least one test_ function.")
    if draft.target_framework == "playwright" and not re.search(r"\btest\s*\(", code):
        reasons.append("Playwright draft must define at least one test(...) case.")
    if is_placeholder_only_draft_code(code):
        reasons.append("Draft only contains placeholder assertions.")
    if contains_demo_adapter_reference(code):
        reasons.append(
            "Draft code references fake/stub/demo adapters and cannot be approved as real regression evidence."
        )
    if automation_draft_domain_mismatch(draft):
        reasons.append("Draft code does not align with the linked requirement or test-case domain.")
    if not draft.suggested_file_path or invalid_suggested_path(draft.suggested_file_path):
        reasons.append("Suggested file path must be relative and stay inside the test workspace.")
    return reasons


def automation_draft_domain_mismatch(draft: AutomationDraft) -> bool:
    """Reject generated code that has drifted away from its linked requirement."""
    requirement = draft.requirement
    if requirement is None:
        return False
    terms = extract_domain_terms(
        f"{requirement.title}\n{requirement.content}\n{requirement.source_ref or ''}",
    )
    if not terms:
        return False
    candidate = {
        "title": draft.title,
        "precondition": draft.execution_notes or "",
        "steps": [draft.draft_code],
        "expected_results": [draft.risk_notes or ""],
    }
    return not case_domain_aligned(candidate, terms)


def automation_draft_evidence_warnings(draft: AutomationDraft) -> list[str]:
    warnings: list[str] = []
    code = draft.draft_code or ""
    evidence_text = "\n".join(
        part
        for part in (
            draft.draft_code,
            draft.execution_notes,
            draft.risk_notes,
            draft.review_comment,
        )
        if part
    )
    if contains_demo_adapter_reference(code):
        warnings.append(
            "Draft references fake/stub/demo adapters; replace them with project-local fixtures, selectors, or API hooks."
        )
    if LIMITED_EVIDENCE_PATTERN.search(evidence_text):
        warnings.append(
            "Draft mentions limited evidence such as fake, stub, demo, mock, double, placeholder, or assert True."
        )
    return warnings


def validate_context_artifacts(
    session: Session,
    project_id: uuid.UUID,
    context_artifact_ids: list[uuid.UUID],
) -> None:
    if not context_artifact_ids:
        return
    artifacts = {
        artifact.id: artifact
        for artifact in session.query(Artifact)
        .filter(
            Artifact.id.in_(context_artifact_ids),
            Artifact.project_id == project_id,
            Artifact.artifact_type.in_(ai_runtime_service.CONTEXT_FILE_NAMES.keys()),
        )
        .all()
    }
    if len(artifacts) != len(set(context_artifact_ids)):
        raise ContextArtifactNotFoundError
    if any(not bool(artifact.metadata_json.get("allowed_for_prompt", False)) for artifact in artifacts.values()):
        raise ContextArtifactNotFoundError


def automation_plan_query(test_case: TestCase) -> str:
    pieces = [
        test_case.title,
        test_case.precondition or "",
        " ".join(str(step) for step in test_case.steps_json),
        " ".join(str(result) for result in test_case.expected_results_json),
        " ".join(str(tag) for tag in test_case.tags),
    ]
    return " ".join(piece for piece in pieces if piece)


def retrieve_automation_plan_knowledge(
    session: Session,
    store: LocalArtifactStore,
    *,
    project_id: uuid.UUID,
    test_case: TestCase,
    candidate: GeneratedCaseCandidate,
    use_knowledge: bool,
) -> tuple[dict | None, list[uuid.UUID]]:
    if not use_knowledge:
        return None, []

    query_text = automation_plan_query(test_case)
    adapter_retrieval = extension_service.retrieve_deterministic_knowledge(
        session,
        store,
        project_id,
        query_text,
        max_results=5,
        max_snippet_chars=320,
    )
    inherited_card_evidence = knowledge_service.revalidate_prompt_evidence_items(
        session,
        project_id=project_id,
        items=[
            dict(item)
            for item in candidate.source_knowledge_evidence_json
            if isinstance(item, dict)
        ],
    )
    retrieval_run, fresh_card_evidence = knowledge_service.retrieve_and_persist_test_knowledge_evidence(
        session,
        store,
        project_id=project_id,
        query_text=query_text,
        limit=5,
        approved_only=True,
        consumer_entity_type="TestCase",
        consumer_entity_id=test_case.id,
    )
    card_evidence = deduplicate_knowledge_card_evidence(
        [*inherited_card_evidence, *fresh_card_evidence],
    )
    adapter_payload = adapter_retrieval.model_dump(mode="json")
    adapter_results = filter_relevant_knowledge_results(
        query_text,
        list(adapter_payload.get("results", [])) if adapter_retrieval.used_knowledge else [],
    )
    card_evidence = filter_relevant_knowledge_results(query_text, card_evidence)
    results = [*adapter_results, *card_evidence]
    if not results:
        return None, []
    knowledge_evidence_refs = knowledge_service.resolve_knowledge_evidence_artifact_refs(
        session,
        project_id=project_id,
        items=card_evidence,
    )
    retrieval_run_ids = list(
        dict.fromkeys(item["knowledge_retrieval_run_id"] for item in knowledge_evidence_refs),
    )
    retrieval_artifact_ids = list(
        dict.fromkeys(item["canonical_artifact_id"] for item in knowledge_evidence_refs),
    )

    card_source_artifact_ids = [
        uuid.UUID(str(item["source_artifact_id"]))
        for item in card_evidence
        if item.get("source_artifact_id")
    ]
    adapter_context_artifact_ids = adapter_retrieval.used_context_artifact_ids if adapter_results else []
    used_context_artifact_ids = list(
        dict.fromkeys([*adapter_context_artifact_ids, *card_source_artifact_ids]),
    )
    retrieval_mode = (
        "deterministic_hybrid"
        if adapter_results and card_evidence
        else "deterministic_local"
        if adapter_results
        else "test_knowledge_hybrid"
    )
    return (
        {
            "adapter_name": adapter_retrieval.adapter_name,
            "retrieval_mode": retrieval_mode,
            "query_text": query_text,
            "query_terms": knowledge_service.normalize_terms(query_text),
            "used_knowledge": True,
            "created_knowledge_retrieval_run_id": str(retrieval_run.id),
            "knowledge_retrieval_run_id": retrieval_run_ids[0] if len(retrieval_run_ids) == 1 else None,
            "knowledge_retrieval_run_ids": retrieval_run_ids,
            "knowledge_retrieval_artifact_id": (
                retrieval_artifact_ids[0]
                if len(retrieval_artifact_ids) == 1
                else None
            ),
            "knowledge_retrieval_artifact_ids": retrieval_artifact_ids,
            "used_context_artifact_ids": [str(artifact_id) for artifact_id in used_context_artifact_ids],
            "result_sources": [
                *([] if not adapter_results else ["context_artifact"]),
                *([] if not card_evidence else ["test_knowledge_card"]),
            ],
            "results": results,
        },
        used_context_artifact_ids,
    )


def deduplicate_knowledge_card_evidence(items: list[dict]) -> list[dict]:
    deduplicated: dict[str, dict] = {}
    for item in items:
        key = str(item.get("knowledge_card_id") or item.get("evidence_id") or len(deduplicated))
        deduplicated.setdefault(key, item)
    return list(deduplicated.values())


def filter_relevant_knowledge_results(query_text: str, items: list[dict]) -> list[dict]:
    query_terms = set(meaningful_knowledge_terms(knowledge_service.normalize_terms(query_text)))
    filtered: list[dict] = []
    for item in items:
        if is_inherited_case_knowledge(item):
            filtered.append(item)
            continue
        matched_terms = meaningful_knowledge_terms([str(term) for term in item.get("matched_terms", [])])
        if query_terms.intersection(matched_terms):
            filtered.append(item)
            continue
        semantic_score = item.get("semantic_score")
        if isinstance(semantic_score, (int, float)) and float(semantic_score) >= AUTOMATION_RELEVANT_SEMANTIC_SCORE:
            filtered.append(item)
    return filtered


def is_inherited_case_knowledge(item: dict) -> bool:
    return str(item.get("retrieval_reason")) == "case_generation_inherited_evidence"


def meaningful_knowledge_terms(terms: list[str]) -> list[str]:
    return [
        normalized
        for term in terms
        if (normalized := term.strip().lower())
        and normalized not in GENERIC_KNOWLEDGE_TERMS
        and len(normalized) >= 2
    ]


def build_plan_payload(
    test_case: TestCase,
    target_framework: str,
    retrieval_payload: dict | None,
) -> dict:
    results = list((retrieval_payload or {}).get("results", []))
    source_steps = [str(step) for step in test_case.steps_json] or ["Execute the reviewed test case scenario."]
    execution_steps = [
        f"Prepare precondition: {test_case.precondition or 'no explicit precondition'}",
        *[f"Automate step: {step}" for step in source_steps],
        "Assert the reviewed expected results and capture failure evidence.",
    ]
    evidence = [
        {
            "context_artifact_id": result.get("context_artifact_id"),
            "source_artifact_id": result.get("source_artifact_id"),
            "knowledge_card_id": result.get("knowledge_card_id"),
            "knowledge_type": result.get("knowledge_type"),
            "title": result.get("title"),
            "score": result.get("score"),
            "matched_terms": result.get("matched_terms", []),
            "snippet": result.get("snippet"),
            "semantic_score": result.get("semantic_score"),
            "retrieval_reason": result.get("retrieval_reason"),
        }
        for result in results
    ]
    plan = {
        "source": "reviewed_test_case",
        "test_case_title": test_case.title,
        "target_framework": target_framework,
        "assertions": [str(result) for result in test_case.expected_results_json],
        "knowledge_evidence": evidence,
    }
    return {
        "title": f"{target_framework} automation plan for {test_case.title}",
        "plan": plan,
        "execution_steps": execution_steps,
        "test_data": dict(test_case.input_data_json),
        "dependency_notes": dependency_notes_for_framework(target_framework, bool(evidence)),
        "risk_notes": "Review selectors, fixtures, and environment data before generating executable code.",
    }


def dependency_notes_for_framework(target_framework: str, used_knowledge: bool) -> str:
    base = {
        "pytest": "Requires pytest and project-local fixtures for the reviewed scenario.",
        "playwright": "Requires Playwright browser dependencies and stable selectors.",
    }.get(target_framework, f"Requires local dependencies for {target_framework}.")
    if used_knowledge:
        return f"{base} Knowledge evidence was used to shape data and assertions."
    return f"{base} No deterministic knowledge evidence matched this plan."


def attach_plan_retrieval_evidence_artifact(
    session: Session,
    store: LocalArtifactStore,
    ai_task: AITask,
    retrieval_payload: dict,
    used_context_artifact_ids: list[uuid.UUID],
) -> Artifact:
    retrieved_context_artifact_ids = list(retrieval_payload.get("used_context_artifact_ids", []))
    retrieval_results = list(retrieval_payload.get("results", []))
    includes_test_knowledge_cards = any(result.get("knowledge_card_id") for result in retrieval_results)
    retrieval_mode = str(retrieval_payload.get("retrieval_mode", "deterministic_local"))
    knowledge_evidence_refs = knowledge_service.resolve_knowledge_evidence_artifact_refs(
        session,
        project_id=ai_task.project_id,
        items=retrieval_results,
    )
    canonical_artifact_ids = list(
        dict.fromkeys(item["canonical_artifact_id"] for item in knowledge_evidence_refs),
    )
    retrieval_run_ids = list(
        dict.fromkeys(item["knowledge_retrieval_run_id"] for item in knowledge_evidence_refs),
    )
    context_result_refs = [
        {
            "context_artifact_id": result.get("context_artifact_id"),
            "score": result.get("score"),
            "matched_term_count": len(result.get("matched_terms", [])),
        }
        for result in retrieval_results
        if result.get("context_artifact_id")
    ]
    if includes_test_knowledge_cards and not context_result_refs and len(canonical_artifact_ids) == 1:
        artifact = session.get(Artifact, uuid.UUID(canonical_artifact_ids[0]))
        if artifact is not None:
            output_json = dict(ai_task.output_json)
            output_json["used_knowledge"] = True
            output_json["used_context_artifact_ids"] = [
                str(context_id) for context_id in used_context_artifact_ids
            ]
            output_json["knowledge_retrieval_run_id"] = retrieval_run_ids[0]
            output_json["knowledge_retrieval_run_ids"] = retrieval_run_ids
            output_json["canonical_retrieval_artifact_ids"] = canonical_artifact_ids
            output_json["retrieval_evidence_artifact_id"] = str(artifact.id)
            ai_task.output_json = output_json
            session.add(ai_task)
            session.flush()
            return artifact

    raw_query = str(retrieval_payload.get("query_text", ""))
    reference_payload = {
        "retrieval_mode": retrieval_mode,
        "query_text_hash": "sha256:" + hashlib.sha256(raw_query.encode("utf-8")).hexdigest(),
        "query_text_redacted": knowledge_service.redact_retrieval_query(raw_query),
        "used_context_artifact_ids": retrieved_context_artifact_ids,
        "result_refs": context_result_refs,
        "knowledge_evidence_refs": knowledge_evidence_refs,
        "canonical_artifact_ids": canonical_artifact_ids,
    }
    payload = ProviderArtifactPayload(
        artifact_type="knowledge_retrieval",
        file_name="knowledge_retrieval.json",
        mime_type="application/json",
        content=json.dumps(reference_payload, ensure_ascii=False, sort_keys=True).encode("utf-8"),
    )
    artifact = ai_runtime_service.write_ai_task_artifact(
        session,
        store,
        ai_task,
        payload,
        metadata_json={
            "created_by_component": (
                "KnowledgeRetrievalReferenceManifest"
                if includes_test_knowledge_cards
                else "DeterministicKnowledgeAdapter"
            ),
            "source_entity_type": "AITask",
            "source_entity_id": str(ai_task.id),
            "safe_to_show": True,
            "redaction_applied": reference_payload["query_text_redacted"] == "[redacted]",
            "description": "Deterministic local knowledge retrieval reference",
            "retrieval_mode": retrieval_mode,
            "query_text_hash": reference_payload["query_text_hash"],
            "result_count": len(retrieval_results),
            "knowledge_evidence_count": len(knowledge_evidence_refs),
            "canonical_artifact_ids": canonical_artifact_ids,
            "used_context_artifact_ids": retrieved_context_artifact_ids,
        },
    )
    output_json = dict(ai_task.output_json)
    output_json["used_knowledge"] = True
    output_json["used_context_artifact_ids"] = [str(context_id) for context_id in used_context_artifact_ids]
    output_json["knowledge_retrieval_run_ids"] = retrieval_run_ids
    if len(retrieval_run_ids) == 1:
        output_json["knowledge_retrieval_run_id"] = retrieval_run_ids[0]
    output_json["canonical_retrieval_artifact_ids"] = canonical_artifact_ids
    output_json["retrieval_evidence_artifact_id"] = str(artifact.id)
    ai_task.output_json = output_json
    session.add(ai_task)
    session.add(artifact)
    session.flush()
    return artifact


def automation_plan_prompt_summary(plan: AutomationPlan) -> dict:
    summary = automation_plan_summary(plan)
    summary["plan"] = dict(plan.plan_json)
    return summary


def automation_plan_summary(plan: AutomationPlan) -> dict:
    return {
        "id": str(plan.id),
        "title": plan.title,
        "test_case_title": str(plan.plan_json.get("test_case_title", "")),
        "status": plan.status,
        "target_framework": plan.target_framework,
        "execution_steps": list(plan.execution_steps_json),
        "test_data": dict(plan.test_data_json),
        "dependency_notes": plan.dependency_notes,
        "risk_notes": plan.risk_notes,
        "used_context_artifact_ids": [str(context_id) for context_id in plan.used_context_artifact_ids],
        "knowledge_retrieval_artifact_id": str(plan.knowledge_retrieval_artifact_id)
        if plan.knowledge_retrieval_artifact_id is not None
        else None,
    }


def test_case_prompt_summary(test_case: TestCase) -> dict:
    return {
        "id": str(test_case.id),
        "title": test_case.title,
        "priority": test_case.priority,
        "test_type": test_case.test_type,
        "precondition": test_case.precondition,
        "steps": list(test_case.steps_json),
        "expected_results": list(test_case.expected_results_json),
        "input_data": dict(test_case.input_data_json),
        "tags": list(test_case.tags),
        "review_status": test_case.review_status,
        "status": test_case.status,
    }


def requirement_prompt_summary(requirement: Requirement | None) -> dict | None:
    if requirement is None:
        return None
    return {
        "id": str(requirement.id),
        "title": requirement.title,
        "content": requirement.content,
        "status": requirement.status,
    }


def validate_automation_draft_output(output: dict, target_framework: str) -> None:
    if not isinstance(output, dict):
        raise AutomationDraftSchemaInvalidError
    for key in ("draft_code", "suggested_file_path"):
        if not isinstance(output.get(key), str) or not output[key].strip():
            raise AutomationDraftSchemaInvalidError
    if "title" in output and not isinstance(output["title"], str):
        raise AutomationDraftSchemaInvalidError
    if "draft_language" in output and not isinstance(output["draft_language"], str):
        raise AutomationDraftSchemaInvalidError
    if "execution_notes" in output and not isinstance(output["execution_notes"], str):
        raise AutomationDraftSchemaInvalidError
    if "risk_notes" in output and not isinstance(output["risk_notes"], str):
        raise AutomationDraftSchemaInvalidError

    code = output["draft_code"].strip()
    if target_framework == "pytest" and not re.search(r"\bdef\s+test_[a-zA-Z0-9_]*\s*\(", code):
        raise AutomationDraftSchemaInvalidError
    if target_framework == "playwright" and not re.search(r"\btest\s*\(", code):
        raise AutomationDraftSchemaInvalidError
    if is_placeholder_only_draft_code(code):
        raise AutomationDraftSchemaInvalidError
    if invalid_suggested_path(output["suggested_file_path"]):
        raise AutomationDraftSchemaInvalidError


def is_placeholder_only_draft_code(code: str) -> bool:
    executable_lines = [
        line.strip()
        for line in code.splitlines()
        if line.strip() and not line.strip().startswith("#") and not line.strip().startswith('"""')
    ]
    assert_true_pattern = r"assert\s+True(?:\s*#.*)?"
    if len(executable_lines) <= 2 and any(re.fullmatch(assert_true_pattern, line) for line in executable_lines):
        return True
    assertions = [line for line in executable_lines if line.startswith("assert ")]
    return bool(assertions) and all(re.fullmatch(assert_true_pattern, line) for line in assertions)


def contains_demo_adapter_reference(code: str) -> bool:
    scan_code = "\n".join(
        line for line in code.splitlines() if not line.strip().startswith(("#", "//"))
    )
    return bool(DEMO_ADAPTER_PATTERN.search(scan_code))


def invalid_suggested_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized


def automation_draft_payload_from_output(
    output: dict,
    *,
    source_title: str,
    target_framework: str,
    automation_plan: AutomationPlan | None,
) -> dict:
    draft_code = output["draft_code"].strip() + "\n"
    return {
        "title": clean_output_string(output.get("title")) or f"{target_framework} draft for {source_title}",
        "draft_code": draft_code,
        "draft_language": clean_output_string(output.get("draft_language")) or language_for_framework(target_framework),
        "suggested_file_path": clean_output_string(output.get("suggested_file_path"))
        or suggested_file_path(source_title, target_framework),
        "execution_notes": clean_output_string(output.get("execution_notes")) or execution_notes_for_draft(automation_plan),
        "risk_notes": clean_output_string(output.get("risk_notes")) or risk_notes_for_draft(automation_plan),
    }


def clean_output_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def language_for_framework(target_framework: str) -> str:
    return "python" if target_framework == "pytest" else "typescript"


def mark_automation_draft_schema_invalid(session: Session, ai_task: AITask) -> None:
    error_json = {
        "error_code": "AUTOMATION_DRAFT_SCHEMA_INVALID",
        "message": "Automation draft output did not match the expected schema.",
        "recoverable": True,
    }
    ai_task.status = "failed"
    ai_task.error_json = error_json
    ai_task.finished_at = ai_runtime_service.utc_now()
    llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))
    if llm_log is not None:
        llm_log.status = "schema_invalid"
        llm_log.error_json = error_json
        session.add(llm_log)
    session.add(ai_task)
    session.commit()


def execution_notes_for_draft(plan: AutomationPlan | None) -> str:
    if plan is None:
        return "Review and approve this draft before any controlled execution."
    return "\n".join(
        [
            "Generated from an approved AutomationPlan.",
            f"Plan: {plan.title}",
            "Review and approve this draft before any controlled execution.",
        ],
    )


def risk_notes_for_draft(plan: AutomationPlan | None) -> str:
    if plan is None:
        return "Mock draft uses placeholder fixtures and must be reviewed before execution."
    return plan.risk_notes or "Review selectors, fixtures, and generated code before execution."


def mock_draft_code(title: str, plan: AutomationPlan | None = None) -> str:
    test_name = slug(title)
    plan_comment = ""
    if plan is not None:
        plan_comment = f"    # AutomationPlan: {plan.title}\n"
    return (
        f"def test_{test_name}():\n"
        f"{plan_comment}"
        f"    # Draft generated from reviewed TestCase: {title}\n"
        f"    scenario = {{'title': {title!r}, 'blocked': True}}\n"
        "    actual = {'title': scenario['title'], 'blocked': scenario['blocked']}\n"
        "    assert actual['title'] == scenario['title']\n"
        "    assert actual['blocked'] is True\n"
    )


def suggested_file_path(title: str, target_framework: str) -> str:
    extension = "py" if target_framework == "pytest" else "spec.ts"
    return f"tests/test_{slug(title)}.{extension}"


def slug(value: str) -> str:
    slugged = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slugged or "automation_draft"
