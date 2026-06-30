from __future__ import annotations

import re
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.ai_runtime.service import CONTEXT_FILE_NAMES
from backend.app.modules.extension.models import KnowledgeAdapterConfig, ToolDefinition
from backend.app.modules.extension.schemas import (
    KnowledgeAdapterRead,
    KnowledgeAdapterUpdate,
    KnowledgeBaseContextArtifactRead,
    KnowledgeBaseLatestRetrievalRead,
    KnowledgeBaseRead,
    KnowledgeBaseRetrievalResultRead,
    KnowledgeRetrievalRead,
    KnowledgeRetrievalResultItem,
    ToolDefinitionListRead,
    ToolDefinitionRead,
)
from backend.app.modules.projects.models import Project


ALLOWED_PROVIDER_TYPES = {"none", "stub", "deterministic_local"}
ALLOWED_STATUSES = {"not_configured", "disabled", "configured_stub"}
RUNTIME_CONFIG_KEYS = {
    "api_key",
    "access_token",
    "token",
    "secret",
    "password",
    "vector_db",
    "vector_db_url",
    "embedding_model",
    "embedding_provider",
    "index_name",
    "reranker",
    "remote_url",
    "server_url",
    "mcp_transport",
}
KNOWLEDGE_BASE_NON_GOALS = [
    "no_vector_index",
    "no_embedding",
    "no_reranking",
    "no_external_rag_runtime",
]
DEFAULT_MAX_RESULTS = 5
DEFAULT_MAX_SNIPPET_CHARS = 320
MAX_RETRIEVAL_RESULTS = 10
MAX_SNIPPET_CHARS = 1000
MIN_SNIPPET_CHARS = 40
TERM_PATTERN = re.compile(r"\w+", re.UNICODE)


class KnowledgeAdapterRuntimeNotAllowedError(Exception):
    pass


class KnowledgeAdapterProjectNotFoundError(Exception):
    pass


def get_project_or_raise(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise KnowledgeAdapterProjectNotFoundError
    return project


def get_knowledge_adapter_config(
    session: Session,
    project_id: uuid.UUID,
    adapter_name: str = "default",
) -> KnowledgeAdapterConfig | None:
    return session.scalar(
        select(KnowledgeAdapterConfig).where(
            KnowledgeAdapterConfig.project_id == project_id,
            KnowledgeAdapterConfig.adapter_name == adapter_name,
        ),
    )


def read_knowledge_adapter(
    session: Session,
    project_id: uuid.UUID,
    *,
    used_knowledge: bool = False,
) -> KnowledgeAdapterRead:
    get_project_or_raise(session, project_id)
    config = get_knowledge_adapter_config(session, project_id)
    if config is None:
        return KnowledgeAdapterRead(
            project_id=project_id,
            adapter_name="default",
            status="not_configured",
            provider_type="none",
            config={},
            safety_policy={},
            used_knowledge=used_knowledge,
        )
    return to_read(config, used_knowledge=used_knowledge)


def read_knowledge_base(session: Session, project_id: uuid.UUID) -> KnowledgeBaseRead:
    get_project_or_raise(session, project_id)
    retrieval_artifacts = knowledge_retrieval_evidence(session, project_id)
    latest_retrievals = [to_latest_retrieval_read(artifact) for artifact in retrieval_artifacts]
    retrieval_usage = context_artifact_retrieval_usage(retrieval_artifacts)
    return KnowledgeBaseRead(
        project_id=project_id,
        knowledge_adapter=read_knowledge_adapter(session, project_id, used_knowledge=bool(latest_retrievals)),
        context_artifacts=list_knowledge_base_context_artifacts(session, project_id, retrieval_usage),
        latest_retrievals=latest_retrievals,
        non_goals=list(KNOWLEDGE_BASE_NON_GOALS),
    )


def list_tool_definitions(session: Session, project_id: uuid.UUID) -> ToolDefinitionListRead:
    get_project_or_raise(session, project_id)
    tool_definitions = session.scalars(
        select(ToolDefinition)
        .where(
            (ToolDefinition.project_id == project_id) | (ToolDefinition.project_id.is_(None)),
        )
        .order_by(ToolDefinition.name.asc()),
    ).all()
    items = [to_tool_definition_read(tool_definition) for tool_definition in tool_definitions]
    return ToolDefinitionListRead(items=items, total=len(items))


def retrieve_deterministic_knowledge(
    session: Session,
    store: LocalArtifactStore,
    project_id: uuid.UUID,
    query_text: str,
    *,
    adapter_name: str = "default",
    max_results: int | None = None,
    max_snippet_chars: int | None = None,
) -> KnowledgeRetrievalRead:
    get_project_or_raise(session, project_id)
    query_terms = normalize_terms(query_text)
    config = get_knowledge_adapter_config(session, project_id, adapter_name)
    limit = bounded_int(
        max_results if max_results is not None else config_value(config, "max_results", DEFAULT_MAX_RESULTS),
        minimum=1,
        maximum=MAX_RETRIEVAL_RESULTS,
    )
    snippet_limit = bounded_int(
        max_snippet_chars
        if max_snippet_chars is not None
        else config_value(config, "max_snippet_chars", DEFAULT_MAX_SNIPPET_CHARS),
        minimum=MIN_SNIPPET_CHARS,
        maximum=MAX_SNIPPET_CHARS,
    )
    min_score = bounded_int(config_value(config, "min_score", 1), minimum=1, maximum=len(query_terms) or 1)

    if not is_deterministic_adapter_enabled(config) or not query_terms:
        return KnowledgeRetrievalRead(
            adapter_name=adapter_name,
            query_text=query_text,
            query_terms=query_terms,
            used_knowledge=False,
        )

    artifacts = list_eligible_context_artifacts(session, project_id)
    results: list[KnowledgeRetrievalResultItem] = []
    for artifact in artifacts:
        text = store.read_bytes(artifact.file_path).decode("utf-8", errors="replace")
        searchable_text = "\n".join(
            [
                str(artifact.metadata_json.get("title", "")),
                str(artifact.metadata_json.get("source_ref", "")),
                text,
            ],
        )
        artifact_terms = set(normalize_terms(searchable_text))
        matched_terms = [term for term in query_terms if term in artifact_terms]
        score = len(matched_terms)
        if score < min_score:
            continue
        results.append(to_retrieval_item(artifact, text, matched_terms, score, snippet_limit))

    results.sort(
        key=lambda item: (
            -item.score,
            item.title.lower(),
            str(item.context_artifact_id),
        ),
    )
    bounded_results = results[:limit]
    return KnowledgeRetrievalRead(
        adapter_name=adapter_name,
        query_text=query_text,
        query_terms=query_terms,
        used_knowledge=bool(bounded_results),
        used_context_artifact_ids=[item.context_artifact_id for item in bounded_results],
        results=bounded_results,
    )


def update_knowledge_adapter(
    session: Session,
    project_id: uuid.UUID,
    data: KnowledgeAdapterUpdate,
) -> KnowledgeAdapterRead:
    get_project_or_raise(session, project_id)
    ensure_stub_only(data)

    config = get_knowledge_adapter_config(session, project_id, data.adapter_name)
    if config is None:
        config = KnowledgeAdapterConfig(project_id=project_id, adapter_name=data.adapter_name)

    config.status = data.status
    config.provider_type = data.provider_type
    config.config_json = dict(data.config)
    config.safety_policy_json = dict(data.safety_policy)
    config.notes = data.notes
    session.add(config)
    session.commit()
    session.refresh(config)
    return to_read(config)


def ensure_stub_only(data: KnowledgeAdapterUpdate) -> None:
    if data.provider_type not in ALLOWED_PROVIDER_TYPES or data.status not in ALLOWED_STATUSES:
        raise KnowledgeAdapterRuntimeNotAllowedError

    if contains_runtime_key(data.config) or contains_runtime_key(data.safety_policy):
        raise KnowledgeAdapterRuntimeNotAllowedError


def contains_runtime_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = str(key).lower()
            if normalized_key in RUNTIME_CONFIG_KEYS:
                return True
            if contains_runtime_key(child):
                return True
    if isinstance(value, list):
        return any(contains_runtime_key(item) for item in value)
    return False


def is_deterministic_adapter_enabled(config: KnowledgeAdapterConfig | None) -> bool:
    return (
        config is not None
        and config.status == "configured_stub"
        and config.provider_type == "deterministic_local"
    )


def config_value(config: KnowledgeAdapterConfig | None, key: str, default: int) -> int:
    if config is None:
        return default
    value = config.config_json.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def bounded_int(value: int, *, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def normalize_terms(text: str) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for match in TERM_PATTERN.finditer(text.lower()):
        term = match.group(0)
        if term not in seen:
            seen.add(term)
            terms.append(term)
    return terms


def list_eligible_context_artifacts(session: Session, project_id: uuid.UUID) -> list[Artifact]:
    artifacts = session.scalars(
        select(Artifact)
        .where(
            Artifact.project_id == project_id,
            Artifact.owner_entity_type == "Project",
            Artifact.owner_entity_id == project_id,
            Artifact.artifact_type.in_(CONTEXT_FILE_NAMES.keys()),
        )
        .order_by(Artifact.created_at.asc(), Artifact.id.asc()),
    ).all()
    return [
        artifact
        for artifact in artifacts
        if bool(artifact.metadata_json.get("safe_to_show", False))
        and bool(artifact.metadata_json.get("allowed_for_prompt", False))
    ]


def to_retrieval_item(
    artifact: Artifact,
    text: str,
    matched_terms: list[str],
    score: int,
    max_snippet_chars: int,
) -> KnowledgeRetrievalResultItem:
    metadata = artifact.metadata_json
    return KnowledgeRetrievalResultItem(
        context_artifact_id=artifact.id,
        title=str(metadata.get("title", "")),
        source_ref=str(metadata.get("source_ref", "")),
        score=score,
        matched_terms=matched_terms,
        snippet=snippet_for_terms(text, matched_terms, max_snippet_chars),
        sha256=f"sha256:{artifact.sha256}",
        redaction_applied=bool(metadata.get("redaction_applied", False)),
        allowed_for_prompt=bool(metadata.get("allowed_for_prompt", False)),
    )


def snippet_for_terms(text: str, terms: list[str], max_chars: int) -> str:
    normalized_text = " ".join(text.split())
    if not normalized_text:
        return ""

    lower_text = normalized_text.lower()
    positions = [lower_text.find(term) for term in terms if lower_text.find(term) >= 0]
    start = min(positions) if positions else 0
    if start > 0:
        start = max(0, start - max_chars // 4)
        next_space = normalized_text.find(" ", start)
        if 0 <= next_space < min(len(normalized_text), start + 24):
            start = next_space + 1
    return normalized_text[start : start + max_chars]


def list_knowledge_base_context_artifacts(
    session: Session,
    project_id: uuid.UUID,
    retrieval_usage: dict[uuid.UUID, dict[str, Any]] | None = None,
) -> list[KnowledgeBaseContextArtifactRead]:
    usage = context_artifact_usage(session, project_id)
    retrieval_usage = retrieval_usage or {}
    artifacts = session.scalars(
        select(Artifact)
        .where(
            Artifact.project_id == project_id,
            Artifact.owner_entity_type == "Project",
            Artifact.owner_entity_id == project_id,
            Artifact.artifact_type.in_(CONTEXT_FILE_NAMES.keys()),
        )
        .order_by(Artifact.created_at.asc()),
    ).all()
    return [
        to_context_artifact_read(artifact, usage.get(artifact.id, {}), retrieval_usage.get(artifact.id, {}))
        for artifact in artifacts
    ]


def context_artifact_usage(
    session: Session,
    project_id: uuid.UUID,
) -> dict[uuid.UUID, dict[str, Any]]:
    usage: dict[uuid.UUID, dict[str, Any]] = {}
    ai_tasks = session.scalars(select(AITask).where(AITask.project_id == project_id)).all()
    for ai_task in ai_tasks:
        for artifact_id in ai_task.context_artifact_ids:
            item = usage.setdefault(artifact_id, {"usage_count": 0, "latest_used_at": None})
            item["usage_count"] += 1
            if item["latest_used_at"] is None or ai_task.created_at > item["latest_used_at"]:
                item["latest_used_at"] = ai_task.created_at
    return usage


def knowledge_retrieval_evidence(session: Session, project_id: uuid.UUID) -> list[Artifact]:
    return list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.project_id == project_id,
                Artifact.owner_entity_type == "AITask",
                Artifact.artifact_type == "knowledge_retrieval",
            )
            .order_by(Artifact.created_at.desc(), Artifact.id.desc()),
        ),
    )


def context_artifact_retrieval_usage(
    retrieval_artifacts: list[Artifact],
) -> dict[uuid.UUID, dict[str, Any]]:
    usage: dict[uuid.UUID, dict[str, Any]] = {}
    for artifact in retrieval_artifacts:
        for context_artifact_id in metadata_context_artifact_ids(artifact.metadata_json):
            item = usage.setdefault(context_artifact_id, {"retrieved_count": 0, "latest_retrieved_at": None})
            item["retrieved_count"] += 1
            if item["latest_retrieved_at"] is None or artifact.created_at > item["latest_retrieved_at"]:
                item["latest_retrieved_at"] = artifact.created_at
    return usage


def metadata_context_artifact_ids(metadata: dict[str, Any]) -> list[uuid.UUID]:
    ids: list[uuid.UUID] = []
    for value in metadata.get("used_context_artifact_ids", []):
        try:
            ids.append(uuid.UUID(str(value)))
        except ValueError:
            continue
    return ids


def to_latest_retrieval_read(artifact: Artifact) -> KnowledgeBaseLatestRetrievalRead:
    metadata = artifact.metadata_json
    results = [
        result
        for raw_result in metadata.get("results", [])
        if (result := to_latest_retrieval_result_read(raw_result)) is not None
    ]
    return KnowledgeBaseLatestRetrievalRead(
        ai_task_id=artifact.owner_entity_id,
        retrieval_evidence_artifact_id=artifact.id,
        query_terms=[str(term) for term in metadata.get("query_terms", [])],
        used_context_artifact_ids=metadata_context_artifact_ids(metadata),
        snippet_count=len(results),
        created_at=artifact.created_at,
        results=results,
    )


def to_latest_retrieval_result_read(result: dict[str, Any]) -> KnowledgeBaseRetrievalResultRead | None:
    try:
        context_artifact_id = uuid.UUID(str(result.get("context_artifact_id")))
    except ValueError:
        return None
    return KnowledgeBaseRetrievalResultRead(
        context_artifact_id=context_artifact_id,
        title=str(result.get("title", "")),
        source_ref=str(result.get("source_ref", "")),
        score=int(result.get("score", 0)),
        matched_terms=[str(term) for term in result.get("matched_terms", [])],
        snippet=str(result.get("snippet", "")),
        sha256=str(result.get("sha256", "")),
        redaction_applied=bool(result.get("redaction_applied", False)),
        allowed_for_prompt=bool(result.get("allowed_for_prompt", False)),
    )


def to_context_artifact_read(
    artifact: Artifact,
    usage: dict[str, Any],
    retrieval_usage: dict[str, Any],
) -> KnowledgeBaseContextArtifactRead:
    metadata = artifact.metadata_json
    return KnowledgeBaseContextArtifactRead(
        id=artifact.id,
        title=str(metadata.get("title", "")),
        artifact_type=artifact.artifact_type,
        mime_type=artifact.mime_type,
        source_ref=str(metadata.get("source_ref", "")),
        safe_to_show=bool(metadata.get("safe_to_show", False)),
        redaction_applied=bool(metadata.get("redaction_applied", False)),
        allowed_for_prompt=bool(metadata.get("allowed_for_prompt", False)),
        usage_count=int(usage.get("usage_count", 0)),
        latest_used_at=usage.get("latest_used_at"),
        retrieved_count=int(retrieval_usage.get("retrieved_count", 0)),
        latest_retrieved_at=retrieval_usage.get("latest_retrieved_at"),
    )


def to_read(config: KnowledgeAdapterConfig, *, used_knowledge: bool = False) -> KnowledgeAdapterRead:
    return KnowledgeAdapterRead(
        project_id=config.project_id,
        adapter_name=config.adapter_name,
        status=config.status,
        provider_type=config.provider_type,
        retrieval_mode="deterministic_local" if config.provider_type == "deterministic_local" else None,
        config=config.config_json,
        safety_policy=config.safety_policy_json,
        last_checked_at=config.last_checked_at,
        notes=config.notes,
        used_knowledge=used_knowledge,
    )


def to_tool_definition_read(tool_definition: ToolDefinition) -> ToolDefinitionRead:
    return ToolDefinitionRead(
        id=tool_definition.id,
        project_id=tool_definition.project_id,
        name=tool_definition.name,
        description=tool_definition.description,
        tool_type=tool_definition.tool_type,
        input_schema=tool_definition.input_schema_json,
        output_schema=tool_definition.output_schema_json,
        risk_level=tool_definition.risk_level,
        approval_required=tool_definition.approval_required,
        timeout_seconds=tool_definition.timeout_seconds,
        command_allowlist=tool_definition.command_allowlist_json,
        allowed_working_directories=tool_definition.allowed_working_directories_json,
        forbidden_shell_operators=tool_definition.forbidden_shell_operators_json,
        max_stdout_bytes=tool_definition.max_stdout_bytes,
        max_stderr_bytes=tool_definition.max_stderr_bytes,
        artifact_policy=tool_definition.artifact_policy_json,
        is_mcp_ready=tool_definition.is_mcp_ready,
        mcp_metadata=tool_definition.mcp_metadata_json,
        status=tool_definition.status,
    )
