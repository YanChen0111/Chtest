from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.modules.projects.models import Project


def get_project(session: Session, project_id: str) -> Project | None:
    return session.get(Project, project_id)
