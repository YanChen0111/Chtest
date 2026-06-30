from __future__ import annotations

import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.execution.models import TestResult, TestRun
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.modules.reporting.schemas import FailureAnalysisRead as AnalysisRead
from backend.app.modules.reporting.schemas import ReportRead as ExecutionReportRead


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


def seed_project_task_and_run(session: Session) -> tuple[Project, AITask, TestRun, TestResult, Artifact]:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    ai_task = AITask(
        project_id=project.id,
        agent_name="FailureAnalysisAgent",
        task_type="failure_analysis",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
        model_provider="mock",
        model_name="mock-failure-analysis",
        status="succeeded",
        input_json={},
        output_json={},
    )
    test_run = TestRun(
        project_id=project.id,
        name="pytest failed run",
        command="pytest tests/test_coupon.py -q",
        working_directory="/Users/yanchen/VscodeProject/sample-app",
        status="failed",
        exit_code=1,
        parsed_result_json={"total": 1, "passed": 0, "failed": 1, "skipped": 0, "error": 0},
    )
    artifact = Artifact(
        project_id=project.id,
        owner_entity_type="TestRun",
        owner_entity_id=uuid.uuid4(),
        artifact_type="stderr",
        file_path="test-runs/run-1/stderr.log",
        mime_type="text/plain",
        size_bytes=32,
        sha256="sha256:stderr",
        metadata_json={},
    )
    session.add_all([ai_task, test_run, artifact])
    session.flush()
    result = TestResult(
        project_id=project.id,
        test_run_id=test_run.id,
        test_name="tests/test_coupon.py::test_expired_coupon",
        test_file="tests/test_coupon.py",
        status="failed",
        failure_message="fixture coupon_client not found",
        failure_artifact_ids=[artifact.id],
        metadata_json={"classname": "tests.test_coupon"},
    )
    session.add(result)
    session.flush()
    return project, ai_task, test_run, result, artifact


def test_failure_analysis_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, ai_task, test_run, test_result, artifact = seed_project_task_and_run(session)
        analysis = FailureAnalysis(
            project_id=project.id,
            test_run_id=test_run.id,
            test_result_id=test_result.id,
            ai_task_id=ai_task.id,
            classification="test_script_issue",
            confidence=0.82,
            evidence_artifact_ids=[artifact.id],
            summary="Fixture lookup failed before business assertion.",
            root_cause="coupon_client fixture is missing.",
            suggested_actions_json=["Add fixture coupon_client"],
        )
        session.add(analysis)
        session.commit()
        persisted = session.scalar(select(FailureAnalysis).where(FailureAnalysis.id == analysis.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.test_run_id == test_run.id
    assert persisted.test_result_id == test_result.id
    assert persisted.ai_task_id == ai_task.id
    assert persisted.classification == "test_script_issue"
    assert float(persisted.confidence) == 0.82
    assert persisted.evidence_artifact_ids == [artifact.id]
    assert persisted.suggested_actions_json == ["Add fixture coupon_client"]
    assert persisted.status == "draft"


def test_report_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, _ai_task, test_run, _test_result, artifact = seed_project_task_and_run(session)
        report = Report(
            project_id=project.id,
            report_type="automation_execution",
            title="Automation execution report",
            related_entity_type="TestRun",
            related_entity_id=test_run.id,
            status="ready",
            conclusion="failed",
            summary="1 pytest test failed.",
            metrics_json={"total": 1, "failed": 1},
            artifact_ids=[artifact.id],
        )
        session.add(report)
        session.commit()
        persisted = session.scalar(select(Report).where(Report.id == report.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.report_type == "automation_execution"
    assert persisted.related_entity_type == "TestRun"
    assert persisted.related_entity_id == test_run.id
    assert persisted.status == "ready"
    assert persisted.conclusion == "failed"
    assert persisted.metrics_json["failed"] == 1
    assert persisted.artifact_ids == [artifact.id]


def test_failure_analysis_read_schema_uses_contract_field_names() -> None:
    analysis_id = uuid.uuid4()
    project_id = uuid.uuid4()
    test_run_id = uuid.uuid4()
    ai_task_id = uuid.uuid4()
    artifact_id = uuid.uuid4()

    read = AnalysisRead(
        id=analysis_id,
        project_id=project_id,
        test_run_id=test_run_id,
        test_result_id=None,
        ai_task_id=ai_task_id,
        classification="insufficient_evidence",
        confidence=0.0,
        evidence_artifact_ids=[artifact_id],
        summary="Not enough evidence.",
        root_cause=None,
        suggested_actions=["Attach stdout and stderr artifacts"],
        status="draft",
    )

    body = read.model_dump(mode="json")
    assert body["id"] == str(analysis_id)
    assert body["classification"] == "insufficient_evidence"
    assert body["evidence_artifact_ids"] == [str(artifact_id)]
    assert body["suggested_actions"] == ["Attach stdout and stderr artifacts"]


def test_report_read_schema_embeds_evidence_manifest() -> None:
    report_id = uuid.uuid4()
    project_id = uuid.uuid4()
    run_id = uuid.uuid4()
    artifact_id = uuid.uuid4()

    read = ExecutionReportRead(
        id=report_id,
        project_id=project_id,
        report_type="automation_execution",
        title="Automation execution report",
        related_entity_type="TestRun",
        related_entity_id=run_id,
        status="ready",
        conclusion="passed",
        summary="1 test passed.",
        metrics={"total": 1, "passed": 1},
        artifact_ids=[artifact_id],
        evidence_manifest={
            "report_id": str(report_id),
            "conclusion": "passed",
            "evidence": [{"artifact_id": str(artifact_id), "required": True}],
            "missing_evidence": [],
        },
        artifacts=[],
    )

    body = read.model_dump(mode="json")
    assert body["id"] == str(report_id)
    assert body["related_entity_id"] == str(run_id)
    assert body["metrics"]["passed"] == 1
    assert body["artifact_ids"] == [str(artifact_id)]
    assert body["evidence_manifest"]["missing_evidence"] == []
