from __future__ import annotations

import hashlib
import json
import math
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service as ai_runtime_service
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase
from backend.app.modules.extension.models import KnowledgeAdapterConfig
from backend.app.modules.knowledge import postgres_adapter
from backend.app.modules.knowledge.optional_providers import OPTIONAL_PROVIDER_TYPES, search_optional_provider
from backend.app.modules.knowledge.models import (
    KnowledgeFeedbackEvent,
    KnowledgeEvidence,
    KnowledgeIngestionRun,
    KnowledgeRetrievalRun,
    TestKnowledgeCard,
    TestKnowledgeEmbeddingIndex,
    TestKnowledgeRelationship,
)
from backend.app.modules.knowledge.schemas import (
    KnowledgeIngestionArtifactRead,
    KnowledgeIngestionRunCreateRequest,
    KnowledgeIngestionRunRead,
    KnowledgeEvidenceRead,
    EvidenceTraceArtifactRefRead,
    EvidenceTraceNodeRead,
    EvidenceTraceRead,
    EvidenceTraceStageRead,
    KnowledgeRetrievalArtifactRead,
    KnowledgeRetrievalRunCreateRequest,
    KnowledgeRetrievalRunRead,
    TestKnowledgeCardRead,
)
from backend.app.modules.projects.models import Module, Project
from backend.app.modules.requirements.models import Requirement, RiskItem
from backend.app.modules.review_history.service import append_review_history


TERM_PATTERN = re.compile(r"\w+", re.UNICODE)
SENTENCE_SPLIT_PATTERN = re.compile(r"[\n。！？!?；;]+")
ENDPOINT_PATTERN = re.compile(r"\b(?:GET|POST|PUT|PATCH|DELETE)\s+(/[A-Za-z0-9_./{}:-]+)|(/[A-Za-z0-9_./{}:-]+)")
PROMPT_ELIGIBLE_STATUSES = {"approved", "extracted"}
REVIEWABLE_STATUSES = {"approved", "stale", "unsafe", "duplicate", "archived"}
STATUS_PRIORITY = {"approved": 0, "extracted": 1}
DEFAULT_EMBEDDING_PROVIDER = "deterministic_local"
DEFAULT_EMBEDDING_MODEL = "deterministic-hashing-v1"
DEFAULT_EMBEDDING_DIM = 64
MIN_VECTOR_SIMILARITY = 0.05
SECRET_CONFIG_KEYS = {
    "api_key",
    "authorization",
    "client_secret",
    "cookie",
    "credential",
    "password",
    "secret",
    "token",
}
INGESTION_EVIDENCE_FILES = {
    "knowledge_ingestion_manifest": "ingestion-manifest.json",
    "knowledge_parse_result": "parse-result.json",
    "knowledge_extraction_result": "extraction-result.json",
    "knowledge_safety_result": "safety-result.json",
    "error_json": "error.json",
}
RETRIEVAL_QUERY_SECRET_PATTERN = re.compile(
    r"(?i)\b(password|token|secret|api[_-]?key|authorization|cookie)\s*[:=]",
)
ALLOWED_CARD_TRANSITIONS = {
    "extracted": {"approved", "stale", "unsafe", "duplicate", "archived"},
    "approved": {"stale", "unsafe", "duplicate", "archived"},
}


class ProjectNotFoundError(Exception):
    pass


TRACE_ENTITY_TYPES = {
    "KnowledgeIngestionRun",
    "KnowledgeRetrievalRun",
    "KnowledgeEvidence",
    "TestKnowledgeCard",
    "KnowledgeFeedbackEvent",
    "GeneratedCaseCandidate",
}


class EvidenceTraceEntityNotFoundError(Exception):
    pass


class EvidenceTraceEntityTypeNotAllowedError(Exception):
    pass


class EvidenceTraceQueryInvalidError(Exception):
    pass


class SourceArtifactNotFoundError(Exception):
    pass


class SourceArtifactNotAllowedError(Exception):
    pass


class KnowledgeIngestionSourceNotAllowedError(Exception):
    pass


class KnowledgeIngestionConfigNotAllowedError(Exception):
    pass


class KnowledgeIngestionRunNotFoundError(Exception):
    pass


class KnowledgeRetrievalRunNotFoundError(Exception):
    pass


class KnowledgeRetrievalConsumerNotAllowedError(Exception):
    pass


class KnowledgeRetrievalInputNotAllowedError(Exception):
    pass


class TestKnowledgeCardNotFoundError(Exception):
    pass


class TestKnowledgeCardInvalidStatusError(Exception):
    pass


class TestKnowledgeCardDuplicateTargetError(Exception):
    pass


@dataclass(frozen=True)
class KnowledgeExtractionResult:
    source_artifact_id: uuid.UUID
    created_count: int
    skipped_count: int
    cards: list[TestKnowledgeCard]


@dataclass(frozen=True)
class KnowledgeBatchExtractionResult:
    project_id: uuid.UUID
    source_artifact_ids: list[uuid.UUID]
    created_count: int
    skipped_count: int
    cards: list[TestKnowledgeCard]


@dataclass(frozen=True)
class KnowledgeIndexRebuildResult:
    project_id: uuid.UUID
    indexed_count: int
    skipped_count: int
    embedding_model: str
    embedding_dim: int
    items: list[TestKnowledgeEmbeddingIndex]


@dataclass(frozen=True)
class KnowledgeIngestionRunPage:
    items: list[KnowledgeIngestionRun]
    total: int
    next_cursor: str | None


@dataclass(frozen=True)
class KnowledgeMatchResult:
    candidate_count: int
    items: list[dict[str, Any]]
    vector_available: bool
    actual_mode: str
    degraded: bool
    fallback_reason: str | None
    provider_type: str = "deterministic_local"
    capability_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeRetrievalRunPage:
    items: list[KnowledgeRetrievalRun]
    total: int
    next_cursor: str | None


def create_knowledge_ingestion_run(
    session: Session,
    store: LocalArtifactStore,
    data: KnowledgeIngestionRunCreateRequest,
) -> KnowledgeIngestionRun:
    if session.get(Project, data.project_id) is None:
        raise ProjectNotFoundError
    serialized_config = json.dumps(data.config_snapshot, ensure_ascii=False, sort_keys=True, default=str)
    if (
        len(serialized_config.encode("utf-8")) > 20_000
        or config_snapshot_contains_secret(data.config_snapshot)
        or ai_runtime_service.has_high_risk_secret(serialized_config)
    ):
        raise KnowledgeIngestionConfigNotAllowedError

    artifacts = resolve_ingestion_source_artifacts(session, data)
    normalized_refs = [
        {"artifact_id": str(artifact.id)}
        for artifact in sorted(artifacts, key=lambda item: str(item.id))
    ]
    config_snapshot = {**data.config_snapshot, "extract_cards": data.extract_cards}
    idempotency_key = ingestion_idempotency_key(
        project_id=data.project_id,
        source_type=data.source_type,
        artifacts=artifacts,
        parser_name=data.parser_name,
        parser_version=data.parser_version,
        config_snapshot=config_snapshot,
    )
    if not data.force:
        existing = session.scalar(
            select(KnowledgeIngestionRun).where(
                KnowledgeIngestionRun.project_id == data.project_id,
                KnowledgeIngestionRun.idempotency_key == idempotency_key,
            ),
        )
        if existing is not None:
            return existing
    else:
        idempotency_key = hashlib.sha256(
            f"{idempotency_key}:{uuid.uuid4()}".encode("utf-8"),
        ).hexdigest()

    run = KnowledgeIngestionRun(
        project_id=data.project_id,
        idempotency_key=idempotency_key,
        source_type=data.source_type,
        source_refs_json=normalized_refs,
        input_artifact_ids_json=[str(artifact.id) for artifact in artifacts],
        parser_name=data.parser_name,
        parser_version=data.parser_version,
        config_snapshot_json=config_snapshot,
        status="created",
    )
    session.add(run)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        existing = session.scalar(
            select(KnowledgeIngestionRun).where(
                KnowledgeIngestionRun.project_id == data.project_id,
                KnowledgeIngestionRun.idempotency_key == idempotency_key,
            ),
        )
        if existing is not None and not data.force:
            return existing
        raise
    session.refresh(run)

    evidence_ids: list[str] = []
    now = datetime.now(UTC)
    run.started_at = now
    run.status = "parsing"
    session.commit()
    session.refresh(run)
    try:
        manifest = {
            "run_id": str(run.id),
            "project_id": str(run.project_id),
            "source_type": run.source_type,
            "source_refs": normalized_refs,
            "input_artifact_ids": [str(artifact.id) for artifact in artifacts],
            "source_sha256s": sorted(artifact.sha256 for artifact in artifacts),
            "parser_name": run.parser_name,
            "parser_version": run.parser_version,
            "config_snapshot": config_snapshot,
            "idempotency_key": run.idempotency_key,
        }
        evidence_ids.append(
            str(write_ingestion_evidence(session, store, run, "knowledge_ingestion_manifest", manifest).id),
        )

        parsed_sources = [
            {
                "artifact_id": str(artifact.id),
                "artifact_type": artifact.artifact_type,
                "sha256": artifact.sha256,
                "source_ref": artifact.metadata_json.get("source_ref"),
            }
            for artifact in artifacts
        ]
        run.parsed_count = len(parsed_sources)
        evidence_ids.append(
            str(
                write_ingestion_evidence(
                    session,
                    store,
                    run,
                    "knowledge_parse_result",
                    {"parsed_count": run.parsed_count, "sources": parsed_sources, "failed_units": []},
                ).id,
            ),
        )

        run.evidence_artifact_ids_json = evidence_ids
        if data.extract_cards:
            run.status = "extracting"
        session.commit()
        session.refresh(run)

        cards: list[TestKnowledgeCard] = []
        skipped_count = 0
        if data.extract_cards:
            for artifact in artifacts:
                result = extract_test_knowledge_cards(
                    session,
                    store,
                    project_id=run.project_id,
                    source_artifact_id=artifact.id,
                    ingestion_run_id=run.id,
                    commit=False,
                )
                cards.extend(result.cards)
                skipped_count += result.skipped_count
        run.extracted_card_count = len(cards)
        run.skipped_count = skipped_count
        evidence_ids.append(
            str(
                write_ingestion_evidence(
                    session,
                    store,
                    run,
                    "knowledge_extraction_result",
                    {
                        "created_count": len(cards),
                        "skipped_count": skipped_count,
                        "card_ids": [str(card.id) for card in cards],
                    },
                ).id,
            ),
        )
        evidence_ids.append(
            str(
                write_ingestion_evidence(
                    session,
                    store,
                    run,
                    "knowledge_safety_result",
                    {
                        "checked_source_count": len(artifacts),
                        "safe_source_count": len(artifacts),
                        "prompt_eligible_source_count": len(artifacts),
                        "unsafe_source_count": 0,
                    },
                ).id,
            ),
        )
        run.status = "waiting_review" if cards else "completed"
        run.completed_at = None if cards else datetime.now(UTC)
        run.evidence_artifact_ids_json = evidence_ids
        session.commit()
        session.refresh(run)
        return run
    except (OSError, UnicodeError):
        session.rollback()
        return mark_ingestion_failed(
            session,
            store,
            run_id=run.id,
            failed_count=max(1, len(artifacts)),
            error_code="KNOWLEDGE_INGESTION_LOCAL_ERROR",
            error_message="Local knowledge ingestion failed while reading or writing evidence.",
        )
    except Exception:
        session.rollback()
        mark_ingestion_failed(
            session,
            store,
            run_id=run.id,
            failed_count=max(1, len(artifacts)),
            error_code="KNOWLEDGE_INGESTION_INTERNAL_ERROR",
            error_message="Knowledge ingestion failed before completion.",
        )
        raise


def mark_ingestion_failed(
    session: Session,
    store: LocalArtifactStore,
    *,
    run_id: uuid.UUID,
    failed_count: int,
    error_code: str,
    error_message: str,
) -> KnowledgeIngestionRun:
    failed_run = session.get(KnowledgeIngestionRun, run_id)
    if failed_run is None:
        raise KnowledgeIngestionRunNotFoundError
    failed_run.status = "failed"
    failed_run.failed_count = failed_count
    failed_run.error_code = error_code
    failed_run.error_message = error_message
    failed_run.completed_at = datetime.now(UTC)
    session.commit()
    session.refresh(failed_run)
    try:
        error_artifact = write_ingestion_evidence(
            session,
            store,
            failed_run,
            "error_json",
            {"error_code": error_code, "message": error_message},
        )
    except OSError:
        session.rollback()
        return failed_run
    failed_run.evidence_artifact_ids_json = [
        *[str(item) for item in failed_run.evidence_artifact_ids_json],
        str(error_artifact.id),
    ]
    session.commit()
    session.refresh(failed_run)
    return failed_run


def resolve_ingestion_source_artifacts(
    session: Session,
    data: KnowledgeIngestionRunCreateRequest,
) -> list[Artifact]:
    artifacts_by_id: dict[uuid.UUID, Artifact] = {}
    for source_ref in data.source_refs:
        artifact = session.get(Artifact, source_ref.artifact_id)
        if artifact is None or artifact.project_id != data.project_id:
            raise KnowledgeIngestionSourceNotAllowedError
        try:
            ensure_extractable_context_artifact(artifact)
        except SourceArtifactNotAllowedError as exc:
            raise KnowledgeIngestionSourceNotAllowedError from exc
        artifacts_by_id[artifact.id] = artifact
    return list(artifacts_by_id.values())


def ingestion_idempotency_key(
    *,
    project_id: uuid.UUID,
    source_type: str,
    artifacts: list[Artifact],
    parser_name: str,
    parser_version: str,
    config_snapshot: dict[str, Any],
) -> str:
    payload = {
        "project_id": str(project_id),
        "source_type": source_type,
        "source_artifacts": sorted(
            ({"artifact_id": str(artifact.id), "sha256": artifact.sha256} for artifact in artifacts),
            key=lambda item: item["artifact_id"],
        ),
        "parser_name": parser_name,
        "parser_version": parser_version,
        "config_snapshot": config_snapshot,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def config_snapshot_contains_secret(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized_key = str(key).strip().lower().replace("-", "_")
            is_reference = normalized_key.endswith(("_ref", "_reference"))
            if not is_reference and (
                normalized_key in SECRET_CONFIG_KEYS
                or normalized_key.endswith(("_password", "_secret", "_token", "_api_key"))
            ):
                return True
            if config_snapshot_contains_secret(item):
                return True
        return False
    if isinstance(value, list):
        return any(config_snapshot_contains_secret(item) for item in value)
    if isinstance(value, str):
        return ai_runtime_service.has_high_risk_secret(value)
    return False


def write_ingestion_evidence(
    session: Session,
    store: LocalArtifactStore,
    run: KnowledgeIngestionRun,
    artifact_type: str,
    payload: dict[str, Any],
) -> Artifact:
    content = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")
    file_name = INGESTION_EVIDENCE_FILES[artifact_type]
    file_path = f"projects/{run.project_id}/knowledge-ingestion-runs/{run.id}/{file_name}"
    write_result = store.write_bytes(file_path, content)
    artifact = Artifact(
        project_id=run.project_id,
        owner_entity_type="KnowledgeIngestionRun",
        owner_entity_id=run.id,
        artifact_type=artifact_type,
        file_path=write_result.file_path,
        mime_type="application/json",
        size_bytes=write_result.size_bytes,
        sha256=write_result.sha256,
        metadata_json={
            "created_by_component": "KnowledgeIngestionService",
            "source_entity_type": "KnowledgeIngestionRun",
            "source_entity_id": str(run.id),
            "safe_to_show": True,
            "redaction_applied": False,
            "description": f"Knowledge ingestion evidence {artifact_type}",
        },
    )
    session.add(artifact)
    session.flush()
    return artifact


def get_knowledge_ingestion_run(session: Session, run_id: uuid.UUID) -> KnowledgeIngestionRun:
    run = session.get(KnowledgeIngestionRun, run_id)
    if run is None:
        raise KnowledgeIngestionRunNotFoundError
    return run


def list_knowledge_ingestion_runs(
    session: Session,
    project_id: uuid.UUID,
    *,
    status: str | None = None,
    source_type: str | None = None,
    limit: int = 50,
    cursor: uuid.UUID | None = None,
) -> KnowledgeIngestionRunPage:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    filters = [KnowledgeIngestionRun.project_id == project_id]
    if status:
        filters.append(KnowledgeIngestionRun.status == status)
    if source_type:
        filters.append(KnowledgeIngestionRun.source_type == source_type)
    total = session.scalar(
        select(func.count(KnowledgeIngestionRun.id)).where(*filters),
    ) or 0
    page_filters = list(filters)
    if cursor is not None:
        cursor_run = session.get(KnowledgeIngestionRun, cursor)
        if cursor_run is None or cursor_run.project_id != project_id:
            raise KnowledgeIngestionRunNotFoundError
        cursor_created_at = (
            select(KnowledgeIngestionRun.created_at)
            .where(KnowledgeIngestionRun.id == cursor)
            .scalar_subquery()
        )
        page_filters.append(
            or_(
                KnowledgeIngestionRun.created_at < cursor_created_at,
                and_(
                    KnowledgeIngestionRun.created_at == cursor_created_at,
                    KnowledgeIngestionRun.id < cursor_run.id,
                ),
            ),
        )
    rows = list(
        session.scalars(
            select(KnowledgeIngestionRun).where(*page_filters).order_by(
                KnowledgeIngestionRun.created_at.desc(),
                KnowledgeIngestionRun.id.desc(),
            ).limit(limit + 1),
        ),
    )
    has_more = len(rows) > limit
    items = rows[:limit]
    return KnowledgeIngestionRunPage(
        items=items,
        total=total,
        next_cursor=str(items[-1].id) if has_more and items else None,
    )


def ingestion_run_to_read(session: Session, run: KnowledgeIngestionRun) -> KnowledgeIngestionRunRead:
    return ingestion_runs_to_read(session, [run])[0]


def ingestion_runs_to_read(
    session: Session,
    runs: list[KnowledgeIngestionRun],
) -> list[KnowledgeIngestionRunRead]:
    if not runs:
        return []
    run_ids = [run.id for run in runs]
    produced_by_run: dict[uuid.UUID, list[uuid.UUID]] = {run_id: [] for run_id in run_ids}
    for ingestion_run_id, card_id in session.execute(
        select(TestKnowledgeCard.ingestion_run_id, TestKnowledgeCard.id)
        .where(TestKnowledgeCard.ingestion_run_id.in_(run_ids))
        .order_by(TestKnowledgeCard.created_at.asc(), TestKnowledgeCard.id.asc()),
    ):
        if ingestion_run_id is not None:
            produced_by_run[ingestion_run_id].append(card_id)

    all_evidence_ids = {
        uuid.UUID(str(item))
        for run in runs
        for item in run.evidence_artifact_ids_json
    }
    project_ids = {run.project_id for run in runs}
    artifacts_by_owner_and_id = {
        (artifact.owner_entity_id, artifact.id): artifact
        for artifact in session.scalars(
            select(Artifact).where(
                Artifact.id.in_(all_evidence_ids),
                Artifact.project_id.in_(project_ids),
                Artifact.owner_entity_type == "KnowledgeIngestionRun",
                Artifact.owner_entity_id.in_(run_ids),
            ),
        )
    } if all_evidence_ids else {}
    return [
        _ingestion_run_read(
            run,
            produced_card_ids=produced_by_run[run.id],
            artifacts_by_owner_and_id=artifacts_by_owner_and_id,
        )
        for run in runs
    ]


def _ingestion_run_read(
    run: KnowledgeIngestionRun,
    *,
    produced_card_ids: list[uuid.UUID],
    artifacts_by_owner_and_id: dict[tuple[uuid.UUID, uuid.UUID], Artifact],
) -> KnowledgeIngestionRunRead:
    evidence_ids = [uuid.UUID(str(item)) for item in run.evidence_artifact_ids_json]
    evidence_artifacts = [
        KnowledgeIngestionArtifactRead(
            id=artifact.id,
            artifact_type=artifact.artifact_type,
            mime_type=artifact.mime_type,
            size_bytes=artifact.size_bytes,
            sha256=artifact.sha256,
            safe_to_show=artifact.metadata_json.get("safe_to_show") is True,
            download_url=f"/api/artifacts/{artifact.id}/download",
        )
        for artifact_id in evidence_ids
        if (artifact := artifacts_by_owner_and_id.get((run.id, artifact_id))) is not None
    ]
    return KnowledgeIngestionRunRead(
        id=run.id,
        project_id=run.project_id,
        idempotency_key=run.idempotency_key,
        source_type=run.source_type,
        source_refs=run.source_refs_json,
        input_artifact_ids=[uuid.UUID(str(item)) for item in run.input_artifact_ids_json],
        parser_name=run.parser_name,
        parser_version=run.parser_version,
        config_snapshot=run.config_snapshot_json,
        status=run.status,
        parsed_count=run.parsed_count,
        extracted_card_count=run.extracted_card_count,
        skipped_count=run.skipped_count,
        failed_count=run.failed_count,
        error_code=run.error_code,
        error_message=run.error_message,
        evidence_artifact_ids=evidence_ids,
        evidence_artifacts=evidence_artifacts,
        produced_card_ids=produced_card_ids,
        ai_task_id=run.ai_task_id,
        started_at=run.started_at,
        completed_at=run.completed_at,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


def extract_test_knowledge_cards(
    session: Session,
    store: LocalArtifactStore,
    *,
    project_id: uuid.UUID,
    source_artifact_id: uuid.UUID,
    ingestion_run_id: uuid.UUID | None = None,
    commit: bool = True,
) -> KnowledgeExtractionResult:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    artifact = session.get(Artifact, source_artifact_id)
    if artifact is None or artifact.project_id != project_id:
        raise SourceArtifactNotFoundError
    ensure_extractable_context_artifact(artifact)

    text = store.read_bytes(artifact.file_path).decode("utf-8", errors="replace")
    source_version = str(artifact.metadata_json.get("version", "v1"))
    existing_hashes = {
        item.source_quote_hash
        for item in session.scalars(
            select(TestKnowledgeCard).where(
                TestKnowledgeCard.project_id == project_id,
                TestKnowledgeCard.source_artifact_id == source_artifact_id,
            ),
        )
    }
    cards: list[TestKnowledgeCard] = []
    skipped_count = 0
    for index, sentence in enumerate(candidate_sentences(text), start=1):
        quote_hash = hashlib.sha256(sentence.encode("utf-8")).hexdigest()
        if quote_hash in existing_hashes:
            skipped_count += 1
            continue
        knowledge_type = classify_knowledge(sentence)
        card = TestKnowledgeCard(
            project_id=project_id,
            source_artifact_id=source_artifact_id,
            source_document_version=source_version,
            source_section=f"section:{index}",
            source_quote_hash=quote_hash,
            source_locator_json={"section": f"section:{index}", "sentence_index": index},
            source_ref=str(artifact.metadata_json.get("source_ref") or "") or None,
            ingestion_run_id=ingestion_run_id,
            knowledge_type=knowledge_type,
            title=card_title(sentence, knowledge_type),
            content=sentence,
            module_key=infer_module_key(sentence),
            api_endpoint=infer_api_endpoint(sentence),
            risk_type=infer_risk_type(sentence),
            case_type_hint=infer_case_type_hint(sentence, knowledge_type),
            applicability="case_generation",
            confidence=confidence_for(sentence, knowledge_type),
            safe_to_show=True,
            allowed_for_prompt=True,
            status="extracted",
        )
        session.add(card)
        cards.append(card)
        existing_hashes.add(quote_hash)

    if commit:
        session.commit()
    else:
        session.flush()
    for card in cards:
        session.refresh(card)
    return KnowledgeExtractionResult(
        source_artifact_id=source_artifact_id,
        created_count=len(cards),
        skipped_count=skipped_count,
        cards=cards,
    )


def extract_all_test_knowledge_cards(
    session: Session,
    store: LocalArtifactStore,
    *,
    project_id: uuid.UUID,
    source_artifact_ids: list[uuid.UUID] | None = None,
) -> KnowledgeBatchExtractionResult:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    artifact_ids = source_artifact_ids or list_extractable_context_artifact_ids(session, project_id)
    created_count = 0
    skipped_count = 0
    cards: list[TestKnowledgeCard] = []
    for artifact_id in artifact_ids:
        result = extract_test_knowledge_cards(
            session,
            store,
            project_id=project_id,
            source_artifact_id=artifact_id,
        )
        created_count += result.created_count
        skipped_count += result.skipped_count
        cards.extend(result.cards)
    return KnowledgeBatchExtractionResult(
        project_id=project_id,
        source_artifact_ids=artifact_ids,
        created_count=created_count,
        skipped_count=skipped_count,
        cards=cards,
    )


def list_test_knowledge_cards(session: Session, project_id: uuid.UUID) -> list[TestKnowledgeCard]:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    return list(
        session.scalars(
            select(TestKnowledgeCard)
            .where(TestKnowledgeCard.project_id == project_id)
            .order_by(TestKnowledgeCard.created_at.asc(), TestKnowledgeCard.id.asc()),
        ),
    )


def review_test_knowledge_card(
    session: Session,
    *,
    project_id: uuid.UUID,
    card_id: uuid.UUID,
    status: str,
    review_comment: str | None = None,
    duplicate_of_card_id: uuid.UUID | None = None,
) -> TestKnowledgeCard:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    if status not in REVIEWABLE_STATUSES:
        raise TestKnowledgeCardInvalidStatusError
    card = session.get(TestKnowledgeCard, card_id)
    if card is None or card.project_id != project_id:
        raise TestKnowledgeCardNotFoundError
    if status not in ALLOWED_CARD_TRANSITIONS.get(card.status, set()):
        raise TestKnowledgeCardInvalidStatusError
    if status == "approved" and (not card.safe_to_show or not card.allowed_for_prompt):
        raise TestKnowledgeCardInvalidStatusError
    from_status = card.status
    if status == "duplicate":
        if duplicate_of_card_id is None:
            raise TestKnowledgeCardDuplicateTargetError
        duplicate_of = session.get(TestKnowledgeCard, duplicate_of_card_id)
        if (
            duplicate_of is None
            or duplicate_of.project_id != project_id
            or duplicate_of.id == card.id
            or duplicate_of.status != "approved"
            or duplicate_of.duplicate_of_card_id is not None
        ):
            raise TestKnowledgeCardDuplicateTargetError
        card.duplicate_of_card_id = duplicate_of.id
    elif duplicate_of_card_id is not None:
        raise TestKnowledgeCardDuplicateTargetError
    else:
        card.duplicate_of_card_id = None

    reviewed_at = datetime.now(UTC)
    card.status = status
    card.reviewed_at = reviewed_at
    card.review_comment = review_comment
    if status == "approved":
        card.last_verified_at = reviewed_at
    elif status == "unsafe":
        card.allowed_for_prompt = False
        card.safe_to_show = False
        revoke_retrieval_artifact_access_for_card(session, card)
    sync_embedding_indexes_for_card_review(session, card)
    append_review_history(
        session,
        project_id=card.project_id,
        entity_type="TestKnowledgeCard",
        entity_id=card.id,
        action=status,
        related_entity_type="TestKnowledgeCard" if status == "duplicate" else None,
        related_entity_id=card.duplicate_of_card_id,
        from_status=from_status,
        to_status=card.status,
        comment=review_comment,
        metadata={
            "safe_to_show": card.safe_to_show,
            "allowed_for_prompt": card.allowed_for_prompt,
        },
    )
    complete_ingestion_run_after_review(session, card, reviewed_at)
    session.commit()
    session.refresh(card)
    return card


def complete_ingestion_run_after_review(
    session: Session,
    card: TestKnowledgeCard,
    reviewed_at: datetime,
) -> None:
    if card.ingestion_run_id is None:
        return
    run = session.get(KnowledgeIngestionRun, card.ingestion_run_id)
    if run is None or run.status != "waiting_review":
        return
    remaining_extracted = session.scalar(
        select(func.count(TestKnowledgeCard.id)).where(
            TestKnowledgeCard.ingestion_run_id == run.id,
            TestKnowledgeCard.status == "extracted",
        ),
    ) or 0
    if remaining_extracted == 0:
        run.status = "completed"
        run.completed_at = reviewed_at


def revoke_retrieval_artifact_access_for_card(
    session: Session,
    card: TestKnowledgeCard,
) -> None:
    canonical_artifact_ids = set(
        session.scalars(
            select(KnowledgeRetrievalRun.evidence_artifact_id)
            .join(KnowledgeEvidence, KnowledgeEvidence.retrieval_run_id == KnowledgeRetrievalRun.id)
            .where(
                KnowledgeEvidence.project_id == card.project_id,
                KnowledgeEvidence.knowledge_card_id == card.id,
                KnowledgeRetrievalRun.evidence_artifact_id.is_not(None),
            ),
        ),
    )
    artifacts = list(
        session.scalars(
            select(Artifact).where(
                Artifact.project_id == card.project_id,
                Artifact.artifact_type == "knowledge_retrieval",
            ),
        ),
    )
    for artifact in artifacts:
        legacy_match = any(
            isinstance(result, dict)
            and str(result.get("knowledge_card_id", "")) == str(card.id)
            for result in (artifact.metadata_json or {}).get("results", [])
        )
        if artifact.id not in canonical_artifact_ids and not legacy_match:
            continue
        metadata = dict(artifact.metadata_json or {})
        metadata["safe_to_show"] = False
        metadata["access_revoked_reason"] = "knowledge_card_marked_unsafe"
        artifact.metadata_json = metadata


def sync_embedding_indexes_for_card_review(session: Session, card: TestKnowledgeCard) -> None:
    indexes = list(
        session.scalars(
            select(TestKnowledgeEmbeddingIndex).where(
                TestKnowledgeEmbeddingIndex.project_id == card.project_id,
                TestKnowledgeEmbeddingIndex.knowledge_card_id == card.id,
            ),
        ),
    )
    prompt_eligible = card.status in PROMPT_ELIGIBLE_STATUSES and card.safe_to_show and card.allowed_for_prompt
    for index_row in indexes:
        metadata = dict(index_row.metadata_json or {})
        metadata["card_status"] = card.status
        metadata["safe_to_show"] = card.safe_to_show
        metadata["allowed_for_prompt"] = card.allowed_for_prompt
        if prompt_eligible:
            index_row.status = "indexed"
            metadata.pop("stale_reason", None)
        else:
            index_row.status = "stale"
            metadata["stale_reason"] = "knowledge_card_no_longer_prompt_eligible"
        index_row.metadata_json = metadata


def rebuild_test_knowledge_index(
    session: Session,
    *,
    project_id: uuid.UUID,
    knowledge_card_ids: list[uuid.UUID] | None = None,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
) -> KnowledgeIndexRebuildResult:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    card_query = select(TestKnowledgeCard).where(
        TestKnowledgeCard.project_id == project_id,
        TestKnowledgeCard.status.in_(PROMPT_ELIGIBLE_STATUSES),
        TestKnowledgeCard.safe_to_show.is_(True),
        TestKnowledgeCard.allowed_for_prompt.is_(True),
    )
    if knowledge_card_ids is not None:
        card_query = card_query.where(TestKnowledgeCard.id.in_(knowledge_card_ids))
    cards = list(session.scalars(card_query.order_by(TestKnowledgeCard.created_at.asc(), TestKnowledgeCard.id.asc())))
    existing_indexes = {
        item.knowledge_card_id: item
        for item in session.scalars(
            select(TestKnowledgeEmbeddingIndex).where(
                TestKnowledgeEmbeddingIndex.project_id == project_id,
                TestKnowledgeEmbeddingIndex.embedding_model == embedding_model,
            ),
        )
    }

    indexed_count = 0
    skipped_count = 0
    items: list[TestKnowledgeEmbeddingIndex] = []
    for card in cards:
        embedding_text = embedding_text_for_card(card)
        content_hash = hashlib.sha256(embedding_text.encode("utf-8")).hexdigest()
        embedding = deterministic_embedding(embedding_text, embedding_dim)
        index_row = existing_indexes.get(card.id)
        if (
            index_row is not None
            and index_row.content_hash == content_hash
            and index_row.embedding_dim == embedding_dim
            and index_row.status == "indexed"
        ):
            skipped_count += 1
            items.append(index_row)
            continue
        if index_row is None:
            index_row = TestKnowledgeEmbeddingIndex(
                project_id=project_id,
                knowledge_card_id=card.id,
                index_kind="test_knowledge_card",
                embedding_provider=DEFAULT_EMBEDDING_PROVIDER,
                embedding_model=embedding_model,
                embedding_dim=embedding_dim,
                content_hash=content_hash,
                embedding_json=embedding,
                status="indexed",
                metadata_json={
                    "source": "test_knowledge_card",
                    "knowledge_type": card.knowledge_type,
                    "card_status": card.status,
                },
            )
            session.add(index_row)
        else:
            index_row.embedding_provider = DEFAULT_EMBEDDING_PROVIDER
            index_row.embedding_dim = embedding_dim
            index_row.content_hash = content_hash
            index_row.embedding_json = embedding
            index_row.status = "indexed"
            index_row.metadata_json = {
                "source": "test_knowledge_card",
                "knowledge_type": card.knowledge_type,
                "card_status": card.status,
            }
        indexed_count += 1
        items.append(index_row)

    session.flush()
    postgres_adapter.sync_native_embeddings(
        session,
        [(item.id, list(item.embedding_json)) for item in items],
    )
    session.commit()
    for item in items:
        session.refresh(item)
    return KnowledgeIndexRebuildResult(
        project_id=project_id,
        indexed_count=indexed_count,
        skipped_count=skipped_count,
        embedding_model=embedding_model,
        embedding_dim=embedding_dim,
        items=items,
    )


def list_test_knowledge_index(session: Session, project_id: uuid.UUID) -> dict[str, Any]:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    items = list(
        session.scalars(
            select(TestKnowledgeEmbeddingIndex)
            .where(TestKnowledgeEmbeddingIndex.project_id == project_id)
            .order_by(
                TestKnowledgeEmbeddingIndex.embedding_model.asc(),
                TestKnowledgeEmbeddingIndex.created_at.asc(),
                TestKnowledgeEmbeddingIndex.id.asc(),
            ),
        ),
    )
    prompt_eligible_card_ids = set(
        session.scalars(
            select(TestKnowledgeCard.id).where(
                TestKnowledgeCard.project_id == project_id,
                TestKnowledgeCard.status.in_(PROMPT_ELIGIBLE_STATUSES),
                TestKnowledgeCard.safe_to_show.is_(True),
                TestKnowledgeCard.allowed_for_prompt.is_(True),
            ),
        ),
    )
    return {
        "items": [embedding_index_to_dict(item) for item in items],
        "total": len(items),
        "indexed_count": sum(
            1
            for item in items
            if item.status == "indexed" and item.knowledge_card_id in prompt_eligible_card_ids
        ),
        "embedding_models": sorted({item.embedding_model for item in items}),
    }


def active_knowledge_adapter_config(
    session: Session,
    project_id: uuid.UUID,
    adapter_name: str,
) -> KnowledgeAdapterConfig | None:
    return session.scalar(
        select(KnowledgeAdapterConfig).where(
            KnowledgeAdapterConfig.project_id == project_id,
            KnowledgeAdapterConfig.adapter_name == adapter_name,
        ),
    )


def match_configured_knowledge_cards(
    session: Session,
    *,
    project_id: uuid.UUID,
    adapter_name: str,
    query_text: str,
    limit: int,
    approved_only: bool,
    filters: dict[str, Any],
    retrieval_mode: str,
) -> KnowledgeMatchResult:
    config = active_knowledge_adapter_config(session, project_id, adapter_name)
    use_postgres = (
        config is not None
        and config.provider_type == "postgres_hybrid"
        and config.status in {"configured", "indexing", "ready", "degraded"}
    )
    use_optional_provider = (
        config is not None
        and config.provider_type in OPTIONAL_PROVIDER_TYPES
        and config.status in {"configured", "indexing", "ready", "degraded"}
    )
    if use_postgres and not normalize_terms(query_text):
        capabilities = postgres_adapter.detect_capabilities(session)
        return KnowledgeMatchResult(
            candidate_count=0,
            items=[],
            vector_available=False,
            actual_mode="keyword" if retrieval_mode in {"hybrid", "vector"} else retrieval_mode,
            degraded=retrieval_mode in {"hybrid", "vector"},
            fallback_reason=(
                "query_redacted_or_empty" if retrieval_mode in {"hybrid", "vector"} else None
            ),
            provider_type="postgres_hybrid",
            capability_snapshot={
                "provider_type": "postgres_hybrid",
                "config": dict(config.config_json),
                "capabilities": capabilities.snapshot(),
            },
        )
    if use_optional_provider and not normalize_terms(query_text):
        return KnowledgeMatchResult(
            candidate_count=0,
            items=[],
            vector_available=False,
            actual_mode="keyword" if retrieval_mode in {"hybrid", "vector"} else retrieval_mode,
            degraded=retrieval_mode in {"hybrid", "vector"},
            fallback_reason=(
                "query_redacted_or_empty" if retrieval_mode in {"hybrid", "vector"} else None
            ),
            provider_type=config.provider_type,
            capability_snapshot={
                "provider_type": config.provider_type,
                "config": dict(config.config_json),
                "available": False,
                "searchable": False,
                "reason": "query_redacted_or_empty",
            },
        )
    if use_optional_provider:
        provider_result = search_optional_provider(
            config.provider_type,
            None,
            query_text=query_text,
            limit=limit,
            filters=filters,
            retrieval_mode=retrieval_mode,
        )
        fallback = match_test_knowledge_cards(
            session,
            project_id=project_id,
            query_text=query_text,
            limit=limit,
            approved_only=approved_only,
            filters=filters,
            retrieval_mode="keyword" if retrieval_mode in {"hybrid", "vector"} else retrieval_mode,
        )
        return KnowledgeMatchResult(
            candidate_count=fallback.candidate_count,
            items=fallback.items,
            vector_available=False,
            actual_mode=fallback.actual_mode,
            degraded=True,
            fallback_reason=provider_result.fallback_reason,
            provider_type=config.provider_type,
            capability_snapshot={
                "provider_type": config.provider_type,
                "config": dict(config.config_json),
                **provider_result.capability_snapshot,
            },
        )
    if not use_postgres:
        result = match_test_knowledge_cards(
            session,
            project_id=project_id,
            query_text=query_text,
            limit=limit,
            approved_only=approved_only,
            filters=filters,
            retrieval_mode=retrieval_mode,
        )
        return result

    capabilities = postgres_adapter.detect_capabilities(session)
    adapter_snapshot = {
        "provider_type": "postgres_hybrid",
        "config": dict(config.config_json),
        "capabilities": capabilities.snapshot(),
    }
    if retrieval_mode == "metadata":
        fallback = match_test_knowledge_cards(
            session,
            project_id=project_id,
            query_text=query_text,
            limit=limit,
            approved_only=approved_only,
            filters=filters,
            retrieval_mode="metadata",
        )
        return KnowledgeMatchResult(
            candidate_count=fallback.candidate_count,
            items=fallback.items,
            vector_available=False,
            actual_mode="metadata",
            degraded=False,
            fallback_reason=None,
            provider_type="postgres_hybrid",
            capability_snapshot=adapter_snapshot,
        )
    if not capabilities.postgresql or not capabilities.full_text:
        fallback = match_test_knowledge_cards(
            session,
            project_id=project_id,
            query_text=query_text,
            limit=limit,
            approved_only=approved_only,
            filters=filters,
            retrieval_mode="keyword" if retrieval_mode in {"hybrid", "vector"} else retrieval_mode,
        )
        return KnowledgeMatchResult(
            candidate_count=fallback.candidate_count,
            items=fallback.items,
            vector_available=False,
            actual_mode=fallback.actual_mode,
            degraded=retrieval_mode in {"hybrid", "vector"},
            fallback_reason="postgresql_unavailable",
            provider_type="postgres_hybrid",
            capability_snapshot=adapter_snapshot,
        )

    embedding_dim = int(config.config_json.get("embedding_dim", DEFAULT_EMBEDDING_DIM))
    embedding_model = str(config.config_json.get("embedding_model", DEFAULT_EMBEDDING_MODEL))
    query_vector = (
        deterministic_embedding(query_text, embedding_dim)
        if retrieval_mode in {"hybrid", "vector"} and capabilities.vector_search
        else None
    )
    try:
        with session.begin_nested():
            native_matches = postgres_adapter.search_postgres_knowledge(
                session,
                project_id=project_id,
                query_text=query_text,
                query_vector=query_vector,
                embedding_model=embedding_model,
                hnsw_ef_search=max(1, min(1000, int(config.config_json.get("hnsw_ef_search", 40)))),
                include_keyword=retrieval_mode != "vector",
                statuses={"approved"} if approved_only else PROMPT_ELIGIBLE_STATUSES,
                filters=filters,
                limit=limit,
                min_vector_similarity=float(config.config_json.get("min_vector_similarity", MIN_VECTOR_SIMILARITY)),
            )
    except Exception as exc:
        fallback = match_test_knowledge_cards(
            session,
            project_id=project_id,
            query_text=query_text,
            limit=limit,
            approved_only=approved_only,
            filters=filters,
            retrieval_mode="keyword" if retrieval_mode in {"hybrid", "vector"} else retrieval_mode,
        )
        return KnowledgeMatchResult(
            candidate_count=fallback.candidate_count,
            items=fallback.items,
            vector_available=False,
            actual_mode=fallback.actual_mode,
            degraded=True,
            fallback_reason="postgresql_search_failed",
            provider_type="postgres_hybrid",
            capability_snapshot={**adapter_snapshot, "search_error": type(exc).__name__},
        )

    cards = {
        card.id: card
        for card in session.scalars(
            select(TestKnowledgeCard).where(
                TestKnowledgeCard.project_id == project_id,
                TestKnowledgeCard.id.in_([item.knowledge_card_id for item in native_matches]),
            ),
        )
    }
    evidence: list[dict[str, Any]] = []
    vector_match_count = 0
    for native in native_matches:
        card = cards.get(native.knowledge_card_id)
        if card is None:
            continue
        if native.content_hash and native.embedding_dim is not None:
            current_hash = hashlib.sha256(embedding_text_for_card(card).encode("utf-8")).hexdigest()
            if current_hash != native.content_hash or native.embedding_dim != embedding_dim:
                continue
        matched_terms = [
            term for term in normalize_terms(query_text)
            if term in set(normalize_terms(search_text_for_card(card)))
        ]
        item = evidence_for_card(
            card,
            matched_terms=matched_terms,
            query_term_count=len(normalize_terms(query_text)),
            metadata_score=(
                1.0
                if any(
                    filters.get(key)
                    for key in {"module_keys", "knowledge_types", "risk_types", "api_endpoints"}
                )
                else 0.0
            ),
            retrieval_reason=(
                "postgres_vector_similarity"
                if retrieval_mode == "vector" and native.vector_score is not None
                else "postgres_hybrid_keyword_vector"
                if native.vector_score is not None
                else "postgres_full_text"
            ),
            semantic_score=native.vector_score,
            embedding_model=native.embedding_model or embedding_model,
        )
        item["keyword_score"] = round(max(0.0, min(native.keyword_score, 1.0)), 6)
        if native.vector_score is not None:
            vector_match_count += 1
        finalize_match_scores(item)
        evidence.append(item)
    evidence.sort(
        key=lambda item: (
            STATUS_PRIORITY.get(str(item.get("status")), 99),
            -float(item["final_score"]),
            str(item["title"]).lower(),
            str(item["knowledge_card_id"]),
        ),
    )
    vector_used = query_vector is not None and vector_match_count > 0
    return KnowledgeMatchResult(
        candidate_count=len(evidence),
        items=evidence[:limit],
        vector_available=vector_used,
        actual_mode=retrieval_mode if vector_used else "keyword",
        degraded=retrieval_mode in {"hybrid", "vector"} and not vector_used,
        fallback_reason=(
            (
                "vector_candidate_unavailable"
                if capabilities.vector_search
                else "pgvector_unavailable"
            )
            if retrieval_mode in {"hybrid", "vector"} and not vector_used
            else None
        ),
        provider_type="postgres_hybrid",
        capability_snapshot=adapter_snapshot,
    )


def create_knowledge_retrieval_run(
    session: Session,
    store: LocalArtifactStore,
    data: KnowledgeRetrievalRunCreateRequest,
    *,
    ai_task_id: uuid.UUID | None = None,
) -> KnowledgeRetrievalRun:
    if session.get(Project, data.project_id) is None:
        raise ProjectNotFoundError
    if ai_task_id is not None:
        ai_task = session.get(AITask, ai_task_id)
        if ai_task is None or ai_task.project_id != data.project_id:
            raise KnowledgeRetrievalConsumerNotAllowedError
    validate_retrieval_consumer(
        session,
        project_id=data.project_id,
        consumer_entity_type=data.consumer_entity_type,
        consumer_entity_id=data.consumer_entity_id,
    )
    filters = data.filters.model_dump(mode="json")
    validate_retrieval_input(data.query_text, filters)
    adapter_config = active_knowledge_adapter_config(session, data.project_id, data.adapter_name)
    configured_provider = (
        adapter_config.provider_type
        if adapter_config is not None
        and adapter_config.provider_type in {"postgres_hybrid", *OPTIONAL_PROVIDER_TYPES}
        and adapter_config.status in {"configured", "indexing", "ready", "degraded"}
        else "deterministic_local"
    )
    started_at = datetime.now(UTC)
    query_text_redacted = redact_retrieval_query(data.query_text)
    run = KnowledgeRetrievalRun(
        project_id=data.project_id,
        ai_task_id=ai_task_id,
        consumer_entity_type=data.consumer_entity_type,
        consumer_entity_id=data.consumer_entity_id,
        adapter_name=data.adapter_name,
        provider_type=configured_provider,
        requested_retrieval_mode=data.retrieval_mode,
        retrieval_mode=data.retrieval_mode,
        adapter_config_snapshot_json={
            "approved_only": data.approved_only,
            "limit": data.limit,
            "scoring_version": "provider-neutral-normalized-v1",
            "provider_config": dict(adapter_config.config_json) if adapter_config is not None else {},
        },
        query_text_hash="sha256:" + hashlib.sha256(data.query_text.encode("utf-8")).hexdigest(),
        query_text_redacted=query_text_redacted,
        filters_json=filters,
        status="retrieving",
        started_at=started_at,
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    started_clock = time.perf_counter()
    try:
        matches = match_configured_knowledge_cards(
            session,
            project_id=data.project_id,
            adapter_name=data.adapter_name,
            query_text=(data.query_text if query_text_redacted != "[redacted]" else ""),
            limit=data.limit,
            approved_only=data.approved_only,
            filters=filters,
            retrieval_mode=data.retrieval_mode,
        )
        run.status = "normalizing"
        run.provider_type = matches.provider_type
        run.retrieval_mode = matches.actual_mode
        run.candidate_count = matches.candidate_count
        run.degraded = matches.degraded
        run.fallback_reason = matches.fallback_reason
        run.adapter_config_snapshot_json = {
            **run.adapter_config_snapshot_json,
            "vector_available": matches.vector_available,
            "requested_retrieval_mode": data.retrieval_mode,
            "actual_retrieval_mode": matches.actual_mode,
            **matches.capability_snapshot,
        }
        session.commit()
        session.refresh(run)

        evidence_rows = persist_knowledge_evidence_rows(session, run, matches.items)
        evidence_payload = [knowledge_evidence_to_payload(session, row) for row in evidence_rows]
        artifact = write_retrieval_artifact(
            session,
            store,
            run,
            results=evidence_payload,
        )
        run.evidence_count = len(evidence_rows)
        run.evidence_artifact_id = artifact.id
        run.latency_ms = max(0, round((time.perf_counter() - started_clock) * 1000))
        run.status = "completed"
        run.completed_at = datetime.now(UTC)
        session.commit()
        session.refresh(run)
        return run
    except Exception:
        session.rollback()
        mark_retrieval_run_failed(session, run.id)
        raise


def retrieve_and_persist_test_knowledge_evidence(
    session: Session,
    store: LocalArtifactStore,
    *,
    project_id: uuid.UUID,
    query_text: str,
    limit: int = 5,
    approved_only: bool = True,
    consumer_entity_type: str | None = None,
    consumer_entity_id: uuid.UUID | None = None,
    ai_task_id: uuid.UUID | None = None,
) -> tuple[KnowledgeRetrievalRun, list[dict[str, Any]]]:
    run = create_knowledge_retrieval_run(
        session,
        store,
        KnowledgeRetrievalRunCreateRequest(
            project_id=project_id,
            query_text=query_text,
            consumer_entity_type=consumer_entity_type,
            consumer_entity_id=consumer_entity_id,
            retrieval_mode="hybrid",
            approved_only=approved_only,
            limit=limit,
        ),
        ai_task_id=ai_task_id,
    )
    run_read = knowledge_retrieval_run_to_read(session, run)
    return run, [knowledge_evidence_to_legacy(item) for item in run_read.items]


def link_retrieval_run_to_ai_task(
    session: Session,
    *,
    project_id: uuid.UUID,
    retrieval_payload: dict[str, Any] | None,
    ai_task_id: uuid.UUID,
) -> None:
    if not retrieval_payload:
        return
    raw_run_id = retrieval_payload.get("created_knowledge_retrieval_run_id") or retrieval_payload.get(
        "knowledge_retrieval_run_id",
    )
    if not raw_run_id:
        return
    try:
        run_id = uuid.UUID(str(raw_run_id))
    except ValueError:
        return
    run = session.get(KnowledgeRetrievalRun, run_id)
    if run is not None and run.project_id == project_id:
        run.ai_task_id = ai_task_id


def validate_retrieval_consumer(
    session: Session,
    *,
    project_id: uuid.UUID,
    consumer_entity_type: str | None,
    consumer_entity_id: uuid.UUID | None,
) -> None:
    if consumer_entity_type is None and consumer_entity_id is None:
        return
    if consumer_entity_type is None or consumer_entity_id is None:
        raise KnowledgeRetrievalConsumerNotAllowedError
    if consumer_entity_type == "Requirement":
        from backend.app.modules.requirements.models import Requirement

        entity = session.get(Requirement, consumer_entity_id)
    elif consumer_entity_type == "CaseGenerationTask":
        entity = session.get(CaseGenerationTask, consumer_entity_id)
    elif consumer_entity_type == "TestCase":
        entity = session.get(TestCase, consumer_entity_id)
    elif consumer_entity_type == "AutomationPlan":
        from backend.app.modules.automation.models import AutomationPlan

        entity = session.get(AutomationPlan, consumer_entity_id)
    elif consumer_entity_type == "AITask":
        entity = session.get(AITask, consumer_entity_id)
    else:
        raise KnowledgeRetrievalConsumerNotAllowedError
    if entity is None or entity.project_id != project_id:
        raise KnowledgeRetrievalConsumerNotAllowedError


def validate_retrieval_input(query_text: str, filters: dict[str, Any]) -> None:
    serialized_filters = json.dumps(filters, ensure_ascii=False, sort_keys=True)
    if (
        config_snapshot_contains_secret(filters)
        or ai_runtime_service.has_high_risk_secret(serialized_filters)
        or "://" in serialized_filters
        or re.search(r"(?i)\b[A-Z]:[\\/]", serialized_filters)
    ):
        raise KnowledgeRetrievalInputNotAllowedError
    if len(query_text.encode("utf-8")) > 8_000:
        raise KnowledgeRetrievalInputNotAllowedError


def redact_retrieval_query(query_text: str) -> str:
    if RETRIEVAL_QUERY_SECRET_PATTERN.search(query_text) or ai_runtime_service.has_high_risk_secret(query_text):
        return "[redacted]"
    return query_text[:500]


def persist_knowledge_evidence_rows(
    session: Session,
    run: KnowledgeRetrievalRun,
    matches: list[dict[str, Any]],
) -> list[KnowledgeEvidence]:
    rows: list[KnowledgeEvidence] = []
    for match in matches:
        card = session.get(TestKnowledgeCard, uuid.UUID(str(match["knowledge_card_id"])))
        if (
            card is None
            or card.project_id != run.project_id
            or str(card.source_artifact_id) != str(match["source_artifact_id"])
        ):
            raise KnowledgeRetrievalInputNotAllowedError
        source_artifact = session.get(Artifact, card.source_artifact_id)
        if source_artifact is None or source_artifact.project_id != run.project_id:
            raise KnowledgeRetrievalInputNotAllowedError
        row = KnowledgeEvidence(
            project_id=run.project_id,
            retrieval_run_id=run.id,
            knowledge_card_id=card.id,
            source_artifact_id=card.source_artifact_id,
            snippet=card.content[:320],
            source_locator_json=dict(card.source_locator_json or {}),
            metadata_score=float(match["metadata_score"]),
            keyword_score=float(match["keyword_score"]),
            vector_score=(
                float(match["vector_score"])
                if match.get("vector_score") is not None
                else None
            ),
            rerank_score=None,
            final_score=float(match["final_score"]),
            matched_terms_json=list(match.get("matched_terms", []))[:50],
            retrieval_reason=str(match["retrieval_reason"])[:500],
            card_status_snapshot=card.status,
            safe_to_show=card.safe_to_show,
            allowed_for_prompt=card.allowed_for_prompt,
        )
        session.add(row)
        rows.append(row)
    session.flush()
    return rows


def write_retrieval_artifact(
    session: Session,
    store: LocalArtifactStore,
    run: KnowledgeRetrievalRun,
    *,
    results: list[dict[str, Any]],
) -> Artifact:
    payload = {
        "knowledge_retrieval_run_id": str(run.id),
        "project_id": str(run.project_id),
        "adapter_name": run.adapter_name,
        "provider_type": run.provider_type,
        "requested_retrieval_mode": run.requested_retrieval_mode,
        "retrieval_mode": run.retrieval_mode,
        "adapter_config_snapshot": run.adapter_config_snapshot_json,
        "query_text_hash": run.query_text_hash,
        "query_text_redacted": run.query_text_redacted,
        "filters": run.filters_json,
        "candidate_count": run.candidate_count,
        "evidence_count": len(results),
        "degraded": run.degraded,
        "fallback_reason": run.fallback_reason,
        "results": results,
    }
    content = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")
    file_path = f"projects/{run.project_id}/knowledge-retrieval-runs/{run.id}/retrieval.json"
    write_result = store.write_bytes(file_path, content)
    artifact = Artifact(
        project_id=run.project_id,
        owner_entity_type="KnowledgeRetrievalRun",
        owner_entity_id=run.id,
        artifact_type="knowledge_retrieval",
        file_path=write_result.file_path,
        mime_type="application/json",
        size_bytes=write_result.size_bytes,
        sha256=write_result.sha256,
        metadata_json={
            "created_by_component": "KnowledgeRetrievalService",
            "source_entity_type": "KnowledgeRetrievalRun",
            "source_entity_id": str(run.id),
            "query_text_hash": run.query_text_hash,
            "provider_type": run.provider_type,
            "retrieval_mode": run.retrieval_mode,
            "candidate_count": run.candidate_count,
            "evidence_count": len(results),
            "degraded": run.degraded,
            "safe_to_show": True,
            "redaction_applied": run.query_text_redacted == "[redacted]",
            "description": "Normalized knowledge retrieval evidence",
        },
    )
    session.add(artifact)
    session.flush()
    return artifact


def mark_retrieval_run_failed(session: Session, run_id: uuid.UUID) -> None:
    run = session.get(KnowledgeRetrievalRun, run_id)
    if run is None:
        return
    run.status = "failed"
    run.error_code = "KNOWLEDGE_RETRIEVAL_FAILED"
    run.error_message = "Knowledge retrieval failed before normalized evidence was completed."
    run.completed_at = datetime.now(UTC)
    session.commit()


def get_knowledge_retrieval_run(session: Session, run_id: uuid.UUID) -> KnowledgeRetrievalRun:
    run = session.get(KnowledgeRetrievalRun, run_id)
    if run is None:
        raise KnowledgeRetrievalRunNotFoundError
    return run


def list_knowledge_retrieval_runs(
    session: Session,
    project_id: uuid.UUID,
    *,
    status: str | None = None,
    provider_type: str | None = None,
    consumer_entity_type: str | None = None,
    consumer_entity_id: uuid.UUID | None = None,
    limit: int = 50,
    cursor: uuid.UUID | None = None,
) -> KnowledgeRetrievalRunPage:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    filters = [KnowledgeRetrievalRun.project_id == project_id]
    if status:
        filters.append(KnowledgeRetrievalRun.status == status)
    if provider_type:
        filters.append(KnowledgeRetrievalRun.provider_type == provider_type)
    if consumer_entity_type:
        filters.append(KnowledgeRetrievalRun.consumer_entity_type == consumer_entity_type)
    if consumer_entity_id:
        filters.append(KnowledgeRetrievalRun.consumer_entity_id == consumer_entity_id)
    total = session.scalar(select(func.count(KnowledgeRetrievalRun.id)).where(*filters)) or 0
    page_filters = list(filters)
    if cursor is not None:
        cursor_run = session.get(KnowledgeRetrievalRun, cursor)
        if (
            cursor_run is None
            or cursor_run.project_id != project_id
            or (status is not None and cursor_run.status != status)
            or (provider_type is not None and cursor_run.provider_type != provider_type)
            or (
                consumer_entity_type is not None
                and cursor_run.consumer_entity_type != consumer_entity_type
            )
            or (
                consumer_entity_id is not None
                and cursor_run.consumer_entity_id != consumer_entity_id
            )
        ):
            raise KnowledgeRetrievalRunNotFoundError
        cursor_created_at = (
            select(KnowledgeRetrievalRun.created_at)
            .where(KnowledgeRetrievalRun.id == cursor)
            .scalar_subquery()
        )
        page_filters.append(
            or_(
                KnowledgeRetrievalRun.created_at < cursor_created_at,
                and_(
                    KnowledgeRetrievalRun.created_at == cursor_created_at,
                    KnowledgeRetrievalRun.id < cursor_run.id,
                ),
            ),
        )
    rows = list(
        session.scalars(
            select(KnowledgeRetrievalRun).where(*page_filters).order_by(
                KnowledgeRetrievalRun.created_at.desc(),
                KnowledgeRetrievalRun.id.desc(),
            ).limit(limit + 1),
        ),
    )
    has_more = len(rows) > limit
    items = rows[:limit]
    return KnowledgeRetrievalRunPage(
        items=items,
        total=total,
        next_cursor=str(items[-1].id) if has_more and items else None,
    )


def knowledge_retrieval_run_to_read(
    session: Session,
    run: KnowledgeRetrievalRun,
) -> KnowledgeRetrievalRunRead:
    return knowledge_retrieval_runs_to_read(session, [run])[0]


def knowledge_retrieval_runs_to_read(
    session: Session,
    runs: list[KnowledgeRetrievalRun],
) -> list[KnowledgeRetrievalRunRead]:
    if not runs:
        return []
    run_ids = [run.id for run in runs]
    evidence_by_run: dict[uuid.UUID, list[KnowledgeEvidence]] = {run_id: [] for run_id in run_ids}
    evidence_rows = list(
        session.scalars(
            select(KnowledgeEvidence)
            .where(KnowledgeEvidence.retrieval_run_id.in_(run_ids))
            .order_by(
                KnowledgeEvidence.retrieval_run_id.asc(),
                KnowledgeEvidence.final_score.desc(),
                KnowledgeEvidence.knowledge_card_id.asc(),
            ),
        ),
    )
    for row in evidence_rows:
        evidence_by_run[row.retrieval_run_id].append(row)
    card_ids = {row.knowledge_card_id for row in evidence_rows}
    cards_by_id = {
        card.id: card
        for card in session.scalars(select(TestKnowledgeCard).where(TestKnowledgeCard.id.in_(card_ids)))
    } if card_ids else {}
    evidence_artifact_ids = {
        run.evidence_artifact_id
        for run in runs
        if run.evidence_artifact_id is not None
    }
    artifacts_by_owner_and_id = {
        (artifact.owner_entity_id, artifact.id): artifact
        for artifact in session.scalars(
            select(Artifact).where(
                Artifact.id.in_(evidence_artifact_ids),
                Artifact.owner_entity_type == "KnowledgeRetrievalRun",
                Artifact.owner_entity_id.in_(run_ids),
                Artifact.project_id.in_({run.project_id for run in runs}),
            ),
        )
    } if evidence_artifact_ids else {}
    return [
        _knowledge_retrieval_run_read(
            run,
            evidence_rows=evidence_by_run[run.id],
            cards_by_id=cards_by_id,
            artifacts_by_owner_and_id=artifacts_by_owner_and_id,
        )
        for run in runs
    ]


def _trace_artifact_refs(session: Session, project_id: uuid.UUID, artifact_ids: list[Any]) -> list[EvidenceTraceArtifactRefRead]:
    ids = []
    for value in artifact_ids:
        try:
            ids.append(uuid.UUID(str(value)))
        except (TypeError, ValueError):
            continue
    if not ids:
        return []
    artifacts = session.scalars(
        select(Artifact).where(Artifact.project_id == project_id, Artifact.id.in_(ids)),
    )
    refs = []
    for artifact in artifacts:
        if artifact.metadata_json.get("safe_to_show") is not True:
            continue
        refs.append(
            EvidenceTraceArtifactRefRead(
                id=artifact.id,
                artifact_type=artifact.artifact_type,
                mime_type=artifact.mime_type,
                safe_to_show=True,
                download_url=f"/api/artifacts/{artifact.id}/download",
            ),
        )
    return refs


def _trace_uuid_values(values: list[Any]) -> list[uuid.UUID]:
    result: list[uuid.UUID] = []
    for value in values:
        try:
            result.append(uuid.UUID(str(value)))
        except (TypeError, ValueError):
            continue
    return result


def _trace_node(
    *,
    stage: str,
    entity_type: str,
    entity_id: uuid.UUID,
    status: str,
    timestamp: datetime,
    summary: str,
    artifact_refs: list[EvidenceTraceArtifactRefRead] | None = None,
    evidence_ids: list[uuid.UUID] | None = None,
    source_locator: dict[str, Any] | None = None,
    provider_type: str | None = None,
    requested_retrieval_mode: str | None = None,
    retrieval_mode: str | None = None,
    degraded: bool | None = None,
    fallback_reason: str | None = None,
    latency_ms: int | None = None,
) -> EvidenceTraceNodeRead:
    return EvidenceTraceNodeRead(
        stage=stage,
        entity_type=entity_type,
        entity_id=entity_id,
        status=status,
        timestamp=timestamp,
        summary=summary[:500],
        artifact_refs=artifact_refs or [],
        evidence_ids=evidence_ids or [],
        source_locator=source_locator or {},
        provider_type=provider_type,
        requested_retrieval_mode=requested_retrieval_mode,
        retrieval_mode=retrieval_mode,
        degraded=degraded,
        fallback_reason=fallback_reason,
        latency_ms=latency_ms,
    )


def _trace_retrieval_nodes(session: Session, project_id: uuid.UUID, run: KnowledgeRetrievalRun) -> list[EvidenceTraceNodeRead]:
    rows = list(session.scalars(select(KnowledgeEvidence).where(KnowledgeEvidence.retrieval_run_id == run.id)))
    artifact_ids = [run.evidence_artifact_id] if run.evidence_artifact_id else []
    return [
        _trace_node(
            stage="ai_retrieval",
            entity_type="KnowledgeRetrievalRun",
            entity_id=run.id,
            status=run.status,
            timestamp=run.created_at,
            summary=f"{run.provider_type} {run.retrieval_mode} retrieval with {run.evidence_count} evidence item(s)",
            artifact_refs=_trace_artifact_refs(session, project_id, artifact_ids),
            evidence_ids=[row.id for row in rows],
            provider_type=run.provider_type,
            requested_retrieval_mode=run.requested_retrieval_mode,
            retrieval_mode=run.retrieval_mode,
            degraded=run.degraded,
            fallback_reason=run.fallback_reason,
            latency_ms=run.latency_ms,
        ),
        *[
            _trace_node(
                stage="evidence",
                entity_type="KnowledgeEvidence",
                entity_id=row.id,
                status="eligible" if row.allowed_for_prompt else "restricted",
                timestamp=row.created_at,
                summary=row.retrieval_reason,
                artifact_refs=_trace_artifact_refs(session, project_id, [row.source_artifact_id]),
                evidence_ids=[row.id],
                source_locator=row.source_locator_json,
            )
            for row in rows
        ],
    ]


def _trace_entity_nodes(session: Session, project_id: uuid.UUID, entity_type: str, entity_id: uuid.UUID) -> list[EvidenceTraceNodeRead]:
    if entity_type not in TRACE_ENTITY_TYPES:
        raise EvidenceTraceEntityTypeNotAllowedError
    if entity_type == "KnowledgeIngestionRun":
        entity = session.get(KnowledgeIngestionRun, entity_id)
        if entity is None or entity.project_id != project_id:
            raise EvidenceTraceEntityNotFoundError
        return [_trace_node(stage="source", entity_type=entity_type, entity_id=entity.id, status=entity.status, timestamp=entity.created_at, summary=f"{entity.source_type} ingestion: {entity.extracted_card_count} card(s)", artifact_refs=_trace_artifact_refs(session, project_id, [*entity.input_artifact_ids_json, *entity.evidence_artifact_ids_json]))]
    if entity_type == "KnowledgeRetrievalRun":
        entity = session.get(KnowledgeRetrievalRun, entity_id)
        if entity is None or entity.project_id != project_id:
            raise EvidenceTraceEntityNotFoundError
        return _trace_retrieval_nodes(session, project_id, entity)
    if entity_type == "KnowledgeEvidence":
        entity = session.get(KnowledgeEvidence, entity_id)
        if entity is None or entity.project_id != project_id:
            raise EvidenceTraceEntityNotFoundError
        run = session.get(KnowledgeRetrievalRun, entity.retrieval_run_id)
        if run is None:
            raise EvidenceTraceEntityNotFoundError
        return _trace_retrieval_nodes(session, project_id, run)
    if entity_type == "TestKnowledgeCard":
        entity = session.get(TestKnowledgeCard, entity_id)
        if entity is None or entity.project_id != project_id:
            raise EvidenceTraceEntityNotFoundError
        rows = list(session.scalars(select(KnowledgeEvidence).where(KnowledgeEvidence.knowledge_card_id == entity.id)))
        nodes = [_trace_node(stage="source", entity_type=entity_type, entity_id=entity.id, status=entity.status, timestamp=entity.created_at, summary=entity.title, artifact_refs=_trace_artifact_refs(session, project_id, [entity.source_artifact_id]), source_locator=entity.source_locator_json)]
        for run_id in dict.fromkeys(row.retrieval_run_id for row in rows):
            run = session.get(KnowledgeRetrievalRun, run_id)
            if run is not None and run.project_id == project_id:
                nodes.extend(_trace_retrieval_nodes(session, project_id, run))
        return nodes
    if entity_type == "KnowledgeFeedbackEvent":
        entity = session.get(KnowledgeFeedbackEvent, entity_id)
        if entity is None or entity.project_id != project_id:
            raise EvidenceTraceEntityNotFoundError
        content = entity.proposed_content_json or {}
        return [_trace_node(stage="feedback", entity_type=entity_type, entity_id=entity.id, status=entity.status, timestamp=entity.created_at, summary=f"{entity.proposed_knowledge_type} feedback from {entity.source_entity_type}", artifact_refs=_trace_artifact_refs(session, project_id, entity.evidence_artifact_ids_json), source_locator=content.get("source_locator") if isinstance(content.get("source_locator"), dict) else {})]
    entity = session.get(GeneratedCaseCandidate, entity_id)
    if entity is None or entity.project_id != project_id:
        raise EvidenceTraceEntityNotFoundError
    refs = entity.source_knowledge_evidence_json or []
    return [_trace_node(stage="case_generation", entity_type=entity_type, entity_id=entity.id, status=entity.status, timestamp=entity.created_at, summary=entity.title, artifact_refs=_trace_artifact_refs(session, project_id, [item.get("source_artifact_id") for item in refs if isinstance(item, dict)]), evidence_ids=_trace_uuid_values([item.get("knowledge_evidence_id") for item in refs if isinstance(item, dict)]), source_locator={"generation_task_id": str(entity.generation_task_id)})]


def search_evidence_trace(session: Session, project_id: uuid.UUID, *, query: str | None, entity_type: str | None, entity_id: uuid.UUID | None, limit: int = 50) -> EvidenceTraceRead:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    if entity_type is not None and entity_type not in TRACE_ENTITY_TYPES:
        raise EvidenceTraceEntityTypeNotAllowedError
    if (entity_type is not None) != (entity_id is not None):
        raise EvidenceTraceQueryInvalidError
    if entity_id is not None and entity_type is not None:
        nodes = _trace_entity_nodes(session, project_id, entity_type, entity_id)
    else:
        text = (query or "").strip()
        if not text:
            return EvidenceTraceRead(project_id=project_id, query=query, stages=[], total=0)
        pattern = f"%{text[:120]}%"
        nodes = []
        for card in session.scalars(select(TestKnowledgeCard).where(TestKnowledgeCard.project_id == project_id, or_(TestKnowledgeCard.title.ilike(pattern), TestKnowledgeCard.content.ilike(pattern))).limit(limit)):
            nodes.extend(_trace_entity_nodes(session, project_id, "TestKnowledgeCard", card.id))
        for run in session.scalars(select(KnowledgeRetrievalRun).where(KnowledgeRetrievalRun.project_id == project_id, or_(KnowledgeRetrievalRun.query_text_redacted.ilike(pattern), KnowledgeRetrievalRun.provider_type.ilike(pattern), KnowledgeRetrievalRun.fallback_reason.ilike(pattern))).limit(limit)):
            nodes.extend(_trace_entity_nodes(session, project_id, "KnowledgeRetrievalRun", run.id))
        for feedback in session.scalars(select(KnowledgeFeedbackEvent).where(KnowledgeFeedbackEvent.project_id == project_id, KnowledgeFeedbackEvent.proposed_knowledge_type.ilike(pattern)).limit(limit)):
            nodes.extend(_trace_entity_nodes(session, project_id, "KnowledgeFeedbackEvent", feedback.id))
        nodes = nodes[:limit]
    grouped: dict[str, list[EvidenceTraceNodeRead]] = {}
    for node in nodes:
        grouped.setdefault(node.stage, []).append(node)
    stages = [EvidenceTraceStageRead(name=name, items=items) for name, items in grouped.items()]
    return EvidenceTraceRead(project_id=project_id, entity_type=entity_type, entity_id=entity_id, query=query, stages=stages, total=len(nodes))


def _knowledge_retrieval_run_read(
    run: KnowledgeRetrievalRun,
    *,
    evidence_rows: list[KnowledgeEvidence],
    cards_by_id: dict[uuid.UUID, TestKnowledgeCard],
    artifacts_by_owner_and_id: dict[tuple[uuid.UUID, uuid.UUID], Artifact],
) -> KnowledgeRetrievalRunRead:
    artifact = (
        artifacts_by_owner_and_id.get((run.id, run.evidence_artifact_id))
        if run.evidence_artifact_id is not None
        else None
    )
    evidence_artifact_read = None
    artifact_currently_safe = all(
        row.safe_to_show
        and (card := cards_by_id.get(row.knowledge_card_id)) is not None
        and card.safe_to_show
        for row in evidence_rows
    )
    if (
        artifact is not None
        and artifact.metadata_json.get("safe_to_show") is True
        and artifact_currently_safe
    ):
        evidence_artifact_read = KnowledgeRetrievalArtifactRead(
            id=artifact.id,
            artifact_type=artifact.artifact_type,
            mime_type=artifact.mime_type,
            size_bytes=artifact.size_bytes,
            sha256=artifact.sha256,
            safe_to_show=True,
            download_url=f"/api/artifacts/{artifact.id}/download",
        )
    return KnowledgeRetrievalRunRead(
        id=run.id,
        project_id=run.project_id,
        ai_task_id=run.ai_task_id,
        consumer_entity_type=run.consumer_entity_type,
        consumer_entity_id=run.consumer_entity_id,
        adapter_name=run.adapter_name,
        provider_type=run.provider_type,
        requested_retrieval_mode=run.requested_retrieval_mode,
        retrieval_mode=run.retrieval_mode,
        adapter_config_snapshot=run.adapter_config_snapshot_json,
        query_text_hash=run.query_text_hash,
        query_text_redacted=run.query_text_redacted,
        filters=run.filters_json,
        status=run.status,
        candidate_count=run.candidate_count,
        evidence_count=run.evidence_count,
        latency_ms=run.latency_ms,
        degraded=run.degraded,
        fallback_reason=run.fallback_reason,
        error_code=run.error_code,
        error_message=run.error_message,
        evidence_artifact_id=run.evidence_artifact_id,
        evidence_artifact=evidence_artifact_read,
        items=[_knowledge_evidence_read(row, cards_by_id.get(row.knowledge_card_id)) for row in evidence_rows],
        started_at=run.started_at,
        completed_at=run.completed_at,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


def knowledge_evidence_to_read(session: Session, row: KnowledgeEvidence) -> KnowledgeEvidenceRead:
    return _knowledge_evidence_read(row, session.get(TestKnowledgeCard, row.knowledge_card_id))


def _knowledge_evidence_read(
    row: KnowledgeEvidence,
    card: TestKnowledgeCard | None,
) -> KnowledgeEvidenceRead:
    currently_safe = row.safe_to_show and card is not None and card.safe_to_show
    currently_prompt_eligible = (
        row.card_status_snapshot == "approved"
        and row.safe_to_show
        and row.allowed_for_prompt
        and card is not None
        and card.status == "approved"
        and card.safe_to_show
        and card.allowed_for_prompt
    )
    return KnowledgeEvidenceRead(
        id=row.id,
        project_id=row.project_id,
        retrieval_run_id=row.retrieval_run_id,
        knowledge_card_id=row.knowledge_card_id,
        source_artifact_id=row.source_artifact_id,
        knowledge_type=card.knowledge_type if currently_safe and card is not None else "restricted",
        title=card.title if currently_safe and card is not None else "Restricted knowledge evidence",
        snippet=row.snippet if currently_safe else "[redacted]",
        source_locator=row.source_locator_json,
        metadata_score=row.metadata_score,
        keyword_score=row.keyword_score,
        vector_score=row.vector_score,
        rerank_score=row.rerank_score,
        final_score=row.final_score,
        matched_terms=[str(item) for item in row.matched_terms_json],
        retrieval_reason=row.retrieval_reason,
        card_status_snapshot=row.card_status_snapshot,
        current_card_status=card.status if card is not None else "missing",
        safe_to_show=currently_safe,
        allowed_for_prompt=(
            row.allowed_for_prompt
            and card is not None
            and card.safe_to_show
            and card.allowed_for_prompt
        ),
        currently_prompt_eligible=currently_prompt_eligible,
    )


def knowledge_evidence_to_payload(session: Session, row: KnowledgeEvidence) -> dict[str, Any]:
    return knowledge_evidence_to_read(session, row).model_dump(mode="json")


def knowledge_evidence_to_legacy(item: KnowledgeEvidenceRead) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "evidence_id": str(item.id),
        "knowledge_evidence_id": str(item.id),
        "knowledge_retrieval_run_id": str(item.retrieval_run_id),
        "knowledge_card_id": str(item.knowledge_card_id),
        "source_artifact_id": str(item.source_artifact_id),
        "knowledge_type": item.knowledge_type,
        "title": item.title,
        "snippet": item.snippet,
        "source_locator": item.source_locator,
        "score": max(1, round(item.final_score * 10)) if item.final_score > 0 else 0,
        "metadata_score": item.metadata_score,
        "keyword_score": item.keyword_score,
        "vector_score": item.vector_score,
        "final_score": item.final_score,
        "matched_terms": item.matched_terms,
        "retrieval_reason": item.retrieval_reason,
        "safe_to_show": item.safe_to_show,
        "allowed_for_prompt": item.allowed_for_prompt,
        "status": item.card_status_snapshot,
        "current_card_status": item.current_card_status,
        "currently_prompt_eligible": item.currently_prompt_eligible,
    }
    if item.vector_score is not None:
        payload["semantic_score"] = item.vector_score
        payload["embedding_model"] = DEFAULT_EMBEDDING_MODEL
    return payload


def resolve_knowledge_evidence_artifact_refs(
    session: Session,
    *,
    project_id: uuid.UUID,
    items: list[dict[str, Any]],
) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    seen_evidence_ids: set[uuid.UUID] = set()
    for item in items:
        if not item.get("knowledge_card_id"):
            continue
        raw_evidence_id = item.get("knowledge_evidence_id") or item.get("evidence_id")
        raw_run_id = item.get("knowledge_retrieval_run_id")
        if not raw_evidence_id or not raw_run_id:
            raise KnowledgeRetrievalInputNotAllowedError
        try:
            evidence_id = uuid.UUID(str(raw_evidence_id))
            run_id = uuid.UUID(str(raw_run_id))
        except ValueError as exc:
            raise KnowledgeRetrievalInputNotAllowedError from exc
        if evidence_id in seen_evidence_ids:
            continue
        row = session.get(KnowledgeEvidence, evidence_id)
        run = session.get(KnowledgeRetrievalRun, run_id)
        artifact = session.get(Artifact, run.evidence_artifact_id) if run is not None else None
        if (
            row is None
            or row.project_id != project_id
            or row.retrieval_run_id != run_id
            or str(row.knowledge_card_id) != str(item.get("knowledge_card_id"))
            or run is None
            or run.project_id != project_id
            or run.status != "completed"
            or artifact is None
            or artifact.project_id != project_id
            or artifact.owner_entity_type != "KnowledgeRetrievalRun"
            or artifact.owner_entity_id != run.id
            or artifact.metadata_json.get("safe_to_show") is not True
        ):
            raise KnowledgeRetrievalInputNotAllowedError
        refs.append(
            {
                "knowledge_evidence_id": str(row.id),
                "knowledge_retrieval_run_id": str(run.id),
                "knowledge_card_id": str(row.knowledge_card_id),
                "canonical_artifact_id": str(artifact.id),
            },
        )
        seen_evidence_ids.add(evidence_id)
    return refs


def verified_prompt_evidence_refs(
    session: Session,
    *,
    project_id: uuid.UUID,
    retrieval_run_id: uuid.UUID,
    evidence_ids: list[uuid.UUID],
) -> list[dict[str, Any]]:
    if not evidence_ids:
        return []
    run = session.get(KnowledgeRetrievalRun, retrieval_run_id)
    if (
        run is None
        or run.project_id != project_id
        or run.status != "completed"
        or run.evidence_artifact_id is None
    ):
        raise KnowledgeRetrievalInputNotAllowedError
    artifact = session.get(Artifact, run.evidence_artifact_id)
    if (
        artifact is None
        or artifact.project_id != project_id
        or artifact.owner_entity_type != "KnowledgeRetrievalRun"
        or artifact.owner_entity_id != run.id
        or artifact.metadata_json.get("safe_to_show") is not True
    ):
        raise KnowledgeRetrievalInputNotAllowedError
    rows = list(
        session.scalars(
            select(KnowledgeEvidence)
            .join(TestKnowledgeCard, TestKnowledgeCard.id == KnowledgeEvidence.knowledge_card_id)
            .where(
                KnowledgeEvidence.id.in_(evidence_ids),
                KnowledgeEvidence.project_id == project_id,
                KnowledgeEvidence.retrieval_run_id == retrieval_run_id,
                KnowledgeEvidence.card_status_snapshot == "approved",
                KnowledgeEvidence.safe_to_show.is_(True),
                KnowledgeEvidence.allowed_for_prompt.is_(True),
                TestKnowledgeCard.project_id == project_id,
                TestKnowledgeCard.status == "approved",
                TestKnowledgeCard.safe_to_show.is_(True),
                TestKnowledgeCard.allowed_for_prompt.is_(True),
            ),
        ),
    )
    rows_by_id = {row.id: row for row in rows}
    if set(rows_by_id) != set(evidence_ids):
        raise KnowledgeRetrievalInputNotAllowedError
    return [
        knowledge_evidence_to_legacy(knowledge_evidence_to_read(session, rows_by_id[evidence_id]))
        for evidence_id in evidence_ids
    ]


def revalidate_prompt_evidence_items(
    session: Session,
    *,
    project_id: uuid.UUID,
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped_ids: dict[uuid.UUID, list[uuid.UUID]] = {}
    for item in items:
        raw_run_id = item.get("knowledge_retrieval_run_id")
        raw_evidence_id = item.get("knowledge_evidence_id") or item.get("evidence_id")
        if not raw_run_id or not raw_evidence_id:
            continue
        try:
            run_id = uuid.UUID(str(raw_run_id))
            evidence_id = uuid.UUID(str(raw_evidence_id))
        except ValueError:
            continue
        grouped_ids.setdefault(run_id, [])
        if evidence_id not in grouped_ids[run_id]:
            grouped_ids[run_id].append(evidence_id)
    verified: list[dict[str, Any]] = []
    for run_id, evidence_ids in grouped_ids.items():
        try:
            verified.extend(
                verified_prompt_evidence_refs(
                    session,
                    project_id=project_id,
                    retrieval_run_id=run_id,
                    evidence_ids=evidence_ids,
                ),
            )
        except KnowledgeRetrievalInputNotAllowedError:
            continue
    return verified


def sanitize_evidence_items_for_display(
    session: Session,
    *,
    project_id: uuid.UUID,
    items: list[Any],
) -> list[Any]:
    allowed_fields = {
        "evidence_id",
        "knowledge_evidence_id",
        "knowledge_retrieval_run_id",
        "knowledge_card_id",
        "context_artifact_id",
        "source_artifact_id",
        "knowledge_type",
        "title",
        "snippet",
        "source_locator",
        "source_ref",
        "sha256",
        "score",
        "metadata_score",
        "keyword_score",
        "vector_score",
        "semantic_score",
        "rerank_score",
        "final_score",
        "matched_terms",
        "retrieval_reason",
        "safe_to_show",
        "allowed_for_prompt",
        "status",
        "card_status_snapshot",
        "current_card_status",
        "currently_prompt_eligible",
        "embedding_model",
        "redaction_applied",
    }
    sanitized: list[Any] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        copy = {key: value for key, value in item.items() if key in allowed_fields}
        raw_card_id = copy.get("knowledge_card_id")
        card = None
        if raw_card_id:
            try:
                card = session.get(TestKnowledgeCard, uuid.UUID(str(raw_card_id)))
            except ValueError:
                card = None
        if raw_card_id and card is not None and card.project_id == project_id:
            copy["current_card_status"] = card.status
            copy["currently_prompt_eligible"] = (
                card.status == "approved"
                and card.safe_to_show
                and card.allowed_for_prompt
                and bool(copy.get("safe_to_show", False))
                and bool(copy.get("allowed_for_prompt", False))
            )
            currently_safe = card.safe_to_show
        else:
            raw_artifact_id = copy.get("context_artifact_id") or copy.get("source_artifact_id")
            source_artifact = None
            if raw_artifact_id:
                try:
                    source_artifact = session.get(Artifact, uuid.UUID(str(raw_artifact_id)))
                except ValueError:
                    source_artifact = None
            currently_safe = (
                source_artifact is not None
                and source_artifact.project_id == project_id
                and source_artifact.metadata_json.get("safe_to_show") is True
            )
            copy["currently_prompt_eligible"] = (
                currently_safe
                and source_artifact is not None
                and source_artifact.metadata_json.get("allowed_for_prompt") is True
            )
        if not currently_safe:
            copy["title"] = "Restricted knowledge evidence"
            copy["snippet"] = "[redacted]"
            copy["source_locator"] = {}
            copy["matched_terms"] = []
            copy["retrieval_reason"] = "restricted_evidence"
            copy["safe_to_show"] = False
            copy["allowed_for_prompt"] = False
            copy["currently_prompt_eligible"] = False
            copy.pop("source_ref", None)
            copy.pop("sha256", None)
        sanitized.append(copy)
    return sanitized


def retrieve_test_knowledge_evidence(
    session: Session,
    *,
    project_id: uuid.UUID,
    query_text: str,
    limit: int = 5,
    approved_only: bool = False,
    filters: dict[str, Any] | None = None,
    retrieval_mode: str = "hybrid",
) -> list[dict[str, Any]]:
    return match_test_knowledge_cards(
        session,
        project_id=project_id,
        query_text=query_text,
        limit=limit,
        approved_only=approved_only,
        filters=filters or {},
        retrieval_mode=retrieval_mode,
    ).items


def match_test_knowledge_cards(
    session: Session,
    *,
    project_id: uuid.UUID,
    query_text: str,
    limit: int,
    approved_only: bool,
    filters: dict[str, Any],
    retrieval_mode: str,
) -> KnowledgeMatchResult:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    query_terms = list(dict.fromkeys(normalize_terms(query_text)))
    if not query_terms:
        return KnowledgeMatchResult(
            candidate_count=0,
            items=[],
            vector_available=False,
            actual_mode="keyword" if retrieval_mode in {"hybrid", "vector"} else retrieval_mode,
            degraded=retrieval_mode in {"hybrid", "vector"},
            fallback_reason="vector_index_unavailable" if retrieval_mode in {"hybrid", "vector"} else None,
        )
    statuses = {"approved"} if approved_only else PROMPT_ELIGIBLE_STATUSES
    card_query = select(TestKnowledgeCard).where(
        TestKnowledgeCard.project_id == project_id,
        TestKnowledgeCard.status.in_(statuses),
        TestKnowledgeCard.safe_to_show.is_(True),
        TestKnowledgeCard.allowed_for_prompt.is_(True),
    )
    filter_columns = {
        "module_keys": TestKnowledgeCard.module_key,
        "knowledge_types": TestKnowledgeCard.knowledge_type,
        "risk_types": TestKnowledgeCard.risk_type,
        "api_endpoints": TestKnowledgeCard.api_endpoint,
    }
    for key, column in filter_columns.items():
        values = filters.get(key) or []
        if values:
            card_query = card_query.where(column.in_(values))
    cards = list(session.scalars(card_query))
    metadata_filter_active = any(filters.get(key) for key in filter_columns)
    evidence_by_card_id: dict[str, dict[str, Any]] = {}
    if retrieval_mode in {"metadata", "keyword", "vector", "hybrid"}:
        for card in cards:
            searchable_text = search_text_for_card(card)
            card_terms = set(normalize_terms(searchable_text))
            matched_terms = [term for term in query_terms if term in card_terms]
            if not matched_terms and retrieval_mode != "metadata":
                continue
            if retrieval_mode == "metadata" and not metadata_filter_active:
                continue
            evidence_by_card_id[str(card.id)] = evidence_for_card(
                card,
                matched_terms=matched_terms,
                query_term_count=len(query_terms),
                metadata_score=1.0 if metadata_filter_active else 0.0,
                retrieval_reason=(
                    "deterministic_metadata_filter"
                    if retrieval_mode == "metadata"
                    else "deterministic_keyword_overlap"
                ),
            )

    cards_by_id = {card.id: card for card in cards}
    indexed_by_card_id = {
        item.knowledge_card_id: item
        for item in session.scalars(
            select(TestKnowledgeEmbeddingIndex).where(
                TestKnowledgeEmbeddingIndex.project_id == project_id,
                TestKnowledgeEmbeddingIndex.status == "indexed",
                TestKnowledgeEmbeddingIndex.embedding_model == DEFAULT_EMBEDDING_MODEL,
            ),
        )
        if item.knowledge_card_id in cards_by_id
        and item.content_hash
        == hashlib.sha256(embedding_text_for_card(cards_by_id[item.knowledge_card_id]).encode("utf-8")).hexdigest()
    }
    vector_requested = retrieval_mode in {"vector", "hybrid"}
    vector_available = vector_requested and bool(indexed_by_card_id)
    if retrieval_mode == "vector" and vector_available:
        evidence_by_card_id = {}
    if vector_available:
        query_vectors_by_dim: dict[int, list[float]] = {}
        for card in cards:
            index_row = indexed_by_card_id.get(card.id)
            if index_row is None:
                continue
            if index_row.embedding_dim not in query_vectors_by_dim:
                query_vectors_by_dim[index_row.embedding_dim] = deterministic_embedding(
                    query_text,
                    index_row.embedding_dim,
                )
            query_vector = query_vectors_by_dim[index_row.embedding_dim]
            semantic_score = cosine_similarity(query_vector, index_row.embedding_json)
            if semantic_score < MIN_VECTOR_SIMILARITY:
                continue
            card_id = str(card.id)
            existing_evidence = evidence_by_card_id.get(card_id)
            if existing_evidence is None:
                evidence_by_card_id[card_id] = evidence_for_card(
                    card,
                    matched_terms=[],
                    query_term_count=len(query_terms),
                    metadata_score=1.0 if metadata_filter_active else 0.0,
                    retrieval_reason="deterministic_vector_similarity",
                    semantic_score=semantic_score,
                    embedding_model=index_row.embedding_model,
                )
            else:
                existing_evidence["vector_score"] = round(max(0.0, min(semantic_score, 1.0)), 6)
                existing_evidence["semantic_score"] = existing_evidence["vector_score"]
                existing_evidence["embedding_model"] = index_row.embedding_model
                existing_evidence["retrieval_reason"] = "deterministic_hybrid_keyword_vector"
                finalize_match_scores(existing_evidence)

    evidence = list(evidence_by_card_id.values())
    evidence.sort(
        key=lambda item: (
            STATUS_PRIORITY.get(str(item.get("status")), 99),
            -float(item["final_score"]),
            str(item["title"]).lower(),
            str(item["knowledge_card_id"]),
        ),
    )
    actual_mode = retrieval_mode
    degraded = False
    fallback_reason = None
    if vector_requested and not vector_available:
        actual_mode = "keyword"
        degraded = True
        fallback_reason = "vector_index_unavailable"
    return KnowledgeMatchResult(
        candidate_count=len(evidence),
        items=evidence[:limit],
        vector_available=vector_available,
        actual_mode=actual_mode,
        degraded=degraded,
        fallback_reason=fallback_reason,
    )


def list_extractable_context_artifact_ids(session: Session, project_id: uuid.UUID) -> list[uuid.UUID]:
    artifacts = list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.project_id == project_id,
                Artifact.owner_entity_type == "Project",
                Artifact.owner_entity_id == project_id,
                Artifact.artifact_type.in_(ai_runtime_service.CONTEXT_FILE_NAMES.keys()),
            )
            .order_by(Artifact.created_at.asc(), Artifact.id.asc()),
        ),
    )
    return [
        artifact.id
        for artifact in artifacts
        if artifact.metadata_json.get("safe_to_show") is True
        and artifact.metadata_json.get("allowed_for_prompt") is True
    ]


def embedding_index_to_dict(index_row: TestKnowledgeEmbeddingIndex) -> dict[str, Any]:
    return {
        "id": str(index_row.id),
        "project_id": str(index_row.project_id),
        "knowledge_card_id": str(index_row.knowledge_card_id),
        "index_kind": index_row.index_kind,
        "embedding_provider": index_row.embedding_provider,
        "embedding_model": index_row.embedding_model,
        "embedding_dim": index_row.embedding_dim,
        "content_hash": index_row.content_hash,
        "status": index_row.status,
        "metadata": index_row.metadata_json,
        "created_at": index_row.created_at.isoformat() if index_row.created_at else None,
    }


def evidence_for_card(
    card: TestKnowledgeCard,
    *,
    matched_terms: list[str],
    query_term_count: int,
    metadata_score: float,
    retrieval_reason: str,
    semantic_score: float | None = None,
    embedding_model: str | None = None,
) -> dict[str, Any]:
    evidence = {
        "evidence_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"test-knowledge-evidence:{card.id}")),
        "knowledge_card_id": str(card.id),
        "source_artifact_id": str(card.source_artifact_id),
        "knowledge_type": card.knowledge_type,
        "title": card.title,
        "snippet": card.content[:320],
        "source_locator": dict(card.source_locator_json or {}),
        "metadata_score": round(max(0.0, min(metadata_score, 1.0)), 6),
        "keyword_score": round(len(set(matched_terms)) / max(1, query_term_count), 6),
        "vector_score": (
            round(max(0.0, min(semantic_score, 1.0)), 6)
            if semantic_score is not None
            else None
        ),
        "rerank_score": None,
        "matched_terms": matched_terms,
        "retrieval_reason": retrieval_reason,
        "card_status_snapshot": card.status,
        "safe_to_show": card.safe_to_show,
        "allowed_for_prompt": card.allowed_for_prompt,
        "status": card.status,
    }
    finalize_match_scores(evidence)
    if evidence["vector_score"] is not None:
        evidence["semantic_score"] = evidence["vector_score"]
    if embedding_model is not None:
        evidence["embedding_model"] = embedding_model
    return evidence


def finalize_match_scores(evidence: dict[str, Any]) -> None:
    components = [
        float(value)
        for value in (
            evidence.get("metadata_score"),
            evidence.get("keyword_score"),
            evidence.get("vector_score"),
            evidence.get("rerank_score"),
        )
        if value is not None and float(value) > 0
    ]
    final_score = sum(components) / len(components) if components else 0.0
    evidence["final_score"] = round(max(0.0, min(final_score, 1.0)), 6)
    evidence["score"] = max(1, round(evidence["final_score"] * 10)) if final_score > 0 else 0


def search_text_for_card(card: TestKnowledgeCard) -> str:
    return " ".join(
        [
            card.title,
            card.content,
            card.knowledge_type,
            card.module_key or "",
            card.api_endpoint or "",
            card.risk_type or "",
            card.case_type_hint or "",
            card.applicability or "",
        ],
    )


def embedding_text_for_card(card: TestKnowledgeCard) -> str:
    return "\n".join(
        [
            f"title: {card.title}",
            f"type: {card.knowledge_type}",
            f"content: {card.content}",
            f"module: {card.module_key or ''}",
            f"api: {card.api_endpoint or ''}",
            f"risk: {card.risk_type or ''}",
            f"case_type: {card.case_type_hint or ''}",
            f"applicability: {card.applicability or ''}",
        ],
    )


def deterministic_embedding(text: str, dim: int = DEFAULT_EMBEDDING_DIM) -> list[float]:
    vector = [0.0] * dim
    for term in normalize_terms(text):
        digest = hashlib.sha256(term.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 6) for value in vector]


def cosine_similarity(left: list[float], right: list[Any]) -> float:
    if not left or not right:
        return 0.0
    pairs = zip(left, [float(value) for value in right], strict=False)
    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for left_value, right_value in pairs:
        dot += left_value * right_value
        left_norm += left_value * left_value
        right_norm += right_value * right_value
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / math.sqrt(left_norm * right_norm)


def build_test_knowledge_graph(session: Session, project_id: uuid.UUID) -> dict[str, Any]:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    cards = list(
        session.scalars(
            select(TestKnowledgeCard)
            .where(TestKnowledgeCard.project_id == project_id)
            .order_by(TestKnowledgeCard.created_at.asc(), TestKnowledgeCard.id.asc()),
        ),
    )
    candidates = list(
        session.scalars(
            select(GeneratedCaseCandidate)
            .where(GeneratedCaseCandidate.project_id == project_id)
            .order_by(GeneratedCaseCandidate.created_at.asc(), GeneratedCaseCandidate.id.asc()),
        ),
    )
    test_cases = list(
        session.scalars(
            select(TestCase)
            .where(TestCase.project_id == project_id)
            .order_by(TestCase.created_at.asc(), TestCase.id.asc()),
        ),
    )
    indexes = list(
        session.scalars(
            select(TestKnowledgeEmbeddingIndex)
            .where(TestKnowledgeEmbeddingIndex.project_id == project_id)
            .order_by(TestKnowledgeEmbeddingIndex.created_at.asc(), TestKnowledgeEmbeddingIndex.id.asc()),
        ),
    )
    relationships = list(
        session.scalars(
            select(TestKnowledgeRelationship)
            .where(
                TestKnowledgeRelationship.project_id == project_id,
                TestKnowledgeRelationship.status == "active",
            )
            .order_by(TestKnowledgeRelationship.created_at.asc(), TestKnowledgeRelationship.id.asc()),
        ),
    )
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    card_node_ids: dict[str, str] = {}
    prompt_eligible_card_ids = {
        str(card.id)
        for card in cards
        if card.status in PROMPT_ELIGIBLE_STATUSES and card.safe_to_show and card.allowed_for_prompt
    }
    covered_card_ids: set[str] = set()
    candidates_with_evidence: set[str] = set()
    indexed_card_ids: set[str] = set()

    for relationship in relationships:
        source = f"{relationship.source_entity_type.lower()}:{relationship.source_entity_id}"
        target = f"{relationship.target_entity_type.lower()}:{relationship.target_entity_id}"
        edges.append(
            {
                "source": source,
                "target": target,
                "edge_type": relationship.relationship_type,
                "weight": relationship.confidence / 100,
                "relationship_id": str(relationship.id),
            },
        )

    for card in cards:
        node_id = f"knowledge_card:{card.id}"
        card_node_ids[str(card.id)] = node_id
        nodes.append(
            {
                "id": node_id,
                "node_type": "knowledge_card",
                "entity_id": str(card.id),
                "title": card.title,
                "status": card.status,
                "knowledge_type": card.knowledge_type,
                "source_artifact_id": str(card.source_artifact_id),
            },
        )

    for index_row in indexes:
        node_id = f"embedding_index:{index_row.id}"
        knowledge_card_id = str(index_row.knowledge_card_id)
        if index_row.status == "indexed" and knowledge_card_id in prompt_eligible_card_ids:
            indexed_card_ids.add(knowledge_card_id)
        nodes.append(
            {
                "id": node_id,
                "node_type": "embedding_index",
                "entity_id": str(index_row.id),
                "title": index_row.embedding_model,
                "status": index_row.status,
                "knowledge_card_id": str(index_row.knowledge_card_id),
                "embedding_provider": index_row.embedding_provider,
                "embedding_dim": index_row.embedding_dim,
            },
        )
        target_node_id = card_node_ids.get(str(index_row.knowledge_card_id))
        if target_node_id:
            edges.append(
                {
                    "source": node_id,
                    "target": target_node_id,
                    "edge_type": "indexes_knowledge_card",
                    "weight": 1,
                },
            )

    for candidate in candidates:
        candidate_node_id = f"generated_case_candidate:{candidate.id}"
        nodes.append(
            {
                "id": candidate_node_id,
                "node_type": "generated_case_candidate",
                "entity_id": str(candidate.id),
                "title": candidate.title,
                "status": candidate.status,
            },
        )
        for evidence in candidate.source_knowledge_evidence_json:
            if not isinstance(evidence, dict):
                continue
            card_id = str(evidence.get("knowledge_card_id") or "")
            target_node_id = card_node_ids.get(card_id)
            if not target_node_id:
                continue
            covered_card_ids.add(card_id)
            candidates_with_evidence.add(str(candidate.id))
            edges.append(
                {
                    "source": candidate_node_id,
                    "target": target_node_id,
                    "edge_type": "uses_knowledge_card",
                    "weight": evidence.get("score", 1),
                },
            )

    for test_case in test_cases:
        test_case_node_id = f"test_case:{test_case.id}"
        nodes.append(
            {
                "id": test_case_node_id,
                "node_type": "test_case",
                "entity_id": str(test_case.id),
                "title": test_case.title,
                "status": test_case.review_status,
            },
        )
        if test_case.source_candidate_id is not None:
            edges.append(
                {
                    "source": test_case_node_id,
                    "target": f"generated_case_candidate:{test_case.source_candidate_id}",
                    "edge_type": "approved_from_candidate",
                    "weight": 1,
                },
            )

    approved_card_count = sum(1 for card in cards if card.status == "approved")
    prompt_eligible_card_count = len(prompt_eligible_card_ids)
    denominator = approved_card_count or len(cards)
    coverage_ratio = round(len(covered_card_ids) / denominator, 4) if denominator else 0
    vector_denominator = prompt_eligible_card_count or len(cards)
    vector_coverage_ratio = round(len(indexed_card_ids) / vector_denominator, 4) if vector_denominator else 0
    return {
        "nodes": nodes,
        "edges": edges,
        "coverage": {
            "knowledge_card_count": len(cards),
            "approved_card_count": approved_card_count,
            "prompt_eligible_card_count": prompt_eligible_card_count,
            "covered_knowledge_card_count": len(covered_card_ids),
            "embedding_index_count": len(indexes),
            "embedding_indexed_card_count": len(indexed_card_ids),
            "generated_candidate_count": len(candidates),
            "candidates_with_knowledge_evidence_count": len(candidates_with_evidence),
            "test_case_count": len(test_cases),
            "knowledge_coverage_ratio": coverage_ratio,
            "vector_index_coverage_ratio": vector_coverage_ratio,
        },
    }


def upsert_test_knowledge_relationship(
    session: Session,
    *,
    project_id: uuid.UUID,
    source_entity_type: str,
    source_entity_id: uuid.UUID,
    target_entity_type: str,
    target_entity_id: uuid.UUID,
    relationship_type: str,
    evidence_artifact_ids: list[uuid.UUID],
    confidence: int,
    metadata: dict[str, Any],
) -> TestKnowledgeRelationship:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    if source_entity_id == target_entity_id:
        raise KnowledgeRetrievalInputNotAllowedError
    if not relationship_entity_belongs_to_project(session, project_id, source_entity_type, source_entity_id):
        raise KnowledgeRetrievalInputNotAllowedError
    if not relationship_entity_belongs_to_project(session, project_id, target_entity_type, target_entity_id):
        raise KnowledgeRetrievalInputNotAllowedError
    relationship = session.scalar(
        select(TestKnowledgeRelationship).where(
            TestKnowledgeRelationship.project_id == project_id,
            TestKnowledgeRelationship.source_entity_type == source_entity_type,
            TestKnowledgeRelationship.source_entity_id == source_entity_id,
            TestKnowledgeRelationship.target_entity_type == target_entity_type,
            TestKnowledgeRelationship.target_entity_id == target_entity_id,
            TestKnowledgeRelationship.relationship_type == relationship_type,
        ),
    )
    if relationship is None:
        relationship = TestKnowledgeRelationship(
            project_id=project_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
        )
        session.add(relationship)
    relationship.evidence_artifact_ids_json = [str(item) for item in evidence_artifact_ids]
    relationship.confidence = confidence
    relationship.metadata_json = dict(metadata)
    relationship.status = "active"
    session.commit()
    session.refresh(relationship)
    return relationship


def relationship_entity_belongs_to_project(
    session: Session,
    project_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
) -> bool:
    model_by_type = {
        "Artifact": Artifact,
        "GeneratedCaseCandidate": GeneratedCaseCandidate,
        "Module": Module,
        "Requirement": Requirement,
        "RiskPoint": RiskItem,
        "TestCase": TestCase,
        "TestKnowledgeCard": TestKnowledgeCard,
    }
    model = model_by_type.get(entity_type)
    if model is None:
        return False
    entity = session.get(model, entity_id)
    return entity is not None and entity.project_id == project_id


FEEDBACK_SOURCE_TYPES = {"TestCase", "GeneratedCaseCandidate", "ReviewHistory", "FailureAnalysis", "Report"}
FEEDBACK_REVIEW_STATUSES = {"approved", "rejected"}


def create_knowledge_feedback_event(
    session: Session,
    *,
    project_id: uuid.UUID,
    source_entity_type: str,
    source_entity_id: uuid.UUID,
    proposed_knowledge_type: str,
    proposed_content: dict[str, Any],
    evidence_artifact_ids: list[uuid.UUID],
) -> KnowledgeFeedbackEvent:
    if source_entity_type not in FEEDBACK_SOURCE_TYPES:
        raise KnowledgeRetrievalInputNotAllowedError
    if not relationship_entity_belongs_to_project(session, project_id, source_entity_type, source_entity_id):
        raise KnowledgeRetrievalInputNotAllowedError
    if config_snapshot_contains_secret(proposed_content):
        raise KnowledgeRetrievalInputNotAllowedError
    event = KnowledgeFeedbackEvent(
        project_id=project_id,
        source_entity_type=source_entity_type,
        source_entity_id=source_entity_id,
        proposed_knowledge_type=proposed_knowledge_type,
        proposed_content_json=dict(proposed_content),
        evidence_artifact_ids_json=[str(item) for item in evidence_artifact_ids],
        status="proposed",
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def review_knowledge_feedback_event(
    session: Session,
    *,
    event_id: uuid.UUID,
    status: str,
    review_comment: str | None,
) -> KnowledgeFeedbackEvent:
    if status not in FEEDBACK_REVIEW_STATUSES:
        raise KnowledgeRetrievalInputNotAllowedError
    event = session.get(KnowledgeFeedbackEvent, event_id)
    if event is None:
        raise KnowledgeRetrievalRunNotFoundError
    if event.status not in {"proposed", "waiting_review"}:
        raise KnowledgeRetrievalInputNotAllowedError
    event.review_comment = review_comment
    if status == "rejected":
        event.status = "rejected"
        session.commit()
        session.refresh(event)
        return event
    content = dict(event.proposed_content_json or {})
    source_artifact_id = content.get("source_artifact_id")
    try:
        source_artifact_uuid = uuid.UUID(str(source_artifact_id))
    except (TypeError, ValueError) as exc:
        raise KnowledgeRetrievalInputNotAllowedError from exc
    source_artifact = session.get(Artifact, source_artifact_uuid)
    if source_artifact is None or source_artifact.project_id != event.project_id:
        raise KnowledgeRetrievalInputNotAllowedError
    if not bool(source_artifact.metadata_json.get("safe_to_show")) or not bool(
        source_artifact.metadata_json.get("allowed_for_prompt"),
    ):
        raise KnowledgeRetrievalInputNotAllowedError
    title = str(content.get("title") or "").strip()
    card_content = str(content.get("content") or "").strip()
    if not title or not card_content:
        raise KnowledgeRetrievalInputNotAllowedError
    quote_hash = hashlib.sha256(card_content.encode("utf-8")).hexdigest()
    card = TestKnowledgeCard(
        project_id=event.project_id,
        source_artifact_id=source_artifact_uuid,
        source_document_version=str(content.get("source_document_version") or "feedback-v1"),
        source_section=str(content.get("source_section") or "feedback"),
        source_quote_hash=quote_hash,
        source_locator_json=dict(content.get("source_locator") or {"source": "feedback"}),
        source_ref=str(content.get("source_ref") or "feedback"),
        knowledge_type=event.proposed_knowledge_type,
        title=title,
        content=card_content,
        applicability="case_generation",
        confidence=max(0, min(100, int(content.get("confidence", 50)))),
        safe_to_show=True,
        allowed_for_prompt=True,
        status="extracted",
    )
    session.add(card)
    session.flush()
    event.resulting_card_id = card.id
    event.status = "applied"
    session.commit()
    session.refresh(event)
    return event


def ensure_extractable_context_artifact(artifact: Artifact) -> None:
    if artifact.artifact_type not in ai_runtime_service.CONTEXT_FILE_NAMES:
        raise SourceArtifactNotAllowedError
    if not bool(artifact.metadata_json.get("safe_to_show", False)):
        raise SourceArtifactNotAllowedError
    if not bool(artifact.metadata_json.get("allowed_for_prompt", False)):
        raise SourceArtifactNotAllowedError


def candidate_sentences(text: str) -> list[str]:
    sentences = [re.sub(r"\s+", " ", item).strip(" -#*") for item in SENTENCE_SPLIT_PATTERN.split(text)]
    return [sentence for sentence in sentences if len(sentence) >= 12][:20]


def classify_knowledge(sentence: str) -> str:
    lower = sentence.lower()
    if re.search(r"\b(get|post|put|patch|delete)\b|/api/|endpoint|接口", lower):
        return "APIContract"
    if any(keyword in lower for keyword in ["expired", "过期", "不能超过", "大于", "小于", "边界", "boundary", "limit"]):
        return "BoundaryCondition"
    if any(keyword in lower for keyword in ["error", "fail", "blocked", "reject", "不可", "不能", "禁止", "失败"]):
        return "ExceptionScenario"
    if any(keyword in lower for keyword in ["risk", "风险", "regression", "回归"]):
        return "RiskPoint"
    if any(keyword in lower for keyword in ["should", "must", "required", "必须", "需要", "规则"]):
        return "BusinessRule"
    return "TestStrategyNote"


def card_title(sentence: str, knowledge_type: str) -> str:
    compact = sentence.strip()
    if len(compact) > 72:
        compact = f"{compact[:69]}..."
    return f"{knowledge_type}: {compact}"


def infer_module_key(sentence: str) -> str | None:
    lower = sentence.lower()
    for key in ("coupon", "checkout", "order", "payment", "login"):
        if key in lower:
            return key
    for key in ("优惠券", "结算", "订单", "支付", "登录"):
        if key in sentence:
            return key
    return None


def infer_api_endpoint(sentence: str) -> str | None:
    match = ENDPOINT_PATTERN.search(sentence)
    if not match:
        return None
    return match.group(1) or match.group(2)


def infer_risk_type(sentence: str) -> str | None:
    lower = sentence.lower()
    if any(keyword in lower for keyword in ["expired", "过期", "不能超过", "limit", "boundary"]):
        return "boundary"
    if any(keyword in lower for keyword in ["error", "fail", "失败", "不可", "不能"]):
        return "business"
    if any(keyword in lower for keyword in ["regression", "回归"]):
        return "regression"
    return None


def infer_case_type_hint(sentence: str, knowledge_type: str) -> str | None:
    if knowledge_type in {"BoundaryCondition", "ExceptionScenario"}:
        return "negative"
    if knowledge_type == "APIContract":
        return "api"
    if knowledge_type == "RiskPoint":
        return "regression"
    return "functional"


def confidence_for(sentence: str, knowledge_type: str) -> int:
    confidence = 70
    if knowledge_type in {"BoundaryCondition", "APIContract", "ExceptionScenario"}:
        confidence += 10
    if infer_api_endpoint(sentence):
        confidence += 5
    return min(confidence, 95)


def normalize_terms(value: str) -> list[str]:
    return [term.lower() for term in TERM_PATTERN.findall(value) if len(term) >= 2]


def to_read(card: TestKnowledgeCard) -> TestKnowledgeCardRead:
    return TestKnowledgeCardRead(
        id=card.id,
        project_id=card.project_id,
        source_artifact_id=card.source_artifact_id,
        source_document_version=card.source_document_version,
        source_section=card.source_section,
        source_quote_hash=card.source_quote_hash,
        source_locator_json=card.source_locator_json,
        source_ref=card.source_ref,
        ingestion_run_id=card.ingestion_run_id,
        knowledge_type=card.knowledge_type,
        title=card.title,
        content=card.content,
        module_key=card.module_key,
        api_endpoint=card.api_endpoint,
        risk_type=card.risk_type,
        case_type_hint=card.case_type_hint,
        applicability=card.applicability,
        confidence=card.confidence,
        safe_to_show=card.safe_to_show,
        allowed_for_prompt=card.allowed_for_prompt,
        status=card.status,
        reviewed_at=card.reviewed_at,
        review_comment=card.review_comment,
        duplicate_of_card_id=card.duplicate_of_card_id,
        last_verified_at=card.last_verified_at,
        created_at=card.created_at,
    )
