from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.modules.cicd import service
from backend.app.modules.cicd.models import CICDChangedFile, CICDRun
from backend.app.modules.cicd.schemas import (
    CICDChangedFileRead,
    CICDRunAnalyzeRead,
    CICDRunAnalyzeRequest,
    CICDRunCreateRead,
    CICDRunCreateRequest,
    CICDRunListRead,
    CICDRunRead,
)
from backend.app.modules.projects.router import get_session


router = APIRouter(tags=["cicd"])


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


@router.post("/cicd/runs", response_model=CICDRunCreateRead, status_code=status.HTTP_202_ACCEPTED)
def create_cicd_run(
    data: CICDRunCreateRequest,
    session: Session = Depends(get_session),
) -> CICDRunCreateRead:
    try:
        cicd_run = service.create_cicd_run(session, data)
    except service.ProjectNotFoundError as exc:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.") from exc
    except (service.RepositoryInvalidError, service.CICDRunInvalidInputError) as exc:
        raise bad_request("CICD_RUN_INVALID_INPUT", "CI/CD run input is invalid.") from exc
    return CICDRunCreateRead(cicd_run_id=cicd_run.id, status=cicd_run.status)


@router.get("/cicd/runs", response_model=CICDRunListRead)
def list_cicd_runs(session: Session = Depends(get_session)) -> CICDRunListRead:
    items = [cicd_run_read(session, cicd_run) for cicd_run in service.list_cicd_runs(session)]
    return CICDRunListRead(items=items, total=len(items))


@router.get("/cicd/runs/{cicd_run_id}", response_model=CICDRunRead)
def get_cicd_run(
    cicd_run_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> CICDRunRead:
    try:
        return cicd_run_read(session, service.get_cicd_run(session, cicd_run_id))
    except service.CICDRunNotFoundError as exc:
        raise not_found("CICD_RUN_NOT_FOUND", "CI/CD run not found.") from exc


@router.post("/cicd/runs/{cicd_run_id}/analyze", response_model=CICDRunAnalyzeRead, status_code=status.HTTP_202_ACCEPTED)
def analyze_cicd_run(
    cicd_run_id: uuid.UUID,
    data: CICDRunAnalyzeRequest,
    session: Session = Depends(get_session),
) -> CICDRunAnalyzeRead:
    try:
        cicd_run, ai_task, artifact = service.analyze_cicd_run(session, cicd_run_id, data)
    except service.CICDRunNotFoundError as exc:
        raise not_found("CICD_RUN_NOT_FOUND", "CI/CD run not found.") from exc
    return CICDRunAnalyzeRead(
        cicd_run_id=cicd_run.id,
        ai_task_id=ai_task.id,
        risk_analysis_artifact_id=artifact.id,
        status=cicd_run.status,
    )


def cicd_run_read(session: Session, cicd_run: CICDRun) -> CICDRunRead:
    return CICDRunRead(
        id=cicd_run.id,
        project_id=cicd_run.project_id,
        repository_id=cicd_run.repository_id,
        source_type=cicd_run.source_type,
        trigger_type=cicd_run.trigger_type,
        provider=cicd_run.provider,
        pipeline_name=cicd_run.pipeline_name,
        base_ref=cicd_run.base_ref,
        head_ref=cicd_run.head_ref,
        summary=cicd_run.summary,
        overall_risk=cicd_run.overall_risk,
        quality_gate_status=cicd_run.quality_gate_status,
        status=cicd_run.status,
        changed_files=[changed_file_read(changed_file) for changed_file in cicd_run.changed_files],
        analysis_artifacts=service.analysis_artifacts_for_run(session, cicd_run),
    )


def changed_file_read(changed_file: CICDChangedFile) -> CICDChangedFileRead:
    return CICDChangedFileRead(
        id=changed_file.id,
        cicd_run_id=changed_file.cicd_run_id,
        path=changed_file.path,
        old_path=changed_file.old_path,
        change_type=changed_file.change_type,
        language=changed_file.language,
        file_role=changed_file.file_role,
        risk_level=changed_file.risk_level,
        risk_reasons=changed_file.risk_reasons_json,
        lines_added=changed_file.lines_added,
        lines_deleted=changed_file.lines_deleted,
    )
