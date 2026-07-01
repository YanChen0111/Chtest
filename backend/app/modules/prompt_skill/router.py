from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.projects.router import get_session
from backend.app.modules.prompt_skill import service
from backend.app.modules.prompt_skill.schemas import (
    PromptVersionListRead,
    PromptVersionRead,
    SkillVersionListRead,
    SkillVersionRead,
)


router = APIRouter(tags=["prompt-skill"])


def prompt_version_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "PROMPT_VERSION_NOT_FOUND",
            "message": "Prompt version not found.",
            "details": {},
        },
    )


def skill_version_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_code": "SKILL_VERSION_NOT_FOUND",
            "message": "Skill version not found.",
            "details": {},
        },
    )


@router.get("/prompt-versions", response_model=PromptVersionListRead)
def list_prompt_versions(session: Session = Depends(get_session)) -> PromptVersionListRead:
    items = service.list_prompt_versions(session)
    return PromptVersionListRead(items=items, total=len(items))


@router.get("/prompt-versions/{prompt_version_id}", response_model=PromptVersionRead)
def get_prompt_version(
    prompt_version_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> PromptVersionRead:
    try:
        return service.get_prompt_version(session, prompt_version_id)
    except service.PromptVersionNotFoundError as exc:
        raise prompt_version_not_found() from exc


@router.get("/skill-versions", response_model=SkillVersionListRead)
def list_skill_versions(session: Session = Depends(get_session)) -> SkillVersionListRead:
    items = service.list_skill_versions(session)
    return SkillVersionListRead(items=items, total=len(items))


@router.get("/skill-versions/{skill_version_id}", response_model=SkillVersionRead)
def get_skill_version(
    skill_version_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> SkillVersionRead:
    try:
        return service.get_skill_version(session, skill_version_id)
    except service.SkillVersionNotFoundError as exc:
        raise skill_version_not_found() from exc
