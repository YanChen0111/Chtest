from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.modules.prompt_skill.registry_loader import RegistryLoadResult, load_builtin_registry


def seed_builtin_prompt_skill_registry(session: Session, root: Path) -> RegistryLoadResult:
    return load_builtin_registry(session, root)
