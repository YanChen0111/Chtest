from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion


class RegistryLoaderError(ValueError):
    pass


class RegistryContentConflict(RegistryLoaderError):
    pass


@dataclass(frozen=True)
class ParsedPrompt:
    name: str
    version: str
    hash: str
    agent_name: str
    content: str
    input_schema_json: dict[str, Any]
    output_schema_json: dict[str, Any]


@dataclass(frozen=True)
class ParsedSkill:
    name: str
    version: str
    hash: str
    applicable_agents: list[str]
    content: str
    quality_gates_json: list[str]
    forbidden_actions_json: list[str]
    tool_permissions_json: list[str]


@dataclass(frozen=True)
class RegistryLoadResult:
    created_prompts: int = 0
    unchanged_prompts: int = 0
    created_skills: int = 0
    unchanged_skills: int = 0


def compute_content_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def discover_builtin_prompt_files(root: Path) -> dict[str, Path]:
    return _discover_version_files(root / "prompts")


def discover_builtin_skill_files(root: Path) -> dict[str, Path]:
    return _discover_version_files(root / "skills")


def parse_prompt_file(path: Path) -> ParsedPrompt:
    content = path.read_text(encoding="utf-8")
    title_match = re.search(r"^# Prompt: ([a-z0-9_]+) (v[0-9]+)\s*$", content, re.MULTILINE)
    if title_match is None:
        raise RegistryLoaderError(f"Invalid prompt title: {path}")

    for required_section in ("Purpose", "Instructions", "Failure Output"):
        _section_body(content, required_section)

    return ParsedPrompt(
        name=title_match.group(1),
        version=title_match.group(2),
        hash=compute_content_hash(content),
        agent_name=_section_body(content, "Agent"),
        content=content,
        input_schema_json=_json_section(content, "Input Schema"),
        output_schema_json=_json_section(content, "Output Schema"),
    )


def parse_skill_file(path: Path) -> ParsedSkill:
    content = path.read_text(encoding="utf-8")
    title_match = re.search(r"^# Skill: ([a-z0-9-]+) (v[0-9]+)\s*$", content, re.MULTILINE)
    if title_match is None:
        raise RegistryLoaderError(f"Invalid skill title: {path}")

    for required_section in ("Methodology", "Input Contract", "Output Contract"):
        _section_body(content, required_section)

    return ParsedSkill(
        name=title_match.group(1),
        version=title_match.group(2),
        hash=compute_content_hash(content),
        applicable_agents=_bullet_items(content, "Applies To"),
        content=content,
        quality_gates_json=_bullet_items(content, "Quality Gates"),
        forbidden_actions_json=_bullet_items(content, "Forbidden Actions"),
        tool_permissions_json=_bullet_items(content, "Tool Permissions"),
    )


def load_builtin_registry(session: Session, root: Path) -> RegistryLoadResult:
    created_prompts = 0
    unchanged_prompts = 0
    created_skills = 0
    unchanged_skills = 0
    parsed_prompts = [parse_prompt_file(path) for path in discover_builtin_prompt_files(root).values()]
    parsed_skills = [parse_skill_file(path) for path in discover_builtin_skill_files(root).values()]

    for parsed_prompt in parsed_prompts:
        existing_prompt = _find_prompt(session, parsed_prompt.name, parsed_prompt.version)
        if existing_prompt is not None and (
            existing_prompt.hash != parsed_prompt.hash or existing_prompt.content != parsed_prompt.content
        ):
            raise RegistryContentConflict(
                f"PromptVersion {parsed_prompt.name}:{parsed_prompt.version} already exists with different content",
            )

    for parsed_skill in parsed_skills:
        existing_skill = _find_skill(session, parsed_skill.name, parsed_skill.version)
        if existing_skill is not None and (
            existing_skill.hash != parsed_skill.hash or existing_skill.content != parsed_skill.content
        ):
            raise RegistryContentConflict(
                f"SkillVersion {parsed_skill.name}:{parsed_skill.version} already exists with different content",
            )

    for parsed_prompt in parsed_prompts:
        existing_prompt = _find_prompt(session, parsed_prompt.name, parsed_prompt.version)
        if existing_prompt is None:
            session.add(
                PromptVersion(
                    name=parsed_prompt.name,
                    version=parsed_prompt.version,
                    hash=parsed_prompt.hash,
                    agent_name=parsed_prompt.agent_name,
                    content=parsed_prompt.content,
                    input_schema_json=parsed_prompt.input_schema_json,
                    output_schema_json=parsed_prompt.output_schema_json,
                ),
            )
            created_prompts += 1
        else:
            unchanged_prompts += 1

    for parsed_skill in parsed_skills:
        existing_skill = _find_skill(session, parsed_skill.name, parsed_skill.version)
        if existing_skill is None:
            session.add(
                SkillVersion(
                    name=parsed_skill.name,
                    version=parsed_skill.version,
                    hash=parsed_skill.hash,
                    applicable_agents=parsed_skill.applicable_agents,
                    content=parsed_skill.content,
                    quality_gates_json=parsed_skill.quality_gates_json,
                    forbidden_actions_json=parsed_skill.forbidden_actions_json,
                    tool_permissions_json=parsed_skill.tool_permissions_json,
                ),
            )
            created_skills += 1
        else:
            unchanged_skills += 1

    session.commit()
    return RegistryLoadResult(
        created_prompts=created_prompts,
        unchanged_prompts=unchanged_prompts,
        created_skills=created_skills,
        unchanged_skills=unchanged_skills,
    )


def _discover_version_files(base: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in sorted(base.glob("*/v1.md")):
        files[path.parent.name] = path
    return files


def _section_body(content: str, section: str) -> str:
    pattern = rf"^## {re.escape(section)}\s*(.*?)\n(?=## |\Z)"
    match = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
    if match is None:
        raise RegistryLoaderError(f"Missing section: {section}")
    body = match.group(1).strip()
    if not body:
        raise RegistryLoaderError(f"Empty section: {section}")
    return body


def _json_section(content: str, section: str) -> dict[str, Any]:
    body = _section_body(content, section)
    match = re.search(r"```json\s*(.*?)\s*```", body, flags=re.DOTALL)
    if match is None:
        raise RegistryLoaderError(f"Missing JSON block in section: {section}")
    parsed = json.loads(match.group(1))
    if not isinstance(parsed, dict):
        raise RegistryLoaderError(f"Section must parse as object: {section}")
    return parsed


def _bullet_items(content: str, section: str) -> list[str]:
    body = _section_body(content, section)
    items = [line.removeprefix("- ").strip() for line in body.splitlines() if line.startswith("- ")]
    if not items:
        raise RegistryLoaderError(f"Section must contain bullet items: {section}")
    return items


def _find_prompt(session: Session, name: str, version: str) -> PromptVersion | None:
    return session.scalar(
        select(PromptVersion).where(PromptVersion.name == name, PromptVersion.version == version),
    )


def _find_skill(session: Session, name: str, version: str) -> SkillVersion | None:
    return session.scalar(
        select(SkillVersion).where(SkillVersion.name == name, SkillVersion.version == version),
    )
