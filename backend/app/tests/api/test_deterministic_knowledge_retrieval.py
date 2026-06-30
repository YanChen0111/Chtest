from __future__ import annotations

import asyncio
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.ai_runtime.schemas import ContextArtifactCreate
from backend.app.modules.ai_runtime.service import create_context_artifact
from backend.app.modules.extension import service
from backend.app.modules.extension.models import KnowledgeAdapterConfig
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.projects.router import get_session


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def post(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("POST", path, json_body)

    def put(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return self.request("PUT", path, json_body)

    def request(self, method: str, path: str, json_body: dict[str, Any] | None = None) -> ASGIResponse:
        return asyncio.run(self._request(method, path, json_body))

    async def _request(
        self,
        method: str,
        path: str,
        json_body: dict[str, Any] | None,
    ) -> ASGIResponse:
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
def session_and_store(tmp_path: Path) -> Iterator[tuple[Session, LocalArtifactStore]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)

    with SessionLocal() as session:
        yield session, LocalArtifactStore(root=tmp_path / "artifacts")


@pytest.fixture()
def api_client(tmp_path: Path) -> Iterator[tuple[ASGIClient, sessionmaker[Session], LocalArtifactStore]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)
    store = LocalArtifactStore(root=tmp_path / "artifacts")

    def override_get_session() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    def override_get_artifact_store() -> LocalArtifactStore:
        return store

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_artifact_store] = override_get_artifact_store

    yield ASGIClient(app), SessionLocal, store

    app.dependency_overrides.clear()


def create_project(session: Session, name: str = "Checkout") -> Project:
    workspace = session.query(Workspace).filter_by(name="Personal Workspace").one_or_none()
    if workspace is None:
        workspace = Workspace(name="Personal Workspace")
    project = Project(workspace=workspace, name=name)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def add_context_artifact(
    session: Session,
    store: LocalArtifactStore,
    project: Project,
    *,
    title: str,
    content: str,
    safe_to_show: bool = True,
    allowed_for_prompt: bool = True,
):
    artifact = create_context_artifact(
        session,
        store,
        ContextArtifactCreate(
            project_id=project.id,
            title=title,
            artifact_type="context_markdown",
            mime_type="text/markdown",
            content=content,
            source_ref=f"manual:{title}",
        ),
    )
    metadata = dict(artifact.metadata_json)
    metadata["safe_to_show"] = safe_to_show
    metadata["allowed_for_prompt"] = allowed_for_prompt
    artifact.metadata_json = metadata
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return artifact


def configure_deterministic_adapter(session: Session, project: Project) -> None:
    session.add(
        KnowledgeAdapterConfig(
            project_id=project.id,
            adapter_name="default",
            status="configured_stub",
            provider_type="deterministic_local",
            config_json={"match_mode": "keyword_overlap"},
        ),
    )
    session.commit()


def test_retrieve_matches_only_eligible_same_project_context_artifacts(
    session_and_store: tuple[Session, LocalArtifactStore],
) -> None:
    session, store = session_and_store
    project = create_project(session)
    other_project = create_project(session, name="Billing")
    configure_deterministic_adapter(session, project)

    included = add_context_artifact(
        session,
        store,
        project,
        title="coupon-api-notes.md",
        content=(
            "Expired coupon validation blocks checkout when the coupon status is "
            "EXPIRED. The response should explain the coupon failure."
        ),
    )
    add_context_artifact(
        session,
        store,
        project,
        title="inventory-notes.md",
        content="Inventory reservation checks stock level and warehouse routing.",
    )
    unsafe = add_context_artifact(
        session,
        store,
        project,
        title="unsafe-coupon-note.md",
        content="Expired coupon checkout details that should not be shown.",
        safe_to_show=False,
    )
    disallowed = add_context_artifact(
        session,
        store,
        project,
        title="prompt-blocked-coupon-note.md",
        content="Expired coupon checkout details that cannot enter prompts.",
        allowed_for_prompt=False,
    )
    other = add_context_artifact(
        session,
        store,
        other_project,
        title="other-project-coupon-note.md",
        content="Expired coupon checkout details for a different project.",
    )

    result = service.retrieve_deterministic_knowledge(
        session=session,
        store=store,
        project_id=project.id,
        query_text="expired coupon checkout",
        max_results=3,
        max_snippet_chars=72,
    )

    assert result.used_knowledge is True
    assert result.retrieval_mode == "deterministic_local"
    assert result.query_terms == ["expired", "coupon", "checkout"]
    assert result.used_context_artifact_ids == [included.id]
    assert len(result.results) == 1

    item = result.results[0]
    assert item.context_artifact_id == included.id
    assert item.title == "coupon-api-notes.md"
    assert item.source_ref == "manual:coupon-api-notes.md"
    assert item.score == 3
    assert item.matched_terms == ["expired", "coupon", "checkout"]
    assert len(item.snippet) <= 72
    assert "Expired coupon validation" in item.snippet
    assert item.allowed_for_prompt is True
    assert item.redaction_applied is False

    excluded_ids = {unsafe.id, disallowed.id, other.id}
    assert not excluded_ids.intersection(result.used_context_artifact_ids)


def test_retrieve_api_returns_bounded_deterministic_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session], LocalArtifactStore],
) -> None:
    client, SessionLocal, store = api_client
    with SessionLocal() as session:
        project = create_project(session)
        configure_deterministic_adapter(session, project)
        first = add_context_artifact(
            session,
            store,
            project,
            title="b-coupon.md",
            content="Coupon checkout validation covers expired coupon errors.",
        )
        second = add_context_artifact(
            session,
            store,
            project,
            title="a-checkout.md",
            content="Checkout validation includes coupon eligibility decisions.",
        )

    response = client.post(
        f"/api/projects/{project.id}/knowledge-adapter/retrieve",
        json_body={
            "query_text": "coupon checkout validation",
            "max_results": 1,
            "max_snippet_chars": 64,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["used_knowledge"] is True
    assert body["retrieval_mode"] == "deterministic_local"
    assert body["query_terms"] == ["coupon", "checkout", "validation"]
    assert body["used_context_artifact_ids"] == [str(second.id)]
    assert len(body["results"]) == 1
    assert body["results"][0]["context_artifact_id"] == str(second.id)
    assert body["results"][0]["matched_terms"] == ["coupon", "checkout", "validation"]
    assert body["results"][0]["score"] == 3
    assert len(body["results"][0]["snippet"]) <= 64
    assert str(first.id) not in body["used_context_artifact_ids"]


def test_retrieve_returns_empty_when_adapter_is_not_configured(
    session_and_store: tuple[Session, LocalArtifactStore],
) -> None:
    session, store = session_and_store
    project = create_project(session)
    add_context_artifact(
        session,
        store,
        project,
        title="coupon.md",
        content="Expired coupon checkout validation evidence.",
    )

    result = service.retrieve_deterministic_knowledge(
        session=session,
        store=store,
        project_id=project.id,
        query_text="expired coupon",
    )

    assert result.used_knowledge is False
    assert result.used_context_artifact_ids == []
    assert result.results == []


def test_retrieve_returns_empty_when_adapter_is_disabled(
    session_and_store: tuple[Session, LocalArtifactStore],
) -> None:
    session, store = session_and_store
    project = create_project(session)
    session.add(
        KnowledgeAdapterConfig(
            project_id=project.id,
            adapter_name="default",
            status="disabled",
            provider_type="deterministic_local",
            config_json={},
        ),
    )
    session.commit()
    add_context_artifact(
        session,
        store,
        project,
        title="coupon.md",
        content="Expired coupon checkout validation evidence.",
    )

    result = service.retrieve_deterministic_knowledge(
        session=session,
        store=store,
        project_id=project.id,
        query_text="expired coupon",
    )

    assert result.used_knowledge is False
    assert result.used_context_artifact_ids == []
    assert result.results == []


def test_retrieve_supports_unicode_query_terms(
    session_and_store: tuple[Session, LocalArtifactStore],
) -> None:
    session, store = session_and_store
    project = create_project(session)
    configure_deterministic_adapter(session, project)
    artifact = add_context_artifact(
        session,
        store,
        project,
        title="coupon-cn.md",
        content="优惠券 过期 校验需要阻止结算。",
    )

    result = service.retrieve_deterministic_knowledge(
        session=session,
        store=store,
        project_id=project.id,
        query_text="优惠券 过期",
    )

    assert result.used_knowledge is True
    assert result.query_terms == ["优惠券", "过期"]
    assert result.used_context_artifact_ids == [artifact.id]
    assert result.results[0].matched_terms == ["优惠券", "过期"]


def test_update_adapter_allows_deterministic_local_without_using_knowledge(
    api_client: tuple[ASGIClient, sessionmaker[Session], LocalArtifactStore],
) -> None:
    client, SessionLocal, _ = api_client
    with SessionLocal() as session:
        project = create_project(session)

    response = client.put(
        f"/api/projects/{project.id}/knowledge-adapter",
        json_body={
            "adapter_name": "default",
            "status": "configured_stub",
            "provider_type": "deterministic_local",
            "config": {
                "match_mode": "keyword_overlap",
                "max_results": 5,
                "max_snippet_chars": 320,
                "min_score": 1,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider_type"] == "deterministic_local"
    assert body["status"] == "configured_stub"
    assert body["used_knowledge"] is False
