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
    CICDQualityReportRead,
    CICDQualityReportRequest,
    CICDRegressionRunRead,
    CICDRegressionRunRequest,
    CICDRegressionSelectRead,
    CICDRegressionSelectRequest,
    CICDRunRead,
    CICDRunNewTestsRead,
    CICDRunNewTestsRequest,
    QualityGateComputeRequest,
    QualityGateDecisionRead,
    UnitTestPatchApplyRead,
    UnitTestPatchApplyRequest,
    UnitTestPatchGenerateRequest,
    UnitTestPatchRead,
    UnitTestPatchReviewRead,
    UnitTestPatchReviewRequest,
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


@router.post(
    "/cicd/runs/{cicd_run_id}/unit-test-patches",
    response_model=UnitTestPatchRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def generate_unit_test_patch(
    cicd_run_id: uuid.UUID,
    data: UnitTestPatchGenerateRequest,
    session: Session = Depends(get_session),
) -> UnitTestPatchRead:
    try:
        patch = service.generate_unit_test_patch(session, cicd_run_id, data)
    except service.CICDRunNotFoundError as exc:
        raise not_found("CICD_RUN_NOT_FOUND", "CI/CD run not found.") from exc
    return unit_test_patch_read(patch)


@router.post("/cicd/unit-test-patches/{unit_test_patch_id}/approve", response_model=UnitTestPatchReviewRead)
def approve_unit_test_patch(
    unit_test_patch_id: uuid.UUID,
    data: UnitTestPatchReviewRequest,
    session: Session = Depends(get_session),
) -> UnitTestPatchReviewRead:
    try:
        patch = service.approve_unit_test_patch(session, unit_test_patch_id, data.review_comment)
    except service.UnitTestPatchNotFoundError as exc:
        raise not_found("UNIT_TEST_PATCH_NOT_FOUND", "Unit test patch not found.") from exc
    except service.UnitTestPatchInvalidStatusError as exc:
        raise bad_request("UNIT_TEST_PATCH_INVALID_STATUS", "Unit test patch status does not allow this action.") from exc
    return UnitTestPatchReviewRead(unit_test_patch_id=patch.id, status=patch.status)


@router.post("/cicd/unit-test-patches/{unit_test_patch_id}/reject", response_model=UnitTestPatchReviewRead)
def reject_unit_test_patch(
    unit_test_patch_id: uuid.UUID,
    data: UnitTestPatchReviewRequest,
    session: Session = Depends(get_session),
) -> UnitTestPatchReviewRead:
    try:
        patch = service.reject_unit_test_patch(session, unit_test_patch_id, data.review_comment)
    except service.UnitTestPatchNotFoundError as exc:
        raise not_found("UNIT_TEST_PATCH_NOT_FOUND", "Unit test patch not found.") from exc
    except service.UnitTestPatchInvalidStatusError as exc:
        raise bad_request("UNIT_TEST_PATCH_INVALID_STATUS", "Unit test patch status does not allow this action.") from exc
    return UnitTestPatchReviewRead(unit_test_patch_id=patch.id, status=patch.status)


@router.post("/cicd/unit-test-patches/{unit_test_patch_id}/apply", response_model=UnitTestPatchApplyRead)
def apply_unit_test_patch(
    unit_test_patch_id: uuid.UUID,
    data: UnitTestPatchApplyRequest,
    session: Session = Depends(get_session),
) -> UnitTestPatchApplyRead:
    if not data.confirm_scope_gate_result:
        raise bad_request("PATCH_SCOPE_CONFIRMATION_REQUIRED", "Patch scope gate confirmation is required.")
    try:
        patch, artifact = service.apply_unit_test_patch(session, unit_test_patch_id)
    except service.UnitTestPatchNotFoundError as exc:
        raise not_found("UNIT_TEST_PATCH_NOT_FOUND", "Unit test patch not found.") from exc
    except service.UnitTestPatchInvalidStatusError as exc:
        raise bad_request("UNIT_TEST_PATCH_INVALID_STATUS", "Unit test patch status does not allow this action.") from exc
    except service.PatchScopeRejectedError as exc:
        raise bad_request("PATCH_SCOPE_REJECTED", "Unit test patch modifies paths outside allowed test directories.") from exc
    return UnitTestPatchApplyRead(unit_test_patch_id=patch.id, status=patch.status, applied_artifact_id=artifact.id)


@router.post("/cicd/runs/{cicd_run_id}/run-new-tests", response_model=CICDRunNewTestsRead, status_code=status.HTTP_202_ACCEPTED)
def run_new_tests(
    cicd_run_id: uuid.UUID,
    data: CICDRunNewTestsRequest,
    session: Session = Depends(get_session),
) -> CICDRunNewTestsRead:
    try:
        test_run = service.run_new_tests(session, cicd_run_id, data)
    except service.CICDRunNotFoundError as exc:
        raise not_found("CICD_RUN_NOT_FOUND", "CI/CD run not found.") from exc
    except service.UnitTestPatchNotFoundError as exc:
        raise not_found("UNIT_TEST_PATCH_NOT_FOUND", "Unit test patch not found.") from exc
    except service.UnitTestPatchInvalidStatusError as exc:
        raise bad_request("UNIT_TEST_PATCH_INVALID_STATUS", "Unit test patch status does not allow this action.") from exc
    except service.TestCommandInvalidError as exc:
        raise bad_request("TEST_COMMAND_INVALID", "Test command is not allowed for this CI/CD run.") from exc
    return CICDRunNewTestsRead(test_run_id=test_run.id, cicd_run_id=cicd_run_id, status=test_run.status)


@router.post("/cicd/runs/{cicd_run_id}/select-regression", response_model=CICDRegressionSelectRead)
def select_regression(
    cicd_run_id: uuid.UUID,
    data: CICDRegressionSelectRequest,
    session: Session = Depends(get_session),
) -> CICDRegressionSelectRead:
    try:
        artifact, command_ids, reasons = service.select_regression(session, cicd_run_id, data)
    except service.CICDRunNotFoundError as exc:
        raise not_found("CICD_RUN_NOT_FOUND", "CI/CD run not found.") from exc
    except service.TestCommandInvalidError as exc:
        raise bad_request("TEST_COMMAND_INVALID", "Test command is not allowed for this CI/CD run.") from exc
    return CICDRegressionSelectRead(
        cicd_run_id=cicd_run_id,
        regression_plan_artifact_id=artifact.id,
        recommended_test_command_ids=command_ids,
        reasons=reasons,
    )


@router.post("/cicd/runs/{cicd_run_id}/run-regression", response_model=CICDRegressionRunRead, status_code=status.HTTP_202_ACCEPTED)
def run_regression(
    cicd_run_id: uuid.UUID,
    data: CICDRegressionRunRequest,
    session: Session = Depends(get_session),
) -> CICDRegressionRunRead:
    try:
        test_runs = service.run_regression(session, cicd_run_id, data)
    except service.CICDRunNotFoundError as exc:
        raise not_found("CICD_RUN_NOT_FOUND", "CI/CD run not found.") from exc
    except service.RegressionPlanInvalidError as exc:
        raise bad_request("REGRESSION_PLAN_INVALID", "Regression plan is invalid for this CI/CD run.") from exc
    except service.TestCommandInvalidError as exc:
        raise bad_request("TEST_COMMAND_INVALID", "Test command is not allowed for this CI/CD run.") from exc
    return CICDRegressionRunRead(cicd_run_id=cicd_run_id, test_run_ids=[test_run.id for test_run in test_runs], status="tests_running")


@router.post("/cicd/runs/{cicd_run_id}/quality-gate", response_model=QualityGateDecisionRead)
def compute_quality_gate(
    cicd_run_id: uuid.UUID,
    data: QualityGateComputeRequest,
    session: Session = Depends(get_session),
) -> QualityGateDecisionRead:
    try:
        decision = service.compute_quality_gate(session, cicd_run_id, data)
    except service.CICDRunNotFoundError as exc:
        raise not_found("CICD_RUN_NOT_FOUND", "CI/CD run not found.") from exc
    return quality_gate_decision_read(decision)


@router.post("/cicd/runs/{cicd_run_id}/generate-report", response_model=CICDQualityReportRead, status_code=status.HTTP_202_ACCEPTED)
def generate_cicd_quality_report(
    cicd_run_id: uuid.UUID,
    data: CICDQualityReportRequest,
    session: Session = Depends(get_session),
) -> CICDQualityReportRead:
    try:
        report, manifest_artifact = service.generate_cicd_quality_report(session, cicd_run_id, data)
    except service.CICDRunNotFoundError as exc:
        raise not_found("CICD_RUN_NOT_FOUND", "CI/CD run not found.") from exc
    except service.QualityGateDecisionMissingError as exc:
        raise bad_request("QUALITY_GATE_DECISION_MISSING", "Quality gate decision is required before report generation.") from exc
    return CICDQualityReportRead(
        report_id=report.id,
        cicd_run_id=cicd_run_id,
        status="generating",
        evidence_manifest_artifact_id=manifest_artifact.id,
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


def quality_gate_decision_read(decision) -> QualityGateDecisionRead:
    return QualityGateDecisionRead(
        id=decision.id,
        project_id=decision.project_id,
        cicd_run_id=decision.cicd_run_id,
        status=decision.status,
        summary=decision.summary,
        blocking_reasons=decision.blocking_reasons_json,
        evidence_artifact_ids=decision.evidence_artifact_ids,
        decided_by=decision.decided_by,
        status_detail=decision.status_detail_json,
    )


def unit_test_patch_read(patch) -> UnitTestPatchRead:
    return UnitTestPatchRead(
        id=patch.id,
        cicd_run_id=patch.cicd_run_id,
        ai_task_id=patch.ai_task_id,
        patch_text=patch.patch_text,
        target_framework=patch.target_framework,
        scope_gate_result=patch.scope_gate_result_json,
        test_intent=patch.test_intent,
        coverage_target=patch.coverage_target_json,
        status=patch.status,
        review_comment=patch.review_comment,
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
