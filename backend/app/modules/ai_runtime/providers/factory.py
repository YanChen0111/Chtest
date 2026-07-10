from __future__ import annotations

import os
from typing import Protocol

from backend.app.modules.ai_runtime.providers.base import LLMProviderRequest, LLMProviderResponse
from backend.app.modules.ai_runtime.providers.mock_provider import MockLLMProvider
from backend.app.modules.ai_runtime.providers.openai_responses_provider import OpenAIResponsesProvider


class LLMProvider(Protocol):
    def generate(self, request: LLMProviderRequest) -> LLMProviderResponse:
        pass


def create_llm_provider(
    provider_name: str | None = None,
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    wire_api: str | None = None,
    timeout_seconds: int | None = None,
    max_output_tokens: int | None = None,
) -> LLMProvider:
    resolved_provider = normalize_provider_name(provider_name or os.getenv("LLM_PROVIDER") or "mock")
    if resolved_provider == "mock":
        return MockLLMProvider()
    if resolved_provider in {"openai", "openai-compatible", "openai_compatible", "openai_responses", "responses"}:
        return OpenAIResponsesProvider(
            base_url=base_url,
            api_key=api_key,
            wire_api=wire_api,
            timeout_seconds=timeout_seconds,
            max_output_tokens=max_output_tokens,
        )
    raise ValueError(f"Unsupported LLM provider: {resolved_provider}")


def normalize_provider_name(provider_name: str) -> str:
    return provider_name.strip().lower().replace(" ", "-")
