from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.base import Base
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion


MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0003_prompt_skill_registry.py"


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def load_prompt_skill_migration():
    spec = importlib.util.spec_from_file_location("prompt_skill_migration", MIGRATION_PATH)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def test_prompt_skill_migration_creates_contract_tables() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    migration = load_prompt_skill_migration()

    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        operations = Operations(context)
        original_op = migration.op
        migration.op = operations
        try:
            migration.upgrade()
        finally:
            migration.op = original_op

        inspector = inspect(connection)
        tables = set(inspector.get_table_names())
        prompt_columns = {column["name"] for column in inspector.get_columns("prompt_versions")}
        skill_columns = {column["name"] for column in inspector.get_columns("skill_versions")}

    assert {"prompt_versions", "skill_versions"}.issubset(tables)
    assert {
        "id",
        "name",
        "version",
        "hash",
        "agent_name",
        "content",
        "input_schema_json",
        "output_schema_json",
        "status",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(prompt_columns)
    assert {
        "id",
        "name",
        "version",
        "hash",
        "applicable_agents",
        "content",
        "quality_gates_json",
        "forbidden_actions_json",
        "tool_permissions_json",
        "status",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(skill_columns)


def test_prompt_version_persists_schema_and_trace_fields(session: Session) -> None:
    prompt = PromptVersion(
        name="requirement_review",
        version="v1",
        hash="sha256:" + "a" * 64,
        agent_name="RequirementReviewAgent",
        content="# Prompt: requirement_review v1",
        input_schema_json={"type": "object", "required": ["requirement"]},
        output_schema_json={"type": "object", "required": ["scores", "issues"]},
    )

    session.add(prompt)
    session.commit()
    session.refresh(prompt)

    assert prompt.id is not None
    assert prompt.status == "active"
    assert prompt.input_schema_json["required"] == ["requirement"]
    assert prompt.output_schema_json["required"] == ["scores", "issues"]


def test_skill_version_persists_quality_gates_and_permissions(session: Session) -> None:
    skill = SkillVersion(
        name="requirement-review-skill",
        version="v1",
        hash="sha256:" + "b" * 64,
        applicable_agents=["RequirementReviewAgent"],
        content="# Skill: requirement-review-skill v1",
        quality_gates_json=["Every issue must reference requirement text."],
        forbidden_actions_json=["Do not claim external evidence when use_knowledge=false."],
        tool_permissions_json=["KnowledgeAdapter.search_context optional"],
    )

    session.add(skill)
    session.commit()
    session.refresh(skill)

    assert skill.id is not None
    assert skill.status == "active"
    assert skill.applicable_agents == ["RequirementReviewAgent"]
    assert skill.quality_gates_json == ["Every issue must reference requirement text."]
    assert skill.forbidden_actions_json == ["Do not claim external evidence when use_knowledge=false."]
    assert skill.tool_permissions_json == ["KnowledgeAdapter.search_context optional"]


def test_prompt_and_skill_versions_are_unique_by_name_and_version(session: Session) -> None:
    session.add_all(
        [
            PromptVersion(
                name="requirement_review",
                version="v1",
                hash="sha256:" + "c" * 64,
                agent_name="RequirementReviewAgent",
                content="first",
            ),
            PromptVersion(
                name="requirement_review",
                version="v1",
                hash="sha256:" + "d" * 64,
                agent_name="RequirementReviewAgent",
                content="duplicate",
            ),
        ],
    )

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
    session.add_all(
        [
            SkillVersion(
                name="requirement-review-skill",
                version="v1",
                hash="sha256:" + "e" * 64,
                content="first",
            ),
            SkillVersion(
                name="requirement-review-skill",
                version="v1",
                hash="sha256:" + "f" * 64,
                content="duplicate",
            ),
        ],
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_prompt_skill_json_fields_track_in_place_updates(session: Session) -> None:
    prompt = PromptVersion(
        name="case_generation",
        version="v1",
        hash="sha256:" + "1" * 64,
        agent_name="CaseGenerationAgent",
        content="# Prompt",
        output_schema_json={"required": ["cases"]},
    )
    skill = SkillVersion(
        name="test-case-generation-skill",
        version="v1",
        hash="sha256:" + "2" * 64,
        content="# Skill",
        quality_gates_json=["Cases must have steps."],
    )

    session.add_all([prompt, skill])
    session.commit()

    prompt.output_schema_json["properties"] = {"cases": {"type": "array"}}
    skill.quality_gates_json.append("Cases must have expected results.")
    session.commit()
    session.expire_all()

    refreshed_prompt = session.get(PromptVersion, prompt.id)
    refreshed_skill = session.get(SkillVersion, skill.id)

    assert refreshed_prompt is not None
    assert refreshed_skill is not None
    assert refreshed_prompt.output_schema_json["properties"]["cases"]["type"] == "array"
    assert refreshed_skill.quality_gates_json == [
        "Cases must have steps.",
        "Cases must have expected results.",
    ]
