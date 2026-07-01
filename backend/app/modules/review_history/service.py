from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import Artifact
from backend.app.modules.projects.models import Project
from backend.app.modules.review_history.models import ReviewHistory


DEFAULT_REVIEWER = "Default User"
MAX_LIMIT = 200
DEFAULT_LIMIT = 50


class ProjectNotFoundError(Exception):
    pass


class EvidenceArtifactInvalidError(Exception):
    def __init__(self, artifact_ids: list[uuid.UUID]) -> None:
        super().__init__("Review history evidence artifacts must exist in the same project.")
        self.artifact_ids = artifact_ids


def append_review_history(
    session: Session,
    *,
    project_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    action: str,
    related_entity_type: str | None = None,
    related_entity_id: uuid.UUID | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    reviewer: str | None = None,
    comment: str | None = None,
    evidence_artifact_ids: list[uuid.UUID] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ReviewHistory:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError

    artifact_ids = evidence_artifact_ids or []
    if artifact_ids:
        valid_artifact_ids = set(
            session.scalars(
                select(Artifact.id).where(
                    Artifact.project_id == project_id,
                    Artifact.id.in_(artifact_ids),
                ),
            ),
        )
        invalid_artifact_ids = [artifact_id for artifact_id in artifact_ids if artifact_id not in valid_artifact_ids]
        if invalid_artifact_ids:
            raise EvidenceArtifactInvalidError(invalid_artifact_ids)

    event = ReviewHistory(
        project_id=project_id,
        entity_type=entity_type,
        entity_id=entity_id,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        action=action,
        from_status=from_status,
        to_status=to_status,
        reviewer=reviewer or DEFAULT_REVIEWER,
        comment=comment,
        evidence_artifact_ids=artifact_ids,
        metadata_json=metadata or {},
    )
    session.add(event)
    session.flush()
    return event


def list_review_history(
    session: Session,
    *,
    project_id: uuid.UUID,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    related_entity_type: str | None = None,
    related_entity_id: uuid.UUID | None = None,
    limit: int = DEFAULT_LIMIT,
) -> list[ReviewHistory]:
    if session.get(Project, project_id) is None:
        raise ProjectNotFoundError

    effective_limit = max(1, min(limit, MAX_LIMIT))
    statement = select(ReviewHistory).where(ReviewHistory.project_id == project_id)
    if entity_type is not None:
        statement = statement.where(ReviewHistory.entity_type == entity_type)
    if entity_id is not None:
        statement = statement.where(ReviewHistory.entity_id == entity_id)
    if related_entity_type is not None:
        statement = statement.where(ReviewHistory.related_entity_type == related_entity_type)
    if related_entity_id is not None:
        statement = statement.where(ReviewHistory.related_entity_id == related_entity_id)
    statement = statement.order_by(ReviewHistory.created_at.desc(), ReviewHistory.id.desc()).limit(effective_limit)
    return list(session.scalars(statement))
