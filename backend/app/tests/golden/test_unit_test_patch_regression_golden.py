from __future__ import annotations

import uuid

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.automation.models import AutomationDraft
from backend.app.modules.cicd.models import CICDRun, QualityGateDecision, UnitTestPatch
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.models import Project, Repository, TestCommand, Workspace
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

GOLDEN_UNIT_TEST_PATCH = """diff --git a/tests/test_coupon.py b/tests/test_coupon.py
index 3333333..4444444 100644
--- a/tests/test_coupon.py
+++ b/tests/test_coupon.py
@@ -20,3 +20,12 @@ def test_expired_coupon_is_rejected():
     assert result.success is False
     assert result.error_code == 'COUPON_EXPIRED'
+
+
+def test_coupon_amount_cannot_exceed_order_total():
+    coupon = Coupon(status='active', amount=120)
+
+    result = apply_coupon(order_total=100, coupon=coupon)
+
+    assert result.success is False
+    assert result.error_code == 'COUPON_AMOUNT_EXCEEDS_ORDER_TOTAL'
+    assert result.final_total == 100
"""


def test_golden_local_diff_flows_through_unit_patch_regression_gate_and_report(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    with SessionLocal() as session:
        project, repository, test_command = seed_project_repository_command(session)
        session.commit()
        project_id = project.id
        repository_id = repository.id
        test_command_id = test_command.id

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
    cicd_run_id = uuid.UUID(create_response.json()["cicd_run_id"])

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

    patch_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/unit-test-patches",
        json_body={
            "patch_text": GOLDEN_UNIT_TEST_PATCH,
            "target_framework": "pytest",
            "test_intent": "覆盖优惠券金额大于订单总额的新分支",
            "coverage_target": [{"path": "src/coupon.py", "reason": "coupon.amount > order_total"}],
        },
    )
    assert patch_response.status_code == 202
    patch_body = patch_response.json()
    assert patch_body["status"] == "scope_validated"
    assert patch_body["scope_gate_result"]["allowed"] is True
    assert patch_body["scope_gate_result"]["checked_paths"] == ["tests/test_coupon.py"]
    unit_test_patch_id = uuid.UUID(patch_body["id"])

    approve_response = client.post(
        f"/api/cicd/unit-test-patches/{unit_test_patch_id}/approve",
        json_body={"review_comment": "Golden patch only modifies tests/test_coupon.py"},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    apply_response = client.post(
        f"/api/cicd/unit-test-patches/{unit_test_patch_id}/apply",
        json_body={"confirm_scope_gate_result": True},
    )
    assert apply_response.status_code == 200
    assert apply_response.json()["status"] == "applied"
    applied_artifact_id = uuid.UUID(apply_response.json()["applied_artifact_id"])

    new_tests_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/run-new-tests",
        json_body={
            "unit_test_patch_id": str(unit_test_patch_id),
            "test_command_id": str(test_command_id),
        },
    )
    assert new_tests_response.status_code == 202
    new_test_run_id = uuid.UUID(new_tests_response.json()["test_run_id"])

    regression_select_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/select-regression",
        json_body={
            "skill_version": "regression-selection-skill:v1",
            "candidate_test_command_ids": [str(test_command_id)],
        },
    )
    assert regression_select_response.status_code == 200
    regression_plan_artifact_id = uuid.UUID(regression_select_response.json()["regression_plan_artifact_id"])

    regression_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/run-regression",
        json_body={
            "regression_plan_artifact_id": str(regression_plan_artifact_id),
            "test_command_ids": [str(test_command_id)],
        },
    )
    assert regression_response.status_code == 202
    regression_run_id = uuid.UUID(regression_response.json()["test_run_ids"][0])

    mark_test_runs_succeeded(SessionLocal, [new_test_run_id, regression_run_id])

    gate_response = client.post(f"/api/cicd/runs/{cicd_run_id}/quality-gate", json_body={})
    assert gate_response.status_code == 200
    gate_body = gate_response.json()
    assert gate_body["status"] == "passed"
    assert gate_body["blocking_reasons"] == []
    quality_gate_decision_id = uuid.UUID(gate_body["id"])

    report_response = client.post(
        f"/api/cicd/runs/{cicd_run_id}/generate-report",
        json_body={"report_format": ["json"]},
    )
    assert report_response.status_code == 202
    report_body = report_response.json()
    report_id = uuid.UUID(report_body["report_id"])
    manifest_artifact_id = uuid.UUID(report_body["evidence_manifest_artifact_id"])

    with SessionLocal() as session:
        run = session.get(CICDRun, cicd_run_id)
        patch = session.get(UnitTestPatch, unit_test_patch_id)
        applied_artifact = session.get(Artifact, applied_artifact_id)
        regression_plan_artifact = session.get(Artifact, regression_plan_artifact_id)
        decision = session.get(QualityGateDecision, quality_gate_decision_id)
        report = session.get(Report, report_id)
        manifest = session.get(Artifact, manifest_artifact_id)
        ai_tasks = list(session.scalars(select(AITask)))
        test_runs = list(session.scalars(select(TestRun).where(TestRun.cicd_run_id == cicd_run_id)))
        tables = set(inspect(session.bind).get_table_names())

        assert session.scalar(select(AutomationDraft)) is None

    assert run is not None
    assert run.quality_gate_status == "passed"
    assert patch is not None
    assert patch.status == "applied"
    assert patch.patch_text == GOLDEN_UNIT_TEST_PATCH
    assert applied_artifact is not None
    assert applied_artifact.artifact_type == "unit_test_patch"
    assert applied_artifact.metadata_json["scope_gate_result"]["allowed"] is True
    assert regression_plan_artifact is not None
    assert regression_plan_artifact.artifact_type == "regression_plan"
    assert decision is not None
    assert decision.status == "passed"
    assert report is not None
    assert report.report_type == "cicd_quality"
    assert report.conclusion == "passed"
    assert manifest is not None
    manifest_json = manifest.metadata_json["manifest_json"]
    assert manifest_json["quality_gate_decision_id"] == str(quality_gate_decision_id)
    assert "unit_test_patch" in manifest_json["evidence_kinds"]
    assert "regression_plan" in manifest_json["evidence_kinds"]
    assert len(test_runs) == 2
    assert {test_run.parsed_result_json["run_type"] for test_run in test_runs} == {"new_tests", "regression"}
    assert {task.task_type for task in ai_tasks} == {"cicd_change_analysis", "unit_test_patch"}
    assert "tenants" not in tables
    assert "roles" not in tables
    assert "permissions" not in tables
    assert "rag_indexes" not in tables
    assert "mcp_servers" not in tables


def mark_test_runs_succeeded(SessionLocal: sessionmaker[Session], test_run_ids: list[uuid.UUID]) -> None:
    with SessionLocal() as session:
        for test_run_id in test_run_ids:
            test_run = session.get(TestRun, test_run_id)
            assert test_run is not None
            test_run.status = "succeeded"
            test_run.exit_code = 0
            session.add(test_run)
        session.commit()


def seed_project_repository_command(session: Session) -> tuple[Project, Repository, TestCommand]:
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
    test_command = TestCommand(
        project_id=project.id,
        repository_id=repository.id,
        name="pytest coupon regression",
        command="pytest tests -q --junitxml=artifacts/junit.xml",
        working_directory=".",
        command_type="pytest",
    )
    session.add(test_command)
    session.flush()
    return project, repository, test_command
