from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.extension import service
from backend.app.modules.extension.schemas import (
    KnowledgeAdapterRead,
    KnowledgeAdapterUpdate,
    KnowledgeBaseRead,
)
from backend.app.modules.projects.router import get_session


router = APIRouter(tags=["extension"])


def project_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "PROJECT_NOT_FOUND",
            "message": "Project not found.",
            "details": {},
        },
    )


def runtime_not_allowed() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "KNOWLEDGE_ADAPTER_RUNTIME_NOT_ALLOWED",
            "message": "KnowledgeAdapter is a V1 stub and cannot store runtime provider config.",
            "details": {},
        },
    )


@router.get("/projects/{project_id}/knowledge-adapter", response_model=KnowledgeAdapterRead)
def get_knowledge_adapter(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> KnowledgeAdapterRead:
    try:
        return service.read_knowledge_adapter(session, project_id)
    except service.KnowledgeAdapterProjectNotFoundError as exc:
        raise project_not_found() from exc


@router.get("/projects/{project_id}/knowledge-base", response_model=KnowledgeBaseRead)
def get_knowledge_base(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> KnowledgeBaseRead:
    try:
        return service.read_knowledge_base(session, project_id)
    except service.KnowledgeAdapterProjectNotFoundError as exc:
        raise project_not_found() from exc


@router.put("/projects/{project_id}/knowledge-adapter", response_model=KnowledgeAdapterRead)
def put_knowledge_adapter(
    project_id: uuid.UUID,
    data: KnowledgeAdapterUpdate,
    session: Session = Depends(get_session),
) -> KnowledgeAdapterRead:
    try:
        return service.update_knowledge_adapter(session, project_id, data)
    except service.KnowledgeAdapterProjectNotFoundError as exc:
        raise project_not_found() from exc
    except service.KnowledgeAdapterRuntimeNotAllowedError as exc:
        raise runtime_not_allowed() from exc
