from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime import service
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.ai_runtime.schemas import (
    AITaskDetailRead,
    AITaskListRead,
    ContextArtifactCreate,
    ContextArtifactListRead,
    ContextArtifactRead,
)
from backend.app.modules.projects.router import get_session


ARTIFACT_ROOT = os.getenv("CHTEST_ARTIFACT_ROOT", "artifacts")

router = APIRouter(tags=["ai-runtime"])


def get_artifact_store() -> LocalArtifactStore:
    return LocalArtifactStore(root=ARTIFACT_ROOT)


def project_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "PROJECT_NOT_FOUND",
            "message": "Project not found.",
            "details": {},
        },
    )


def ai_task_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "AI_TASK_NOT_FOUND",
            "message": "AI task not found.",
            "details": {},
        },
    )


def context_artifact_not_allowed() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CONTEXT_ARTIFACT_NOT_ALLOWED",
            "message": "Context artifact type or MIME type is not allowed.",
            "details": {},
        },
    )


def context_artifact_too_large() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CONTEXT_ARTIFACT_TOO_LARGE",
            "message": "Context artifact exceeds the V1 size limit.",
            "details": {},
        },
    )


def context_artifact_secret_detected() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CONTEXT_ARTIFACT_SECRET_DETECTED",
            "message": "Context artifact content contains a high-risk secret.",
            "details": {},
        },
    )


@router.post(
    "/context-artifacts",
    response_model=ContextArtifactRead,
    status_code=status.HTTP_201_CREATED,
)
def create_context_artifact(
    data: ContextArtifactCreate,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> ContextArtifactRead:
    try:
        artifact = service.create_context_artifact(session, store, data)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc
    except service.ContextArtifactNotAllowedError as exc:
        raise context_artifact_not_allowed() from exc
    except service.ContextArtifactTooLargeError as exc:
        raise context_artifact_too_large() from exc
    except service.ContextArtifactSecretDetectedError as exc:
        raise context_artifact_secret_detected() from exc

    return context_artifact_read(artifact)


@router.get(
    "/projects/{project_id}/context-artifacts",
    response_model=ContextArtifactListRead,
)
def list_context_artifacts(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ContextArtifactListRead:
    try:
        items = service.list_context_artifacts(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc
    return ContextArtifactListRead(items=items, total=len(items))


@router.get("/ai-tasks/{ai_task_id}", response_model=AITaskDetailRead)
def get_ai_task(
    ai_task_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> AITaskDetailRead:
    try:
        return service.get_ai_task_detail(session, ai_task_id)
    except service.AITaskNotFoundError as exc:
        raise ai_task_not_found() from exc


@router.get("/projects/{project_id}/ai-tasks", response_model=AITaskListRead)
def list_project_ai_tasks(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> AITaskListRead:
    try:
        return service.list_project_ai_tasks(session, project_id)
    except service.ProjectNotFoundError as exc:
        raise project_not_found() from exc


def context_artifact_read(artifact: Artifact) -> ContextArtifactRead:
    return ContextArtifactRead(
        id=artifact.id,
        project_id=artifact.project_id,
        owner_entity_type=artifact.owner_entity_type,
        owner_entity_id=artifact.owner_entity_id,
        artifact_type=artifact.artifact_type,
        mime_type=artifact.mime_type,
        file_path=artifact.file_path,
        sha256=f"sha256:{artifact.sha256}",
        metadata=artifact.metadata_json,
    )
