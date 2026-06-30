from __future__ import annotations

import re
import uuid

from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.automation.schemas import (
    AutomationDraftApproveRequest,
    AutomationDraftCreateRequest,
    AutomationDraftEditRequest,
)
from backend.app.modules.cases.models import TestCase
from backend.app.modules.projects.models import Project
from backend.app.modules.requirements.models import Requirement


class ProjectNotFoundError(Exception):
    pass


class TestCaseNotFoundError(Exception):
    pass


class RequirementNotFoundError(Exception):
    pass


class AutomationDraftInvalidInputError(Exception):
    pass


class AutomationDraftNotFoundError(Exception):
    pass


class AutomationDraftInvalidActionError(Exception):
    pass


def create_automation_draft(session: Session, data: AutomationDraftCreateRequest) -> tuple[AutomationDraft, AITask]:
    project = session.get(Project, data.project_id)
    if project is None:
        raise ProjectNotFoundError
    test_case = None
    if data.test_case_id is not None:
        test_case = session.get(TestCase, data.test_case_id)
        if test_case is None or test_case.project_id != data.project_id:
            raise TestCaseNotFoundError
    requirement = None
    if data.requirement_id is not None:
        requirement = session.get(Requirement, data.requirement_id)
        if requirement is None or requirement.project_id != data.project_id:
            raise RequirementNotFoundError
    if test_case is None and requirement is None:
        raise AutomationDraftInvalidInputError

    source_title = test_case.title if test_case is not None else requirement.title
    ai_task = AITask(
        project_id=data.project_id,
        agent_name="AutomationDraftAgent",
        task_type="automation_draft_generation",
        prompt_version_id=uuid.uuid5(uuid.NAMESPACE_URL, data.prompt_version),
        skill_version_id=uuid.uuid5(uuid.NAMESPACE_URL, data.skill_version),
        model_provider=data.model_provider,
        model_name=data.model_name,
        status="succeeded",
        input_json={
            "test_case_id": str(data.test_case_id) if data.test_case_id is not None else None,
            "requirement_id": str(data.requirement_id) if data.requirement_id is not None else None,
            "target_framework": data.target_framework,
        },
        output_json={"draft_title": source_title},
    )
    session.add(ai_task)
    session.flush()

    draft = AutomationDraft(
        project_id=data.project_id,
        test_case_id=data.test_case_id,
        requirement_id=data.requirement_id,
        ai_task_id=ai_task.id,
        target_framework=data.target_framework,
        title=f"{data.target_framework} draft for {source_title}",
        draft_code=mock_draft_code(source_title),
        draft_language="python" if data.target_framework == "pytest" else "typescript",
        suggested_file_path=suggested_file_path(source_title, data.target_framework),
        execution_notes="Review and approve this draft before any controlled execution.",
        risk_notes="Mock draft uses placeholder fixtures and must be reviewed before execution.",
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)
    session.refresh(ai_task)
    return draft, ai_task


def get_automation_draft(session: Session, draft_id: uuid.UUID) -> AutomationDraft:
    draft = session.get(AutomationDraft, draft_id)
    if draft is None:
        raise AutomationDraftNotFoundError
    return draft


def edit_automation_draft(session: Session, draft_id: uuid.UUID, data: AutomationDraftEditRequest) -> AutomationDraft:
    draft = get_automation_draft(session, draft_id)
    if draft.status == "approved":
        raise AutomationDraftInvalidActionError
    draft.draft_code = data.draft_code
    draft.suggested_file_path = data.suggested_file_path
    draft.execution_notes = data.execution_notes
    draft.risk_notes = data.risk_notes
    draft.review_comment = data.review_comment
    draft.status = "edited"
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft


def approve_automation_draft(session: Session, draft_id: uuid.UUID, data: AutomationDraftApproveRequest) -> AutomationDraft:
    draft = get_automation_draft(session, draft_id)
    if data.action != "approve" or draft.status not in {"draft_generated", "edited"}:
        raise AutomationDraftInvalidActionError
    draft.status = "approved"
    draft.review_comment = data.review_comment
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft


def mock_draft_code(title: str) -> str:
    test_name = slug(title)
    return f"def test_{test_name}():\n    # Draft generated from reviewed TestCase: {title}\n    assert True\n"


def suggested_file_path(title: str, target_framework: str) -> str:
    extension = "py" if target_framework == "pytest" else "spec.ts"
    return f"tests/test_{slug(title)}.{extension}"


def slug(value: str) -> str:
    slugged = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slugged or "automation_draft"
