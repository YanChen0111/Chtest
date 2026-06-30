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
    PatchScopeGateRead,
    UnitTestPatchCreate,
    UnitTestPatchRead,
)
from backend.app.modules.cicd.service import evaluate_patch_scope
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


def test_patch_scope_gate_allows_test_only_unified_diff() -> None:
    patch_text = """diff --git a/tests/test_coupon.py b/tests/test_coupon.py
new file mode 100644
--- /dev/null
+++ b/tests/test_coupon.py
@@ -0,0 +1,2 @@
+def test_coupon_boundary():
+    assert True
diff --git a/frontend/src/cart/__tests__/coupon.spec.ts b/frontend/src/cart/__tests__/coupon.spec.ts
--- a/frontend/src/cart/__tests__/coupon.spec.ts
+++ b/frontend/src/cart/__tests__/coupon.spec.ts
@@ -1 +1,2 @@
 test("coupon", () => {})
+test("coupon boundary", () => {})
diff --git a/frontend/src/cart/coupon.test.tsx b/frontend/src/cart/coupon.test.tsx
--- a/frontend/src/cart/coupon.test.tsx
+++ b/frontend/src/cart/coupon.test.tsx
@@ -1 +1,2 @@
 test("coupon", () => {})
+test("coupon ui", () => {})
"""

    result = evaluate_patch_scope(patch_text)

    assert result.allowed is True
    assert result.checked_paths == [
        "tests/test_coupon.py",
        "frontend/src/cart/__tests__/coupon.spec.ts",
        "frontend/src/cart/coupon.test.tsx",
    ]
    assert result.blocked_paths == []
    assert result.forbidden_patterns == []
    assert result.risk_level == "low"
    assert result.reason is None
    assert result.to_artifact_metadata()["allowed"] is True


def test_patch_scope_gate_schema_uses_artifact_metadata_field_names() -> None:
    read = PatchScopeGateRead(
        allowed=False,
        checked_paths=["app/coupon.py"],
        blocked_paths=["app/coupon.py"],
        forbidden_patterns=["source path modified: app/coupon.py"],
        risk_level="high",
        reason="PATCH_SCOPE_REJECTED",
    )

    body = read.model_dump(mode="json")
    assert body == {
        "allowed": False,
        "checked_paths": ["app/coupon.py"],
        "blocked_paths": ["app/coupon.py"],
        "forbidden_patterns": ["source path modified: app/coupon.py"],
        "risk_level": "high",
        "reason": "PATCH_SCOPE_REJECTED",
    }


def test_patch_scope_gate_rejects_empty_or_unparseable_patch() -> None:
    result = evaluate_patch_scope("")

    assert result.allowed is False
    assert result.checked_paths == []
    assert result.blocked_paths == []
    assert result.forbidden_patterns == []
    assert result.risk_level == "high"
    assert result.reason == "PATCH_SCOPE_REJECTED"


def test_patch_scope_gate_rejects_generated_paths_even_when_named_like_tests() -> None:
    patch_text = """diff --git a/frontend/dist/coupon.test.tsx b/frontend/dist/coupon.test.tsx
--- a/frontend/dist/coupon.test.tsx
+++ b/frontend/dist/coupon.test.tsx
@@ -1 +1,2 @@
 test("generated", () => {})
+test("generated new", () => {})
diff --git a/coverage/foo.spec.ts b/coverage/foo.spec.ts
--- a/coverage/foo.spec.ts
+++ b/coverage/foo.spec.ts
@@ -1 +1,2 @@
 test("coverage", () => {})
+test("coverage new", () => {})
"""

    result = evaluate_patch_scope(patch_text)

    assert result.allowed is False
    assert result.blocked_paths == ["frontend/dist/coupon.test.tsx", "coverage/foo.spec.ts"]
    assert result.risk_level == "high"
    assert result.reason == "PATCH_SCOPE_REJECTED"
    assert "generated artifact path modified: frontend/dist/coupon.test.tsx" in result.forbidden_patterns
    assert "generated artifact path modified: coverage/foo.spec.ts" in result.forbidden_patterns


def test_patch_scope_gate_rejects_source_config_migration_and_generated_paths() -> None:
    patch_text = """diff --git a/app/coupon.py b/app/coupon.py
--- a/app/coupon.py
+++ b/app/coupon.py
@@ -1 +1,2 @@
 old = True
+new = True
diff --git a/pyproject.toml b/pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -1 +1,2 @@
 [tool.pytest.ini_options]
+addopts = "-q"
diff --git a/migrations/001_coupon.sql b/migrations/001_coupon.sql
--- a/migrations/001_coupon.sql
+++ b/migrations/001_coupon.sql
@@ -1 +1,2 @@
 select 1;
+select 2;
diff --git a/frontend/dist/app.js b/frontend/dist/app.js
--- a/frontend/dist/app.js
+++ b/frontend/dist/app.js
@@ -1 +1,2 @@
 console.log("old")
+console.log("new")
diff --git a/scripts/helper.sh b/scripts/helper.sh
--- a/scripts/helper.sh
+++ b/scripts/helper.sh
@@ -1 +1,2 @@
 echo old
+echo new
"""

    result = evaluate_patch_scope(patch_text)

    assert result.allowed is False
    assert result.checked_paths == [
        "app/coupon.py",
        "pyproject.toml",
        "migrations/001_coupon.sql",
        "frontend/dist/app.js",
        "scripts/helper.sh",
    ]
    assert result.blocked_paths == [
        "app/coupon.py",
        "pyproject.toml",
        "migrations/001_coupon.sql",
        "frontend/dist/app.js",
        "scripts/helper.sh",
    ]
    assert result.risk_level == "high"
    assert result.reason == "PATCH_SCOPE_REJECTED"
    assert "source path modified: app/coupon.py" in result.forbidden_patterns
    assert "config path modified: pyproject.toml" in result.forbidden_patterns
    assert "migration path modified: migrations/001_coupon.sql" in result.forbidden_patterns
    assert "generated artifact path modified: frontend/dist/app.js" in result.forbidden_patterns
    assert "unknown non-test path modified: scripts/helper.sh" in result.forbidden_patterns
    assert result.to_artifact_metadata()["reason"] == "PATCH_SCOPE_REJECTED"
