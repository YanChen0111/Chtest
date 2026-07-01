from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate
from backend.app.modules.cases.service import calculate_case_metrics
from backend.app.modules.projects.router import get_session
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.requirements.models import Requirement


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
        return asyncio.run(self._request("GET", path))

    async def _request(self, method: str, path: str) -> ASGIResponse:
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
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": b"",
            "headers": [(b"host", b"testserver"), (b"accept", b"application/json")],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }

        await self.asgi_app(scope, receive, send)
        assert status_code is not None
        return ASGIResponse(status_code, b"".join(body_chunks))


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


def api_client(SessionLocal: sessionmaker[Session]) -> Iterator[ASGIClient]:
    def override_get_session() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield ASGIClient(app)
    app.dependency_overrides.clear()


def add_candidate(
    session: Session,
    task: CaseGenerationTask,
    *,
    title: str,
    status: str,
    steps_json: list[str] | None = None,
    expected_results_json: list[str] | None = None,
    requirement_refs_json: list[str] | None = None,
    ai_reason: str = "covers fixture behavior",
) -> None:
    session.add(
        GeneratedCaseCandidate(
            generation_task_id=task.id,
            project_id=task.project_id,
            module_id=None,
            title=title,
            priority="P0",
            test_type="functional",
            precondition="fixture precondition",
            steps_json=steps_json if steps_json is not None else ["step"],
            expected_results_json=expected_results_json if expected_results_json is not None else ["expected"],
            input_data_json={},
            tags=[],
            requirement_refs_json=requirement_refs_json if requirement_refs_json is not None else ["requirement"],
            risk_refs_json=[],
            ai_reason=ai_reason,
            status=status,
        ),
    )


def create_generation_task(session: Session) -> CaseGenerationTask:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    requirement = Requirement(
        project_id=project.id,
        title="Coupon checkout rules",
        content="Coupon cannot be used with points.",
    )
    session.add(requirement)
    session.flush()
    task = CaseGenerationTask(
        project_id=project.id,
        requirement_id=requirement.id,
        requirement_review_id=None,
        ai_task_id=uuid.uuid4(),
        target_test_types=["functional", "ui"],
        status="succeeded",
        generated_count=5,
    )
    session.add(task)
    session.flush()
    return task


def test_calculate_case_metrics_from_candidate_review_states() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        task = create_generation_task(session)
        add_candidate(session, task, title="main flow", status="approved")
        add_candidate(session, task, title="conflict rule", status="approved")
        add_candidate(session, task, title="expired coupon", status="approved_after_edit")
        add_candidate(session, task, title="amount boundary", status="needs_optimization")
        add_candidate(session, task, title="unclear duplicate", status="rejected")
        session.commit()

        metrics = calculate_case_metrics(session, task.id)

    assert metrics.generation_task_id == task.id
    assert metrics.generated_count == 5
    assert metrics.approved_count == 2
    assert metrics.edited_count == 1
    assert metrics.rejected_count == 1
    assert metrics.optimization_count == 1
    assert metrics.reviewed_count == 5
    assert metrics.acceptance_rate == 0.6
    assert metrics.edit_rate == 0.2
    assert metrics.rejection_rate == 0.2
    assert metrics.optimization_rate == 0.2
    assert metrics.review_progress == 1.0
    assert metrics.field_complete_rate == 1.0


def test_field_complete_rate_counts_candidates_with_required_case_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        task = create_generation_task(session)
        add_candidate(session, task, title="complete", status="generated")
        add_candidate(session, task, title="missing steps", status="generated", steps_json=[])
        add_candidate(session, task, title="missing expected", status="generated", expected_results_json=[])
        add_candidate(session, task, title="missing refs", status="generated", requirement_refs_json=[])
        add_candidate(session, task, title="missing reason", status="generated", ai_reason="")
        session.commit()

        metrics = calculate_case_metrics(session, task.id)

    assert metrics.generated_count == 5
    assert metrics.reviewed_count == 0
    assert metrics.review_progress == 0.0
    assert metrics.field_complete_rate == 0.2


def test_get_case_generation_task_metrics_returns_batch_metrics() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        task = create_generation_task(session)
        add_candidate(session, task, title="main flow", status="approved")
        add_candidate(session, task, title="conflict rule", status="approved_after_edit")
        add_candidate(session, task, title="amount boundary", status="needs_optimization")
        session.commit()
        task_id = task.id

    client = next(api_client(SessionLocal))
    response = client.get(f"/api/case-generation/tasks/{task_id}/metrics")

    assert response.status_code == 200
    body = response.json()
    assert body["generation_task_id"] == str(task_id)
    assert body["generated_count"] == 3
    assert body["approved_count"] == 1
    assert body["edited_count"] == 1
    assert body["rejected_count"] == 0
    assert body["optimization_count"] == 1
    assert body["reviewed_count"] == 3
    assert body["acceptance_rate"] == 0.6667
    assert body["edit_rate"] == 0.3333
    assert body["review_progress"] == 1.0


def test_get_unknown_case_generation_task_metrics_returns_contract_error() -> None:
    SessionLocal = session_factory()
    client = next(api_client(SessionLocal))

    response = client.get(f"/api/case-generation/tasks/{uuid.uuid4()}/metrics")

    assert response.status_code == 404
    assert response.json()["error_code"] == "CASE_GENERATION_TASK_NOT_FOUND"
