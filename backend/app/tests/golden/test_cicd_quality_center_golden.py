from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import CICDChangedFile, CICDRun, QualityGateDecision
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.models import Project, Repository, Workspace
from backend.app.modules.reporting.models import Report
from backend.app.tests.golden.test_test_case_library_golden import ASGIClient, api_client


GOLDEN_DIFF = """diff --git a/src/coupon.py b/src/coupon.py
index 1111111..2222222 100644
--- a/src/coupon.py
+++ b/src/coupon.py
@@ -10,6 +10,8 @@ def apply_coupon(order_total, coupon):
     if coupon.status == 'expired':
         return ApplyResult(False, 'COUPON_EXPIRED', order_total)
+    if coupon.amount > order_total:
+        return ApplyResult(False, 'COUPON_AMOUNT_EXCEEDS_ORDER_TOTAL', order_total)
     return ApplyResult(True, None, order_total - coupon.amount)
"""


def test_golden_local_diff_creates_cicd_run_and_risk_analysis_evidence(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    with SessionLocal() as session:
        project, repository = seed_project_repository(session)
        session.commit()
        project_id = project.id
        repository_id = repository.id

    create_response = client.post(
        "/api/cicd/runs",
        json_body={
            "project_id": str(project_id),
            "repository_id": str(repository_id),
            "source_type": "local_diff",
            "base_ref": "main",
            "head_ref": "HEAD",
            "diff_text": GOLDEN_DIFF,
        },
    )
    assert create_response.status_code == 202
    cicd_run_id = create_response.json()["cicd_run_id"]

    get_response = client.get(f"/api/cicd/runs/{cicd_run_id}")
    assert get_response.status_code == 200
    run = get_response.json()
    assert run["source_type"] == "local_diff"
    assert run["trigger_type"] == "manual"
    assert run["provider"] == "local"
    assert run["quality_gate_status"] == "pending"
    assert run["changed_files"][0]["path"] == "src/coupon.py"
    assert run["changed_files"][0]["file_role"] == "source"
    assert run["changed_files"][0]["risk_level"] == "medium"

    analyze_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/analyze",
        json_body={
            "prompt_version": "cicd_change_analysis:v1",
            "skill_version": "regression-selection-skill:v1",
            "model_provider": "mock",
            "model_name": "mock-cicd-analysis",
        },
    )
    assert analyze_response.status_code == 202
    analyzed = analyze_response.json()
    assert analyzed["status"] == "analyzed"
    assert analyzed["risk_analysis_artifact_id"] is not None

    analyzed_get_response = client.get(f"/api/cicd/runs/{cicd_run_id}")
    assert analyzed_get_response.status_code == 200
    analyzed_run = analyzed_get_response.json()
    assert analyzed_run["status"] == "analyzed"
    assert analyzed_run["overall_risk"] == "medium"
    assert analyzed_run["analysis_artifacts"][0]["artifact_type"] == "risk_analysis"

    with SessionLocal() as session:
        persisted_run = session.get(CICDRun, uuid.UUID(cicd_run_id))
        changed_files = list(
            session.scalars(select(CICDChangedFile).where(CICDChangedFile.cicd_run_id == uuid.UUID(cicd_run_id))),
        )
        ai_task = session.get(AITask, uuid.UUID(analyzed["ai_task_id"]))
        artifacts = list(
            session.scalars(
                select(Artifact).where(
                    Artifact.owner_entity_type == "CICDRun",
                    Artifact.owner_entity_id == uuid.UUID(cicd_run_id),
                ),
            ),
        )
        assert session.scalar(select(AutomationDraft)) is None
        assert session.scalar(select(TestRun)) is None
        assert session.scalar(select(Report)) is None
        assert session.scalar(select(QualityGateDecision)) is None

    assert persisted_run is not None
    assert persisted_run.status == "analyzed"
    assert persisted_run.quality_gate_status == "pending"
    assert len(changed_files) == 1
    assert changed_files[0].path == "src/coupon.py"
    assert changed_files[0].risk_reasons_json == ["source file changed"]
    assert ai_task is not None
    assert ai_task.status == "succeeded"
    assert ai_task.task_type == "cicd_change_analysis"
    artifact_types = {artifact.artifact_type for artifact in artifacts}
    assert artifact_types == {"diff_patch", "changed_files", "risk_analysis"}
    risk_artifact = next(artifact for artifact in artifacts if artifact.artifact_type == "risk_analysis")
    assert risk_artifact.metadata_json["overall_risk"] == "medium"
    assert risk_artifact.metadata_json["changed_file_count"] == 1


def seed_project_repository(session: Session) -> tuple[Project, Repository]:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout Golden")
    session.add(project)
    session.flush()
    repository = Repository(
        project_id=project.id,
        name="sample-checkout",
        local_path="/Users/yanchen/VscodeProject/sample-checkout",
        default_base_branch="main",
        language_hint="python",
    )
    session.add(repository)
    session.flush()
    return project, repository
