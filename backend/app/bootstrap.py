from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from sqlalchemy.orm import Session

from backend.app.modules.projects import service as project_service
from backend.app.modules.prompt_skill import service as prompt_skill_service
from backend.app.modules.prompt_skill.registry_loader import RegistryLoadResult


REPO_ROOT = Path(__file__).resolve().parents[2]

_BOOTSTRAP_LOCK = Lock()
_BOOTSTRAPPED_DATABASE_KEYS: set[str] = set()


@dataclass(frozen=True)
class LocalBootstrapResult:
    database_key: str
    registry: RegistryLoadResult


def ensure_local_database_bootstrap(
    session: Session,
    *,
    root: Path = REPO_ROOT,
    database_key: str = "default",
    force: bool = False,
) -> LocalBootstrapResult | None:
    if not force and database_key in _BOOTSTRAPPED_DATABASE_KEYS:
        return None

    with _BOOTSTRAP_LOCK:
        if not force and database_key in _BOOTSTRAPPED_DATABASE_KEYS:
            return None

        project_service.ensure_local_default_project(session)
        registry_result = prompt_skill_service.seed_builtin_prompt_skill_registry(session, root)

        if not force:
            _BOOTSTRAPPED_DATABASE_KEYS.add(database_key)

        return LocalBootstrapResult(database_key=database_key, registry=registry_result)
