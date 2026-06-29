from __future__ import annotations

import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.ai_runtime.schemas import (
    ContextArtifactCreate,
    ContextArtifactListItemRead,
)
from backend.app.modules.projects.models import Project


MAX_CONTEXT_ARTIFACT_BYTES = 1024 * 1024
CONTEXT_ARTIFACT_MIME_TYPES = {
    "context_markdown": {"text/markdown"},
    "context_text": {"text/plain"},
    "context_json": {"application/json"},
    "context_yaml": {"application/yaml", "text/yaml"},
    "context_openapi": {"application/yaml", "application/json", "text/yaml"},
}
CONTEXT_FILE_NAMES = {
    "context_markdown": "content.md",
    "context_text": "content.txt",
    "context_json": "content.json",
    "context_yaml": "content.yaml",
    "context_openapi": "openapi.yaml",
}
SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bghp_[A-Za-z0-9_]{8,}"),
    re.compile(r"\bAKIA[0-9A-Z]{8,}"),
    re.compile(r"authorization\s*:\s*bearer\s+\S+", re.IGNORECASE),
    re.compile(r"cookie\s*:\s*\S+", re.IGNORECASE),
    re.compile(r"\b(password|token|secret|api_key)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    re.compile(r"\b1[3-9]\d{9}\b"),
    re.compile(r"\b\d{17}[\dXx]\b"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\bpostgres(?:ql)?://\S+", re.IGNORECASE),
    re.compile(r"\bmysql://\S+", re.IGNORECASE),
    re.compile(r"\bmongodb(?:\+srv)?://\S+", re.IGNORECASE),
    re.compile(r"\bprod(?:uction)?[.-][A-Za-z0-9.-]+\b", re.IGNORECASE),
]


class ContextArtifactNotAllowedError(Exception):
    pass


class ContextArtifactTooLargeError(Exception):
    pass


class ContextArtifactSecretDetectedError(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


def create_context_artifact(
    session: Session,
    store: LocalArtifactStore,
    data: ContextArtifactCreate,
) -> Artifact:
    project = session.get(Project, data.project_id)
    if project is None:
        raise ProjectNotFoundError

    validate_context_artifact_input(data)
    content_bytes = data.content.encode("utf-8")
    artifact_id = uuid.uuid4()
    file_name = CONTEXT_FILE_NAMES[data.artifact_type]
    file_path = f"projects/{project.id}/context-artifacts/{artifact_id}/{file_name}"
    write_result = store.write_bytes(file_path, content_bytes)
    metadata_json = {
        "created_by_component": "ContextArtifactAPI",
        "source_entity_type": "Project",
        "source_entity_id": str(project.id),
        "description": f"Context artifact {data.title}",
        "title": data.title,
        "source_ref": data.source_ref,
        "safe_to_show": True,
        "redaction_applied": False,
        "redaction_report_artifact_id": None,
        "allowed_for_prompt": True,
    }
    artifact = Artifact(
        id=artifact_id,
        project_id=project.id,
        owner_entity_type="Project",
        owner_entity_id=project.id,
        artifact_type=data.artifact_type,
        file_path=write_result.file_path,
        mime_type=data.mime_type,
        size_bytes=write_result.size_bytes,
        sha256=write_result.sha256,
        metadata_json=metadata_json,
    )
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return artifact


def list_context_artifacts(session: Session, project_id: uuid.UUID) -> list[ContextArtifactListItemRead]:
    project = session.get(Project, project_id)
    if project is None:
        raise ProjectNotFoundError

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
        ContextArtifactListItemRead(
            id=artifact.id,
            title=str(artifact.metadata_json.get("title", "")),
            artifact_type=artifact.artifact_type,
            mime_type=artifact.mime_type,
            safe_to_show=bool(artifact.metadata_json.get("safe_to_show", False)),
            redaction_applied=bool(artifact.metadata_json.get("redaction_applied", False)),
        )
        for artifact in artifacts
    ]


def validate_context_artifact_input(data: ContextArtifactCreate) -> None:
    if data.mime_type not in CONTEXT_ARTIFACT_MIME_TYPES.get(data.artifact_type, set()):
        raise ContextArtifactNotAllowedError

    content_bytes = data.content.encode("utf-8")
    if len(content_bytes) > MAX_CONTEXT_ARTIFACT_BYTES:
        raise ContextArtifactTooLargeError

    if has_high_risk_secret("\n".join([data.title, data.source_ref, data.content])):
        raise ContextArtifactSecretDetectedError


def has_high_risk_secret(content: str) -> bool:
    return any(pattern.search(content) for pattern in SECRET_PATTERNS)
