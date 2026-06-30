from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.ai_runtime.providers.base import ProviderArtifactPayload
from backend.app.modules.ai_runtime.schemas import (
    AIArtifactSummaryRead,
    AITaskDetailRead,
    AITaskListRead,
    AITaskListItemRead,
    ContextArtifactCreate,
    ContextArtifactListItemRead,
    LLMCallLogSummaryRead,
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
UNSAFE_AI_TASK_ARTIFACT_TYPES = {"raw_llm_output", "error_json"}


class ContextArtifactNotAllowedError(Exception):
    pass


class ContextArtifactTooLargeError(Exception):
    pass


class ContextArtifactSecretDetectedError(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


class AITaskNotFoundError(Exception):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


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


def write_ai_task_artifact(
    session: Session,
    store: LocalArtifactStore,
    ai_task: AITask,
    payload: ProviderArtifactPayload,
    metadata_json: dict | None = None,
) -> Artifact:
    file_path = f"projects/{ai_task.project_id}/ai-tasks/{ai_task.id}/{payload.file_name}"
    write_result = store.write_bytes(file_path, payload.content)
    artifact_metadata = metadata_json or {
        "created_by_component": "AITaskWorker",
        "source_entity_type": "AITask",
        "source_entity_id": str(ai_task.id),
        "safe_to_show": is_ai_task_artifact_safe_to_show(payload),
        "redaction_applied": False,
        "description": f"AI task artifact {payload.file_name}",
    }
    artifact = Artifact(
        project_id=ai_task.project_id,
        owner_entity_type="AITask",
        owner_entity_id=ai_task.id,
        artifact_type=payload.artifact_type,
        file_path=write_result.file_path,
        mime_type=payload.mime_type,
        size_bytes=write_result.size_bytes,
        sha256=write_result.sha256,
        metadata_json=artifact_metadata,
    )
    session.add(artifact)
    session.flush()
    return artifact


def is_ai_task_artifact_safe_to_show(payload: ProviderArtifactPayload) -> bool:
    return payload.artifact_type not in UNSAFE_AI_TASK_ARTIFACT_TYPES


def create_llm_call_log(
    session: Session,
    ai_task: AITask,
    *,
    status: str,
    artifacts_by_name: dict[str, Artifact],
    input_summary_json: dict,
    output_summary_json: dict,
    token_usage_json: dict,
    error_json: dict | None = None,
) -> LLMCallLog:
    llm_call_log = LLMCallLog(
        project_id=ai_task.project_id,
        ai_task_id=ai_task.id,
        prompt_version_id=ai_task.prompt_version_id,
        skill_version_id=ai_task.skill_version_id,
        provider=ai_task.model_provider,
        model_name=ai_task.model_name,
        status=status,
        request_artifact_id=artifact_id_for(artifacts_by_name, "input.json"),
        response_artifact_id=artifact_id_for(artifacts_by_name, "raw_output.json"),
        parsed_artifact_id=artifact_id_for(artifacts_by_name, "parsed_output.json"),
        schema_validation_artifact_id=artifact_id_for(artifacts_by_name, "schema_validation.json"),
        input_summary_json=input_summary_json,
        output_summary_json=output_summary_json,
        token_usage_json=token_usage_json,
        error_json=error_json,
        started_at=ai_task.started_at,
        finished_at=utc_now(),
    )
    session.add(llm_call_log)
    session.flush()
    return llm_call_log


def artifact_id_for(artifacts_by_name: dict[str, Artifact], file_name: str) -> uuid.UUID | None:
    artifact = artifacts_by_name.get(file_name)
    if artifact is None:
        return None
    return artifact.id


def get_ai_task_detail(session: Session, ai_task_id: uuid.UUID) -> AITaskDetailRead:
    ai_task = session.get(AITask, ai_task_id)
    if ai_task is None:
        raise AITaskNotFoundError

    artifacts = list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.owner_entity_type == "AITask",
                Artifact.owner_entity_id == ai_task.id,
            )
            .order_by(Artifact.created_at.asc()),
        ),
    )
    llm_call_logs = list(
        session.scalars(
            select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id).order_by(LLMCallLog.call_index.asc()),
        ),
    )
    context_manifest_artifact = next(
        (artifact for artifact in artifacts if artifact.file_path.endswith("/context_manifest.json")),
        None,
    )
    return AITaskDetailRead(
        id=ai_task.id,
        project_id=ai_task.project_id,
        agent_name=ai_task.agent_name,
        task_type=ai_task.task_type,
        status=ai_task.status,
        prompt_version_id=ai_task.prompt_version_id,
        skill_version_id=ai_task.skill_version_id,
        model_provider=ai_task.model_provider,
        model_name=ai_task.model_name,
        token_usage=ai_task.token_usage_json,
        used_knowledge=bool(ai_task.output_json.get("used_knowledge", False)),
        context_artifact_ids=ai_task.context_artifact_ids,
        used_context_artifact_ids=used_context_artifact_ids(ai_task),
        context_manifest_artifact_id=context_manifest_artifact.id if context_manifest_artifact else None,
        artifacts=[artifact_summary(artifact) for artifact in artifacts],
        llm_call_logs=[llm_call_log_summary(llm_call_log) for llm_call_log in llm_call_logs],
        started_at=ai_task.started_at,
        finished_at=ai_task.finished_at,
    )


def list_project_ai_tasks(session: Session, project_id: uuid.UUID) -> AITaskListRead:
    project = session.get(Project, project_id)
    if project is None:
        raise ProjectNotFoundError

    ai_tasks = list(
        session.scalars(
            select(AITask).where(AITask.project_id == project_id).order_by(AITask.created_at.desc()),
        ),
    )
    return AITaskListRead(
        items=[
            AITaskListItemRead(
                id=ai_task.id,
                project_id=ai_task.project_id,
                agent_name=ai_task.agent_name,
                task_type=ai_task.task_type,
                status=ai_task.status,
                model_provider=ai_task.model_provider,
                model_name=ai_task.model_name,
                context_artifact_ids=ai_task.context_artifact_ids,
                started_at=ai_task.started_at,
                finished_at=ai_task.finished_at,
            )
            for ai_task in ai_tasks
        ],
        total=len(ai_tasks),
    )


def used_context_artifact_ids(ai_task: AITask) -> list[uuid.UUID]:
    raw_ids = ai_task.output_json.get("used_context_artifact_ids", ai_task.context_artifact_ids)
    return [uuid.UUID(str(context_artifact_id)) for context_artifact_id in raw_ids]


def artifact_summary(artifact: Artifact) -> AIArtifactSummaryRead:
    return AIArtifactSummaryRead(
        id=artifact.id,
        artifact_type=artifact.artifact_type,
        file_path=artifact.file_path,
        mime_type=artifact.mime_type,
        size_bytes=artifact.size_bytes,
        sha256=f"sha256:{artifact.sha256}",
        safe_to_show=bool(artifact.metadata_json.get("safe_to_show", False)),
        redaction_applied=bool(artifact.metadata_json.get("redaction_applied", False)),
    )


def llm_call_log_summary(llm_call_log: LLMCallLog) -> LLMCallLogSummaryRead:
    return LLMCallLogSummaryRead(
        id=llm_call_log.id,
        provider=llm_call_log.provider,
        model_name=llm_call_log.model_name,
        call_index=llm_call_log.call_index,
        status=llm_call_log.status,
        request_artifact_id=llm_call_log.request_artifact_id,
        response_artifact_id=llm_call_log.response_artifact_id,
        parsed_artifact_id=llm_call_log.parsed_artifact_id,
        schema_validation_artifact_id=llm_call_log.schema_validation_artifact_id,
        token_usage_json=llm_call_log.token_usage_json,
        latency_ms=llm_call_log.latency_ms,
        error_json=llm_call_log.error_json,
        started_at=llm_call_log.started_at,
        finished_at=llm_call_log.finished_at,
    )
