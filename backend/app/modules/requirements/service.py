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
from backend.app.modules.extension import service as extension_service
from backend.app.modules.knowledge import service as knowledge_service
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.projects.models import Module, Project
from backend.app.modules.requirements.models import Requirement, RequirementReview, RiskItem
from backend.app.modules.requirements.schemas import (
    RequirementCreate,
    RequirementDocumentCreate,
    RequirementDocumentRead,
    RequirementReviewDetailRead,
    RequirementReviewStartRequest,
)
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


class RequirementDocumentNotFoundError(Exception):
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
    retrieval_payload, retrieval_context_artifact_ids = retrieve_requirement_knowledge(
        session,
        store,
        requirement,
        use_knowledge=data.use_knowledge,
    )
    context_artifact_ids = list(dict.fromkeys([*data.context_artifact_ids, *retrieval_context_artifact_ids]))
    model_provider, model_name = resolve_model_identity(
        model_provider=data.model_provider,
        model_name=data.model_name,
        default_provider="mock",
        default_model_name="mock-requirement-review",
    )
    ai_task = AITask(
        project_id=requirement.project_id,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=prompt.id,
        skill_version_id=skill.id,
        model_provider=model_provider,
        model_name=model_name,
        status="created",
        input_json={
            "requirement": requirement.content,
            "requirement_id": str(requirement.id),
            "use_knowledge": data.use_knowledge,
            "context_artifact_ids": [str(context_id) for context_id in context_artifact_ids],
            "context_manifest": context_manifest(session, requirement.project_id, context_artifact_ids),
            "clarification_context": clarification_context(data),
            "knowledge_retrieval": retrieval_payload,
            "mock_mode": data.mock_mode,
        },
        context_artifact_ids=context_artifact_ids,
    )
    session.add(ai_task)
    session.flush()
    knowledge_service.link_retrieval_run_to_ai_task(
        session,
        project_id=requirement.project_id,
        retrieval_payload=retrieval_payload,
        ai_task_id=ai_task.id,
    )
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
    if retrieval_payload is not None:
        attach_retrieval_evidence_artifact(session, store, ai_task, retrieval_payload, context_artifact_ids)
    review = persist_requirement_review(session, requirement, ai_task, output)
    return ai_task, review


def retrieve_requirement_knowledge(
    session: Session,
    store: LocalArtifactStore,
    requirement: Requirement,
    *,
    use_knowledge: bool,
) -> tuple[dict | None, list[uuid.UUID]]:
    if not use_knowledge:
        return None, []

    adapter_retrieval = extension_service.retrieve_deterministic_knowledge(
        session=session,
        store=store,
        project_id=requirement.project_id,
        query_text=requirement.content,
    )
    retrieval_run, card_evidence = knowledge_service.retrieve_and_persist_test_knowledge_evidence(
        session,
        store,
        project_id=requirement.project_id,
        query_text=requirement.content,
        limit=5,
        approved_only=True,
        consumer_entity_type="Requirement",
        consumer_entity_id=requirement.id,
    )
    if not adapter_retrieval.used_knowledge and not card_evidence:
        return None, []

    adapter_payload = adapter_retrieval.model_dump(mode="json")
    adapter_payload["created_knowledge_retrieval_run_id"] = str(retrieval_run.id)
    adapter_payload["knowledge_retrieval_run_id"] = str(retrieval_run.id)
    adapter_payload["knowledge_retrieval_run_ids"] = [str(retrieval_run.id)] if card_evidence else []
    adapter_payload["knowledge_retrieval_artifact_id"] = (
        str(retrieval_run.evidence_artifact_id)
        if retrieval_run.evidence_artifact_id is not None
        else None
    )
    if not card_evidence:
        return adapter_payload, list(adapter_retrieval.used_context_artifact_ids)

    card_source_artifact_ids = [
        uuid.UUID(str(item["source_artifact_id"]))
        for item in card_evidence
        if item.get("source_artifact_id")
    ]
    used_context_artifact_ids = list(
        dict.fromkeys([*adapter_retrieval.used_context_artifact_ids, *card_source_artifact_ids]),
    )
    adapter_results = list(adapter_payload.get("results", [])) if adapter_retrieval.used_knowledge else []
    return (
        {
            "adapter_name": adapter_retrieval.adapter_name,
            "retrieval_mode": (
                "deterministic_hybrid"
                if adapter_retrieval.used_knowledge
                else "test_knowledge_hybrid"
            ),
            "query_text": requirement.content,
            "query_terms": knowledge_service.normalize_terms(requirement.content),
            "used_knowledge": True,
            "created_knowledge_retrieval_run_id": str(retrieval_run.id),
            "knowledge_retrieval_run_id": str(retrieval_run.id),
            "knowledge_retrieval_run_ids": [str(retrieval_run.id)],
            "knowledge_retrieval_artifact_id": (
                str(retrieval_run.evidence_artifact_id)
                if retrieval_run.evidence_artifact_id is not None
                else None
            ),
            "used_context_artifact_ids": [str(artifact_id) for artifact_id in used_context_artifact_ids],
            "result_sources": [
                *([] if not adapter_results else ["context_artifact"]),
                "test_knowledge_card",
            ],
            "results": [*adapter_results, *card_evidence],
        },
        used_context_artifact_ids,
    )


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


def create_requirement_document(
    session: Session,
    store: LocalArtifactStore,
    requirement_id: uuid.UUID,
    data: RequirementDocumentCreate,
) -> RequirementDocumentRead:
    requirement = get_requirement(session, requirement_id)
    review = session.scalar(
        select(RequirementReview).where(
            RequirementReview.id == data.requirement_review_id,
            RequirementReview.requirement_id == requirement.id,
        ),
    )
    if review is None:
        raise RequirementReviewNotFoundError

    risk_items = list(
        session.scalars(
            select(RiskItem)
            .where(RiskItem.requirement_review_id == review.id)
            .order_by(RiskItem.created_at.asc(), RiskItem.id.asc()),
        ),
    )
    document_number = next_requirement_document_number(session, requirement.project_id)
    markdown = render_requirement_document(
        requirement=requirement,
        review=review,
        risk_items=risk_items,
        document_number=document_number,
        version=data.version,
        status=data.status,
    )
    artifact_id = uuid.uuid4()
    file_path = f"projects/{requirement.project_id}/requirement-documents/{artifact_id}.md"
    write_result = store.write_bytes(file_path, markdown.encode("utf-8"))
    artifact = Artifact(
        id=artifact_id,
        project_id=requirement.project_id,
        owner_entity_type="RequirementReview",
        owner_entity_id=review.id,
        artifact_type="requirement_md",
        file_path=write_result.file_path,
        mime_type="text/markdown",
        size_bytes=write_result.size_bytes,
        sha256=write_result.sha256,
        metadata_json={
            "created_by_component": "RequirementDocumentGenerator",
            "source_entity_type": "RequirementReview",
            "source_entity_id": str(review.id),
            "requirement_id": str(requirement.id),
            "requirement_review_id": str(review.id),
            "document_number": document_number,
            "version": data.version,
            "title": requirement.title,
            "status": data.status,
            "safe_to_show": True,
            "redaction_applied": False,
            "description": f"Requirement document {document_number}",
        },
    )
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return requirement_document_read(artifact)


def list_requirement_documents(session: Session, project_id: uuid.UUID) -> list[RequirementDocumentRead]:
    ensure_project_exists(session, project_id)
    artifacts = list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.project_id == project_id,
                Artifact.artifact_type == "requirement_md",
            )
            .order_by(Artifact.created_at.desc(), Artifact.id.desc()),
        ),
    )
    return [requirement_document_read(artifact) for artifact in artifacts if is_requirement_document_artifact(artifact)]


def get_requirement_document_artifact(
    session: Session,
    artifact_id: uuid.UUID,
    *,
    project_id: uuid.UUID | None = None,
    requirement_id: uuid.UUID | None = None,
) -> Artifact:
    artifact = session.get(Artifact, artifact_id)
    if (
        artifact is None
        or artifact.artifact_type != "requirement_md"
        or not is_requirement_document_artifact(artifact)
        or (project_id is not None and artifact.project_id != project_id)
        or (requirement_id is not None and document_requirement_id(artifact) != requirement_id)
    ):
        raise RequirementDocumentNotFoundError
    return artifact


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


def clarification_context(data: RequirementReviewStartRequest) -> dict:
    return {
        "supplement_text": data.supplement_text or "",
        "clarification_answers": [
            {"question": item.question, "answer": item.answer}
            for item in data.clarification_answers
        ],
    }


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
            session.commit()
            session.refresh(ai_task)
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
            "description": (
                "Hybrid TestKnowledgeCard retrieval evidence"
                if includes_test_knowledge_cards
                else "Deterministic local knowledge retrieval evidence"
            ),
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


def next_requirement_document_number(session: Session, project_id: uuid.UUID) -> str:
    project = ensure_project_exists(session, project_id)
    prefix = f"RD-{project_code(project.name)}-{ai_runtime_service.utc_now().strftime('%Y%m%d')}"
    existing_numbers = [
        str(artifact.metadata_json.get("document_number", ""))
        for artifact in session.scalars(
            select(Artifact).where(
                Artifact.project_id == project_id,
                Artifact.artifact_type == "requirement_md",
            ),
        )
        if str(artifact.metadata_json.get("document_number", "")).startswith(prefix)
    ]
    return f"{prefix}-{len(existing_numbers) + 1:04d}"


def project_code(project_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", project_name).strip("-").upper()
    if not normalized:
        return "PROJECT"
    return normalized[:16].strip("-") or "PROJECT"


def render_requirement_document(
    *,
    requirement: Requirement,
    review: RequirementReview,
    risk_items: list[RiskItem],
    document_number: str,
    version: str,
    status: str,
) -> str:
    issues = review.issues_json
    questions = review.clarification_questions_json
    notes = review.test_design_notes_json
    lines = [
        "# 需求规格说明书",
        "",
        "## 1. 文档信息",
        f"- 需求文档编号：{document_number}",
        f"- 需求标题：{requirement.title}",
        f"- 需求来源：{requirement.source_ref or 'manual'}",
        f"- 版本：{version}",
        f"- 状态：{status}",
        f"- Requirement ID：{requirement.id}",
        f"- RequirementReview ID：{review.id}",
        "",
        "## 2. 背景与目标",
        requirement.content,
        "",
        "## 3. 质量评审摘要",
        f"- 综合评分：{review.overall_score}",
        f"- 完整性：{review.completeness_score}",
        f"- 清晰度：{review.clarity_score}",
        f"- 一致性：{review.consistency_score}",
        f"- 可测试性：{review.testability_score}",
        f"- 可行性：{review.feasibility_score}",
        f"- 逻辑性：{review.logic_score}",
        "",
        "## 4. 功能需求",
        "| 编号 | 需求描述 | 优先级 | 验收标准 | 来源 | 状态 |",
        "|---|---|---|---|---|---|",
        f"| FR-001 | {one_line(requirement.content)} | P1 | 能被测试用例覆盖且结果可验证 | {requirement.source_ref or requirement.id} | active |",
        "",
        "## 5. 待澄清问题",
        *markdown_list(questions, empty="暂无待澄清问题。"),
        "",
        "## 6. 评审发现",
        *markdown_issue_list(issues),
        "",
        "## 7. 测试设计要点",
        *markdown_list(notes, empty="暂无额外测试设计建议。"),
        "",
        "## 8. 风险与建议",
        "| 风险 | 等级 | 类型 | 影响 | 建议 |",
        "|---|---|---|---|---|",
        *markdown_risk_rows(risk_items),
        "",
        "## 9. 追踪矩阵",
        "| 需求编号 | 风险项 | 用例 | 自动化草稿 | 执行证据 |",
        "|---|---|---|---|---|",
        "| FR-001 | 见风险与建议 | 待生成 | 待生成 | 待执行 |",
        "",
    ]
    return "\n".join(lines)


def one_line(value: str, *, limit: int = 120) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 1]}…"


def markdown_list(items: list, *, empty: str) -> list[str]:
    if not items:
        return [f"- {empty}"]
    return [f"- {one_line(str(item), limit=180)}" for item in items]


def markdown_issue_list(items: list) -> list[str]:
    if not items:
        return ["- 暂无评审发现。"]
    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            label = str(item.get("type", "issue"))
            severity = str(item.get("severity", "medium"))
            text = str(item.get("text", item))
            lines.append(f"- [{severity}] {label}: {text}")
        else:
            lines.append(f"- {item}")
    return lines


def markdown_risk_rows(risk_items: list[RiskItem]) -> list[str]:
    if not risk_items:
        return ["| 暂无风险项 | low | business | 暂无 | 暂无 |"]
    return [
        f"| {risk.title} | {risk.risk_level} | {risk.category} | {one_line(risk.impact)} | {one_line(risk.suggestion)} |"
        for risk in risk_items
    ]


def is_requirement_document_artifact(artifact: Artifact) -> bool:
    return (
        artifact.artifact_type == "requirement_md"
        and bool(artifact.metadata_json.get("document_number"))
        and bool(artifact.metadata_json.get("requirement_id"))
        and bool(artifact.metadata_json.get("requirement_review_id"))
    )


def document_requirement_id(artifact: Artifact) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(artifact.metadata_json.get("requirement_id")))
    except (TypeError, ValueError):
        return None


def requirement_document_read(artifact: Artifact) -> RequirementDocumentRead:
    metadata = artifact.metadata_json
    return RequirementDocumentRead(
        id=artifact.id,
        project_id=artifact.project_id,
        requirement_id=uuid.UUID(str(metadata["requirement_id"])),
        requirement_review_id=uuid.UUID(str(metadata["requirement_review_id"])),
        document_number=str(metadata["document_number"]),
        version=str(metadata.get("version", "v1")),
        title=str(metadata.get("title", "")),
        status=str(metadata.get("status", "draft")),
        artifact_id=artifact.id,
        download_url=f"/api/artifacts/{artifact.id}/download",
        created_at=artifact.created_at,
    )
