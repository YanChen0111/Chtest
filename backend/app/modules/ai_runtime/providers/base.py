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
class RuntimePolicyBundle:
    agent_name: str
    prompt_name: str
    prompt_version: str
    prompt_hash: str
    prompt_content: str
    input_schema_json: dict[str, Any]
    output_schema_json: dict[str, Any]
    skill_name: str
    skill_version: str
    skill_hash: str
    skill_content: str
    quality_gates: list[Any] = field(default_factory=list)
    forbidden_actions: list[Any] = field(default_factory=list)
    tool_permissions: list[Any] = field(default_factory=list)

    def manifest(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "prompt": {
                "name": self.prompt_name,
                "version": self.prompt_version,
                "hash": self.prompt_hash,
                "content": self.prompt_content,
                "input_schema": self.input_schema_json,
                "output_schema": self.output_schema_json,
            },
            "skill": {
                "name": self.skill_name,
                "version": self.skill_version,
                "hash": self.skill_hash,
                "content": self.skill_content,
                "quality_gates": self.quality_gates,
                "forbidden_actions": self.forbidden_actions,
                "tool_permissions": self.tool_permissions,
            },
        }


@dataclass(frozen=True)
class LLMProviderRequest:
    task_type: str
    model_name: str
    input_json: dict[str, Any]
    context_artifact_ids: list[uuid.UUID] = field(default_factory=list)
    context_manifest: list[dict[str, Any]] = field(default_factory=list)
    runtime_policy: RuntimePolicyBundle | None = None
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
