from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DEFAULT_WIRE_API = "responses"
MODEL_CONFIG_PATH_ENV = "CHTEST_MODEL_CONNECTION_PATH"


class ModelConnectionConfigError(ValueError):
    pass


@dataclass(frozen=True)
class ModelConnectionConfig:
    provider: str
    model_name: str
    base_url: str
    wire_api: str = DEFAULT_WIRE_API
    api_key: str = ""

    @property
    def api_key_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def api_key_hint(self) -> str | None:
        if not self.api_key:
            return None
        tail = self.api_key[-4:] if len(self.api_key) >= 4 else self.api_key
        return f"***{tail}"


def model_connection_config_path() -> Path:
    configured_path = os.getenv(MODEL_CONFIG_PATH_ENV)
    if configured_path:
        return Path(configured_path)
    return Path("storage") / "model-connection.json"


def load_model_connection_config(path: Path | None = None) -> ModelConnectionConfig | None:
    target_path = path or model_connection_config_path()
    if not target_path.exists():
        return None
    try:
        payload = json.loads(target_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelConnectionConfigError("Model connection config could not be read.") from exc
    if not isinstance(payload, dict):
        raise ModelConnectionConfigError("Model connection config must be a JSON object.")

    return _config_from_payload(payload)


def save_model_connection_config(config: ModelConnectionConfig, path: Path | None = None) -> ModelConnectionConfig:
    target_path = path or model_connection_config_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return config


def merge_model_connection_config(
    *,
    existing_config: ModelConnectionConfig | None = None,
    import_config_text: str | None = None,
    import_auth_json: str | None = None,
    codex_config_toml: str | None = None,
    codex_auth_json: str | None = None,
    api_key: str | None = None,
    provider: str | None = None,
    model_name: str | None = None,
    base_url: str | None = None,
    wire_api: str | None = None,
) -> ModelConnectionConfig:
    config_text = _first_present(import_config_text, codex_config_toml)
    auth_json = _first_present(import_auth_json, codex_auth_json)
    parsed_import_config = parse_model_config_text(config_text or "")
    parsed_auth_key = parse_model_auth_json(auth_json or "")
    resolved_provider = _first_present(
        provider,
        parsed_import_config.get("provider"),
        existing_config.provider if existing_config else None,
    )
    resolved_model_name = _first_present(
        model_name,
        parsed_import_config.get("model_name"),
        existing_config.model_name if existing_config else None,
    )
    resolved_base_url = _first_present(
        base_url,
        parsed_import_config.get("base_url"),
        existing_config.base_url if existing_config else None,
    )
    resolved_wire_api = (
        _first_present(
            wire_api,
            parsed_import_config.get("wire_api"),
            existing_config.wire_api if existing_config else None,
        )
        or DEFAULT_WIRE_API
    )
    resolved_api_key = _first_present(api_key, parsed_auth_key, existing_config.api_key if existing_config else None)

    if not resolved_provider:
        raise ModelConnectionConfigError("Model provider is required.")
    if not resolved_model_name:
        raise ModelConnectionConfigError("Model name is required.")
    if not resolved_base_url:
        raise ModelConnectionConfigError("Base URL is required.")
    if not resolved_api_key:
        raise ModelConnectionConfigError("API key is required.")
    if resolved_wire_api.strip().lower() != DEFAULT_WIRE_API:
        raise ModelConnectionConfigError("Only Responses wire API is supported.")
    resolved_base_url = _validate_base_url(resolved_base_url)

    return ModelConnectionConfig(
        provider=resolved_provider,
        model_name=resolved_model_name,
        base_url=resolved_base_url,
        wire_api=DEFAULT_WIRE_API,
        api_key=resolved_api_key,
    )


def parse_model_config_text(config_toml: str) -> dict[str, str]:
    top_level: dict[str, str] = {}
    provider_sections: dict[str, dict[str, str]] = {}
    current_provider: str | None = None

    for raw_line in config_toml.splitlines():
        line = _strip_toml_comment(raw_line).strip()
        if not line:
            continue
        section_match = re.match(r"^\[(?P<section>[^\]]+)\]$", line)
        if section_match:
            section = section_match.group("section").strip()
            current_provider = _provider_name_from_section(section)
            if current_provider:
                provider_sections.setdefault(current_provider.lower(), {})
            continue

        key_match = re.match(r'^(?P<key>[A-Za-z0-9_\-]+)\s*=\s*(?P<value>.+)$', line)
        if not key_match:
            continue
        key = key_match.group("key")
        value = _parse_toml_string(key_match.group("value"))
        if value is None:
            continue
        if current_provider:
            provider_sections.setdefault(current_provider.lower(), {})[key] = value
        else:
            top_level[key] = value

    provider = top_level.get("model_provider")
    provider_config = provider_sections.get(provider.lower(), {}) if provider else {}
    if not provider_config and len(provider_sections) == 1:
        provider_config = next(iter(provider_sections.values()))

    result: dict[str, str] = {}
    if provider:
        result["provider"] = provider
    if top_level.get("model"):
        result["model_name"] = top_level["model"]
    if provider_config.get("base_url"):
        result["base_url"] = provider_config["base_url"]
    if provider_config.get("wire_api"):
        result["wire_api"] = provider_config["wire_api"]
    return result


def parse_model_auth_json(auth_json: str) -> str | None:
    if not auth_json.strip():
        return None
    try:
        payload = json.loads(auth_json)
    except json.JSONDecodeError as exc:
        raise ModelConnectionConfigError("Codex auth JSON is invalid.") from exc

    value = _find_api_key(payload)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


parse_codex_config_toml = parse_model_config_text
parse_codex_auth_json = parse_model_auth_json


def public_model_connection_config(config: ModelConnectionConfig | None) -> dict[str, Any]:
    if config is None:
        return {
            "configured": False,
            "provider": None,
            "model_name": None,
            "base_url": None,
            "wire_api": DEFAULT_WIRE_API,
            "api_key_configured": False,
            "api_key_hint": None,
        }
    return {
        "configured": True,
        "provider": config.provider,
        "model_name": config.model_name,
        "base_url": config.base_url,
        "wire_api": config.wire_api,
        "api_key_configured": config.api_key_configured,
        "api_key_hint": config.api_key_hint,
    }


def resolve_model_identity(
    *,
    model_provider: str | None = None,
    model_name: str | None = None,
    default_provider: str = "mock",
    default_model_name: str = "mock-model",
) -> tuple[str, str]:
    if _first_present(model_provider) and _first_present(model_name):
        return str(_first_present(model_provider)), str(_first_present(model_name))

    config = load_model_connection_config()
    resolved_provider = _first_present(model_provider, config.provider if config else None, default_provider)
    resolved_model_name = _first_present(model_name, config.model_name if config else None, default_model_name)
    return str(resolved_provider), str(resolved_model_name)


def _config_from_payload(payload: dict[str, Any]) -> ModelConnectionConfig:
    return merge_model_connection_config(
        provider=_string_or_none(payload.get("provider")),
        model_name=_string_or_none(payload.get("model_name")),
        base_url=_string_or_none(payload.get("base_url")),
        wire_api=_string_or_none(payload.get("wire_api")),
        api_key=_string_or_none(payload.get("api_key")),
    )


def _validate_base_url(base_url: str) -> str:
    value = base_url.strip()
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise ModelConnectionConfigError("Base URL must be an HTTP(S) URL with a host.")
    if parsed.username or parsed.password:
        raise ModelConnectionConfigError("Base URL must not include credentials.")
    if parsed.query or parsed.fragment:
        raise ModelConnectionConfigError("Base URL must not include query or fragment.")
    return value.rstrip("/")


def _first_present(*values: str | None) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _provider_name_from_section(section: str) -> str | None:
    parts = [part.strip('"') for part in section.split(".")]
    if len(parts) >= 2 and parts[-2] in {"model_providers", "providers"}:
        return parts[-1]
    return None


def _parse_toml_string(raw_value: str) -> str | None:
    value = raw_value.strip().rstrip(",")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1]
    return value if value and value[0].isalnum() else None


def _strip_toml_comment(line: str) -> str:
    in_quote: str | None = None
    for index, character in enumerate(line):
        if character in {'"', "'"}:
            in_quote = None if in_quote == character else character
        if character == "#" and in_quote is None:
            return line[:index]
    return line


def _find_api_key(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if str(key).upper() == "OPENAI_API_KEY" and isinstance(nested_value, str):
                return nested_value
        for nested_value in value.values():
            found = _find_api_key(nested_value)
            if found:
                return found
    if isinstance(value, list):
        for nested_value in value:
            found = _find_api_key(nested_value)
            if found:
                return found
    return None


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None
