from __future__ import annotations

import json
import uuid
from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.model_config import resolve_model_identity
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.automation.service import automation_draft_quality_gate
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.requirements.models import Requirement, RequirementReview
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.modules.reporting.schemas import (
    FailureAnalysisCreateRequest,
    ReportCreateRequest,
    ReportReviewWorkflowActionRequest,
    ReportReviewWorkflowContinueRequest,
    ReportReviewWorkflowEditRequest,
    ReportReviewWorkflowRead,
)
from backend.app.modules.workflow_control import service as workflow_service
from backend.app.modules.workflow_control.models import (
    WorkflowHumanDecision,
    WorkflowRun,
    WorkflowStageSnapshot,
    WorkflowTransitionEvent,
)
from backend.app.modules.workflow_control.policy import (
    Actor,
    ApprovalDecision,
    ApprovalGrant,
    ControlledStage,
    GateState,
    TransitionAction,
    WorkflowKind,
)
from backend.app.modules.workflow_control.schemas import (
    HumanApprovalCreate,
    HumanReviewCreate,
    WorkflowRevisionCreate,
)


WorkflowPersistenceError = workflow_service.WorkflowPersistenceError


class TestRunNotFoundError(Exception):
    pass


class FailureAnalysisNotFoundError(Exception):
    pass


class ReportNotFoundError(Exception):
    pass


class ReportInvalidInputError(Exception):
    pass


class ExecutionResultReviewApprovalRequiredError(Exception):
    pass


class ReportReviewWorkflowStageError(Exception):
    code = "REPORT_REVIEW_WORKFLOW_STAGE_REQUIRED"


class ReportReviewGateError(Exception):
    code = "REPORT_REVIEW_ARTIFACT_REQUIRED"


class ReportReviewApprovalRequiredError(Exception):
    code = "REPORT_REVIEW_APPROVAL_REQUIRED"


@dataclass(frozen=True)
class FailureClassification:
    classification: str
    confidence: float
    summary: str
    root_cause: str | None
    suggested_actions: list[str]


def create_failure_analysis(
    session: Session,
    test_run_id: uuid.UUID,
    data: FailureAnalysisCreateRequest,
) -> FailureAnalysis:
    test_run = session.get(TestRun, test_run_id)
    if test_run is None:
        raise TestRunNotFoundError
    require_execution_result_review_approval(
        session,
        test_run,
        data.execution_result_review_decision_id,
    )

    test_results = list(
        session.scalars(
            select(TestResult)
            .where(TestResult.test_run_id == test_run.id)
            .order_by(TestResult.created_at.asc()),
        ),
    )
    artifacts = list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.owner_entity_type == "TestRun",
                Artifact.owner_entity_id == test_run.id,
            )
            .order_by(Artifact.created_at.asc()),
        ),
    )
    evidence_artifact_ids = collect_evidence_artifact_ids(test_results, artifacts)
    classification = classify_failure(test_run, test_results, artifacts)
    model_provider, model_name = resolve_model_identity(
        model_provider=data.model_provider,
        model_name=data.model_name,
        default_provider="mock",
        default_model_name="mock-failure-analysis",
    )

    ai_task = AITask(
        project_id=test_run.project_id,
        agent_name="FailureAnalysisAgent",
        task_type="failure_analysis",
        prompt_version_id=stable_version_uuid(data.prompt_version),
        skill_version_id=stable_version_uuid(data.skill_version),
        model_provider=model_provider,
        model_name=model_name,
        status="succeeded",
        input_json={
            "test_run_id": str(test_run.id),
            "test_result_ids": [str(result.id) for result in test_results],
            "evidence_artifact_ids": [str(artifact_id) for artifact_id in evidence_artifact_ids],
        },
        output_json={
            "classification": classification.classification,
            "confidence": classification.confidence,
            "summary": classification.summary,
            "root_cause": classification.root_cause,
            "suggested_actions": classification.suggested_actions,
        },
    )
    session.add(ai_task)
    session.flush()

    failed_result = next((result for result in test_results if result.status == "failed"), None)
    analysis = FailureAnalysis(
        project_id=test_run.project_id,
        test_run_id=test_run.id,
        test_result_id=failed_result.id if failed_result is not None else None,
        ai_task_id=ai_task.id,
        classification=classification.classification,
        confidence=classification.confidence,
        evidence_artifact_ids=evidence_artifact_ids,
        summary=classification.summary,
        root_cause=classification.root_cause,
        suggested_actions_json=classification.suggested_actions,
        status="draft",
    )
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def get_failure_analysis(session: Session, test_run_id: uuid.UUID) -> FailureAnalysis:
    test_run = session.get(TestRun, test_run_id)
    if test_run is None:
        raise TestRunNotFoundError

    analysis = session.scalar(
        select(FailureAnalysis)
        .where(FailureAnalysis.test_run_id == test_run_id)
        .order_by(FailureAnalysis.created_at.desc()),
    )
    if analysis is None:
        raise FailureAnalysisNotFoundError
    return analysis


def collect_evidence_artifact_ids(test_results: list[TestResult], artifacts: list[Artifact]) -> list[uuid.UUID]:
    ordered_ids: list[uuid.UUID] = []
    for artifact in artifacts:
        ordered_ids.append(artifact.id)
    for result in test_results:
        ordered_ids.extend(result.failure_artifact_ids)
    return list(dict.fromkeys(ordered_ids))


def classify_failure(
    test_run: TestRun,
    test_results: list[TestResult],
    artifacts: list[Artifact],
) -> FailureClassification:
    failed_result = next((result for result in test_results if result.status == "failed"), None)
    if failed_result is None and not artifacts and not has_parsed_failure(test_run):
        return FailureClassification(
            classification="insufficient_evidence",
            confidence=0.0,
            summary="The failed test run does not include stdout, stderr, parsed result, or failed TestResult evidence.",
            root_cause=None,
            suggested_actions=["Attach stdout, stderr, and failed TestResult evidence before analysis."],
        )

    if failed_result is not None and failed_result.failure_message:
        message = failed_result.failure_message.strip()
        lower_message = message.lower()
        if "fixture" in lower_message or "not found" in lower_message:
            return FailureClassification(
                classification="test_script_issue",
                confidence=0.82,
                summary="The failure points to missing or invalid test code setup rather than product behavior.",
                root_cause=message,
                suggested_actions=["Add or fix the missing test fixture before rerunning the suite."],
            )
        return FailureClassification(
            classification="product_defect",
            confidence=0.72,
            summary="A failed TestResult includes assertion evidence that should be reviewed as product behavior.",
            root_cause=message,
            suggested_actions=["Review the failing assertion and attach implementation evidence before repair work."],
        )

    if artifacts or has_parsed_failure(test_run):
        return FailureClassification(
            classification="test_script_issue",
            confidence=0.55,
            summary="The run failed and includes execution evidence, but no failed TestResult message is available.",
            root_cause=None,
            suggested_actions=["Inspect stdout and stderr artifacts, then rerun with structured test result parsing."],
        )

    return FailureClassification(
        classification="insufficient_evidence",
        confidence=0.0,
        summary="Failure evidence is missing.",
        root_cause=None,
        suggested_actions=["Attach stdout, stderr, and failed TestResult evidence before analysis."],
    )


def has_parsed_failure(test_run: TestRun) -> bool:
    parsed = test_run.parsed_result_json or {}
    return bool(parsed.get("failed") or parsed.get("error"))


def stable_version_uuid(version: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_URL, f"chtest:{version}")


def create_report(
    session: Session,
    data: ReportCreateRequest,
    store: LocalArtifactStore,
) -> tuple[Report, uuid.UUID | None]:
    if data.report_type != "automation_execution" or data.related_entity_type != "TestRun":
        raise ReportInvalidInputError

    test_run = session.get(TestRun, data.related_entity_id)
    if test_run is None or test_run.project_id != data.project_id:
        raise ReportInvalidInputError
    require_execution_result_review_approval(
        session,
        test_run,
        data.execution_result_review_decision_id,
    )
    requirement_review_id = workflow_requirement_review_id_for_test_run(test_run)
    if requirement_review_id is not None:
        _report_review_workflow(session, data.project_id, requirement_review_id)

    test_results = list(
        session.scalars(
            select(TestResult)
            .where(TestResult.test_run_id == test_run.id)
            .order_by(TestResult.created_at.asc()),
        ),
    )
    execution_artifacts = list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.owner_entity_type == "TestRun",
                Artifact.owner_entity_id == test_run.id,
            )
            .order_by(Artifact.created_at.asc()),
        ),
    )
    metrics = dict(test_run.parsed_result_json or {})
    conclusion = report_conclusion(test_run, test_results, execution_artifacts)
    summary = report_summary(conclusion, metrics, test_results, execution_artifacts)

    report = Report(
        project_id=data.project_id,
        report_type="automation_execution",
        title="Automation execution report",
        related_entity_type="TestRun",
        related_entity_id=test_run.id,
        status="draft",
        conclusion=conclusion,
        summary=summary,
        metrics_json=metrics,
        artifact_ids=[],
    )
    session.add(report)
    session.flush()

    evidence_manifest = build_evidence_manifest(report, conclusion, test_run, test_results, execution_artifacts)
    report_artifacts = create_report_artifacts(session, report, evidence_manifest, store=store)
    report.artifact_ids = [artifact.id for artifact in report_artifacts]
    report.status = "draft" if requirement_review_id is not None else "ready"
    session.add(report)
    session.commit()
    session.refresh(report)
    manifest_artifact = next(
        (artifact for artifact in report_artifacts if artifact.metadata_json.get("manifest_kind") == "evidence_manifest"),
        None,
    )
    return report, manifest_artifact.id if manifest_artifact is not None else None


def get_report(session: Session, report_id: uuid.UUID) -> Report:
    report = session.get(Report, report_id)
    if report is None:
        raise ReportNotFoundError
    return report


def get_report_review_workflow_detail(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
) -> ReportReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    return _report_review_workflow_read(session, project_id, review.id, run, snapshot)


def submit_report_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
) -> ReportReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, _ = _report_review_workflow(session, project_id, review.id)
    workflow_service.submit_for_review(session, project_id, run.id, expected_version=data.expected_version)
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    return _report_review_workflow_read(session, project_id, review.id, run, snapshot)


def complete_report_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
) -> ReportReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, _ = _report_review_workflow(session, project_id, review.id)
    workflow_service.complete_human_review(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanReviewCreate(reviewer=data.reviewer, comment=data.comment),
    )
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    return _report_review_workflow_read(session, project_id, review.id, run, snapshot)


def edit_report_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowEditRequest,
) -> ReportReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    payload = dict(snapshot.input_payload_json)
    test_run_ids = _test_run_ids_from_payload(payload)
    reports = _reports_for_test_runs(session, project_id, test_run_ids)
    payload["generated_report_ids"] = [str(report.id) for report in reports]
    payload["report_artifact_ids"] = [
        str(artifact_id)
        for report in reports
        for artifact_id in report.artifact_ids
    ]
    payload["report_decisions"] = _json_safe(data.report_decisions)
    workflow_service.revise_workflow(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=WorkflowRevisionCreate(input_payload=payload, reviewer=data.reviewer, comment=data.comment),
    )
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    return _report_review_workflow_read(session, project_id, review.id, run, snapshot)


def decide_report_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
    *,
    decision: ApprovalDecision,
) -> ReportReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    if decision is ApprovalDecision.APPROVED:
        _require_report_review_evidence(session, project_id, snapshot.input_payload_json)
    workflow_service.record_human_approval(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanApprovalCreate(decision=decision, reviewer=data.reviewer, comment=data.comment),
    )
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    return _report_review_workflow_read(session, project_id, review.id, run, snapshot)


def continue_report_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowContinueRequest,
) -> ReportReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    _publish_report_review(
        session,
        project_id,
        run,
        snapshot,
        expected_version=data.expected_version,
        approval_decision_id=data.approval_decision_id,
    )
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    return _report_review_workflow_read(session, project_id, review.id, run, snapshot)


def approve_and_continue_report_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
    data: ReportReviewWorkflowActionRequest,
) -> ReportReviewWorkflowRead:
    review = _require_requirement_review_in_project(session, project_id, requirement_review_id)
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    _require_report_review_evidence(session, project_id, snapshot.input_payload_json)
    _updated_run, decision = workflow_service.record_human_approval(
        session,
        project_id,
        run.id,
        expected_version=data.expected_version,
        data=HumanApprovalCreate(decision=ApprovalDecision.APPROVED, reviewer=data.reviewer, comment=data.comment),
    )
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    _publish_report_review(
        session,
        project_id,
        run,
        snapshot,
        expected_version=data.expected_version + 1,
        approval_decision_id=decision.id,
    )
    run, snapshot = _report_review_workflow(session, project_id, review.id)
    return _report_review_workflow_read(session, project_id, review.id, run, snapshot)


def report_conclusion(test_run: TestRun, test_results: list[TestResult], artifacts: list[Artifact]) -> str:
    if not artifacts and not test_results:
        return "insufficient_evidence"
    parsed = test_run.parsed_result_json or {}
    if parsed.get("failed") or parsed.get("error") or test_run.status in {"failed", "error"}:
        return "failed"
    draft = test_run.automation_draft
    if draft is not None and draft.ai_task is not None:
        quality_gate = automation_draft_quality_gate(draft)
        if quality_gate["execution_evidence_level"] != "reviewed_candidate":
            return "insufficient_evidence"
    if parsed.get("passed") and artifacts:
        return "passed"
    return "insufficient_evidence"


def report_summary(
    conclusion: str,
    metrics: dict,
    test_results: list[TestResult],
    artifacts: list[Artifact],
) -> str:
    if conclusion == "insufficient_evidence":
        return "Automation execution evidence is insufficient for a passing conclusion."
    total = metrics.get("total") or len(test_results)
    failed = metrics.get("failed") or 0
    passed = metrics.get("passed") or 0
    if conclusion == "failed":
        return f"{failed} of {total} tests failed with {len(artifacts)} execution artifact(s)."
    return f"{passed} of {total} tests passed with required execution evidence."


def build_evidence_manifest(
    report: Report,
    conclusion: str,
    test_run: TestRun,
    test_results: list[TestResult],
    artifacts: list[Artifact],
) -> dict:
    evidence = [
        {
            "artifact_id": str(artifact.id),
            "artifact_type": artifact.artifact_type,
            "supports_claim": f"{test_run.name} includes {artifact.artifact_type} evidence",
            "required": artifact.artifact_type in {"stdout", "stderr", "runtime_manifest"},
        }
        for artifact in artifacts
    ]
    evidence.extend(
        {
            "metric": f"test_result:{result.status}",
            "test_result_id": str(result.id),
            "supports_claim": result.failure_message or f"{result.test_name} status is {result.status}",
            "required": result.status == "failed",
        }
        for result in test_results
    )
    return {
        "report_id": str(report.id),
        "conclusion": conclusion,
        "evidence": evidence,
        "missing_evidence": [] if artifacts else ["execution_artifact"],
    }


def create_report_artifacts(
    session: Session,
    report: Report,
    evidence_manifest: dict,
    *,
    store: LocalArtifactStore,
) -> list[Artifact]:
    base_path = f"projects/{report.project_id}/reports/{report.id}"
    specs = [
        (
            "report_md",
            "report.md",
            "text/markdown",
            {"report_kind": report.report_type},
        ),
        (
            "report_json",
            "report.json",
            "application/json",
            {"report_kind": report.report_type},
        ),
        (
            "report_json",
            "evidence_manifest.json",
            "application/json",
            {
                "manifest_kind": "evidence_manifest",
                "related_entity_type": report.related_entity_type,
                "related_entity_id": str(report.related_entity_id),
                "evidence_count": len(evidence_manifest["evidence"]),
                "manifest_json": evidence_manifest,
            },
        ),
    ]
    # Keep the database record and local evidence file in lockstep.
    report_json = {
        "report_id": str(report.id),
        "project_id": str(report.project_id),
        "report_type": report.report_type,
        "conclusion": report.conclusion,
        "summary": report.summary,
        "metrics": report.metrics_json,
        "evidence_manifest": evidence_manifest,
    }
    report_markdown = (
        f"# {report.title}\n\n"
        f"- Conclusion: **{report.conclusion}**\n"
        f"- Summary: {report.summary}\n\n"
        "## Evidence\n\n"
        + "\n".join(
            f"- {item.get('artifact_type', item.get('metric', 'evidence'))}: {item.get('supports_claim', '')}"
            for item in evidence_manifest.get("evidence", [])
        )
        + "\n"
    )
    contents = {
        "report.md": report_markdown.encode("utf-8"),
        "report.json": json.dumps(report_json, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8"),
        "evidence_manifest.json": json.dumps(
            evidence_manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8"),
    }
    artifacts: list[Artifact] = []
    for artifact_type, filename, mime_type, metadata in specs:
        content = contents[filename]
        relative_path = f"{base_path}/{filename}"
        write_result = store.write_bytes(relative_path, content)
        artifact = Artifact(
            project_id=report.project_id,
            owner_entity_type="Report",
            owner_entity_id=report.id,
            artifact_type=artifact_type,
            file_path=relative_path,
            mime_type=mime_type,
            size_bytes=write_result.size_bytes,
            sha256=f"sha256:{write_result.sha256}",
            metadata_json=metadata,
        )
        session.add(artifact)
        artifacts.append(artifact)
    session.flush()
    return artifacts


def report_evidence_manifest(session: Session, report: Report) -> dict:
    report_artifacts = report_artifacts_for_report(session, report)
    manifest_artifact = next(
        (item for item in report_artifacts if item.metadata_json.get("manifest_kind") == "evidence_manifest"),
        None,
    )
    if manifest_artifact is None:
        return {}
    return dict(manifest_artifact.metadata_json.get("manifest_json") or {})


def report_artifacts_for_report(session: Session, report: Report) -> list[Artifact]:
    return list(
        session.scalars(
            select(Artifact)
            .where(
                Artifact.owner_entity_type == "Report",
                Artifact.owner_entity_id == report.id,
            )
            .order_by(Artifact.created_at.asc()),
        ),
    )


def require_execution_result_review_approval(
    session: Session,
    test_run: TestRun,
    decision_id: uuid.UUID | None,
) -> None:
    requirement_review_id = workflow_requirement_review_id_for_test_run(test_run)
    if requirement_review_id is None:
        return
    if decision_id is None:
        raise ExecutionResultReviewApprovalRequiredError

    run = session.scalar(
        select(WorkflowRun).where(
            WorkflowRun.project_id == test_run.project_id,
            WorkflowRun.workflow_kind == WorkflowKind.REQUIREMENT_TO_EXECUTION.value,
            WorkflowRun.subject_ref == str(requirement_review_id),
            WorkflowRun.status == "active",
        ),
    )
    if run is None:
        raise ExecutionResultReviewApprovalRequiredError

    decision = session.scalar(
        select(WorkflowHumanDecision).where(
            WorkflowHumanDecision.id == decision_id,
            WorkflowHumanDecision.project_id == test_run.project_id,
            WorkflowHumanDecision.workflow_run_id == run.id,
            WorkflowHumanDecision.stage == ControlledStage.EXECUTION_RESULT_REVIEW.value,
            WorkflowHumanDecision.action == TransitionAction.APPROVE.value,
            WorkflowHumanDecision.decision == ApprovalDecision.APPROVED.value,
            WorkflowHumanDecision.allowed_action == TransitionAction.ADVANCE.value,
        ),
    )
    if decision is None:
        raise ExecutionResultReviewApprovalRequiredError

    source_snapshot = session.get(WorkflowStageSnapshot, decision.snapshot_id)
    if source_snapshot is None or not _snapshot_contains_test_run(source_snapshot, test_run.id):
        raise ExecutionResultReviewApprovalRequiredError

    if run.current_stage == ControlledStage.EXECUTION_RESULT_REVIEW.value:
        if run.gate_state != GateState.APPROVED.value or run.current_snapshot_id != decision.snapshot_id:
            raise ExecutionResultReviewApprovalRequiredError
        return

    if run.current_stage == ControlledStage.REPORT_REVIEW.value:
        consumed = session.scalar(
            select(WorkflowTransitionEvent).where(
                WorkflowTransitionEvent.project_id == test_run.project_id,
                WorkflowTransitionEvent.workflow_run_id == run.id,
                WorkflowTransitionEvent.consumed_approval_decision_id == decision.id,
                WorkflowTransitionEvent.source_snapshot_id == decision.snapshot_id,
                WorkflowTransitionEvent.to_stage == ControlledStage.REPORT_REVIEW.value,
            ),
        )
        if consumed is not None:
            return

    raise ExecutionResultReviewApprovalRequiredError


def workflow_requirement_review_id_for_test_run(test_run: TestRun) -> uuid.UUID | None:
    draft = test_run.automation_draft
    if draft is None:
        return None
    plan = draft.automation_plan
    if plan is None:
        return None
    return plan.requirement_review_id


def _snapshot_contains_test_run(snapshot: WorkflowStageSnapshot, test_run_id: uuid.UUID) -> bool:
    test_run_ids = snapshot.input_payload_json.get("generated_test_run_ids") or []
    return str(test_run_id) in {str(value) for value in test_run_ids}


def _require_requirement_review_in_project(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
) -> RequirementReview:
    row = session.execute(
        select(RequirementReview, Requirement)
        .join(Requirement, Requirement.id == RequirementReview.requirement_id)
        .where(RequirementReview.id == requirement_review_id, Requirement.project_id == project_id),
    ).first()
    if row is None:
        raise workflow_service.WorkflowRunNotFoundError
    return row[0]


def _report_review_workflow(
    session: Session,
    project_id: uuid.UUID,
    requirement_review_id: uuid.UUID,
) -> tuple[WorkflowRun, WorkflowStageSnapshot]:
    run = session.scalar(
        select(WorkflowRun)
        .where(
            WorkflowRun.project_id == project_id,
            WorkflowRun.workflow_kind == WorkflowKind.REQUIREMENT_TO_EXECUTION.value,
            WorkflowRun.subject_ref == str(requirement_review_id),
            WorkflowRun.status == "active",
        )
        .order_by(WorkflowRun.created_at.desc(), WorkflowRun.id.desc()),
    )
    if run is None:
        raise workflow_service.WorkflowRunNotFoundError
    run, snapshot = workflow_service.get_workflow_run_authoritative(session, project_id, run.id)
    if run.current_stage != ControlledStage.REPORT_REVIEW.value:
        raise ReportReviewWorkflowStageError
    return run, snapshot


def _report_review_workflow_read(
    session: Session,
    project_id: uuid.UUID,
    review_id: uuid.UUID,
    run: WorkflowRun,
    snapshot: WorkflowStageSnapshot,
) -> ReportReviewWorkflowRead:
    payload = snapshot.input_payload_json
    latest_approval = session.scalar(
        select(WorkflowHumanDecision)
        .where(
            WorkflowHumanDecision.project_id == run.project_id,
            WorkflowHumanDecision.workflow_run_id == run.id,
            WorkflowHumanDecision.snapshot_id == run.current_snapshot_id,
            WorkflowHumanDecision.action == TransitionAction.APPROVE.value,
            WorkflowHumanDecision.decision == ApprovalDecision.APPROVED.value,
        )
        .order_by(WorkflowHumanDecision.created_at.desc(), WorkflowHumanDecision.id.desc()),
    )
    approval_consumed = latest_approval is not None and _report_review_approval_consumed(session, run, latest_approval)
    report_ready = _report_review_snapshot_has_current_report_evidence(session, project_id, payload)
    return ReportReviewWorkflowRead(
        project_id=project_id,
        requirement_review_id=review_id,
        workflow={
            "run_id": str(run.id),
            "stage": run.current_stage,
            "state": run.gate_state,
            "lock_version": run.lock_version,
            "snapshot_id": str(run.current_snapshot_id),
            "approval_decision_id": str(latest_approval.id) if latest_approval and not approval_consumed else None,
            "can_submit": run.gate_state == GateState.DRAFT.value,
            "can_complete_review": run.gate_state == GateState.WAITING_REVIEW.value,
            "can_edit": run.gate_state
            in {
                GateState.WAITING_REVIEW.value,
                GateState.WAITING_APPROVAL.value,
                GateState.APPROVED.value,
                GateState.REJECTED.value,
            },
            "can_approve": run.gate_state == GateState.WAITING_APPROVAL.value and report_ready,
            "can_continue": run.gate_state == GateState.APPROVED.value
            and latest_approval is not None
            and not approval_consumed
            and report_ready,
            "published": approval_consumed,
        },
        source_execution_result_review_snapshot_id=payload.get("source_execution_result_review_snapshot_id"),
        source_execution_result_review_snapshot_hash=payload.get("source_execution_result_review_snapshot_hash"),
        source_execution_approval_snapshot_id=payload.get("source_execution_approval_snapshot_id"),
        source_execution_approval_snapshot_hash=payload.get("source_execution_approval_snapshot_hash"),
        generated_test_run_ids=list(payload.get("generated_test_run_ids", [])),
        execution_artifact_ids=list(payload.get("execution_artifact_ids", [])),
        generated_report_ids=list(payload.get("generated_report_ids", [])),
        report_artifact_ids=list(payload.get("report_artifact_ids", [])),
        execution_decisions=list(payload.get("execution_decisions", [])),
        result_decisions=list(payload.get("result_decisions", [])),
        report_decisions=list(payload.get("report_decisions", [])),
    )


def _report_review_approval_consumed(
    session: Session,
    run: WorkflowRun,
    decision: WorkflowHumanDecision,
) -> bool:
    consumed = session.scalar(
        select(WorkflowTransitionEvent.id).where(
            WorkflowTransitionEvent.project_id == run.project_id,
            WorkflowTransitionEvent.workflow_run_id == run.id,
            WorkflowTransitionEvent.consumed_approval_decision_id == decision.id,
            WorkflowTransitionEvent.source_snapshot_id == decision.snapshot_id,
            WorkflowTransitionEvent.to_stage == ControlledStage.REPORT_REVIEW.value,
        ),
    )
    return consumed is not None


def _test_run_ids_from_payload(payload: dict) -> list[uuid.UUID]:
    ids: list[uuid.UUID] = []
    for value in payload.get("generated_test_run_ids") or []:
        try:
            ids.append(uuid.UUID(str(value)))
        except (TypeError, ValueError):
            continue
    return ids


def _report_ids_from_payload(payload: dict) -> list[uuid.UUID]:
    ids: list[uuid.UUID] = []
    for value in payload.get("generated_report_ids") or []:
        try:
            ids.append(uuid.UUID(str(value)))
        except (TypeError, ValueError):
            continue
    return ids


def _reports_for_test_runs(session: Session, project_id: uuid.UUID, test_run_ids: list[uuid.UUID]) -> list[Report]:
    if not test_run_ids:
        return []
    return list(
        session.scalars(
            select(Report)
            .where(
                Report.project_id == project_id,
                Report.related_entity_type == "TestRun",
                Report.related_entity_id.in_(test_run_ids),
                Report.report_type == "automation_execution",
            )
            .order_by(Report.created_at.asc(), Report.id.asc()),
        ),
    )


def _execution_artifact_ids_for_test_runs(
    session: Session,
    project_id: uuid.UUID,
    test_run_ids: list[uuid.UUID],
) -> list[str]:
    if not test_run_ids:
        return []
    return [
        str(artifact_id)
        for artifact_id in session.scalars(
            select(Artifact.id)
            .where(
                Artifact.project_id == project_id,
                Artifact.owner_entity_type == "TestRun",
                Artifact.owner_entity_id.in_(test_run_ids),
            )
            .order_by(Artifact.created_at.asc(), Artifact.id.asc()),
        )
    ]


def _report_review_snapshot_has_current_report_evidence(
    session: Session,
    project_id: uuid.UUID,
    payload: dict,
) -> bool:
    test_run_ids = _test_run_ids_from_payload(payload)
    report_ids = _report_ids_from_payload(payload)
    if not test_run_ids or not report_ids:
        return False
    current_reports = _reports_for_test_runs(session, project_id, test_run_ids)
    current_report_ids = [report.id for report in current_reports]
    if set(report_ids) != set(current_report_ids):
        return False
    payload_artifact_ids = {str(value) for value in payload.get("report_artifact_ids") or []}
    current_artifact_ids = {str(artifact_id) for report in current_reports for artifact_id in report.artifact_ids}
    return bool(current_artifact_ids) and payload_artifact_ids == current_artifact_ids


def _require_report_review_evidence(session: Session, project_id: uuid.UUID, payload: dict) -> None:
    test_run_ids = _test_run_ids_from_payload(payload)
    if not test_run_ids:
        raise ReportReviewGateError
    existing_run = session.scalar(
        select(TestRun.id)
        .where(TestRun.project_id == project_id, TestRun.id.in_(test_run_ids))
        .limit(1),
    )
    if existing_run is None:
        raise ReportReviewGateError
    if set(payload.get("execution_artifact_ids") or []) != set(
        _execution_artifact_ids_for_test_runs(session, project_id, test_run_ids)
    ):
        raise ReportReviewGateError
    if not _report_review_snapshot_has_current_report_evidence(session, project_id, payload):
        raise ReportReviewGateError


def _publish_report_review(
    session: Session,
    project_id: uuid.UUID,
    run: WorkflowRun,
    snapshot: WorkflowStageSnapshot,
    *,
    expected_version: int,
    approval_decision_id: uuid.UUID,
) -> None:
    if run.lock_version != expected_version:
        raise workflow_service.WorkflowVersionConflictError
    if run.current_stage != ControlledStage.REPORT_REVIEW.value or run.gate_state != GateState.APPROVED.value:
        raise ReportReviewApprovalRequiredError
    _require_report_review_evidence(session, project_id, snapshot.input_payload_json)
    decision = session.scalar(
        select(WorkflowHumanDecision).where(
            WorkflowHumanDecision.id == approval_decision_id,
            WorkflowHumanDecision.project_id == project_id,
            WorkflowHumanDecision.workflow_run_id == run.id,
            WorkflowHumanDecision.snapshot_id == run.current_snapshot_id,
            WorkflowHumanDecision.stage == ControlledStage.REPORT_REVIEW.value,
            WorkflowHumanDecision.action == TransitionAction.APPROVE.value,
            WorkflowHumanDecision.decision == ApprovalDecision.APPROVED.value,
            WorkflowHumanDecision.allowed_action == TransitionAction.ADVANCE.value,
        ),
    )
    if decision is None:
        raise ReportReviewApprovalRequiredError
    if _report_review_approval_consumed(session, run, decision):
        raise workflow_service.WorkflowApprovalReplayError
    if decision.source_run_version + 1 != run.lock_version:
        raise workflow_service.WorkflowApprovalStaleError
    grant = ApprovalGrant(
        workflow_kind=WorkflowKind(run.workflow_kind),
        workflow_ref=str(run.id),
        subject_ref=run.subject_ref,
        stage=ControlledStage.REPORT_REVIEW,
        input_snapshot_hash=run.input_snapshot_hash,
        allowed_action=TransitionAction.ADVANCE,
        decision=ApprovalDecision.APPROVED,
        granted_by=decision.reviewer,
    )
    if decision.grant_fingerprint != grant.fingerprint:
        raise workflow_service.WorkflowApprovalStaleError
    report_ids = _report_ids_from_payload(snapshot.input_payload_json)
    session.execute(
        update(Report)
        .where(Report.project_id == project_id, Report.id.in_(report_ids))
        .values(status="ready")
        .execution_options(synchronize_session=False),
    )
    result = session.execute(
        update(WorkflowRun)
        .where(
            WorkflowRun.id == run.id,
            WorkflowRun.project_id == run.project_id,
            WorkflowRun.lock_version == expected_version,
            WorkflowRun.current_stage == run.current_stage,
            WorkflowRun.gate_state == run.gate_state,
            WorkflowRun.current_snapshot_id == run.current_snapshot_id,
        )
        .values(lock_version=expected_version + 1)
        .execution_options(synchronize_session=False),
    )
    if result.rowcount != 1:
        session.rollback()
        raise workflow_service.WorkflowVersionConflictError
    session.add(
        WorkflowTransitionEvent(
            project_id=run.project_id,
            workflow_run_id=run.id,
            actor=Actor.SYSTEM.value,
            action=TransitionAction.ADVANCE.value,
            from_stage=run.current_stage,
            from_state=run.gate_state,
            to_stage=run.current_stage,
            to_state=run.gate_state,
            source_snapshot_id=snapshot.id,
            target_snapshot_id=snapshot.id,
            consumed_approval_decision_id=decision.id,
            grant_fingerprint=grant.fingerprint,
            source_run_version=expected_version,
            result_run_version=expected_version + 1,
        ),
    )
    try:
        session.commit()
        session.expire_all()
    except Exception as exc:
        session.rollback()
        raise workflow_service.WorkflowConflictError from exc


def _json_safe(value):
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value
