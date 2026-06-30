from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.modules.reporting.schemas import FailureAnalysisCreateRequest, ReportCreateRequest


class TestRunNotFoundError(Exception):
    pass


class FailureAnalysisNotFoundError(Exception):
    pass


class ReportNotFoundError(Exception):
    pass


class ReportInvalidInputError(Exception):
    pass


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

    ai_task = AITask(
        project_id=test_run.project_id,
        agent_name="FailureAnalysisAgent",
        task_type="failure_analysis",
        prompt_version_id=stable_version_uuid(data.prompt_version),
        skill_version_id=stable_version_uuid(data.skill_version),
        model_provider=data.model_provider,
        model_name=data.model_name,
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


def create_report(session: Session, data: ReportCreateRequest) -> tuple[Report, uuid.UUID | None]:
    if data.report_type != "automation_execution" or data.related_entity_type != "TestRun":
        raise ReportInvalidInputError

    test_run = session.get(TestRun, data.related_entity_id)
    if test_run is None or test_run.project_id != data.project_id:
        raise ReportInvalidInputError

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
    report_artifacts = create_report_artifacts(session, report, evidence_manifest)
    report.artifact_ids = [artifact.id for artifact in report_artifacts]
    report.status = "ready"
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


def report_conclusion(test_run: TestRun, test_results: list[TestResult], artifacts: list[Artifact]) -> str:
    if not artifacts and not test_results:
        return "insufficient_evidence"
    parsed = test_run.parsed_result_json or {}
    if parsed.get("failed") or parsed.get("error") or test_run.status in {"failed", "error"}:
        return "failed"
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


def create_report_artifacts(session: Session, report: Report, evidence_manifest: dict) -> list[Artifact]:
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
    artifacts: list[Artifact] = []
    for artifact_type, filename, mime_type, metadata in specs:
        artifact = Artifact(
            project_id=report.project_id,
            owner_entity_type="Report",
            owner_entity_id=report.id,
            artifact_type=artifact_type,
            file_path=f"{base_path}/{filename}",
            mime_type=mime_type,
            size_bytes=0,
            sha256=f"sha256:{artifact_type}:{filename}:{report.id}",
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
