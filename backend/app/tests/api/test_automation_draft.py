from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.automation.schemas import AutomationDraftRead
from backend.app.modules.cases.models import TestCase as CaseModel
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.projects.router import get_session
from backend.app.modules.review_history.models import ReviewHistory


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
        return asyncio.run(self._request("GET", path, None))

    def patch(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return asyncio.run(self._request("PATCH", path, json_body))

    def post(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return asyncio.run(self._request("POST", path, json_body))

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


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


@pytest.fixture()
def api_client() -> Iterator[tuple[ASGIClient, sessionmaker[Session]]]:
    SessionLocal = session_factory()

    def override_get_session() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield ASGIClient(app), SessionLocal
    app.dependency_overrides.clear()


def seed_project_case_and_task(session: Session) -> tuple[Project, CaseModel, AITask]:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    test_case = CaseModel(
        project_id=project.id,
        title="Expired coupon cannot submit order",
        priority="P0",
        test_type="functional",
        precondition="User has an expired coupon",
        steps_json=["Prepare expired coupon", "Open checkout", "Submit order"],
        expected_results_json=["Submit is blocked", "Expired coupon message is shown"],
        input_data_json={"coupon_state": "expired"},
        tags=["coupon", "boundary"],
        source_type="ai",
        review_status="approved_after_edit",
        status="active",
    )
    ai_task = AITask(
        project_id=project.id,
        agent_name="AutomationDraftAgent",
        task_type="automation_draft_generation",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
        model_provider="mock",
        model_name="mock-automation-draft",
        status="succeeded",
        input_json={"test_case_id": str(test_case.id)},
        output_json={},
    )
    session.add_all([test_case, ai_task])
    session.flush()
    return project, test_case, ai_task


def test_automation_draft_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, test_case, ai_task = seed_project_case_and_task(session)
        draft = AutomationDraft(
            project_id=project.id,
            test_case_id=test_case.id,
            requirement_id=None,
            ai_task_id=ai_task.id,
            target_framework="pytest",
            title="pytest draft for expired coupon",
            draft_code="def test_expired_coupon():\n    assert True\n",
            draft_language="python",
            suggested_file_path="tests/test_coupon_checkout.py",
            execution_notes="Run with pytest after approval.",
            risk_notes="Uses mock fixture names.",
        )
        session.add(draft)
        session.commit()
        persisted = session.scalar(select(AutomationDraft).where(AutomationDraft.id == draft.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.test_case_id == test_case.id
    assert persisted.target_framework == "pytest"
    assert persisted.draft_language == "python"
    assert persisted.execution_strategy == "artifact_runtime_copy"
    assert persisted.approval_required is True
    assert persisted.status == "draft_generated"
    assert persisted.runtime_artifact_id is None
    assert persisted.promoted_artifact_id is None


def test_automation_draft_read_schema_uses_contract_field_names() -> None:
    draft_id = uuid.uuid4()
    project_id = uuid.uuid4()
    test_case_id = uuid.uuid4()
    ai_task_id = uuid.uuid4()

    read = AutomationDraftRead(
        id=draft_id,
        project_id=project_id,
        test_case_id=test_case_id,
        requirement_id=None,
        ai_task_id=ai_task_id,
        target_framework="pytest",
        title="pytest draft for expired coupon",
        draft_code="def test_expired_coupon():\n    assert True\n",
        draft_language="python",
        suggested_file_path="tests/test_coupon_checkout.py",
        execution_notes="Run with pytest after approval.",
        risk_notes="Uses mock fixture names.",
        execution_strategy="artifact_runtime_copy",
        approval_required=True,
        status="draft_generated",
        review_comment=None,
        runtime_artifact_id=None,
        promoted_artifact_id=None,
    )

    body = read.model_dump(mode="json")
    assert body["id"] == str(draft_id)
    assert body["test_case_id"] == str(test_case_id)
    assert body["draft_code"].startswith("def test_expired_coupon")
    assert body["execution_strategy"] == "artifact_runtime_copy"
    assert body["approval_required"] is True


def test_create_automation_draft_from_reviewed_test_case(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    with SessionLocal() as session:
        project, test_case, _ai_task = seed_project_case_and_task(session)
        session.commit()
        project_id = project.id
        test_case_id = test_case.id

    response = client.post(
        "/api/automation/drafts",
        json_body={
            "project_id": str(project_id),
            "test_case_id": str(test_case_id),
            "requirement_id": None,
            "target_framework": "pytest",
            "prompt_version": "automation_draft_generation:v1",
            "skill_version": "automation-draft-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-automation-draft",
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["automation_draft_id"]
    assert body["ai_task_id"]
    assert body["status"] == "draft_generated"

    with SessionLocal() as session:
        draft = session.get(AutomationDraft, uuid.UUID(body["automation_draft_id"]))
        ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
        assert draft is not None
        assert ai_task is not None
        assert draft.project_id == project_id
        assert draft.test_case_id == test_case_id
        assert draft.ai_task_id == ai_task.id
        assert draft.status == "draft_generated"
        assert draft.target_framework == "pytest"
        assert draft.suggested_file_path == "tests/test_expired_coupon_cannot_submit_order.py"
        assert "Expired coupon cannot submit order" in draft.draft_code
        assert draft.execution_strategy == "artifact_runtime_copy"
        assert draft.approval_required is True
        assert draft.runtime_artifact_id is None
        assert draft.promoted_artifact_id is None
        assert ai_task.agent_name == "AutomationDraftAgent"
        assert ai_task.status == "succeeded"


def create_draft_via_api(client: ASGIClient, SessionLocal: sessionmaker[Session]) -> uuid.UUID:
    with SessionLocal() as session:
        project, test_case, _ai_task = seed_project_case_and_task(session)
        session.commit()
        project_id = project.id
        test_case_id = test_case.id

    response = client.post(
        "/api/automation/drafts",
        json_body={
            "project_id": str(project_id),
            "test_case_id": str(test_case_id),
            "requirement_id": None,
            "target_framework": "pytest",
            "prompt_version": "automation_draft_generation:v1",
            "skill_version": "automation-draft-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-automation-draft",
        },
    )
    assert response.status_code == 202
    return uuid.UUID(response.json()["automation_draft_id"])


def test_get_edit_and_approve_automation_draft(api_client: tuple[ASGIClient, sessionmaker[Session]]) -> None:
    client, SessionLocal = api_client
    draft_id = create_draft_via_api(client, SessionLocal)

    get_response = client.get(f"/api/automation/drafts/{draft_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["id"] == str(draft_id)
    assert body["status"] == "draft_generated"
    assert body["draft_code"].startswith("def test_expired_coupon")

    edit_response = client.patch(
        f"/api/automation/drafts/{draft_id}",
        json_body={
            "draft_code": "def test_expired_coupon_reviewed():\n    assert True\n",
            "suggested_file_path": "tests/test_coupon_reviewed.py",
            "execution_notes": "Reviewed but not executed.",
            "risk_notes": "Fixture names still need local confirmation.",
            "review_comment": "Adjusted naming before approval.",
        },
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["status"] == "edited"

    approve_response = client.post(
        f"/api/automation/drafts/{draft_id}/approve",
        json_body={"action": "approve", "review_comment": "Draft is safe to execute later."},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    with SessionLocal() as session:
        draft = session.get(AutomationDraft, draft_id)
        assert draft is not None
        assert draft.status == "approved"
        assert draft.draft_code.startswith("def test_expired_coupon_reviewed")
        assert draft.suggested_file_path == "tests/test_coupon_reviewed.py"
        assert draft.review_comment == "Draft is safe to execute later."
        assert draft.runtime_artifact_id is None
        assert draft.promoted_artifact_id is None
        history = {
            (item.action, item.from_status, item.to_status, item.comment)
            for item in session.scalars(
                select(ReviewHistory).where(
                    ReviewHistory.entity_type == "AutomationDraft",
                    ReviewHistory.entity_id == draft_id,
                ),
            )
        }

    assert history == {
        ("edit", "draft_generated", "edited", "Adjusted naming before approval."),
        ("approve", "edited", "approved", "Draft is safe to execute later."),
    }


def test_invalid_automation_draft_approve_action_returns_error(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    draft_id = create_draft_via_api(client, SessionLocal)

    response = client.post(
        f"/api/automation/drafts/{draft_id}/approve",
        json_body={"action": "reject", "review_comment": "No."},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "AUTOMATION_DRAFT_INVALID_ACTION"
