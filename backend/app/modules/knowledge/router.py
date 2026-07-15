from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.knowledge import service
from backend.app.modules.knowledge.schemas import (
    KnowledgeIngestionRunCreateRequest,
    KnowledgeIngestionRunListRead,
    KnowledgeIngestionRunRead,
    KnowledgeRetrievalRunCreateRequest,
    KnowledgeRetrievalRunListRead,
    KnowledgeRetrievalRunRead,
    TestKnowledgeCardExtractBatchRead,
    TestKnowledgeCardExtractBatchRequest,
    TestKnowledgeCardExtractRead,
    TestKnowledgeCardExtractRequest,
    TestKnowledgeCardListRead,
    TestKnowledgeCardRead,
    TestKnowledgeCardReviewRequest,
    TestKnowledgeCardRetrievalRead,
    TestKnowledgeCardRetrieveRequest,
    TestKnowledgeGraphRead,
    TestKnowledgeRelationshipCreateRequest,
    TestKnowledgeIndexRead,
    TestKnowledgeIndexRebuildRead,
    TestKnowledgeIndexRebuildRequest,
)
from backend.app.modules.projects.router import get_session


router = APIRouter(tags=["test-knowledge"])


def not_found(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def bad_request(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


@router.post(
    "/knowledge/ingestion-runs",
    response_model=KnowledgeIngestionRunRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_knowledge_ingestion_run(
    data: KnowledgeIngestionRunCreateRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> KnowledgeIngestionRunRead:
    try:
        run = service.create_knowledge_ingestion_run(session, store, data)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.KnowledgeIngestionSourceNotAllowedError as exc:
        raise bad_request(
            "KNOWLEDGE_INGESTION_SOURCE_NOT_ALLOWED",
            "Knowledge ingestion sources must be prompt-safe persisted artifacts in the same project.",
        ) from exc
    except service.KnowledgeIngestionConfigNotAllowedError as exc:
        raise bad_request(
            "KNOWLEDGE_INGESTION_CONFIG_NOT_ALLOWED",
            "Knowledge ingestion config must be bounded and must not contain secrets.",
        ) from exc
    return service.ingestion_run_to_read(session, run)


@router.get(
    "/projects/{project_id}/knowledge/ingestion-runs",
    response_model=KnowledgeIngestionRunListRead,
)
def list_knowledge_ingestion_runs(
    project_id: uuid.UUID,
    run_status: str | None = Query(default=None, alias="status", max_length=40),
    source_type: str | None = Query(default=None, max_length=80),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: uuid.UUID | None = Query(default=None),
    session: Session = Depends(get_session),
) -> KnowledgeIngestionRunListRead:
    try:
        page = service.list_knowledge_ingestion_runs(
            session,
            project_id,
            status=run_status,
            source_type=source_type,
            limit=limit,
            cursor=cursor,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.KnowledgeIngestionRunNotFoundError as exc:
        raise bad_request("KNOWLEDGE_INGESTION_CURSOR_INVALID", "Knowledge ingestion cursor is invalid.") from exc
    return KnowledgeIngestionRunListRead(
        items=service.ingestion_runs_to_read(session, page.items),
        total=page.total,
        next_cursor=page.next_cursor,
    )


@router.get(
    "/knowledge/ingestion-runs/{run_id}",
    response_model=KnowledgeIngestionRunRead,
)
def read_knowledge_ingestion_run(
    run_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> KnowledgeIngestionRunRead:
    try:
        run = service.get_knowledge_ingestion_run(session, run_id)
    except service.KnowledgeIngestionRunNotFoundError as exc:
        raise not_found("KNOWLEDGE_INGESTION_RUN_NOT_FOUND", "Knowledge ingestion run not found.") from exc
    return service.ingestion_run_to_read(session, run)


@router.post(
    "/knowledge/retrieval-runs",
    response_model=KnowledgeRetrievalRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_retrieval_run(
    data: KnowledgeRetrievalRunCreateRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> KnowledgeRetrievalRunRead:
    try:
        run = service.create_knowledge_retrieval_run(session, store, data)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.KnowledgeRetrievalConsumerNotAllowedError as exc:
        raise bad_request(
            "KNOWLEDGE_RETRIEVAL_CONSUMER_NOT_ALLOWED",
            "Knowledge retrieval consumer must be a persisted entity in the same project.",
        ) from exc
    except service.KnowledgeRetrievalInputNotAllowedError as exc:
        raise bad_request(
            "KNOWLEDGE_RETRIEVAL_INPUT_NOT_ALLOWED",
            "Knowledge retrieval query or filters contain unsupported unsafe values.",
        ) from exc
    return service.knowledge_retrieval_run_to_read(session, run)


@router.get(
    "/projects/{project_id}/knowledge/retrieval-runs",
    response_model=KnowledgeRetrievalRunListRead,
)
def list_knowledge_retrieval_runs(
    project_id: uuid.UUID,
    run_status: str | None = Query(default=None, alias="status", max_length=40),
    provider_type: str | None = Query(default=None, max_length=80),
    consumer_entity_type: str | None = Query(default=None, max_length=80),
    consumer_entity_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: uuid.UUID | None = Query(default=None),
    session: Session = Depends(get_session),
) -> KnowledgeRetrievalRunListRead:
    if (consumer_entity_type is None) != (consumer_entity_id is None):
        raise bad_request(
            "KNOWLEDGE_RETRIEVAL_CONSUMER_FILTER_INVALID",
            "Consumer type and id filters must be provided together.",
        )
    try:
        page = service.list_knowledge_retrieval_runs(
            session,
            project_id,
            status=run_status,
            provider_type=provider_type,
            consumer_entity_type=consumer_entity_type,
            consumer_entity_id=consumer_entity_id,
            limit=limit,
            cursor=cursor,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.KnowledgeRetrievalRunNotFoundError as exc:
        raise bad_request("KNOWLEDGE_RETRIEVAL_CURSOR_INVALID", "Knowledge retrieval cursor is invalid.") from exc
    return KnowledgeRetrievalRunListRead(
        items=service.knowledge_retrieval_runs_to_read(session, page.items),
        total=page.total,
        next_cursor=page.next_cursor,
    )


@router.get(
    "/knowledge/retrieval-runs/{run_id}",
    response_model=KnowledgeRetrievalRunRead,
)
def read_knowledge_retrieval_run(
    run_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> KnowledgeRetrievalRunRead:
    try:
        run = service.get_knowledge_retrieval_run(session, run_id)
    except service.KnowledgeRetrievalRunNotFoundError as exc:
        raise not_found("KNOWLEDGE_RETRIEVAL_RUN_NOT_FOUND", "Knowledge retrieval run not found.") from exc
    return service.knowledge_retrieval_run_to_read(session, run)


@router.post(
    "/test-knowledge/cards/extract",
    response_model=TestKnowledgeCardExtractRead,
    status_code=status.HTTP_201_CREATED,
)
def extract_test_knowledge_cards(
    data: TestKnowledgeCardExtractRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> TestKnowledgeCardExtractRead:
    try:
        result = service.extract_test_knowledge_cards(
            session,
            store,
            project_id=data.project_id,
            source_artifact_id=data.source_artifact_id,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.SourceArtifactNotFoundError as exc:
        raise not_found("ARTIFACT_NOT_FOUND", "Source artifact not found.") from exc
    except service.SourceArtifactNotAllowedError as exc:
        raise bad_request(
            "TEST_KNOWLEDGE_SOURCE_NOT_ALLOWED",
            "Source artifact cannot be extracted into knowledge cards.",
        ) from exc
    return TestKnowledgeCardExtractRead(
        source_artifact_id=result.source_artifact_id,
        created_count=result.created_count,
        skipped_count=result.skipped_count,
        items=[service.to_read(card) for card in result.cards],
    )


@router.post(
    "/test-knowledge/cards/extract-batch",
    response_model=TestKnowledgeCardExtractBatchRead,
    status_code=status.HTTP_201_CREATED,
)
def extract_all_test_knowledge_cards(
    data: TestKnowledgeCardExtractBatchRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> TestKnowledgeCardExtractBatchRead:
    try:
        result = service.extract_all_test_knowledge_cards(
            session,
            store,
            project_id=data.project_id,
            source_artifact_ids=data.source_artifact_ids,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.SourceArtifactNotFoundError as exc:
        raise not_found("ARTIFACT_NOT_FOUND", "Source artifact not found.") from exc
    except service.SourceArtifactNotAllowedError as exc:
        raise bad_request(
            "TEST_KNOWLEDGE_SOURCE_NOT_ALLOWED",
            "Source artifact cannot be extracted into knowledge cards.",
        ) from exc
    return TestKnowledgeCardExtractBatchRead(
        project_id=result.project_id,
        source_artifact_ids=result.source_artifact_ids,
        created_count=result.created_count,
        skipped_count=result.skipped_count,
        items=[service.to_read(card) for card in result.cards],
    )


@router.get("/projects/{project_id}/test-knowledge/cards", response_model=TestKnowledgeCardListRead)
def list_test_knowledge_cards(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> TestKnowledgeCardListRead:
    try:
        cards = service.list_test_knowledge_cards(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return TestKnowledgeCardListRead(items=[service.to_read(card) for card in cards], total=len(cards))


@router.get("/projects/{project_id}/test-knowledge/graph", response_model=TestKnowledgeGraphRead)
def get_test_knowledge_graph(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> TestKnowledgeGraphRead:
    try:
        graph = service.build_test_knowledge_graph(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return TestKnowledgeGraphRead(
        project_id=project_id,
        nodes=graph["nodes"],
        edges=graph["edges"],
        coverage=graph["coverage"],
    )


@router.post("/projects/{project_id}/test-knowledge/relationships", status_code=status.HTTP_201_CREATED)
def create_test_knowledge_relationship(
    project_id: uuid.UUID,
    data: TestKnowledgeRelationshipCreateRequest,
    session: Session = Depends(get_session),
) -> dict:
    if project_id != data.project_id:
        raise bad_request("TEST_KNOWLEDGE_PROJECT_MISMATCH", "Relationship project does not match the path.")
    try:
        relationship = service.upsert_test_knowledge_relationship(
            session,
            project_id=project_id,
            source_entity_type=data.source_entity_type,
            source_entity_id=data.source_entity_id,
            target_entity_type=data.target_entity_type,
            target_entity_id=data.target_entity_id,
            relationship_type=data.relationship_type,
            evidence_artifact_ids=data.evidence_artifact_ids,
            confidence=data.confidence,
            metadata=data.metadata,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.KnowledgeRetrievalInputNotAllowedError as exc:
        raise bad_request(
            "TEST_KNOWLEDGE_RELATIONSHIP_INVALID",
            "Relationship entities must exist in the same project.",
        ) from exc
    return {
        "id": str(relationship.id),
        "project_id": str(relationship.project_id),
        "source_entity_type": relationship.source_entity_type,
        "source_entity_id": str(relationship.source_entity_id),
        "target_entity_type": relationship.target_entity_type,
        "target_entity_id": str(relationship.target_entity_id),
        "relationship_type": relationship.relationship_type,
        "evidence_artifact_ids": relationship.evidence_artifact_ids_json,
        "confidence": relationship.confidence,
        "status": relationship.status,
        "metadata": relationship.metadata_json,
    }


@router.get("/projects/{project_id}/test-knowledge/index", response_model=TestKnowledgeIndexRead)
def get_test_knowledge_index(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> TestKnowledgeIndexRead:
    try:
        index = service.list_test_knowledge_index(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return TestKnowledgeIndexRead(
        project_id=project_id,
        total=index["total"],
        indexed_count=index["indexed_count"],
        embedding_models=index["embedding_models"],
        items=index["items"],
    )


@router.post(
    "/test-knowledge/index/rebuild",
    response_model=TestKnowledgeIndexRebuildRead,
    status_code=status.HTTP_201_CREATED,
)
def rebuild_test_knowledge_index(
    data: TestKnowledgeIndexRebuildRequest,
    session: Session = Depends(get_session),
) -> TestKnowledgeIndexRebuildRead:
    try:
        result = service.rebuild_test_knowledge_index(
            session,
            project_id=data.project_id,
            knowledge_card_ids=data.knowledge_card_ids,
            embedding_model=data.embedding_model,
            embedding_dim=data.embedding_dim,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return TestKnowledgeIndexRebuildRead(
        project_id=result.project_id,
        indexed_count=result.indexed_count,
        skipped_count=result.skipped_count,
        embedding_model=result.embedding_model,
        embedding_dim=result.embedding_dim,
        items=[service.embedding_index_to_dict(item) for item in result.items],
    )


@router.patch("/test-knowledge/cards/{card_id}", response_model=TestKnowledgeCardRead)
def review_test_knowledge_card(
    card_id: uuid.UUID,
    data: TestKnowledgeCardReviewRequest,
    session: Session = Depends(get_session),
) -> TestKnowledgeCardRead:
    try:
        card = service.review_test_knowledge_card(
            session,
            project_id=data.project_id,
            card_id=card_id,
            status=data.status,
            review_comment=data.review_comment,
            duplicate_of_card_id=data.duplicate_of_card_id,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.TestKnowledgeCardNotFoundError as exc:
        raise not_found("TEST_KNOWLEDGE_CARD_NOT_FOUND", "Test knowledge card not found.") from exc
    except service.TestKnowledgeCardInvalidStatusError as exc:
        raise bad_request("TEST_KNOWLEDGE_CARD_INVALID_STATUS", "Unsupported test knowledge card status.") from exc
    except service.TestKnowledgeCardDuplicateTargetError as exc:
        raise bad_request(
            "TEST_KNOWLEDGE_CARD_DUPLICATE_TARGET_INVALID",
            "Duplicate knowledge cards require a different canonical card in the same project.",
        ) from exc
    return service.to_read(card)


@router.post("/test-knowledge/cards/retrieve", response_model=TestKnowledgeCardRetrievalRead)
def retrieve_test_knowledge_cards(
    data: TestKnowledgeCardRetrieveRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> TestKnowledgeCardRetrievalRead:
    try:
        run = service.create_knowledge_retrieval_run(
            session,
            store,
            KnowledgeRetrievalRunCreateRequest(
                project_id=data.project_id,
                query_text=data.query_text,
                retrieval_mode="hybrid",
                approved_only=data.approved_only,
                limit=data.limit,
            ),
        )
        run_read = service.knowledge_retrieval_run_to_read(session, run)
        items = [
            service.knowledge_evidence_to_legacy(item)
            for item in run_read.items
        ]
    except service.KnowledgeRetrievalInputNotAllowedError as exc:
        raise bad_request(
            "KNOWLEDGE_RETRIEVAL_INPUT_NOT_ALLOWED",
            "Knowledge retrieval query or filters contain unsupported unsafe values.",
        ) from exc
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return TestKnowledgeCardRetrievalRead(
        project_id=data.project_id,
        query_text=data.query_text,
        approved_only=data.approved_only,
        items=items,
        total=len(items),
    )
