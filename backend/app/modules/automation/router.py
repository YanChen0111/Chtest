from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.automation import service
from backend.app.modules.automation.schemas import AutomationDraftCreateRead, AutomationDraftCreateRequest
from backend.app.modules.projects.router import get_session


router = APIRouter(tags=["automation"])


def not_found(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def bad_request(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


@router.post(
    "/automation/drafts",
    response_model=AutomationDraftCreateRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_automation_draft(
    data: AutomationDraftCreateRequest,
    session: Session = Depends(get_session),
) -> AutomationDraftCreateRead:
    try:
        draft, ai_task = service.create_automation_draft(session, data)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.TestCaseNotFoundError as exc:
        raise not_found("TEST_CASE_NOT_FOUND", "Test case not found.") from exc
    except service.RequirementNotFoundError as exc:
        raise not_found("REQUIREMENT_NOT_FOUND", "Requirement not found.") from exc
    except service.AutomationDraftInvalidInputError as exc:
        raise bad_request("AUTOMATION_DRAFT_INVALID_INPUT", "TestCase or Requirement reference is required.") from exc

    return AutomationDraftCreateRead(
        automation_draft_id=draft.id,
        ai_task_id=ai_task.id,
        status=draft.status,
    )
