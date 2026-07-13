from __future__ import annotations

import re
import uuid
from collections import Counter

from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service as ai_runtime_service
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.model_config import resolve_model_identity
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase
from backend.app.modules.cases.schemas import (
    CaseGenerationStartRequest,
    CaseGenerationTaskRead,
    CaseMetricsRead,
    CaseReviewRequest,
    GeneratedCaseCandidateListItemRead,
    TestCaseListItemRead,
)
from backend.app.modules.knowledge import service as knowledge_service
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.projects.models import Project
from backend.app.modules.requirements.models import Requirement, RequirementReview, RiskItem
from backend.app.modules.requirements import service as requirements_service
from backend.app.modules.review_history.service import append_review_history
from backend.app.workers.enqueue import FakeAIQueue, enqueue_ai_task
from backend.app.workers.handlers.ai_task_handler import run_ai_task


class ProjectNotFoundError(Exception):
    pass


class RequirementNotFoundError(Exception):
    pass


class RequirementReviewNotFoundError(Exception):
    pass


class RequirementDocumentNotFoundError(Exception):
    pass


class PromptVersionNotFoundError(Exception):
    pass


class SkillVersionNotFoundError(Exception):
    pass


class ContextArtifactNotFoundError(Exception):
    pass


class CaseGenerationSchemaInvalidError(Exception):
    pass


class CaseGenerationTaskNotFoundError(Exception):
    pass


class CaseGenerationDomainMismatchError(Exception):
    pass


class CaseGenerationDecisionTableRequiredError(Exception):
    pass


CASE_COVERAGE_DIMENSION_LABELS = {
    "positive": "主流程",
    "negative": "异常/负向",
    "boundary": "边界值",
    "state": "状态转换",
    "permission": "权限",
    "channel": "下发链路",
    "condition": "设备/电流条件",
    "risk": "风险引用",
}

CASE_COVERAGE_DIMENSION_ALIASES = {
    "happy_path": "positive",
    "main_flow": "positive",
    "success": "positive",
    "exception": "negative",
    "error": "negative",
    "invalid": "negative",
    "limit": "boundary",
    "time_window": "boundary",
    "state_transition": "state",
    "lifecycle": "state",
    "role": "permission",
    "network": "channel",
    "delivery": "channel",
    "device": "condition",
    "current": "condition",
}

class CaseCandidateNotFoundError(Exception):
    pass


class CaseCandidateAlreadyFinalError(Exception):
    pass


class CaseReviewInvalidActionError(Exception):
    pass


def start_case_generation(
    session: Session,
    store: LocalArtifactStore,
    data: CaseGenerationStartRequest,
) -> tuple[CaseGenerationTask, AITask]:
    project = session.get(Project, data.project_id)
    if project is None:
        raise ProjectNotFoundError
    requirement = session.scalar(select(Requirement).where(Requirement.id == data.requirement_id, Requirement.project_id == data.project_id))
    if requirement is None:
        raise RequirementNotFoundError
    review = None
    if data.requirement_review_id is not None:
        review = session.scalar(
            select(RequirementReview).where(
                RequirementReview.id == data.requirement_review_id,
                RequirementReview.requirement_id == requirement.id,
            ),
        )
        if review is None:
            raise RequirementReviewNotFoundError

    requirement_document = None
    requirement_document_text = None
    if data.requirement_document_artifact_id is not None:
        try:
            requirement_document = requirements_service.get_requirement_document_artifact(
                session,
                data.requirement_document_artifact_id,
                project_id=data.project_id,
                requirement_id=requirement.id,
            )
        except requirements_service.RequirementDocumentNotFoundError as exc:
            raise RequirementDocumentNotFoundError from exc
        requirement_document_text = store.read_bytes(requirement_document.file_path).decode("utf-8", errors="replace")

    if not data.decision_table_acknowledged:
        raise CaseGenerationDecisionTableRequiredError

    prompt = get_prompt_version_by_ref(session, data.prompt_version)
    skill = get_skill_version_by_ref(session, data.skill_version)
    context = context_manifest(session, data.project_id, data.context_artifact_ids)
    knowledge_evidence = []
    if data.use_knowledge:
        knowledge_evidence = knowledge_service.retrieve_test_knowledge_evidence(
            session,
            project_id=data.project_id,
            query_text=requirement.content,
            limit=5,
            approved_only=True,
        )
    used_knowledge_source_artifact_ids = sorted(
        {
            str(item["source_artifact_id"])
            for item in knowledge_evidence
            if isinstance(item.get("source_artifact_id"), str)
        },
    )
    risk_items = []
    if data.requirement_review_id is not None:
        risk_items = list(
            session.scalars(select(RiskItem).where(RiskItem.requirement_review_id == data.requirement_review_id)),
        )
    model_provider, model_name = resolve_model_identity(
        model_provider=data.model_provider,
        model_name=data.model_name,
        default_provider="mock",
        default_model_name="mock-case-generator",
    )
    ai_task = AITask(
        project_id=data.project_id,
        agent_name="CaseGenerationAgent",
        task_type="case_generation",
        prompt_version_id=prompt.id,
        skill_version_id=skill.id,
        model_provider=model_provider,
        model_name=model_name,
        status="created",
        input_json={
            "requirement": requirement.content,
            "requirement_id": str(requirement.id),
            "requirement_document": requirement_document_summary(requirement_document, requirement_document_text),
            "requirement_review": review_summary(review) if review is not None else None,
            "risk_items": [risk_summary(risk) for risk in risk_items],
            "target_test_types": data.target_test_types,
            "decision_table_acknowledged": data.decision_table_acknowledged,
            "decision_table_dimensions": [
                {"key": key, "label": label}
                for key, label in CASE_COVERAGE_DIMENSION_LABELS.items()
            ],
            "use_knowledge": data.use_knowledge,
            "knowledge_evidence": knowledge_evidence,
            "knowledge_retrieval": {
                "used_knowledge": bool(knowledge_evidence),
                "results": knowledge_evidence,
                "used_context_artifact_ids": used_knowledge_source_artifact_ids,
            },
            "context_artifact_ids": [str(context_id) for context_id in data.context_artifact_ids],
            "context_manifest": context,
            "mock_mode": data.mock_mode,
        },
        context_artifact_ids=data.context_artifact_ids,
    )
    session.add(ai_task)
    session.commit()
    session.refresh(ai_task)

    generation_task = CaseGenerationTask(
        project_id=data.project_id,
        requirement_id=requirement.id,
        requirement_review_id=review.id if review is not None else None,
        ai_task_id=ai_task.id,
        target_test_types=data.target_test_types,
        status="pending",
        generated_count=0,
    )
    session.add(generation_task)
    session.commit()
    session.refresh(generation_task)
    return generation_task, ai_task


def run_case_generation_task(session: Session, store: LocalArtifactStore, generation_task_id: uuid.UUID) -> None:
    generation_task = session.get(CaseGenerationTask, generation_task_id)
    if generation_task is None:
        raise CaseGenerationTaskNotFoundError
    ai_task = session.get(AITask, generation_task.ai_task_id)
    if ai_task is None:
        generation_task.status = "failed"
        session.add(generation_task)
        session.commit()
        return

    generation_task.status = "running"
    session.add(generation_task)
    session.commit()

    queue = FakeAIQueue()
    job = enqueue_ai_task(session, queue, ai_task.id)
    run_ai_task(session, store, job)
    session.refresh(ai_task)
    session.refresh(generation_task)

    if ai_task.status != "succeeded":
        generation_task.status = "failed"
        session.add(generation_task)
        session.commit()
        return

    try:
        validate_case_generation_output(ai_task.output_json)
        validate_case_generation_domain_alignment(session, generation_task, ai_task.output_json)
    except CaseGenerationSchemaInvalidError:
        mark_case_generation_schema_invalid(session, ai_task)
        generation_task.status = "failed"
        session.add(generation_task)
        session.commit()
        return
    except CaseGenerationDomainMismatchError:
        mark_case_generation_domain_mismatch(session, ai_task)
        generation_task.status = "failed"
        session.add(generation_task)
        session.commit()
        return

    persist_case_generation_candidates(session, generation_task, ai_task.output_json)


def read_case_generation_task(session: Session, generation_task_id: uuid.UUID) -> CaseGenerationTaskRead:
    generation_task = session.get(CaseGenerationTask, generation_task_id)
    if generation_task is None:
        raise CaseGenerationTaskNotFoundError
    ai_task = session.get(AITask, generation_task.ai_task_id)
    error_json = ai_task.error_json if ai_task is not None and isinstance(ai_task.error_json, dict) else {}
    return CaseGenerationTaskRead(
        id=generation_task.id,
        project_id=generation_task.project_id,
        requirement_id=generation_task.requirement_id,
        requirement_review_id=generation_task.requirement_review_id,
        ai_task_id=generation_task.ai_task_id,
        target_test_types=generation_task.target_test_types,
        status=generation_task.status,
        generated_count=generation_task.generated_count,
        ai_task_status=ai_task.status if ai_task is not None else None,
        error_code=str(error_json.get("error_code")) if error_json.get("error_code") else None,
        error_message=str(error_json.get("message")) if error_json.get("message") else None,
        created_at=generation_task.created_at,
        updated_at=generation_task.updated_at,
    )


def list_candidates(session: Session, generation_task_id: uuid.UUID) -> list[GeneratedCaseCandidateListItemRead]:
    generation_task = session.get(CaseGenerationTask, generation_task_id)
    if generation_task is None:
        raise CaseGenerationTaskNotFoundError
    candidates = list(
        session.scalars(
            select(GeneratedCaseCandidate)
            .where(GeneratedCaseCandidate.generation_task_id == generation_task_id)
            .order_by(GeneratedCaseCandidate.created_at.asc(), GeneratedCaseCandidate.id.asc()),
        ),
    )
    return [
        GeneratedCaseCandidateListItemRead(
            id=candidate.id,
            title=candidate.title,
            priority=candidate.priority,
            test_type=candidate.test_type,
            precondition=candidate.precondition,
            steps=candidate.steps_json,
            expected_results=candidate.expected_results_json,
            input_data=candidate.input_data_json,
            requirement_refs=candidate.requirement_refs_json,
            risk_refs=candidate.risk_refs_json,
            source_knowledge_evidence=candidate.source_knowledge_evidence_json,
            coverage_dimensions=candidate.coverage_dimensions_json,
            ai_reason=candidate.ai_reason,
            status=candidate.status,
        )
        for candidate in candidates
    ]


def list_test_cases(
    session: Session,
    *,
    project_id: uuid.UUID,
    module_id: uuid.UUID | None = None,
    status: str | None = None,
    test_type: str | None = None,
    priority: str | None = None,
    keyword: str | None = None,
) -> list[TestCaseListItemRead]:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError

    query = select(TestCase).where(TestCase.project_id == project_id)
    if module_id is not None:
        query = query.where(TestCase.module_id == module_id)
    if status is not None:
        query = query.where(TestCase.status == status)
    if test_type is not None:
        query = query.where(TestCase.test_type == test_type)
    if priority is not None:
        query = query.where(TestCase.priority == priority)
    if keyword:
        keyword_pattern = f"%{keyword}%"
        query = query.where(
            or_(
                TestCase.title.ilike(keyword_pattern),
                TestCase.precondition.ilike(keyword_pattern),
                cast(TestCase.steps_json, String).ilike(keyword_pattern),
                cast(TestCase.expected_results_json, String).ilike(keyword_pattern),
                cast(TestCase.input_data_json, String).ilike(keyword_pattern),
                cast(TestCase.tags, String).ilike(keyword_pattern),
            ),
        )
    test_cases = list(session.scalars(query.order_by(TestCase.created_at.asc(), TestCase.id.asc())))
    return [
        TestCaseListItemRead(
            id=test_case.id,
            project_id=test_case.project_id,
            module_id=test_case.module_id,
            source_candidate_id=test_case.source_candidate_id,
            title=test_case.title,
            priority=test_case.priority,
            test_type=test_case.test_type,
            precondition=test_case.precondition,
            steps=test_case.steps_json,
            expected_results=test_case.expected_results_json,
            input_data=test_case.input_data_json,
            tags=test_case.tags,
            source_type=test_case.source_type,
            review_status=test_case.review_status,
            status=test_case.status,
        )
        for test_case in test_cases
    ]


def review_candidate(session: Session, candidate_id: uuid.UUID, data: CaseReviewRequest) -> tuple[GeneratedCaseCandidate, TestCase | None]:
    candidate = session.get(GeneratedCaseCandidate, candidate_id)
    if candidate is None:
        raise CaseCandidateNotFoundError
    if candidate.status in {"approved", "approved_after_edit", "rejected"}:
        raise CaseCandidateAlreadyFinalError

    from_status = candidate.status
    test_case: TestCase | None = None
    if data.action == "approve":
        candidate.status = "approved"
        candidate.review_comment = data.review_comment
        test_case = test_case_from_candidate(candidate, review_status="approved")
        session.add(test_case)
    elif data.action == "approve_after_edit":
        if data.edited_case is None:
            raise CaseReviewInvalidActionError
        candidate.status = "approved_after_edit"
        candidate.review_comment = data.review_comment
        test_case = test_case_from_edited_candidate(candidate, data, review_status="approved_after_edit")
        session.add(test_case)
    elif data.action == "reject":
        candidate.status = "rejected"
        candidate.review_comment = data.review_comment
    elif data.action == "needs_optimization":
        candidate.status = "needs_optimization"
        candidate.review_comment = data.review_comment
    else:
        raise CaseReviewInvalidActionError

    session.add(candidate)
    if data.action in {"approve", "approve_after_edit", "reject"}:
        append_review_history(
            session,
            project_id=candidate.project_id,
            entity_type="GeneratedCaseCandidate",
            entity_id=candidate.id,
            action=data.action,
            from_status=from_status,
            to_status=candidate.status,
            comment=data.review_comment,
        )
    session.commit()
    session.refresh(candidate)
    if test_case is not None:
        session.refresh(test_case)
    return candidate, test_case


def calculate_case_metrics(session: Session, generation_task_id: uuid.UUID) -> CaseMetricsRead:
    generation_task = session.get(CaseGenerationTask, generation_task_id)
    if generation_task is None:
        raise CaseGenerationTaskNotFoundError

    candidates = list(
        session.scalars(
            select(GeneratedCaseCandidate).where(GeneratedCaseCandidate.generation_task_id == generation_task_id),
        ),
    )
    generated_count = len(candidates)
    approved_count = count_by_status(candidates, "approved")
    edited_count = count_by_status(candidates, "approved_after_edit")
    rejected_count = count_by_status(candidates, "rejected")
    optimization_count = count_by_status(candidates, "needs_optimization")
    reviewed_count = approved_count + edited_count + rejected_count + optimization_count
    return CaseMetricsRead(
        generation_task_id=generation_task.id,
        generated_count=generated_count,
        approved_count=approved_count,
        edited_count=edited_count,
        rejected_count=rejected_count,
        optimization_count=optimization_count,
        reviewed_count=reviewed_count,
        acceptance_rate=ratio(approved_count + edited_count, generated_count),
        edit_rate=ratio(edited_count, generated_count),
        rejection_rate=ratio(rejected_count, generated_count),
        optimization_rate=ratio(optimization_count, generated_count),
        review_progress=ratio(reviewed_count, generated_count),
        field_complete_rate=ratio(sum(1 for candidate in candidates if candidate_fields_complete(candidate)), generated_count),
    )


def count_by_status(candidates: list[GeneratedCaseCandidate], status: str) -> int:
    return sum(1 for candidate in candidates if candidate.status == status)


def ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def candidate_fields_complete(candidate: GeneratedCaseCandidate) -> bool:
    return all(
        [
            bool(candidate.title),
            bool(candidate.priority),
            bool(candidate.test_type),
            bool(candidate.steps_json),
            bool(candidate.expected_results_json),
            bool(candidate.requirement_refs_json),
            bool(candidate.ai_reason),
        ],
    )


def test_case_from_candidate(candidate: GeneratedCaseCandidate, review_status: str) -> TestCase:
    return TestCase(
        project_id=candidate.project_id,
        module_id=candidate.module_id,
        source_candidate_id=candidate.id,
        title=candidate.title,
        priority=candidate.priority,
        test_type=candidate.test_type,
        precondition=candidate.precondition,
        steps_json=list(candidate.steps_json),
        expected_results_json=list(candidate.expected_results_json),
        input_data_json=dict(candidate.input_data_json),
        tags=list(candidate.tags),
        source_type="ai",
        review_status=review_status,
    )


def test_case_from_edited_candidate(
    candidate: GeneratedCaseCandidate,
    data: CaseReviewRequest,
    review_status: str,
) -> TestCase:
    if data.edited_case is None:
        raise CaseReviewInvalidActionError
    edited = data.edited_case
    return TestCase(
        project_id=candidate.project_id,
        module_id=candidate.module_id,
        source_candidate_id=candidate.id,
        title=edited.title,
        priority=edited.priority,
        test_type=edited.test_type,
        precondition=edited.precondition,
        steps_json=edited.steps,
        expected_results_json=edited.expected_results,
        input_data_json=edited.input_data,
        tags=edited.tags,
        source_type="ai",
        review_status=review_status,
    )


def get_prompt_version_by_ref(session: Session, version_ref: str) -> PromptVersion:
    name, _, version = version_ref.partition(":")
    prompt = session.scalar(
        select(PromptVersion).where(
            PromptVersion.name == name,
            PromptVersion.version == (version or "v1"),
            PromptVersion.status == "active",
        ),
    )
    if prompt is None:
        raise PromptVersionNotFoundError
    return prompt


def get_skill_version_by_ref(session: Session, version_ref: str) -> SkillVersion:
    name, _, version = version_ref.partition(":")
    skill = session.scalar(
        select(SkillVersion).where(
            SkillVersion.name == name,
            SkillVersion.version == (version or "v1"),
            SkillVersion.status == "active",
        ),
    )
    if skill is None:
        raise SkillVersionNotFoundError
    return skill


def context_manifest(session: Session, project_id: uuid.UUID, context_artifact_ids: list[uuid.UUID]) -> list[dict]:
    if not context_artifact_ids:
        return []
    artifacts = list(
        session.scalars(
            select(Artifact).where(
                Artifact.project_id == project_id,
                Artifact.id.in_(context_artifact_ids),
                Artifact.owner_entity_type == "Project",
                Artifact.owner_entity_id == project_id,
            ),
        ),
    )
    artifacts_by_id = {artifact.id: artifact for artifact in artifacts}
    if len(artifacts_by_id) != len(set(context_artifact_ids)):
        raise ContextArtifactNotFoundError
    return [
        {
            "artifact_id": str(artifact.id),
            "title": str(artifact.metadata_json.get("title", "")),
            "mime_type": artifact.mime_type,
            "sha256": f"sha256:{artifact.sha256}",
            "redaction_applied": bool(artifact.metadata_json.get("redaction_applied", False)),
        }
        for artifact_id in context_artifact_ids
        if (artifact := artifacts_by_id.get(artifact_id)) is not None
    ]


def review_summary(review: RequirementReview | None) -> dict | None:
    if review is None:
        return None
    return {
        "id": str(review.id),
        "overall_score": review.overall_score,
        "issues": review.issues_json,
        "clarification_questions": review.clarification_questions_json,
        "test_design_notes": review.test_design_notes_json,
    }


def risk_summary(risk: RiskItem) -> dict:
    return {
        "id": str(risk.id),
        "title": risk.title,
        "risk_level": risk.risk_level,
        "category": risk.category,
        "impact": risk.impact,
        "suggestion": risk.suggestion,
    }


def requirement_document_summary(artifact: Artifact | None, content: str | None) -> dict | None:
    if artifact is None or content is None:
        return None
    return {
        "artifact_id": str(artifact.id),
        "document_number": str(artifact.metadata_json.get("document_number", "")),
        "version": str(artifact.metadata_json.get("version", "v1")),
        "title": str(artifact.metadata_json.get("title", "")),
        "content": content,
        "sha256": f"sha256:{artifact.sha256}",
    }


def validate_case_generation_output(output: dict) -> None:
    cases = output.get("cases")
    if not isinstance(cases, list) or not cases:
        raise CaseGenerationSchemaInvalidError
    priorities = {"P0", "P1", "P2", "P3"}
    test_types = {"functional", "api", "ui", "performance", "security", "compatibility", "regression", "unit"}
    for case in cases:
        if not isinstance(case, dict):
            raise CaseGenerationSchemaInvalidError
        for key in ("title", "priority", "test_type", "ai_reason"):
            if not isinstance(case.get(key), str) or not case[key]:
                raise CaseGenerationSchemaInvalidError
        if case["priority"] not in priorities or case["test_type"] not in test_types:
            raise CaseGenerationSchemaInvalidError
        if "precondition" in case and case["precondition"] is not None and not isinstance(case["precondition"], str):
            raise CaseGenerationSchemaInvalidError
        if "tags" in case and not isinstance(case["tags"], list):
            raise CaseGenerationSchemaInvalidError
        if not isinstance(case.get("steps"), list) or not case["steps"]:
            raise CaseGenerationSchemaInvalidError
        if not isinstance(case.get("expected_results"), list) or not case["expected_results"]:
            raise CaseGenerationSchemaInvalidError
        if not isinstance(case.get("requirement_refs"), list) or not case["requirement_refs"]:
            raise CaseGenerationSchemaInvalidError
        if "risk_refs" in case and not isinstance(case["risk_refs"], list):
            raise CaseGenerationSchemaInvalidError
        if "source_knowledge_evidence" in case and not isinstance(case["source_knowledge_evidence"], list):
            raise CaseGenerationSchemaInvalidError
        coverage_dimensions = case.get("coverage_dimensions")
        if not isinstance(coverage_dimensions, list) or not coverage_dimensions:
            raise CaseGenerationSchemaInvalidError
        for dimension in coverage_dimensions:
            if not isinstance(dimension, dict):
                raise CaseGenerationSchemaInvalidError
            raw_key = str(dimension.get("key") or dimension.get("dimension") or dimension.get("name") or "")
            evidence = str(dimension.get("evidence") or dimension.get("reason") or dimension.get("note") or "")
            if normalize_coverage_dimension_key(raw_key) is None or not evidence.strip():
                raise CaseGenerationSchemaInvalidError
        if "input_data" in case and not isinstance(case["input_data"], dict):
            raise CaseGenerationSchemaInvalidError


def mark_case_generation_schema_invalid(session: Session, ai_task: AITask) -> None:
    error_json = {
        "error_code": "CASE_GENERATION_SCHEMA_INVALID",
        "message": "Case generation output did not match the expected schema.",
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


def mark_case_generation_domain_mismatch(session: Session, ai_task: AITask) -> None:
    error_json = {
        "error_code": "CASE_GENERATION_DOMAIN_MISMATCH",
        "message": "Generated cases do not match the requirement domain.",
        "recoverable": True,
    }
    ai_task.status = "failed"
    ai_task.error_json = error_json
    ai_task.finished_at = ai_runtime_service.utc_now()
    llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))
    if llm_log is not None:
        llm_log.status = "domain_mismatch"
        llm_log.error_json = error_json
        session.add(llm_log)
    session.add(ai_task)
    session.commit()


COMMON_DOMAIN_TERMS = {
    "用户",
    "系统",
    "平台",
    "功能",
    "支持",
    "规则",
    "任务",
    "影响",
    "条件",
    "状态",
    "信息",
    "配置",
    "当前",
    "后续",
    "不同",
    "是否",
    "进入",
    "执行",
    "决定",
    "修改",
    "删除",
    "创建",
    "查看",
    "提交",
    "失败",
    "成功",
    "提示",
    "local",
    "test",
    "case",
}

DOMAIN_TERM_ALIASES = {
    "coupon": {"优惠券"},
    "coupons": {"优惠券"},
    "checkout": {"结算"},
    "points": {"积分"},
    "expired": {"过期"},
}


def validate_case_generation_domain_alignment(
    session: Session,
    generation_task: CaseGenerationTask,
    output: dict,
) -> None:
    requirement = session.get(Requirement, generation_task.requirement_id)
    if requirement is None:
        return
    document_content = ""
    input_json = generation_task.ai_task.input_json if generation_task.ai_task is not None else {}
    requirement_document = input_json.get("requirement_document") if isinstance(input_json, dict) else None
    if isinstance(requirement_document, dict) and isinstance(requirement_document.get("content"), str):
        document_content = str(requirement_document["content"])
    domain_terms = extract_domain_terms(f"{requirement.title}\n{requirement.content}\n{document_content}")
    if not domain_terms:
        return
    cases = output.get("cases", [])
    aligned_count = sum(1 for case in cases if case_domain_aligned(case, domain_terms))
    if aligned_count == 0:
        raise CaseGenerationDomainMismatchError


def extract_domain_terms(text: str) -> set[str]:
    normalized = text.lower()
    terms: Counter[str] = Counter()
    for word in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", normalized):
        if word not in COMMON_DOMAIN_TERMS:
            terms[word] += 1
            for alias in DOMAIN_TERM_ALIASES.get(word, set()):
                terms[alias] += 1
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", normalized):
        for size in (2, 3, 4):
            for index in range(0, max(len(chunk) - size + 1, 0)):
                term = chunk[index : index + size]
                if term not in COMMON_DOMAIN_TERMS:
                    terms[term] += 1
    return {term for term, _count in terms.most_common(30)}


def case_domain_aligned(case: dict, domain_terms: set[str]) -> bool:
    candidate_text = " ".join(
        [
            str(case.get("title", "")),
            str(case.get("precondition", "")),
            " ".join(str(item) for item in case.get("steps", [])),
            " ".join(str(item) for item in case.get("expected_results", [])),
            " ".join(str(item) for item in case.get("requirement_refs", [])),
            str(case.get("ai_reason", "")),
        ],
    ).lower()
    return any(term in candidate_text for term in domain_terms)


def case_coverage_dimensions(case: dict) -> list[dict[str, str]]:
    return normalize_case_coverage_dimensions(case.get("coverage_dimensions"))


def normalize_case_coverage_dimensions(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    dimensions: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in value:
        if isinstance(item, str):
            raw_key = item
            evidence = ""
        elif isinstance(item, dict):
            raw_key = str(item.get("key") or item.get("dimension") or item.get("name") or "")
            evidence = str(item.get("evidence") or item.get("reason") or item.get("note") or "")
        else:
            continue
        key = normalize_coverage_dimension_key(raw_key)
        if key is None or key in seen:
            continue
        seen.add(key)
        dimensions.append(
            {
                "key": key,
                "label": CASE_COVERAGE_DIMENSION_LABELS[key],
                "evidence": evidence,
                "source": "model",
            },
        )
    return dimensions


def normalize_coverage_dimension_key(value: str) -> str | None:
    key = value.strip().lower().replace(" ", "_").replace("-", "_")
    key = CASE_COVERAGE_DIMENSION_ALIASES.get(key, key)
    return key if key in CASE_COVERAGE_DIMENSION_LABELS else None


def persist_case_generation_candidates(
    session: Session,
    generation_task: CaseGenerationTask,
    output: dict,
) -> CaseGenerationTask:
    for case in output["cases"]:
        session.add(
            GeneratedCaseCandidate(
                generation_task_id=generation_task.id,
                project_id=generation_task.project_id,
                title=case["title"],
                priority=case.get("priority", "P2"),
                test_type=case.get("test_type", "functional"),
                precondition=case.get("precondition"),
                steps_json=case["steps"],
                expected_results_json=case["expected_results"],
                input_data_json=case.get("input_data", {}),
                tags=case.get("tags", []),
                requirement_refs_json=case["requirement_refs"],
                risk_refs_json=case.get("risk_refs", []),
                source_knowledge_evidence_json=case.get("source_knowledge_evidence", []),
                coverage_dimensions_json=case_coverage_dimensions(case),
                ai_reason=case["ai_reason"],
            ),
        )
    generation_task.status = "succeeded"
    generation_task.generated_count = len(output["cases"])
    session.add(generation_task)
    session.commit()
    session.refresh(generation_task)
    return generation_task
