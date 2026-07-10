from __future__ import annotations

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
    AutomationPlanApproveRequest,
    AutomationPlanCreateRequest,
    AutomationPlanUpdateRequest,
)
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase
from backend.app.modules.extension import service as extension_service
from backend.app.modules.knowledge import service as knowledge_service
from backend.app.modules.projects.models import Project
from backend.app.modules.prompt_skill import service as prompt_skill_service
from backend.app.modules.requirements.models import Requirement
from backend.app.modules.review_history.service import append_review_history
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


def validate_automation_draft_approval(draft: AutomationDraft) -> None:
    code = (draft.draft_code or "").strip()
    if not code:
        raise AutomationDraftQualityGateError
    if draft.target_framework == "pytest" and not re.search(r"\bdef\s+test_[a-zA-Z0-9_]*\s*\(", code):
        raise AutomationDraftQualityGateError
    if draft.target_framework == "playwright" and not re.search(r"\btest\s*\(", code):
        raise AutomationDraftQualityGateError
    if is_placeholder_only_draft_code(code):
        raise AutomationDraftQualityGateError
    if not draft.suggested_file_path or invalid_suggested_path(draft.suggested_file_path):
        raise AutomationDraftQualityGateError


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
    inherited_card_evidence = [
        dict(item)
        for item in candidate.source_knowledge_evidence_json
        if isinstance(item, dict)
    ]
    fresh_card_evidence = knowledge_service.retrieve_test_knowledge_evidence(
        session,
        project_id=project_id,
        query_text=query_text,
        limit=5,
        approved_only=True,
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
    retrieval_results = list(retrieval_payload.get("results", []))
    retrieval_mode = str(retrieval_payload.get("retrieval_mode", "deterministic_local"))
    payload = ProviderArtifactPayload(
        artifact_type="knowledge_retrieval",
        file_name="knowledge_retrieval.json",
        mime_type="application/json",
        content=json.dumps(retrieval_payload, ensure_ascii=False, sort_keys=True).encode("utf-8"),
    )
    artifact = ai_runtime_service.write_ai_task_artifact(
        session,
        store,
        ai_task,
        payload,
        metadata_json={
            "created_by_component": "AutomationPlanAgent",
            "source_entity_type": "AITask",
            "source_entity_id": str(ai_task.id),
            "safe_to_show": True,
            "redaction_applied": any(bool(result.get("redaction_applied", False)) for result in retrieval_results),
            "description": "Automation plan hybrid knowledge retrieval evidence",
            "retrieval_mode": retrieval_mode,
            "query_terms": list(retrieval_payload.get("query_terms", [])),
            "result_count": len(retrieval_results),
            "results": retrieval_results,
            "used_context_artifact_ids": list(retrieval_payload.get("used_context_artifact_ids", [])),
        },
    )
    output_json = dict(ai_task.output_json)
    output_json["used_knowledge"] = True
    output_json["used_context_artifact_ids"] = [str(context_id) for context_id in used_context_artifact_ids]
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
    return f"def test_{test_name}():\n{plan_comment}    # Draft generated from reviewed TestCase: {title}\n    assert True\n"


def suggested_file_path(title: str, target_framework: str) -> str:
    extension = "py" if target_framework == "pytest" else "spec.ts"
    return f"tests/test_{slug(title)}.{extension}"


def slug(value: str) -> str:
    slugged = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slugged or "automation_draft"
