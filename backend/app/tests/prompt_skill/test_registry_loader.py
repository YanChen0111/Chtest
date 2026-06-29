from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.models.base import Base
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.prompt_skill.registry_loader import (
    RegistryContentConflict,
    compute_content_hash,
    discover_builtin_prompt_files,
    discover_builtin_skill_files,
    load_builtin_registry,
    parse_prompt_file,
    parse_skill_file,
)


ROOT = Path(__file__).parents[4]


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_discovers_builtin_prompt_and_skill_files() -> None:
    prompt_files = discover_builtin_prompt_files(ROOT)
    skill_files = discover_builtin_skill_files(ROOT)

    assert len(prompt_files) == 11
    assert len(skill_files) == 9
    assert prompt_files["requirement_review"] == ROOT / "prompts/requirement_review/v1.md"
    assert skill_files["requirement-review-skill"] == ROOT / "skills/requirement-review-skill/v1.md"


def test_parses_prompt_and_skill_contract_fields() -> None:
    prompt = parse_prompt_file(ROOT / "prompts/requirement_review/v1.md")
    skill = parse_skill_file(ROOT / "skills/requirement-review-skill/v1.md")

    assert prompt.name == "requirement_review"
    assert prompt.version == "v1"
    assert prompt.agent_name == "RequirementReviewAgent"
    assert prompt.input_schema_json["type"] == "object"
    assert prompt.output_schema_json["type"] == "object"
    assert prompt.hash == compute_content_hash(prompt.content)

    assert skill.name == "requirement-review-skill"
    assert skill.version == "v1"
    assert skill.applicable_agents == ["RequirementReviewAgent"]
    assert skill.quality_gates_json
    assert skill.forbidden_actions_json
    assert skill.tool_permissions_json
    assert skill.hash == compute_content_hash(skill.content)


def test_loader_rejects_prompt_missing_required_contract_sections(tmp_path: Path) -> None:
    prompt_path = tmp_path / "broken_prompt.md"
    prompt_path.write_text(
        "\n".join(
            [
                "# Prompt: broken_prompt v1",
                "",
                "## Agent",
                "",
                "RequirementReviewAgent",
                "",
                "## Input Schema",
                "",
                '```json\n{"type":"object"}\n```',
                "",
                "## Output Schema",
                "",
                '```json\n{"type":"object"}\n```',
            ],
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_prompt_file(prompt_path)


def test_loader_rejects_skill_missing_required_contract_sections(tmp_path: Path) -> None:
    skill_path = tmp_path / "broken-skill.md"
    skill_path.write_text(
        "\n".join(
            [
                "# Skill: broken-skill v1",
                "",
                "## Applies To",
                "",
                "- RequirementReviewAgent",
                "",
                "## Quality Gates",
                "",
                "- Gate",
                "",
                "## Forbidden Actions",
                "",
                "- Forbidden",
                "",
                "## Tool Permissions",
                "",
                "- None",
            ],
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        parse_skill_file(skill_path)


def test_load_builtin_registry_is_idempotent(session: Session) -> None:
    first_result = load_builtin_registry(session, ROOT)
    second_result = load_builtin_registry(session, ROOT)

    prompts = session.scalars(select(PromptVersion)).all()
    skills = session.scalars(select(SkillVersion)).all()

    assert first_result.created_prompts == 11
    assert first_result.created_skills == 9
    assert second_result.created_prompts == 0
    assert second_result.created_skills == 0
    assert second_result.unchanged_prompts == 11
    assert second_result.unchanged_skills == 9
    assert len(prompts) == 11
    assert len(skills) == 9


def test_loader_rejects_existing_version_with_different_content(session: Session) -> None:
    session.add(
        PromptVersion(
            name="requirement_review",
            version="v1",
            hash="sha256:" + "0" * 64,
            agent_name="RequirementReviewAgent",
            content="# Prompt: requirement_review v1\nchanged",
        ),
    )
    session.commit()

    with pytest.raises(RegistryContentConflict):
        load_builtin_registry(session, ROOT)

    existing = session.scalar(
        select(PromptVersion).where(
            PromptVersion.name == "requirement_review",
            PromptVersion.version == "v1",
        ),
    )

    assert existing is not None
    assert existing.content == "# Prompt: requirement_review v1\nchanged"
    assert len(session.scalars(select(PromptVersion)).all()) == 1
    assert len(session.scalars(select(SkillVersion)).all()) == 0


def test_loader_rejects_existing_skill_version_with_different_content(session: Session) -> None:
    session.add(
        SkillVersion(
            name="requirement-review-skill",
            version="v1",
            hash="sha256:" + "0" * 64,
            applicable_agents=["RequirementReviewAgent"],
            content="# Skill: requirement-review-skill v1\nchanged",
        ),
    )
    session.commit()

    with pytest.raises(RegistryContentConflict):
        load_builtin_registry(session, ROOT)

    existing = session.scalar(
        select(SkillVersion).where(
            SkillVersion.name == "requirement-review-skill",
            SkillVersion.version == "v1",
        ),
    )

    assert existing is not None
    assert existing.content == "# Skill: requirement-review-skill v1\nchanged"
    assert len(session.scalars(select(PromptVersion)).all()) == 0
    assert len(session.scalars(select(SkillVersion)).all()) == 1
