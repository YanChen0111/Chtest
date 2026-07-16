from __future__ import annotations

import asyncio
from typing import Any

from backend.app.main import app


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    @property
    def text(self) -> str:
        return self.body.decode("utf-8")


def request_get(path: str) -> ASGIResponse:
    return asyncio.run(asgi_get(path))


async def asgi_get(path: str) -> ASGIResponse:
    status_code: int | None = None
    body_chunks: list[bytes] = []
    request_complete = False

    async def receive() -> dict[str, Any]:
        nonlocal request_complete
        if not request_complete:
            request_complete = True
            return {"type": "http.request", "body": b"", "more_body": False}
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
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": [(b"host", b"testserver")],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }

    await app(scope, receive, send)
    assert status_code is not None
    return ASGIResponse(status_code, b"".join(body_chunks))


def test_health_endpoint_returns_ok() -> None:
    response = request_get("/health")

    assert response.status_code == 200
    assert response.text == "ok"


def test_api_health_endpoint_returns_ok_for_frontend_proxy() -> None:
    response = request_get("/api/health")

    assert response.status_code == 200
    assert response.text == "ok"
