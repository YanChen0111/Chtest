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


def get_active_prompt_version_by_ref(session: Session, version_ref: str) -> PromptVersion:
    name, version = split_version_ref(version_ref)
    prompt = session.scalar(
        select(PromptVersion).where(
            PromptVersion.name == name,
            PromptVersion.version == version,
            PromptVersion.status == "active",
        ),
    )
    if prompt is None:
        raise PromptVersionNotFoundError
    return prompt


def get_active_skill_version_by_ref(session: Session, version_ref: str) -> SkillVersion:
    name, version = split_version_ref(version_ref)
    skill = session.scalar(
        select(SkillVersion).where(
            SkillVersion.name == name,
            SkillVersion.version == version,
            SkillVersion.status == "active",
        ),
    )
    if skill is None:
        raise SkillVersionNotFoundError
    return skill


def split_version_ref(version_ref: str) -> tuple[str, str]:
    name, separator, version = version_ref.partition(":")
    return name, version if separator and version else "v1"
