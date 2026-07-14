from __future__ import annotations

import hashlib
import json
import math
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service as ai_runtime_service
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.cases.models import GeneratedCaseCandidate, TestCase
from backend.app.modules.knowledge.models import (
    KnowledgeIngestionRun,
    TestKnowledgeCard,
    TestKnowledgeEmbeddingIndex,
)
from backend.app.modules.knowledge.schemas import (
    KnowledgeIngestionArtifactRead,
    KnowledgeIngestionRunCreateRequest,
    KnowledgeIngestionRunRead,
    TestKnowledgeCardRead,
)
from backend.app.modules.projects.models import Project
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
ALLOWED_CARD_TRANSITIONS = {
    "extracted": {"approved", "stale", "unsafe", "duplicate", "archived"},
    "approved": {"stale", "unsafe", "duplicate", "archived"},
}


class ProjectNotFoundError(Exception):
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


def retrieve_test_knowledge_evidence(
    session: Session,
    *,
    project_id: uuid.UUID,
    query_text: str,
    limit: int = 5,
    approved_only: bool = False,
) -> list[dict[str, Any]]:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError
    query_terms = normalize_terms(query_text)
    if not query_terms:
        return []
    statuses = {"approved"} if approved_only else PROMPT_ELIGIBLE_STATUSES
    cards = list(
        session.scalars(
            select(TestKnowledgeCard).where(
                TestKnowledgeCard.project_id == project_id,
                TestKnowledgeCard.status.in_(statuses),
                TestKnowledgeCard.safe_to_show.is_(True),
                TestKnowledgeCard.allowed_for_prompt.is_(True),
            ),
        ),
    )
    evidence_by_card_id: dict[str, dict[str, Any]] = {}
    for card in cards:
        searchable_text = search_text_for_card(card)
        card_terms = set(normalize_terms(searchable_text))
        matched_terms = [term for term in query_terms if term in card_terms]
        if not matched_terms:
            continue
        evidence_by_card_id[str(card.id)] = evidence_for_card(
            card,
            score=len(matched_terms),
            matched_terms=matched_terms,
            retrieval_reason="deterministic_keyword_overlap",
        )

    indexed_by_card_id = {
        item.knowledge_card_id: item
        for item in session.scalars(
            select(TestKnowledgeEmbeddingIndex).where(
                TestKnowledgeEmbeddingIndex.project_id == project_id,
                TestKnowledgeEmbeddingIndex.status == "indexed",
                TestKnowledgeEmbeddingIndex.embedding_model == DEFAULT_EMBEDDING_MODEL,
            ),
        )
    }
    if indexed_by_card_id:
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
            vector_score = max(1, round(semantic_score * 10))
            existing_evidence = evidence_by_card_id.get(card_id)
            if existing_evidence is None:
                evidence_by_card_id[card_id] = evidence_for_card(
                    card,
                    score=vector_score,
                    matched_terms=[],
                    retrieval_reason="deterministic_vector_similarity",
                    semantic_score=semantic_score,
                    embedding_model=index_row.embedding_model,
                )
            else:
                existing_evidence["score"] = int(existing_evidence["score"]) + vector_score
                existing_evidence["semantic_score"] = round(semantic_score, 4)
                existing_evidence["embedding_model"] = index_row.embedding_model
                existing_evidence["retrieval_reason"] = "deterministic_hybrid_keyword_vector"

    evidence = list(evidence_by_card_id.values())
    evidence.sort(
        key=lambda item: (
            STATUS_PRIORITY.get(str(item.get("status")), 99),
            -int(item["score"]),
            str(item["title"]).lower(),
            str(item["knowledge_card_id"]),
        ),
    )
    return evidence[:limit]


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
    score: int,
    matched_terms: list[str],
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
        "score": score,
        "matched_terms": matched_terms,
        "retrieval_reason": retrieval_reason,
        "safe_to_show": card.safe_to_show,
        "allowed_for_prompt": card.allowed_for_prompt,
        "status": card.status,
    }
    if semantic_score is not None:
        evidence["semantic_score"] = round(semantic_score, 4)
    if embedding_model is not None:
        evidence["embedding_model"] = embedding_model
    return evidence


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
