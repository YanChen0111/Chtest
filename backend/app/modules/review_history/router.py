from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.modules.projects.router import get_session
from backend.app.modules.review_history import service
from backend.app.modules.review_history.schemas import ReviewHistoryListRead, ReviewHistoryRead


router = APIRouter(tags=["review-history"])


def not_found(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


@router.get("/review-history", response_model=ReviewHistoryListRead)
def list_review_history(
    project_id: uuid.UUID,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    related_entity_type: str | None = None,
    related_entity_id: uuid.UUID | None = None,
    limit: int = Query(default=service.DEFAULT_LIMIT, ge=1, le=service.MAX_LIMIT),
    session: Session = Depends(get_session),
) -> ReviewHistoryListRead:
    try:
        items = service.list_review_history(
            session,
            project_id=project_id,
            entity_type=entity_type,
            entity_id=entity_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            limit=limit,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return ReviewHistoryListRead(
        items=[ReviewHistoryRead.model_validate(item) for item in items],
        total=len(items),
    )
