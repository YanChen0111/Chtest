from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.ai_runtime.service import CONTEXT_FILE_NAMES
from backend.app.modules.extension.models import KnowledgeAdapterConfig
from backend.app.modules.extension.schemas import (
    KnowledgeAdapterRead,
    KnowledgeAdapterUpdate,
    KnowledgeBaseContextArtifactRead,
    KnowledgeBaseRead,
)
from backend.app.modules.projects.models import Project


ALLOWED_PROVIDER_TYPES = {"none", "stub"}
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


def read_knowledge_adapter(session: Session, project_id: uuid.UUID) -> KnowledgeAdapterRead:
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
            used_knowledge=False,
        )
    return to_read(config)


def read_knowledge_base(session: Session, project_id: uuid.UUID) -> KnowledgeBaseRead:
    get_project_or_raise(session, project_id)
    return KnowledgeBaseRead(
        project_id=project_id,
        knowledge_adapter=read_knowledge_adapter(session, project_id),
        context_artifacts=list_knowledge_base_context_artifacts(session, project_id),
        non_goals=list(KNOWLEDGE_BASE_NON_GOALS),
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


def list_knowledge_base_context_artifacts(
    session: Session,
    project_id: uuid.UUID,
) -> list[KnowledgeBaseContextArtifactRead]:
    usage = context_artifact_usage(session, project_id)
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
    return [to_context_artifact_read(artifact, usage.get(artifact.id, {})) for artifact in artifacts]


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


def to_context_artifact_read(
    artifact: Artifact,
    usage: dict[str, Any],
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
    )


def to_read(config: KnowledgeAdapterConfig) -> KnowledgeAdapterRead:
    return KnowledgeAdapterRead(
        project_id=config.project_id,
        adapter_name=config.adapter_name,
        status=config.status,
        provider_type=config.provider_type,
        config=config.config_json,
        safety_policy=config.safety_policy_json,
        last_checked_at=config.last_checked_at,
        notes=config.notes,
        used_knowledge=False,
    )
