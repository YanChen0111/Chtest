from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.app.bootstrap import ensure_local_database_bootstrap
from backend.app.models.base import Base
from backend.app.modules.projects.models import Project
from backend.app.modules.projects.service import DEFAULT_FRONTEND_PROJECT_ID
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion


ROOT = Path(__file__).parents[4]


def test_local_bootstrap_seeds_default_project_and_builtin_prompt_skill_registry() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        first_result = ensure_local_database_bootstrap(
            session,
            root=ROOT,
            database_key="local-bootstrap-test",
            force=True,
        )
        second_result = ensure_local_database_bootstrap(
            session,
            root=ROOT,
            database_key="local-bootstrap-test",
            force=True,
        )

        default_project = session.get(Project, DEFAULT_FRONTEND_PROJECT_ID)
        prompt_count = session.scalar(select(func.count(PromptVersion.id)))
        skill_count = session.scalar(select(func.count(SkillVersion.id)))

    assert first_result is not None
    assert first_result.registry.created_prompts == 13
    assert first_result.registry.created_skills == 11
    assert second_result is not None
    assert second_result.registry.created_prompts == 0
    assert second_result.registry.created_skills == 0
    assert second_result.registry.unchanged_prompts == 13
    assert second_result.registry.unchanged_skills == 11
    assert default_project is not None
    assert prompt_count == 13
    assert skill_count == 11
