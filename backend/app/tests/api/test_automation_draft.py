from __future__ import annotations

import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.automation.schemas import AutomationDraftRead
from backend.app.modules.cases.models import TestCase as CaseModel
from backend.app.modules.projects.models import Project, Workspace


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


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
