from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any

from backend.app.modules.ai_runtime.model_config import ModelConnectionConfigError, load_model_connection_config
from backend.app.modules.ai_runtime.providers.base import (
    LLMProviderError,
    LLMProviderRequest,
    LLMProviderResponse,
    LLMProviderTimeoutError,
    ProviderArtifactPayload,
)


class OpenAIResponsesProvider:
    provider = "openai"
    network_required = True
    deterministic = False

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        wire_api: str | None = None,
        timeout_seconds: int | None = None,
        max_output_tokens: int | None = None,
    ) -> None:
        try:
            local_config = (
                load_model_connection_config()
                if base_url is None or api_key is None
                else None
            )
        except ModelConnectionConfigError as exc:
            raise LLMProviderError("OpenAI Responses provider model connection config is invalid.") from exc
        self.base_url = (
            base_url
            or (local_config.base_url if local_config else None)
            or os.getenv("LLM_BASE_URL")
            or "https://api.openai.com/v1"
        )
        self.api_key = (
            api_key
            or (local_config.api_key if local_config else None)
            or os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        self.wire_api = normalize_wire_api(
            wire_api
            or (local_config.wire_api if local_config else None)
            or os.getenv("LLM_WIRE_API")
            or "responses",
        )
        self.timeout_seconds = timeout_seconds or int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))
        self.max_output_tokens = max_output_tokens

    def generate(self, request: LLMProviderRequest) -> LLMProviderResponse:
        if not self.api_key:
            raise LLMProviderError("OpenAI Responses provider requires LLM_API_KEY or OPENAI_API_KEY.")

        raw_artifacts: list[ProviderArtifactPayload] = []
        adapter = "openai_responses"
        response_json: dict[str, Any]
        response_text: str
        if self.wire_api == "chat_completions":
            response_json = self._post_json(self._chat_payload(request), self._chat_completions_url())
            response_text = self._extract_chat_completion_text(response_json)
            adapter = "openai_chat_completions"
        else:
            try:
                response_json = self._post_json(self._responses_payload(request), self._responses_url())
            except (LLMProviderError, LLMProviderTimeoutError) as exc:
                if not self._can_fallback_to_chat_completions(exc):
                    raise
                raw_artifacts.append(
                    self._json_artifact(
                        "raw_llm_output",
                        "raw_responses_error.json",
                        {
                            "error_code": "OPENAI_RESPONSES_RECOVERABLE_ERROR",
                            "message": str(exc),
                            "recoverable": True,
                        },
                    ),
                )
                response_json = self._post_json(self._chat_payload(request), self._chat_completions_url())
                response_text = self._extract_chat_completion_text(response_json)
                adapter = "openai_chat_completions_fallback"
            else:
                response_text = self._extract_response_text(response_json)
                if not response_text.strip():
                    raw_artifacts.append(
                        self._json_artifact(
                            "raw_llm_output",
                            "raw_responses_output.json",
                            response_json,
                        ),
                    )
                    response_json = self._post_json(self._chat_payload(request), self._chat_completions_url())
                    response_text = self._extract_chat_completion_text(response_json)
                    adapter = "openai_chat_completions_fallback"

        raw_artifacts.append(self._json_artifact("raw_llm_output", "raw_output.json", response_json))
        try:
            output_json = self._output_json(request, response_json, response_text)
        except LLMProviderError as exc:
            error_json = {
                "error_code": "OPENAI_RESPONSES_SCHEMA_INVALID",
                "message": str(exc),
                "recoverable": True,
            }
            return LLMProviderResponse(
                provider=self.provider,
                model_name=request.model_name,
                status="schema_invalid",
                output_json={
                    "response_text": response_text,
                    "provider_response_id": response_json.get("id"),
                    "adapter": adapter,
                },
                artifacts=[
                    *raw_artifacts,
                    self._json_artifact("schema_validation", "schema_validation.json", error_json),
                ],
                error_json=error_json,
                token_usage_json=self._token_usage(response_json),
            )
        return LLMProviderResponse(
            provider=self.provider,
            model_name=request.model_name,
            status="succeeded",
            output_json=output_json,
            artifacts=[
                *raw_artifacts,
                self._json_artifact("parsed_output", "parsed_output.json", output_json),
                self._json_artifact(
                    "schema_validation",
                    "schema_validation.json",
                    {"schema_valid": True, "adapter": adapter},
                ),
            ],
            token_usage_json=self._token_usage(response_json),
        )

    def _responses_payload(self, request: LLMProviderRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model_name,
            "input": self._input_text(request),
            "max_output_tokens": self.max_output_tokens or int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "800")),
        }
        reasoning_effort = os.getenv("LLM_REASONING_EFFORT", "low").strip().lower()
        if reasoning_effort and reasoning_effort not in {"default", "auto"}:
            payload["reasoning"] = {"effort": reasoning_effort}
        if self._expects_json_object(request):
            payload["text"] = {"format": {"type": "json_object"}}
        return payload

    def _chat_payload(self, request: LLMProviderRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": self._input_text(request),
                },
            ],
            "max_tokens": self.max_output_tokens or int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "800")),
        }
        reasoning_effort = os.getenv("LLM_REASONING_EFFORT", "low").strip().lower()
        if reasoning_effort and reasoning_effort not in {"default", "auto"}:
            payload["reasoning_effort"] = reasoning_effort
        return payload

    def _post_json(self, payload: dict[str, Any], url: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "chtest-ai-runtime/0.1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except TimeoutError as exc:
            raise LLMProviderTimeoutError("OpenAI Responses request timed out.") from exc
        except socket.timeout as exc:
            raise LLMProviderTimeoutError("OpenAI Responses request timed out.") from exc
        except urllib.error.HTTPError as exc:
            raise LLMProviderError(f"OpenAI Responses request failed with HTTP {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise LLMProviderError(f"OpenAI Responses request failed: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise LLMProviderError("OpenAI Responses request returned invalid JSON.") from exc

    def _responses_url(self) -> str:
        base_url = self.base_url.rstrip("/")
        if base_url.endswith("/chat/completions"):
            return f"{base_url.removesuffix('/chat/completions')}/responses"
        if base_url.endswith("/responses"):
            return base_url
        if base_url.endswith("/v1"):
            return f"{base_url}/responses"
        return f"{base_url}/v1/responses"

    def _chat_completions_url(self) -> str:
        base_url = self.base_url.rstrip("/")
        if base_url.endswith("/responses"):
            return f"{base_url.removesuffix('/responses')}/chat/completions"
        if base_url.endswith("/chat/completions"):
            return base_url
        if base_url.endswith("/v1"):
            return f"{base_url}/chat/completions"
        return f"{base_url}/v1/chat/completions"

    def _input_text(self, request: LLMProviderRequest) -> str:
        payload = {
            "task_type": request.task_type,
            "input_json": request.input_json,
            "context_artifact_ids": [str(context_id) for context_id in request.context_artifact_ids],
            "context_manifest": request.context_manifest,
        }
        policy = request.runtime_policy
        if policy is None:
            instruction = (
                "Return valid JSON for the caller's task. Do not add Markdown fences or prose. "
                "A production workflow must provide a versioned runtime policy bundle."
            )
        else:
            instruction = (
                "Follow this versioned runtime policy as the authoritative instruction. "
                "Do not replace it with general knowledge or hidden task rules.\n"
                f"Agent: {policy.agent_name}\n"
                f"Prompt {policy.prompt_name}:{policy.prompt_version} ({policy.prompt_hash})\n"
                f"{policy.prompt_content}\n"
                f"Skill {policy.skill_name}:{policy.skill_version} ({policy.skill_hash})\n"
                f"{policy.skill_content}\n"
                "The input and output schemas in the policy are mandatory."
            )
        return f"{instruction}\n{json.dumps(payload, ensure_ascii=False, sort_keys=True)}"

    def _expects_json_object(self, request: LLMProviderRequest) -> bool:
        policy = request.runtime_policy
        return policy is not None and policy.output_schema_json.get("type") == "object"

    def _output_json(
        self,
        request: LLMProviderRequest,
        response_json: dict[str, Any],
        response_text: str,
    ) -> dict[str, Any]:
        if self._expects_json_object(request):
            parsed = self._parse_json_object(response_text)
            parsed.setdefault("used_knowledge", bool(request.input_json.get("knowledge_retrieval")))
            parsed.setdefault("used_context_artifact_ids", [str(context_id) for context_id in request.context_artifact_ids])
            parsed["provider_response_id"] = response_json.get("id")
            return parsed
        return {
            "response_text": response_text,
            "provider_response_id": response_json.get("id"),
            "used_knowledge": False,
            "used_context_artifact_ids": [str(context_id) for context_id in request.context_artifact_ids],
        }

    def _parse_json_object(self, response_text: str) -> dict[str, Any]:
        text = response_text.strip()
        if not text:
            raise LLMProviderError("OpenAI Responses request returned empty text.")
        for candidate in [text, self._extract_json_object_text(text)]:
            if candidate is None:
                continue
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
        raise LLMProviderError("OpenAI Responses request did not return a JSON object.")

    def _extract_json_object_text(self, text: str) -> str | None:
        start = text.find("{")
        if start < 0:
            return None
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(text)):
            character = text[index]
            if in_string:
                if escape:
                    escape = False
                elif character == "\\":
                    escape = True
                elif character == '"':
                    in_string = False
                continue
            if character == '"':
                in_string = True
            elif character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
        return None

    def _extract_response_text(self, response_json: dict[str, Any]) -> str:
        output_text = response_json.get("output_text")
        if isinstance(output_text, str) and output_text:
            return output_text

        texts: list[str] = []
        for output_item in response_json.get("output", []):
            if not isinstance(output_item, dict):
                continue
            for content_item in output_item.get("content", []):
                if not isinstance(content_item, dict):
                    continue
                if content_item.get("type") in {"output_text", "text"} and isinstance(content_item.get("text"), str):
                    texts.append(content_item["text"])
        return "\n".join(texts)

    def _extract_chat_completion_text(self, response_json: dict[str, Any]) -> str:
        choices = response_json.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            return ""
        message = choices[0].get("message")
        if not isinstance(message, dict):
            return ""
        content = message.get("content")
        if isinstance(content, str):
            return content
        if not isinstance(content, list):
            return ""
        texts: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                texts.append(item["text"])
        return "\n".join(texts)

    def _token_usage(self, response_json: dict[str, Any]) -> dict[str, int]:
        usage = response_json.get("usage")
        if not isinstance(usage, dict):
            return {}
        token_usage: dict[str, int] = {}
        prompt_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
        completion_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
        if isinstance(prompt_tokens, int):
            token_usage["prompt_tokens"] = prompt_tokens
        if isinstance(completion_tokens, int):
            token_usage["completion_tokens"] = completion_tokens
        if isinstance(usage.get("total_tokens"), int):
            token_usage["total_tokens"] = usage["total_tokens"]
        return token_usage

    def _json_artifact(self, artifact_type: str, file_name: str, payload: dict[str, Any]) -> ProviderArtifactPayload:
        return ProviderArtifactPayload(
            artifact_type=artifact_type,
            file_name=file_name,
            mime_type="application/json",
            content=json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"),
        )

    def _can_fallback_to_chat_completions(self, exc: BaseException) -> bool:
        if isinstance(exc, LLMProviderTimeoutError):
            return True
        message = str(exc)
        recoverable_http_statuses = {"408", "409", "429", "500", "502", "503", "504", "524"}
        return any(f"HTTP {status}" in message for status in recoverable_http_statuses)


def normalize_wire_api(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace("/", "_")
    if normalized in {"chat", "chat_completion", "chat_completions"}:
        return "chat_completions"
    return "responses"
