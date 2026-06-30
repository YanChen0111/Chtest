from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.projects.router import get_session
from backend.app.modules.reporting import service
from backend.app.modules.reporting.models import FailureAnalysis
from backend.app.modules.reporting.schemas import (
    FailureAnalysisCreateRead,
    FailureAnalysisCreateRequest,
    FailureAnalysisRead,
)


router = APIRouter(tags=["reporting"])


def not_found(error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": error_code, "message": message, "details": {}},
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
