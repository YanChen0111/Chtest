from __future__ import annotations

import json
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service as ai_runtime_service
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.ai_runtime.providers.base import ProviderArtifactPayload
from backend.app.modules.extension import service as extension_service
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.projects.models import Module, Project
from backend.app.modules.requirements.models import Requirement, RequirementReview, RiskItem
from backend.app.modules.requirements.schemas import RequirementCreate, RequirementReviewDetailRead, RequirementReviewStartRequest
from backend.app.workers.enqueue import FakeAIQueue, enqueue_ai_task
from backend.app.workers.handlers.ai_task_handler import run_ai_task


class ProjectNotFoundError(Exception):
    pass


class ModuleNotFoundError(Exception):
    pass


class RequirementNotFoundError(Exception):
    pass


class PromptVersionNotFoundError(Exception):
    pass


class SkillVersionNotFoundError(Exception):
    pass


class RequirementReviewSchemaInvalidError(Exception):
    pass


class RequirementReviewNotFoundError(Exception):
    pass


class ContextArtifactNotFoundError(Exception):
    pass


def ensure_project_exists(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise ProjectNotFoundError
    return project


def ensure_module_belongs_to_project(
    session: Session,
    project_id: uuid.UUID,
    module_id: uuid.UUID | None,
) -> None:
    if module_id is None:
        return

    module = session.scalar(select(Module).where(Module.id == module_id, Module.project_id == project_id))
    if module is None:
        raise ModuleNotFoundError


def create_requirement(session: Session, data: RequirementCreate) -> Requirement:
    ensure_project_exists(session, data.project_id)
    ensure_module_belongs_to_project(session, data.project_id, data.module_id)

    requirement = Requirement(
        project_id=data.project_id,
        module_id=data.module_id,
        title=data.title,
        content=data.content,
        source_type=data.source_type,
        source_ref=data.source_ref,
    )
    session.add(requirement)
    session.commit()
    session.refresh(requirement)
    return requirement


def get_requirement(session: Session, requirement_id: uuid.UUID) -> Requirement:
    requirement = session.get(Requirement, requirement_id)
    if requirement is None:
        raise RequirementNotFoundError
    return requirement


def list_requirements(session: Session, project_id: uuid.UUID) -> list[Requirement]:
    ensure_project_exists(session, project_id)
    return list(
        session.scalars(
            select(Requirement)
            .where(Requirement.project_id == project_id)
            .order_by(Requirement.created_at.asc(), Requirement.title.asc(), Requirement.id.asc()),
        ),
    )


def start_requirement_review(
    session: Session,
    store: LocalArtifactStore,
    requirement_id: uuid.UUID,
    data: RequirementReviewStartRequest,
) -> tuple[AITask, RequirementReview]:
    requirement = get_requirement(session, requirement_id)
    prompt = get_prompt_version_by_ref(session, data.prompt_version)
    skill = get_skill_version_by_ref(session, data.skill_version)
    retrieval = None
    retrieval_context_artifact_ids: list[uuid.UUID] = []
    if data.use_knowledge:
        retrieval = extension_service.retrieve_deterministic_knowledge(
            session=session,
            store=store,
            project_id=requirement.project_id,
            query_text=requirement.content,
        )
        retrieval_context_artifact_ids = retrieval.used_context_artifact_ids
    context_artifact_ids = list(dict.fromkeys([*data.context_artifact_ids, *retrieval_context_artifact_ids]))
    ai_task = AITask(
        project_id=requirement.project_id,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=prompt.id,
        skill_version_id=skill.id,
        model_provider=data.model_provider,
        model_name=data.model_name,
        status="created",
        input_json={
            "requirement": requirement.content,
            "requirement_id": str(requirement.id),
            "use_knowledge": data.use_knowledge,
            "context_artifact_ids": [str(context_id) for context_id in context_artifact_ids],
            "context_manifest": context_manifest(session, requirement.project_id, context_artifact_ids),
            "knowledge_retrieval": retrieval.model_dump(mode="json") if retrieval and retrieval.used_knowledge else None,
            "mock_mode": data.mock_mode,
        },
        context_artifact_ids=context_artifact_ids,
    )
    session.add(ai_task)
    session.commit()
    session.refresh(ai_task)

    queue = FakeAIQueue()
    job = enqueue_ai_task(session, queue, ai_task.id)
    run_ai_task(session, store, job)
    session.refresh(ai_task)

    if ai_task.status != "succeeded":
        raise RequirementReviewSchemaInvalidError

    output = ai_task.output_json
    try:
        validate_requirement_review_output(output)
    except RequirementReviewSchemaInvalidError:
        mark_review_schema_invalid(session, ai_task)
        raise
    if retrieval is not None and retrieval.used_knowledge:
        attach_retrieval_evidence_artifact(session, store, ai_task, retrieval.model_dump(mode="json"), context_artifact_ids)
    review = persist_requirement_review(session, requirement, ai_task, output)
    return ai_task, review


def get_requirement_review_detail(session: Session, requirement_id: uuid.UUID) -> RequirementReviewDetailRead:
    get_requirement(session, requirement_id)
    review = session.scalar(
        select(RequirementReview)
        .where(RequirementReview.requirement_id == requirement_id)
        .order_by(RequirementReview.created_at.desc(), RequirementReview.id.desc()),
    )
    if review is None:
        raise RequirementReviewNotFoundError
    return requirement_review_detail(session, review)


def get_prompt_version_by_ref(session: Session, version_ref: str) -> PromptVersion:
    name, version = split_version_ref(version_ref)
    prompt = session.scalar(
        select(PromptVersion).where(
            PromptVersion.name == name,
            PromptVersion.version == version,
            PromptVersion.status == "active",
        ),
    )
    if prompt is None:
        raise PromptVersionNotFoundError
    return prompt


def get_skill_version_by_ref(session: Session, version_ref: str) -> SkillVersion:
    name, version = split_version_ref(version_ref)
    skill = session.scalar(
        select(SkillVersion).where(
            SkillVersion.name == name,
            SkillVersion.version == version,
            SkillVersion.status == "active",
        ),
    )
    if skill is None:
        raise SkillVersionNotFoundError
    return skill


def split_version_ref(version_ref: str) -> tuple[str, str]:
    name, _, version = version_ref.partition(":")
    return name, version or "v1"


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


def validate_requirement_review_output(output: dict) -> None:
    scores = output.get("scores")
    required_scores = {"completeness", "clarity", "consistency", "testability", "feasibility", "logic"}
    if not isinstance(scores, dict) or not required_scores.issubset(scores):
        raise RequirementReviewSchemaInvalidError
    for score_name in required_scores:
        score = scores[score_name]
        if not isinstance(score, int) or score < 0 or score > 100:
            raise RequirementReviewSchemaInvalidError
    overall_score = output.get("overall_score", scores.get("overall", 0))
    if not isinstance(overall_score, int) or overall_score < 0 or overall_score > 100:
        raise RequirementReviewSchemaInvalidError
    if not isinstance(output.get("issues"), list):
        raise RequirementReviewSchemaInvalidError
    if not isinstance(output.get("clarification_questions"), list):
        raise RequirementReviewSchemaInvalidError
    if "test_design_notes" in output and not isinstance(output["test_design_notes"], list):
        raise RequirementReviewSchemaInvalidError
    if not isinstance(output.get("risk_items"), list):
        raise RequirementReviewSchemaInvalidError
    for risk in output["risk_items"]:
        if not isinstance(risk, dict):
            raise RequirementReviewSchemaInvalidError
        if not isinstance(risk.get("title"), str) or not risk["title"]:
            raise RequirementReviewSchemaInvalidError
        if not isinstance(risk.get("suggestion"), str) or not risk["suggestion"]:
            raise RequirementReviewSchemaInvalidError
        risk_level = risk.get("risk_level", "medium")
        if risk_level not in {"low", "medium", "high", "critical"}:
            raise RequirementReviewSchemaInvalidError
        if "impact" in risk and not isinstance(risk["impact"], str):
            raise RequirementReviewSchemaInvalidError
        if "category" in risk and risk["category"] not in {"business", "technical", "data", "environment", "regression"}:
            raise RequirementReviewSchemaInvalidError


def mark_review_schema_invalid(session: Session, ai_task: AITask) -> None:
    error_json = {
        "error_code": "REQUIREMENT_REVIEW_SCHEMA_INVALID",
        "message": "Requirement review output did not match the expected schema.",
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


def attach_retrieval_evidence_artifact(
    session: Session,
    store: LocalArtifactStore,
    ai_task: AITask,
    retrieval_payload: dict,
    used_context_artifact_ids: list[uuid.UUID],
) -> Artifact:
    retrieved_context_artifact_ids = list(retrieval_payload.get("used_context_artifact_ids", []))
    retrieval_results = list(retrieval_payload.get("results", []))
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
            "created_by_component": "DeterministicKnowledgeAdapter",
            "source_entity_type": "AITask",
            "source_entity_id": str(ai_task.id),
            "safe_to_show": True,
            "redaction_applied": any(
                bool(result.get("redaction_applied", False)) for result in retrieval_results
            ),
            "description": "Deterministic local knowledge retrieval evidence",
            "retrieval_mode": "deterministic_local",
            "query_terms": list(retrieval_payload.get("query_terms", [])),
            "result_count": len(retrieval_results),
            "results": retrieval_results,
            "used_context_artifact_ids": retrieved_context_artifact_ids,
        },
    )
    output_json = dict(ai_task.output_json)
    output_json["used_knowledge"] = True
    output_json["used_context_artifact_ids"] = [str(context_id) for context_id in used_context_artifact_ids]
    output_json["retrieval_evidence_artifact_id"] = str(artifact.id)
    ai_task.output_json = output_json
    session.add(ai_task)
    session.add(artifact)
    session.commit()
    session.refresh(ai_task)
    session.refresh(artifact)
    return artifact


def persist_requirement_review(
    session: Session,
    requirement: Requirement,
    ai_task: AITask,
    output: dict,
) -> RequirementReview:
    scores = output["scores"]
    review = RequirementReview(
        requirement_id=requirement.id,
        ai_task_id=ai_task.id,
        completeness_score=int(scores["completeness"]),
        clarity_score=int(scores["clarity"]),
        consistency_score=int(scores["consistency"]),
        testability_score=int(scores["testability"]),
        feasibility_score=int(scores["feasibility"]),
        logic_score=int(scores["logic"]),
        overall_score=int(output.get("overall_score", scores.get("overall", 0))),
        issues_json=output["issues"],
        clarification_questions_json=output["clarification_questions"],
        test_design_notes_json=output.get("test_design_notes", []),
        status="reviewed",
    )
    session.add(review)
    session.flush()

    for risk in output["risk_items"]:
        session.add(
            RiskItem(
                project_id=requirement.project_id,
                requirement_review_id=review.id,
                title=str(risk["title"]),
                risk_level=str(risk.get("risk_level", "medium")),
                category=str(risk.get("category", "business")),
                impact=str(risk.get("impact", risk["title"])),
                suggestion=str(risk["suggestion"]),
            ),
        )
    session.commit()
    session.refresh(review)
    return review


def requirement_review_detail(session: Session, review: RequirementReview) -> RequirementReviewDetailRead:
    ai_task = session.get(AITask, review.ai_task_id)
    risk_items = list(
        session.scalars(
            select(RiskItem)
            .where(RiskItem.requirement_review_id == review.id)
            .order_by(RiskItem.created_at.asc(), RiskItem.id.asc()),
        ),
    )
    context_manifest_artifact = session.scalar(
        select(Artifact).where(
            Artifact.owner_entity_type == "AITask",
            Artifact.owner_entity_id == review.ai_task_id,
            Artifact.file_path.like("%/context_manifest.json"),
        ),
    )
    used_context_ids = []
    used_knowledge = False
    if ai_task is not None:
        used_context_ids = [
            uuid.UUID(str(context_id))
            for context_id in ai_task.output_json.get("used_context_artifact_ids", ai_task.context_artifact_ids)
        ]
        used_knowledge = bool(ai_task.output_json.get("used_knowledge", False))

    return RequirementReviewDetailRead(
        id=review.id,
        requirement_id=review.requirement_id,
        ai_task_id=review.ai_task_id,
        overall_score=review.overall_score,
        scores={
            "completeness": review.completeness_score,
            "clarity": review.clarity_score,
            "consistency": review.consistency_score,
            "testability": review.testability_score,
            "feasibility": review.feasibility_score,
            "logic": review.logic_score,
        },
        issues=review.issues_json,
        clarification_questions=review.clarification_questions_json,
        test_design_notes=review.test_design_notes_json,
        risk_items=risk_items,
        used_knowledge=used_knowledge,
        used_context_artifact_ids=used_context_ids,
        context_manifest_artifact_id=context_manifest_artifact.id if context_manifest_artifact else None,
        status=review.status,
    )
