from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from backend.app.main import app
from backend.app.modules.ai_runtime.providers.base import LLMProviderError, LLMProviderRequest, LLMProviderResponse


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def get(self, path: str) -> ASGIResponse:
        return self.request("GET", path)

    def put(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("PUT", path, json_body)

    def request(self, method: str, path: str, json_body: dict[str, Any] | None = None) -> ASGIResponse:
        return asyncio.run(self._request(method, path, json_body))

    async def _request(self, method: str, path: str, json_body: dict[str, Any] | None) -> ASGIResponse:
        body = json.dumps(json_body).encode("utf-8") if json_body is not None else b""
        status_code: int | None = None
        body_chunks: list[bytes] = []
        request_complete = False

        async def receive() -> dict[str, Any]:
            nonlocal request_complete
            if not request_complete:
                request_complete = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        async def send(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                body_chunks.append(message.get("body", b""))

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": b"",
            "headers": [
                (b"host", b"testserver"),
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }

        await self.asgi_app(scope, receive, send)
        assert status_code is not None
        return ASGIResponse(status_code, b"".join(body_chunks))


@pytest.fixture()
def config_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "model-connection.json"
    monkeypatch.setenv("CHTEST_MODEL_CONNECTION_PATH", str(path))
    return path


def test_model_connection_config_imports_toml_style_config_without_echoing_key(config_path: Path) -> None:
    client = ASGIClient(app)

    response = client.put(
        "/api/settings/model-connection",
        {
            "import_config_text": '\n'.join(
                [
                    'model_provider = "OpenAI"',
                    'model = "gpt-5.5"',
                    '[model_providers.OpenAI]',
                    'base_url = "https://lucen.cc"',
                    'wire_api = "responses"',
                ],
            ),
            "import_auth_json": '{"OPENAI_API_KEY":"sk-local-secret"}',
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "configured": True,
        "provider": "OpenAI",
        "model_name": "gpt-5.5",
        "base_url": "https://lucen.cc",
        "wire_api": "responses",
        "api_key_configured": True,
        "api_key_hint": "***cret",
    }
    assert "sk-local-secret" not in json.dumps(body)
    assert json.loads(config_path.read_text(encoding="utf-8"))["api_key"] == "sk-local-secret"

    read_response = client.get("/api/settings/model-connection")

    assert read_response.status_code == 200
    assert read_response.json() == body


def test_model_connection_config_saves_manual_model_service_config(config_path: Path) -> None:
    client = ASGIClient(app)

    response = client.put(
        "/api/settings/model-connection",
        {
            "provider": "OpenAI Compatible",
            "model_name": "gpt-test",
            "base_url": "https://gateway.example.test/v1",
            "wire_api": "responses",
            "api_key": "sk-local-secret",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "configured": True,
        "provider": "OpenAI Compatible",
        "model_name": "gpt-test",
        "base_url": "https://gateway.example.test/v1",
        "wire_api": "responses",
        "api_key_configured": True,
        "api_key_hint": "***cret",
    }
    saved_config = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved_config["provider"] == "OpenAI Compatible"
    assert saved_config["model_name"] == "gpt-test"
    assert saved_config["base_url"] == "https://gateway.example.test/v1"
    assert saved_config["api_key"] == "sk-local-secret"


def test_model_connection_config_rejects_incomplete_import(config_path: Path) -> None:
    client = ASGIClient(app)

    response = client.put(
        "/api/settings/model-connection",
        {
            "import_config_text": 'model = "gpt-5.5"',
            "import_auth_json": "{}",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "MODEL_CONFIG_INVALID"
    assert not config_path.exists()


def test_model_connection_config_rejects_base_url_credentials(config_path: Path) -> None:
    client = ASGIClient(app)

    response = client.put(
        "/api/settings/model-connection",
        {
            "provider": "OpenAI",
            "model_name": "gpt-5.5",
            "base_url": "https://user:pass@example.test",
            "api_key": "sk-local-secret",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "MODEL_CONFIG_INVALID"
    assert not config_path.exists()


def test_model_connection_config_reports_invalid_local_file(config_path: Path) -> None:
    config_path.write_text("[]", encoding="utf-8")
    client = ASGIClient(app)

    response = client.get("/api/settings/model-connection")

    assert response.status_code == 422
    assert response.json()["error_code"] == "MODEL_CONFIG_INVALID"


def test_model_connection_config_validation_error_does_not_echo_secret(config_path: Path) -> None:
    client = ASGIClient(app)
    secret = "sk-" + ("local-secret" * 400)

    response = client.put(
        "/api/settings/model-connection",
        {
            "provider": "OpenAI",
            "model_name": "gpt-5.5",
            "base_url": "https://api.example.test",
            "api_key": secret,
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"
    assert secret not in response.body.decode("utf-8")
    assert "input" not in response.json()["details"]["errors"][0]
    assert not config_path.exists()


def test_model_connection_config_can_update_key_from_existing_config(config_path: Path) -> None:
    config_path.write_text(
        json.dumps(
            {
                "provider": "OpenAI",
                "model_name": "gpt-5.5",
                "base_url": "https://api.example.test",
                "wire_api": "responses",
                "api_key": "sk-old-secret",
            },
        ),
        encoding="utf-8",
    )
    client = ASGIClient(app)

    response = client.put(
        "/api/settings/model-connection",
        {
            "import_auth_json": '{"OPENAI_API_KEY":"sk-new-secret"}',
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["configured"] is True
    assert body["provider"] == "OpenAI"
    assert body["model_name"] == "gpt-5.5"
    assert body["base_url"] == "https://api.example.test"
    assert body["api_key_hint"] == "***cret"
    assert json.loads(config_path.read_text(encoding="utf-8"))["api_key"] == "sk-new-secret"


def test_model_connection_test_reports_missing_config(config_path: Path) -> None:
    client = ASGIClient(app)

    response = client.request("POST", "/api/settings/model-connection/test")

    assert response.status_code == 200
    assert response.json() == {
        "ok": False,
        "provider": None,
        "model_name": None,
        "base_url": None,
        "wire_api": "responses",
        "message": "Model connection is not configured.",
        "error_code": "MODEL_CONFIG_MISSING",
        "http_status": None,
        "diagnostic": None,
        "suggestion": None,
    }


def test_model_connection_test_uses_saved_config(config_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path.write_text(
        json.dumps(
            {
                "provider": "OpenAI Compatible",
                "model_name": "gpt-test",
                "base_url": "https://gateway.example.test/v1",
                "wire_api": "responses",
                "api_key": "sk-local-secret",
            },
        ),
        encoding="utf-8",
    )
    captured: dict[str, Any] = {}

    class FakeProvider:
        def generate(self, request: LLMProviderRequest) -> LLMProviderResponse:
            captured["request"] = request
            return LLMProviderResponse(
                provider="openai",
                model_name=request.model_name,
                status="succeeded",
                output_json={"response_text": "ok"},
                artifacts=[],
            )

    def fake_create_llm_provider(provider_name: str | None = None, **kwargs: Any) -> FakeProvider:
        captured["kwargs"] = {"provider_name": provider_name, **kwargs}
        return FakeProvider()

    monkeypatch.setattr("backend.app.modules.ai_runtime.router.create_llm_provider", fake_create_llm_provider)
    client = ASGIClient(app)

    response = client.request("POST", "/api/settings/model-connection/test")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "provider": "OpenAI Compatible",
        "model_name": "gpt-test",
        "base_url": "https://gateway.example.test/v1",
        "wire_api": "responses",
        "message": "Model connection test succeeded.",
        "error_code": None,
        "http_status": None,
        "diagnostic": None,
        "suggestion": None,
    }
    assert captured["kwargs"] == {
        "provider_name": "OpenAI Compatible",
        "base_url": "https://gateway.example.test/v1",
        "api_key": "sk-local-secret",
        "wire_api": "responses",
        "timeout_seconds": 20,
        "max_output_tokens": 32,
    }
    assert captured["request"].task_type == "model_connection_test"
    assert captured["request"].model_name == "gpt-test"


def test_model_connection_test_rejects_empty_model_response(
    config_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path.write_text(
        json.dumps(
            {
                "provider": "OpenAI Compatible",
                "model_name": "gpt-empty",
                "base_url": "https://gateway.example.test/v1",
                "wire_api": "responses",
                "api_key": "sk-local-secret",
            },
        ),
        encoding="utf-8",
    )

    class FakeProvider:
        def generate(self, request: LLMProviderRequest) -> LLMProviderResponse:
            return LLMProviderResponse(
                provider="openai",
                model_name=request.model_name,
                status="succeeded",
                output_json={"response_text": ""},
                artifacts=[],
            )

    monkeypatch.setattr(
        "backend.app.modules.ai_runtime.router.create_llm_provider",
        lambda *_args, **_kwargs: FakeProvider(),
    )
    client = ASGIClient(app)

    response = client.request("POST", "/api/settings/model-connection/test")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error_code"] == "MODEL_CONNECTION_EMPTY_RESPONSE"
    assert body["message"] == "Model connection test returned an empty response."


def test_model_connection_test_uses_unsaved_form_config(
    config_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeProvider:
        def generate(self, request: LLMProviderRequest) -> LLMProviderResponse:
            captured["request"] = request
            return LLMProviderResponse(
                provider="openai",
                model_name=request.model_name,
                status="succeeded",
                output_json={"response_text": "ok"},
                artifacts=[],
            )

    def fake_create_llm_provider(provider_name: str | None = None, **kwargs: Any) -> FakeProvider:
        captured["kwargs"] = {"provider_name": provider_name, **kwargs}
        return FakeProvider()

    monkeypatch.setattr("backend.app.modules.ai_runtime.router.create_llm_provider", fake_create_llm_provider)
    client = ASGIClient(app)

    response = client.request(
        "POST",
        "/api/settings/model-connection/test",
        {
            "provider": "OpenAI Compatible",
            "model_name": "gpt-form",
            "base_url": "https://form-gateway.example.test/v1",
            "wire_api": "responses",
            "api_key": "sk-form-secret",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["provider"] == "OpenAI Compatible"
    assert body["model_name"] == "gpt-form"
    assert body["base_url"] == "https://form-gateway.example.test/v1"
    assert captured["kwargs"] == {
        "provider_name": "OpenAI Compatible",
        "base_url": "https://form-gateway.example.test/v1",
        "api_key": "sk-form-secret",
        "wire_api": "responses",
        "timeout_seconds": 20,
        "max_output_tokens": 32,
    }
    assert captured["request"].model_name == "gpt-form"
    assert not config_path.exists()


def test_model_connection_test_reports_http_provider_diagnostic(
    config_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path.write_text(
        json.dumps(
            {
                "provider": "OpenAI",
                "model_name": "gpt-test",
                "base_url": "https://api.example.test/v1",
                "wire_api": "responses",
                "api_key": "sk-local-secret",
            },
        ),
        encoding="utf-8",
    )

    class FakeProvider:
        def generate(self, request: LLMProviderRequest) -> LLMProviderResponse:
            raise LLMProviderError("OpenAI Responses request failed with HTTP 403.")

    def fake_create_llm_provider(_provider_name: str | None = None, **_kwargs: Any) -> FakeProvider:
        return FakeProvider()

    monkeypatch.setattr("backend.app.modules.ai_runtime.router.create_llm_provider", fake_create_llm_provider)
    client = ASGIClient(app)

    response = client.request("POST", "/api/settings/model-connection/test")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error_code"] == "MODEL_CONNECTION_HTTP_403"
    assert body["http_status"] == 403
    assert body["diagnostic"] == "HTTP 403"
    assert "permissions" in body["suggestion"]
    assert "sk-local-secret" not in response.body.decode("utf-8")


def test_model_connection_test_does_not_echo_provider_secret(
    config_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path.write_text(
        json.dumps(
            {
                "provider": "OpenAI",
                "model_name": "gpt-test",
                "base_url": "https://api.example.test/v1",
                "wire_api": "responses",
                "api_key": "sk-local-secret",
            },
        ),
        encoding="utf-8",
    )

    class FakeProvider:
        def generate(self, request: LLMProviderRequest) -> LLMProviderResponse:
            raise LLMProviderError("upstream echoed sk-local-secret")

    def fake_create_llm_provider(_provider_name: str | None = None, **_kwargs: Any) -> FakeProvider:
        return FakeProvider()

    monkeypatch.setattr("backend.app.modules.ai_runtime.router.create_llm_provider", fake_create_llm_provider)
    client = ASGIClient(app)

    response = client.request("POST", "/api/settings/model-connection/test")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error_code"] == "MODEL_CONNECTION_FAILED"
    assert body["diagnostic"] == "upstream echoed [redacted]"
    assert "sk-local-secret" not in response.body.decode("utf-8")
