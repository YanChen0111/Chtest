from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.cases import service
from backend.app.modules.cases.schemas import (
    CaseGenerationStartRead,
    CaseGenerationStartRequest,
    CaseGenerationTaskRead,
    CaseMetricsRead,
    CaseReviewRead,
    CaseReviewRequest,
    CaseReviewWorkflowActionRequest,
    CaseReviewWorkflowContinueRequest,
    CaseReviewWorkflowEditRequest,
    CaseReviewWorkflowRead,
    GeneratedCaseCandidateListRead,
    TestCaseListRead,
    TestCaseImportRead,
    TestCaseImportRequest,
    TestCaseStatusUpdateRequest,
)
from backend.app.modules.projects.router import get_session
from backend.app.modules.workflow_control.policy import ApprovalDecision, TransitionPolicyError


router = APIRouter(tags=["cases"])


def not_found(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def schema_invalid() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "error_code": "CASE_GENERATION_SCHEMA_INVALID",
            "message": "Case generation output did not match the expected schema.",
            "details": {},
        },
    )


def conflict(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def bad_request(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error_code": error_code, "message": message, "details": {}},
    )


def workflow_error(exc: Exception) -> HTTPException:
    error_code = getattr(exc, "code", exc.__class__.__name__.replace("Error", "").upper())
    status_code = (
        status.HTTP_404_NOT_FOUND
        if error_code in {"WORKFLOW_RUN_NOT_FOUND", "WORKFLOW_PROJECT_NOT_FOUND"}
        else status.HTTP_409_CONFLICT
    )
    return HTTPException(
        status_code=status_code,
        detail={"error_code": error_code, "message": "Workflow action was rejected.", "details": {}},
    )


@router.post(
    "/case-generation/tasks",
    response_model=CaseGenerationStartRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_case_generation(
    data: CaseGenerationStartRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> CaseGenerationStartRead:
    try:
        generation_task, ai_task = service.start_case_generation(session, store, data)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except service.RequirementNotFoundError as exc:
        raise not_found("REQUIREMENT_NOT_FOUND", "Requirement not found.") from exc
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except service.RequirementDocumentNotFoundError as exc:
        raise not_found("REQUIREMENT_DOCUMENT_NOT_FOUND", "Requirement document not found.") from exc
    except (service.PromptVersionNotFoundError, service.SkillVersionNotFoundError) as exc:
        raise not_found("PROMPT_OR_SKILL_NOT_FOUND", "Prompt or skill version not found.") from exc
    except service.ContextArtifactNotFoundError as exc:
        raise not_found("CONTEXT_ARTIFACT_NOT_FOUND", "Context artifact not found in this project.") from exc
    except service.CaseGenerationDecisionTableRequiredError as exc:
        raise bad_request(
            "CASE_GENERATION_DECISION_TABLE_REQUIRED",
            "Case generation requires pre-generation decision table acknowledgement.",
        ) from exc
    background_tasks.add_task(run_case_generation_background, session.get_bind(), generation_task.id, str(store.root))

    return CaseGenerationStartRead(
        case_generation_task_id=generation_task.id,
        ai_task_id=ai_task.id,
        status="pending",
        used_knowledge=bool(ai_task.input_json.get("knowledge_retrieval", {}).get("used_knowledge", False)),
        used_context_artifact_ids=[
            uuid.UUID(str(context_id))
            for context_id in ai_task.input_json.get("knowledge_retrieval", {}).get(
                "used_context_artifact_ids",
                ai_task.context_artifact_ids,
            )
        ],
    )

def run_case_generation_background(bind: object, generation_task_id: uuid.UUID, artifact_root: str) -> None:
    session_factory = sessionmaker(bind, expire_on_commit=False, future=True)
    with session_factory() as session:
        service.run_case_generation_task(session, LocalArtifactStore(root=artifact_root), generation_task_id)


@router.get(
    "/case-generation/tasks/{generation_task_id}",
    response_model=CaseGenerationTaskRead,
)
def read_case_generation_task(
    generation_task_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> CaseGenerationTaskRead:
    try:
        return service.read_case_generation_task(session, generation_task_id)
    except service.CaseGenerationTaskNotFoundError as exc:
        raise not_found("CASE_GENERATION_TASK_NOT_FOUND", "Case generation task not found.") from exc


@router.get(
    "/case-generation/tasks/{generation_task_id}/candidates",
    response_model=GeneratedCaseCandidateListRead,
)
def list_candidates(
    generation_task_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> GeneratedCaseCandidateListRead:
    try:
        items = service.list_candidates(session, generation_task_id)
    except service.CaseGenerationTaskNotFoundError as exc:
        raise not_found("CASE_GENERATION_TASK_NOT_FOUND", "Case generation task not found.") from exc
    return GeneratedCaseCandidateListRead(items=items, total=len(items))


@router.get(
    "/case-generation/tasks/{generation_task_id}/metrics",
    response_model=CaseMetricsRead,
)
def get_case_metrics(
    generation_task_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> CaseMetricsRead:
    try:
        return service.calculate_case_metrics(session, generation_task_id)
    except service.CaseGenerationTaskNotFoundError as exc:
        raise not_found("CASE_GENERATION_TASK_NOT_FOUND", "Case generation task not found.") from exc


@router.get("/test-cases", response_model=TestCaseListRead)
def list_test_cases(
    project_id: uuid.UUID,
    module_id: uuid.UUID | None = None,
    status: str | None = None,
    test_type: str | None = None,
    priority: str | None = None,
    keyword: str | None = None,
    session: Session = Depends(get_session),
) -> TestCaseListRead:
    try:
        items = service.list_test_cases(
            session,
            project_id=project_id,
            module_id=module_id,
            status=status,
            test_type=test_type,
            priority=priority,
            keyword=keyword,
        )
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return TestCaseListRead(items=items, total=len(items))


@router.post("/test-cases/import", response_model=TestCaseImportRead, status_code=status.HTTP_201_CREATED)
def import_test_cases(
    data: TestCaseImportRequest,
    session: Session = Depends(get_session),
) -> TestCaseImportRead:
    try:
        imported, skipped = service.import_test_cases(
            session,
            project_id=data.project_id,
            items=[item.model_dump() for item in data.items],
        )
        items = service.list_test_cases(session, project_id=data.project_id)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    return TestCaseImportRead(
        project_id=data.project_id,
        imported_count=len(imported),
        skipped_count=skipped,
        items=[item for item in items if item.id in {case.id for case in imported}],
    )


@router.patch("/test-cases/{case_id}")
def update_test_case_status(
    case_id: uuid.UUID,
    data: TestCaseStatusUpdateRequest,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    try:
        updated = service.update_test_case_status(
            session,
            case_id=case_id,
            project_id=data.project_id,
            status=data.status,
        )
    except service.CaseNotFoundError as exc:
        raise not_found("TEST_CASE_NOT_FOUND", "Test case not found in this project.") from exc
    return {"id": updated.id, "status": updated.status}


@router.post("/case-review/items/{candidate_id}/approve", response_model=CaseReviewRead)
def review_candidate(
    candidate_id: uuid.UUID,
    data: CaseReviewRequest,
    session: Session = Depends(get_session),
) -> CaseReviewRead:
    try:
        candidate, test_case = service.review_candidate(session, candidate_id, data)
    except service.CaseCandidateNotFoundError as exc:
        raise not_found("CASE_CANDIDATE_NOT_FOUND", "Case candidate not found.") from exc
    except service.CaseCandidateAlreadyFinalError as exc:
        raise conflict("CASE_CANDIDATE_ALREADY_FINAL", "Case candidate is already in a final review state.") from exc
    except service.CaseReviewInvalidActionError as exc:
        raise bad_request("CASE_REVIEW_INVALID_ACTION", "Case review action payload is invalid.") from exc

    return CaseReviewRead(
        candidate_id=candidate.id,
        status=candidate.status,
        test_case_id=test_case.id if test_case is not None else None,
    )


@router.get(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/case-review",
    response_model=CaseReviewWorkflowRead,
)
def read_case_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> CaseReviewWorkflowRead:
    try:
        return service.get_case_review_workflow_detail(session, project_id, requirement_review_id)
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (
        service.WorkflowPersistenceError,
        service.CaseReviewWorkflowStageError,
        service.CaseReviewCandidateGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/case-review/submit",
    response_model=CaseReviewWorkflowRead,
)
def submit_case_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: CaseReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> CaseReviewWorkflowRead:
    try:
        return service.submit_case_review_workflow(session, project_id, requirement_review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (
        service.WorkflowPersistenceError,
        service.CaseReviewWorkflowStageError,
        service.CaseReviewCandidateGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/case-review/complete-review",
    response_model=CaseReviewWorkflowRead,
)
def complete_case_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: CaseReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> CaseReviewWorkflowRead:
    try:
        return service.complete_case_review_workflow(session, project_id, requirement_review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (service.WorkflowPersistenceError, service.CaseReviewWorkflowStageError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/case-review/edit",
    response_model=CaseReviewWorkflowRead,
)
def edit_case_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: CaseReviewWorkflowEditRequest,
    session: Session = Depends(get_session),
) -> CaseReviewWorkflowRead:
    try:
        return service.edit_case_review_workflow(session, project_id, requirement_review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (service.WorkflowPersistenceError, service.CaseReviewWorkflowStageError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/case-review/approve",
    response_model=CaseReviewWorkflowRead,
)
def approve_case_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: CaseReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> CaseReviewWorkflowRead:
    try:
        return service.decide_case_review_workflow(
            session,
            project_id,
            requirement_review_id,
            data,
            decision=ApprovalDecision.APPROVED,
        )
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (
        service.WorkflowPersistenceError,
        service.CaseReviewWorkflowStageError,
        service.CaseReviewCandidateGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/case-review/reject",
    response_model=CaseReviewWorkflowRead,
)
def reject_case_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: CaseReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> CaseReviewWorkflowRead:
    try:
        return service.decide_case_review_workflow(
            session,
            project_id,
            requirement_review_id,
            data,
            decision=ApprovalDecision.REJECTED,
        )
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (service.WorkflowPersistenceError, service.CaseReviewWorkflowStageError, TransitionPolicyError) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/case-review/continue",
    response_model=CaseReviewWorkflowRead,
)
def continue_case_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: CaseReviewWorkflowContinueRequest,
    session: Session = Depends(get_session),
) -> CaseReviewWorkflowRead:
    try:
        return service.continue_case_review_workflow(session, project_id, requirement_review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (
        service.WorkflowPersistenceError,
        service.CaseReviewWorkflowStageError,
        service.CaseReviewCandidateGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/case-review/approve-and-continue",
    response_model=CaseReviewWorkflowRead,
)
def approve_and_continue_case_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: CaseReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> CaseReviewWorkflowRead:
    try:
        return service.approve_and_continue_case_review_workflow(session, project_id, requirement_review_id, data)
    except service.RequirementReviewNotFoundError as exc:
        raise not_found("REQUIREMENT_REVIEW_NOT_FOUND", "Requirement review not found.") from exc
    except (
        service.WorkflowPersistenceError,
        service.CaseReviewWorkflowStageError,
        service.CaseReviewCandidateGateError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc
