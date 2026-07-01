from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.prompt_skill.registry_loader import RegistryLoadResult, load_builtin_registry


class PromptVersionNotFoundError(LookupError):
    pass


class SkillVersionNotFoundError(LookupError):
    pass


def seed_builtin_prompt_skill_registry(session: Session, root: Path) -> RegistryLoadResult:
    return load_builtin_registry(session, root)


def list_prompt_versions(session: Session) -> list[PromptVersion]:
    return list(session.scalars(select(PromptVersion).order_by(PromptVersion.name, PromptVersion.version)))


def get_prompt_version(session: Session, prompt_version_id: uuid.UUID) -> PromptVersion:
    prompt = session.get(PromptVersion, prompt_version_id)
    if prompt is None:
        raise PromptVersionNotFoundError
    return prompt


def list_skill_versions(session: Session) -> list[SkillVersion]:
    return list(session.scalars(select(SkillVersion).order_by(SkillVersion.name, SkillVersion.version)))


def get_skill_version(session: Session, skill_version_id: uuid.UUID) -> SkillVersion:
    skill = session.get(SkillVersion, skill_version_id)
    if skill is None:
        raise SkillVersionNotFoundError
    return skill
