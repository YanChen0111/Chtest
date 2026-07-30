from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.projects.router import get_session
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.router import get_artifact_store
from backend.app.modules.reporting import service
from backend.app.modules.reporting.models import FailureAnalysis
from backend.app.modules.reporting.schemas import (
    FailureAnalysisCreateRead,
    FailureAnalysisCreateRequest,
    FailureAnalysisRead,
    ReportCreateRead,
    ReportCreateRequest,
    ReportRead,
    ReportReviewWorkflowActionRequest,
    ReportReviewWorkflowContinueRequest,
    ReportReviewWorkflowEditRequest,
    ReportReviewWorkflowRead,
)
from backend.app.modules.workflow_control.policy import ApprovalDecision, TransitionPolicyError


router = APIRouter(tags=["reporting"])


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
    "/test-runs/{test_run_id}/failure-analysis",
    response_model=FailureAnalysisCreateRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_failure_analysis(
    test_run_id: uuid.UUID,
    data: FailureAnalysisCreateRequest,
    session: Session = Depends(get_session),
) -> FailureAnalysisCreateRead:
    try:
        analysis = service.create_failure_analysis(session, test_run_id, data)
    except service.TestRunNotFoundError as exc:
        raise not_found("TEST_RUN_NOT_FOUND", "Test run not found.") from exc
    except service.ExecutionResultReviewApprovalRequiredError as exc:
        raise bad_request(
            "EXECUTION_RESULT_REVIEW_APPROVAL_REQUIRED",
            "ExecutionResultReview approval is required before failure analysis.",
        ) from exc
    return FailureAnalysisCreateRead(
        ai_task_id=analysis.ai_task_id,
        failure_analysis_id=analysis.id,
        status=analysis.status,
    )


@router.get("/test-runs/{test_run_id}/failure-analysis", response_model=FailureAnalysisRead)
def get_failure_analysis(
    test_run_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> FailureAnalysisRead:
    try:
        analysis = service.get_failure_analysis(session, test_run_id)
    except service.TestRunNotFoundError as exc:
        raise not_found("TEST_RUN_NOT_FOUND", "Test run not found.") from exc
    except service.FailureAnalysisNotFoundError as exc:
        raise not_found("FAILURE_ANALYSIS_NOT_FOUND", "Failure analysis not found.") from exc
    return failure_analysis_read(analysis)


@router.post("/reports", response_model=ReportCreateRead, status_code=status.HTTP_202_ACCEPTED)
def create_report(
    data: ReportCreateRequest,
    session: Session = Depends(get_session),
    store: LocalArtifactStore = Depends(get_artifact_store),
) -> ReportCreateRead:
    try:
        report, evidence_manifest_artifact_id = service.create_report(session, data, store=store)
    except service.ReportInvalidInputError as exc:
        raise bad_request("REPORT_INVALID_INPUT", "Report input is invalid.") from exc
    except service.ExecutionResultReviewApprovalRequiredError as exc:
        raise bad_request(
            "EXECUTION_RESULT_REVIEW_APPROVAL_REQUIRED",
            "ExecutionResultReview approval is required before report generation.",
        ) from exc
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc
    return ReportCreateRead(
        report_id=report.id,
        status=report.status,
        evidence_manifest_artifact_id=evidence_manifest_artifact_id,
    )


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(
    report_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ReportRead:
    try:
        report = service.get_report(session, report_id)
    except service.ReportNotFoundError as exc:
        raise not_found("REPORT_NOT_FOUND", "Report not found.") from exc
    return ReportRead(
        id=report.id,
        project_id=report.project_id,
        report_type=report.report_type,
        title=report.title,
        related_entity_type=report.related_entity_type,
        related_entity_id=report.related_entity_id,
        status=report.status,
        conclusion=report.conclusion,
        summary=report.summary,
        metrics=report.metrics_json,
        artifact_ids=report.artifact_ids,
        evidence_manifest=service.report_evidence_manifest(session, report),
        artifacts=service.report_artifacts_for_report(session, report),
    )


@router.get(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/report-review",
    response_model=ReportReviewWorkflowRead,
)
def read_report_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ReportReviewWorkflowRead:
    try:
        return service.get_report_review_workflow_detail(session, project_id, requirement_review_id)
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/report-review/submit",
    response_model=ReportReviewWorkflowRead,
)
def submit_report_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ReportReviewWorkflowRead:
    try:
        return service.submit_report_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/report-review/complete-review",
    response_model=ReportReviewWorkflowRead,
)
def complete_report_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ReportReviewWorkflowRead:
    try:
        return service.complete_report_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/report-review/edit",
    response_model=ReportReviewWorkflowRead,
)
def edit_report_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowEditRequest,
    session: Session = Depends(get_session),
) -> ReportReviewWorkflowRead:
    try:
        return service.edit_report_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/report-review/approve",
    response_model=ReportReviewWorkflowRead,
)
def approve_report_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ReportReviewWorkflowRead:
    try:
        return service.decide_report_review_workflow(
            session,
            project_id,
            requirement_review_id,
            data,
            decision=ApprovalDecision.APPROVED,
        )
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/report-review/reject",
    response_model=ReportReviewWorkflowRead,
)
def reject_report_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ReportReviewWorkflowRead:
    try:
        return service.decide_report_review_workflow(
            session,
            project_id,
            requirement_review_id,
            data,
            decision=ApprovalDecision.REJECTED,
        )
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/report-review/continue",
    response_model=ReportReviewWorkflowRead,
)
def continue_report_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowContinueRequest,
    session: Session = Depends(get_session),
) -> ReportReviewWorkflowRead:
    try:
        return service.continue_report_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.ReportReviewApprovalRequiredError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


@router.post(
    "/projects/{project_id}/requirement-reviews/{requirement_review_id}/report-review/approve-and-continue",
    response_model=ReportReviewWorkflowRead,
)
def approve_and_continue_report_review_workflow(
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
    session: Session = Depends(get_session),
) -> ReportReviewWorkflowRead:
    try:
        return service.approve_and_continue_report_review_workflow(session, project_id, requirement_review_id, data)
    except (
        service.ReportReviewWorkflowStageError,
        service.ReportReviewGateError,
        service.ReportReviewApprovalRequiredError,
        service.WorkflowPersistenceError,
        TransitionPolicyError,
    ) as exc:
        raise workflow_error(exc) from exc


def failure_analysis_read(analysis: FailureAnalysis) -> FailureAnalysisRead:
    return FailureAnalysisRead(
        id=analysis.id,
        project_id=analysis.project_id,
        test_run_id=analysis.test_run_id,
        test_result_id=analysis.test_result_id,
        ai_task_id=analysis.ai_task_id,
        classification=analysis.classification,
        confidence=float(analysis.confidence),
        evidence_artifact_ids=analysis.evidence_artifact_ids,
        summary=analysis.summary,
        root_cause=analysis.root_cause,
        suggested_actions=analysis.suggested_actions_json,
        status=analysis.status,
    )
