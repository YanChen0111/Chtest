from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.ai_runtime.providers.base import (
    LLMProviderError,
    LLMProviderRequest,
    LLMProviderTimeoutError,
    ProviderArtifactPayload,
)
from backend.app.modules.ai_runtime.providers.mock_provider import MockLLMProvider
from backend.app.workers.enqueue import AIQueueJob


def run_ai_task(
    session: Session,
    store: LocalArtifactStore,
    job: AIQueueJob | None,
    provider: MockLLMProvider | None = None,
) -> None:
    if job is None:
        return

    ai_task = session.get(AITask, job.ai_task_id)
    if ai_task is None or ai_task.status == "cancelled":
        return
    if ai_task.status != "pending":
        raise ValueError("AI task must be pending before worker start.")

    provider = provider or MockLLMProvider()
    ai_task.status = "running"
    ai_task.started_at = service.utc_now()
    session.add(ai_task)
    session.commit()
    session.refresh(ai_task)

    request = LLMProviderRequest(
        task_type=ai_task.task_type,
        model_name=ai_task.model_name,
        input_json=ai_task.input_json,
        context_artifact_ids=ai_task.context_artifact_ids,
        context_manifest=list(ai_task.input_json.get("context_manifest", [])),
        mode=str(ai_task.input_json.get("mock_mode", "success")),
    )
    try:
        request_artifacts_by_name = write_request_artifacts(session, store, ai_task)
        session.commit()
    except OSError as exc:
        mark_artifact_write_failed(session, ai_task.id, exc)
        return

    try:
        response = provider.generate(request)
    except LLMProviderTimeoutError as exc:
        error_json = {
            "error_code": "MOCK_PROVIDER_TIMEOUT",
            "message": str(exc),
            "recoverable": True,
        }
        try:
            artifacts_by_name = dict(request_artifacts_by_name)
            artifacts_by_name.update(write_error_artifact(session, store, ai_task, error_json))
        except OSError as write_exc:
            mark_artifact_write_failed(session, ai_task.id, write_exc, request_artifacts_by_name)
            return
        finish_failed_task(session, ai_task, artifacts_by_name, "timeout", error_json)
        return
    except LLMProviderError as exc:
        error_json = {
            "error_code": "MOCK_PROVIDER_ERROR",
            "message": str(exc),
            "recoverable": True,
        }
        try:
            artifacts_by_name = dict(request_artifacts_by_name)
            artifacts_by_name.update(write_error_artifact(session, store, ai_task, error_json))
        except OSError as write_exc:
            mark_artifact_write_failed(session, ai_task.id, write_exc, request_artifacts_by_name)
            return
        finish_failed_task(session, ai_task, artifacts_by_name, "failed", error_json)
        return

    try:
        artifacts_by_name = dict(request_artifacts_by_name)
        artifacts_by_name.update(write_provider_artifacts(session, store, ai_task, response.artifacts, artifacts_by_name))
        if response.status == "schema_invalid" and response.error_json is not None:
            artifacts_by_name.update(write_error_artifact(session, store, ai_task, response.error_json))
    except OSError as exc:
        mark_artifact_write_failed(session, ai_task.id, exc, request_artifacts_by_name)
        return

    if response.status == "schema_invalid":
        ai_task.status = "failed"
        ai_task.error_json = response.error_json
    else:
        ai_task.status = "succeeded"
        ai_task.output_json = response.output_json
        ai_task.token_usage_json = response.token_usage_json

    ai_task.finished_at = service.utc_now()
    service.create_llm_call_log(
        session,
        ai_task,
        status=response.status,
        artifacts_by_name=artifacts_by_name,
        input_summary_json={"task_type": ai_task.task_type, "model_name": ai_task.model_name},
        output_summary_json=response.output_json,
        token_usage_json=response.token_usage_json,
        error_json=response.error_json,
    )
    session.add(ai_task)
    session.commit()


def write_request_artifacts(
    session: Session,
    store: LocalArtifactStore,
    ai_task: AITask,
) -> dict[str, Artifact]:
    payloads = [
        ProviderArtifactPayload(
            artifact_type="input_json",
            file_name="input.json",
            mime_type="application/json",
            content=json.dumps(ai_task.input_json, ensure_ascii=False, sort_keys=True).encode("utf-8"),
        ),
    ]
    if ai_task.context_artifact_ids:
        payloads.append(
            ProviderArtifactPayload(
                artifact_type="input_json",
                file_name="context_manifest.json",
                mime_type="application/json",
                content=json.dumps(
                    {
                        "context_artifact_ids": [
                            str(context_artifact_id) for context_artifact_id in ai_task.context_artifact_ids
                        ],
                        "context_manifest": list(ai_task.input_json.get("context_manifest", [])),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ).encode("utf-8"),
            ),
        )
    return write_provider_artifacts(session, store, ai_task, payloads)


def write_provider_artifacts(
    session: Session,
    store: LocalArtifactStore,
    ai_task: AITask,
    payloads: list[ProviderArtifactPayload],
    existing_artifacts_by_name: dict[str, Artifact] | None = None,
) -> dict[str, Artifact]:
    existing_artifacts_by_name = existing_artifacts_by_name or {}
    artifacts_by_name: dict[str, Artifact] = {}
    for payload in payloads:
        if payload.file_name in existing_artifacts_by_name:
            continue
        artifacts_by_name[payload.file_name] = service.write_ai_task_artifact(session, store, ai_task, payload)
    return artifacts_by_name


def mark_artifact_write_failed(
    session: Session,
    ai_task_id: uuid.UUID,
    exc: OSError,
    artifacts_by_name: dict[str, Artifact] | None = None,
) -> None:
    session.rollback()
    ai_task = session.get(AITask, ai_task_id)
    if ai_task is None:
        return

    error_json = {
        "error_code": "ARTIFACT_WRITE_FAILED",
        "message": str(exc),
        "recoverable": True,
    }
    ai_task.status = "failed"
    ai_task.error_json = error_json
    ai_task.finished_at = service.utc_now()
    service.create_llm_call_log(
        session,
        ai_task,
        status="failed",
        artifacts_by_name=artifacts_by_name or {},
        input_summary_json={"task_type": ai_task.task_type, "model_name": ai_task.model_name},
        output_summary_json={},
        token_usage_json={},
        error_json=error_json,
    )
    session.add(ai_task)
    session.commit()


def write_error_artifact(
    session: Session,
    store: LocalArtifactStore,
    ai_task: AITask,
    error_json: dict,
) -> dict[str, Artifact]:
    payload = ProviderArtifactPayload(
        artifact_type="error_json",
        file_name="error.json",
        mime_type="application/json",
        content=json.dumps(error_json, sort_keys=True).encode("utf-8"),
    )
    artifact = service.write_ai_task_artifact(session, store, ai_task, payload)
    return {payload.file_name: artifact}


def finish_failed_task(
    session: Session,
    ai_task: AITask,
    artifacts_by_name: dict[str, Artifact],
    llm_status: str,
    error_json: dict,
) -> None:
    ai_task.status = "failed"
    ai_task.error_json = error_json
    ai_task.finished_at = service.utc_now()
    service.create_llm_call_log(
        session,
        ai_task,
        status=llm_status,
        artifacts_by_name=artifacts_by_name,
        input_summary_json={"task_type": ai_task.task_type, "model_name": ai_task.model_name},
        output_summary_json={},
        token_usage_json={},
        error_json=error_json,
    )
    session.add(ai_task)
    session.commit()
