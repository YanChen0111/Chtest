from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, TypeDecorator

from backend.app.models.base import Base
from backend.app.modules.projects.models import TimestampMixin, uuid_pk


class StringListJSON(TypeDecorator[list[str]]):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.ARRAY(String()))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: list[str] | None, dialect) -> list[str]:
        if value is None:
            return []
        return [str(item) for item in value]

    def process_result_value(self, value: list[str] | None, dialect) -> list[str]:
        if value is None:
            return []
        return [str(item) for item in value]


def json_dict_column() -> Mapped[dict[str, Any]]:
    return mapped_column(
        MutableDict.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=dict,
        nullable=False,
    )


def json_list_column() -> Mapped[list[Any]]:
    return mapped_column(
        MutableList.as_mutable(JSON().with_variant(JSONB, "postgresql")),
        default=list,
        nullable=False,
    )


def string_list_column() -> Mapped[list[str]]:
    return mapped_column(MutableList.as_mutable(StringListJSON), default=list, nullable=False)


class PromptVersion(TimestampMixin, Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (UniqueConstraint("name", "version", name="uq_prompt_versions_name_version"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False, default="v1")
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    input_schema_json: Mapped[dict[str, Any]] = json_dict_column()
    output_schema_json: Mapped[dict[str, Any]] = json_dict_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")


class SkillVersion(TimestampMixin, Base):
    __tablename__ = "skill_versions"
    __table_args__ = (UniqueConstraint("name", "version", name="uq_skill_versions_name_version"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False, default="v1")
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    applicable_agents: Mapped[list[str]] = string_list_column()
    content: Mapped[str] = mapped_column(Text, nullable=False)
    quality_gates_json: Mapped[list[Any]] = json_list_column()
    forbidden_actions_json: Mapped[list[Any]] = json_list_column()
    tool_permissions_json: Mapped[list[Any]] = json_list_column()
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
