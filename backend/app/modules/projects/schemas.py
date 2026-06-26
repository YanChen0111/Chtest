from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    default_language: str = "python"
    default_test_type: str = "functional"


class ProjectRead(ProjectCreate):
    id: str
    status: str
