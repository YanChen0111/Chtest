from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service as ai_runtime_service
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase
from backend.app.modules.cases.schemas import (
    CaseGenerationStartRequest,
    CaseReviewRequest,
    GeneratedCaseCandidateListItemRead,
)
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.projects.models import Project
from backend.app.modules.requirements.models import Requirement, RequirementReview, RiskItem
from backend.app.workers.enqueue import FakeAIQueue, enqueue_ai_task
from backend.app.workers.handlers.ai_task_handler import run_ai_task


class ProjectNotFoundError(Exception):
    pass


class RequirementNotFoundError(Exception):
    pass


class RequirementReviewNotFoundError(Exception):
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

    prompt = get_prompt_version_by_ref(session, data.prompt_version)
    skill = get_skill_version_by_ref(session, data.skill_version)
    context = context_manifest(session, data.project_id, data.context_artifact_ids)
    risk_items = []
    if data.requirement_review_id is not None:
        risk_items = list(
            session.scalars(select(RiskItem).where(RiskItem.requirement_review_id == data.requirement_review_id)),
        )
    ai_task = AITask(
        project_id=data.project_id,
        agent_name="CaseGenerationAgent",
        task_type="case_generation",
        prompt_version_id=prompt.id,
        skill_version_id=skill.id,
        model_provider=data.model_provider,
        model_name=data.model_name,
        status="created",
        input_json={
            "requirement": requirement.content,
            "requirement_id": str(requirement.id),
            "requirement_review": review_summary(review) if review is not None else None,
            "risk_items": [risk_summary(risk) for risk in risk_items],
            "target_test_types": data.target_test_types,
            "use_knowledge": data.use_knowledge,
            "context_artifact_ids": [str(context_id) for context_id in data.context_artifact_ids],
            "context_manifest": context,
            "mock_mode": data.mock_mode,
        },
        context_artifact_ids=data.context_artifact_ids,
    )
    session.add(ai_task)
    session.commit()
    session.refresh(ai_task)

    queue = FakeAIQueue()
    job = enqueue_ai_task(session, queue, ai_task.id)
    run_ai_task(session, store, job)
    session.refresh(ai_task)

    if ai_task.status != "succeeded":
        raise CaseGenerationSchemaInvalidError

    try:
        validate_case_generation_output(ai_task.output_json)
    except CaseGenerationSchemaInvalidError:
        mark_case_generation_schema_invalid(session, ai_task)
        raise

    generation_task = persist_case_generation_task(session, requirement, review, ai_task, data, ai_task.output_json)
    return generation_task, ai_task


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
            ai_reason=candidate.ai_reason,
            status=candidate.status,
        )
        for candidate in candidates
    ]


def review_candidate(session: Session, candidate_id: uuid.UUID, data: CaseReviewRequest) -> tuple[GeneratedCaseCandidate, TestCase | None]:
    candidate = session.get(GeneratedCaseCandidate, candidate_id)
    if candidate is None:
        raise CaseCandidateNotFoundError
    if candidate.status in {"approved", "approved_after_edit", "rejected"}:
        raise CaseCandidateAlreadyFinalError

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
    session.commit()
    session.refresh(candidate)
    if test_case is not None:
        session.refresh(test_case)
    return candidate, test_case


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


def persist_case_generation_task(
    session: Session,
    requirement: Requirement,
    review: RequirementReview | None,
    ai_task: AITask,
    data: CaseGenerationStartRequest,
    output: dict,
) -> CaseGenerationTask:
    generation_task = CaseGenerationTask(
        project_id=data.project_id,
        requirement_id=requirement.id,
        requirement_review_id=review.id if review is not None else None,
        ai_task_id=ai_task.id,
        target_test_types=data.target_test_types,
        status="succeeded",
        generated_count=len(output["cases"]),
    )
    session.add(generation_task)
    session.flush()
    for case in output["cases"]:
        session.add(
            GeneratedCaseCandidate(
                generation_task_id=generation_task.id,
                project_id=data.project_id,
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
                ai_reason=case["ai_reason"],
            ),
        )
    session.commit()
    session.refresh(generation_task)
    return generation_task
