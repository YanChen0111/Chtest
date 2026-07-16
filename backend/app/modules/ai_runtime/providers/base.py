from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Literal


ProviderMode = Literal["success", "provider_error", "schema_invalid", "timeout"]
ProviderStatus = Literal["succeeded", "failed", "timeout", "schema_invalid"]


class LLMProviderError(RuntimeError):
    pass


class LLMProviderTimeoutError(TimeoutError):
    pass


@dataclass(frozen=True)
class LLMProviderRequest:
    task_type: str
    model_name: str
    input_json: dict[str, Any]
    context_artifact_ids: list[uuid.UUID] = field(default_factory=list)
    context_manifest: list[dict[str, Any]] = field(default_factory=list)
    mode: ProviderMode = "success"


@dataclass(frozen=True)
class ProviderArtifactPayload:
    artifact_type: str
    file_name: str
    mime_type: str
    content: bytes


@dataclass(frozen=True)
class LLMProviderResponse:
    provider: str
    model_name: str
    status: ProviderStatus
    output_json: dict[str, Any]
    artifacts: list[ProviderArtifactPayload]
    error_json: dict[str, Any] | None = None
    token_usage_json: dict[str, int] = field(default_factory=dict)
