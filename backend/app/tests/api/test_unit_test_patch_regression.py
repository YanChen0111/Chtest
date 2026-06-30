from __future__ import annotations

import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.cicd.models import CICDRun, QualityGateDecision, UnitTestPatch
from backend.app.modules.cicd.schemas import (
    QualityGateDecisionCreate,
    QualityGateDecisionRead,
    UnitTestPatchCreate,
    UnitTestPatchRead,
)
from backend.app.modules.projects.models import Project, Repository, Workspace


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


def seed_cicd_run_and_ai_task(session: Session) -> tuple[Project, CICDRun, AITask]:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    repository = Repository(
        project_id=project.id,
        name="sample-app",
        local_path="/Users/yanchen/VscodeProject/sample-app",
        default_base_branch="main",
        language_hint="python",
    )
    session.add(repository)
    session.flush()
    cicd_run = CICDRun(project_id=project.id, repository_id=repository.id)
    session.add(cicd_run)
    session.flush()
    ai_task = AITask(
        project_id=project.id,
        agent_name="UnitTestAgent",
        task_type="unit_test_patch",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
        model_provider="mock",
        model_name="mock-unit-test-patch",
        status="succeeded",
        input_json={"cicd_run_id": str(cicd_run.id)},
        output_json={"patch": "generated"},
    )
    session.add(ai_task)
    session.flush()
    return project, cicd_run, ai_task


def test_unit_test_patch_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        _project, cicd_run, ai_task = seed_cicd_run_and_ai_task(session)
        patch = UnitTestPatch(
            cicd_run_id=cicd_run.id,
            ai_task_id=ai_task.id,
            patch_text="diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n",
            target_framework="pytest",
            scope_gate_result_json={
                "allowed": True,
                "checked_paths": ["tests/test_coupon.py"],
                "blocked_paths": [],
                "forbidden_patterns": [],
                "risk_level": "low",
            },
            test_intent="Cover coupon boundary change",
            coverage_target_json=[{"path": "app/coupon.py", "reason": "changed source"}],
            status="scope_validated",
            review_comment="Looks focused",
        )
        session.add(patch)
        session.commit()
        persisted = session.scalar(select(UnitTestPatch).where(UnitTestPatch.id == patch.id))

    assert persisted is not None
    assert persisted.cicd_run_id == cicd_run.id
    assert persisted.ai_task_id == ai_task.id
    assert persisted.patch_text.startswith("diff --git")
    assert persisted.target_framework == "pytest"
    assert persisted.scope_gate_result_json["allowed"] is True
    assert persisted.coverage_target_json == [{"path": "app/coupon.py", "reason": "changed source"}]
    assert persisted.test_intent == "Cover coupon boundary change"
    assert persisted.status == "scope_validated"
    assert persisted.review_comment == "Looks focused"


def test_quality_gate_decision_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    evidence_id = uuid.uuid4()
    with SessionLocal() as session:
        project, cicd_run, _ai_task = seed_cicd_run_and_ai_task(session)
        decision = QualityGateDecision(
            project_id=project.id,
            cicd_run_id=cicd_run.id,
            status="needs_review",
            summary="Regression evidence is missing",
            blocking_reasons_json=["missing regression evidence"],
            evidence_artifact_ids=[evidence_id],
            decided_by="system",
            status_detail_json={"regression": "missing", "patch_scope_gate": "passed"},
        )
        session.add(decision)
        session.commit()
        persisted = session.scalar(select(QualityGateDecision).where(QualityGateDecision.id == decision.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.cicd_run_id == cicd_run.id
    assert persisted.status == "needs_review"
    assert persisted.summary == "Regression evidence is missing"
    assert persisted.blocking_reasons_json == ["missing regression evidence"]
    assert persisted.evidence_artifact_ids == [evidence_id]
    assert persisted.decided_by == "system"
    assert persisted.status_detail_json == {"regression": "missing", "patch_scope_gate": "passed"}


def test_unit_test_patch_schemas_use_contract_field_names() -> None:
    cicd_run_id = uuid.uuid4()
    ai_task_id = uuid.uuid4()
    patch_id = uuid.uuid4()

    create = UnitTestPatchCreate(
        cicd_run_id=cicd_run_id,
        ai_task_id=ai_task_id,
        patch_text="diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n",
        test_intent="Cover coupon boundary change",
    )
    read = UnitTestPatchRead(
        id=patch_id,
        cicd_run_id=create.cicd_run_id,
        ai_task_id=create.ai_task_id,
        patch_text=create.patch_text,
        target_framework=create.target_framework,
        scope_gate_result=create.scope_gate_result,
        test_intent=create.test_intent,
        coverage_target=create.coverage_target,
        status=create.status,
        review_comment=None,
    )

    body = read.model_dump(mode="json")
    assert body["id"] == str(patch_id)
    assert body["cicd_run_id"] == str(cicd_run_id)
    assert body["ai_task_id"] == str(ai_task_id)
    assert body["target_framework"] == "pytest"
    assert body["scope_gate_result"] == {}
    assert body["coverage_target"] == []
    assert body["status"] == "generated"


def test_quality_gate_decision_schemas_use_contract_field_names() -> None:
    project_id = uuid.uuid4()
    cicd_run_id = uuid.uuid4()
    decision_id = uuid.uuid4()
    evidence_id = uuid.uuid4()

    create = QualityGateDecisionCreate(
        project_id=project_id,
        cicd_run_id=cicd_run_id,
        summary="Regression evidence is missing",
        blocking_reasons=["missing regression evidence"],
        evidence_artifact_ids=[evidence_id],
        status_detail={"regression": "missing"},
    )
    read = QualityGateDecisionRead(
        id=decision_id,
        project_id=create.project_id,
        cicd_run_id=create.cicd_run_id,
        status=create.status,
        summary=create.summary,
        blocking_reasons=create.blocking_reasons,
        evidence_artifact_ids=create.evidence_artifact_ids,
        decided_by=create.decided_by,
        status_detail=create.status_detail,
    )

    body = read.model_dump(mode="json")
    assert body["id"] == str(decision_id)
    assert body["project_id"] == str(project_id)
    assert body["cicd_run_id"] == str(cicd_run_id)
    assert body["status"] == "needs_review"
    assert body["blocking_reasons"] == ["missing regression evidence"]
    assert body["evidence_artifact_ids"] == [str(evidence_id)]
    assert body["decided_by"] == "system"
    assert body["status_detail"] == {"regression": "missing"}
