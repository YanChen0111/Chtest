from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.cicd.models import CICDRun, QualityGateDecision, UnitTestPatch
from backend.app.modules.cicd.schemas import (
    QualityGateDecisionCreate,
    QualityGateDecisionRead,
    PatchScopeGateRead,
    UnitTestPatchCreate,
    UnitTestPatchRead,
)
from backend.app.modules.cicd.service import evaluate_patch_scope
from backend.app.modules.execution.models import TestRun
from backend.app.modules.projects.models import Project, Repository, Workspace
from backend.app.modules.projects.router import get_session
from backend.app.modules.reporting.models import Report


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


class ASGIResponse:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self.body = body

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class ASGIClient:
    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def post(self, path: str, json_body: dict[str, Any]) -> ASGIResponse:
        return asyncio.run(self._request("POST", path, json_body))

    async def _request(self, method: str, path: str, json_body: dict[str, Any] | None) -> ASGIResponse:
        body = json.dumps(json_body).encode("utf-8") if json_body is not None else b""
        status_code: int | None = None
        body_chunks: list[bytes] = []
        request_complete = False

        async def receive() -> dict[str, Any]:
            nonlocal request_complete
            if not request_complete:
                request_complete = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        async def send(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                body_chunks.append(message.get("body", b""))

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": b"",
            "headers": [
                (b"host", b"testserver"),
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }

        await self.asgi_app(scope, receive, send)
        assert status_code is not None
        return ASGIResponse(status_code, b"".join(body_chunks))


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


def test_generate_unit_test_patch_api_creates_review_gated_scope_validated_patch() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            _project, cicd_run, _ai_task = seed_cicd_run_and_ai_task(session)
            session.commit()
            cicd_run_id = cicd_run.id

        patch_text = """diff --git a/tests/test_coupon.py b/tests/test_coupon.py
new file mode 100644
--- /dev/null
+++ b/tests/test_coupon.py
@@ -0,0 +1,2 @@
+def test_coupon_boundary():
+    assert True
"""
        client = ASGIClient(app)
        response = client.post(
            f"/api/cicd/runs/{cicd_run_id}/unit-test-patches",
            {
                "patch_text": patch_text,
                "target_framework": "pytest",
                "test_intent": "Cover coupon boundary change",
                "coverage_target": [{"path": "app/coupon.py", "reason": "changed source"}],
            },
        )

        assert response.status_code == 202
        body = response.json()
        assert body["cicd_run_id"] == str(cicd_run_id)
        assert body["status"] == "scope_validated"
        assert body["target_framework"] == "pytest"
        assert body["scope_gate_result"]["allowed"] is True
        assert body["scope_gate_result"]["checked_paths"] == ["tests/test_coupon.py"]

        with SessionLocal() as session:
            patch = session.get(UnitTestPatch, uuid.UUID(body["id"]))
            ai_task = session.get(AITask, uuid.UUID(body["ai_task_id"]))
            assert session.scalar(select(TestRun)) is None
            assert session.scalar(select(QualityGateDecision)) is None
            assert session.scalar(select(Report)) is None

        assert patch is not None
        assert patch.status == "scope_validated"
        assert patch.scope_gate_result_json["allowed"] is True
        assert patch.patch_text == patch_text
        assert ai_task is not None
        assert ai_task.agent_name == "UnitTestAgent"
        assert ai_task.task_type == "unit_test_patch"
        assert ai_task.status == "succeeded"
    finally:
        app.dependency_overrides.clear()


def test_generate_unit_test_patch_api_blocks_approve_for_scope_rejected_patch() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            _project, cicd_run, _ai_task = seed_cicd_run_and_ai_task(session)
            session.commit()
            cicd_run_id = cicd_run.id

        client = ASGIClient(app)
        generate_response = client.post(
            f"/api/cicd/runs/{cicd_run_id}/unit-test-patches",
            {
                "patch_text": "diff --git a/app/coupon.py b/app/coupon.py\n--- a/app/coupon.py\n+++ b/app/coupon.py\n@@ -1 +1,2 @@\n-old\n+new\n",
                "test_intent": "This should be rejected",
            },
        )
        patch_id = generate_response.json()["id"]

        approve_response = client.post(
            f"/api/cicd/unit-test-patches/{patch_id}/approve",
            {"review_comment": "Do not allow source patch"},
        )

        assert generate_response.status_code == 202
        assert generate_response.json()["status"] == "scope_rejected"
        assert generate_response.json()["scope_gate_result"]["reason"] == "PATCH_SCOPE_REJECTED"
        assert approve_response.status_code == 400
        assert approve_response.json()["error_code"] == "UNIT_TEST_PATCH_INVALID_STATUS"

        with SessionLocal() as session:
            patch = session.get(UnitTestPatch, uuid.UUID(patch_id))

        assert patch is not None
        assert patch.status == "scope_rejected"
        assert patch.review_comment is None
    finally:
        app.dependency_overrides.clear()


def test_approve_and_reject_unit_test_patch_api_updates_review_status() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            _project, cicd_run, ai_task = seed_cicd_run_and_ai_task(session)
            approve_patch = UnitTestPatch(
                cicd_run_id=cicd_run.id,
                ai_task_id=ai_task.id,
                patch_text="diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n",
                scope_gate_result_json={"allowed": True},
                test_intent="Approve me",
                status="scope_validated",
            )
            reject_patch = UnitTestPatch(
                cicd_run_id=cicd_run.id,
                ai_task_id=ai_task.id,
                patch_text="diff --git a/tests/test_other.py b/tests/test_other.py\n",
                scope_gate_result_json={"allowed": True},
                test_intent="Reject me",
                status="awaiting_review",
            )
            session.add_all([approve_patch, reject_patch])
            session.commit()
            approve_patch_id = approve_patch.id
            reject_patch_id = reject_patch.id

        client = ASGIClient(app)
        approve_response = client.post(
            f"/api/cicd/unit-test-patches/{approve_patch_id}/approve",
            {"review_comment": "Only tests are modified"},
        )
        reject_response = client.post(
            f"/api/cicd/unit-test-patches/{reject_patch_id}/reject",
            {"review_comment": "Need stronger assertions"},
        )

        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "approved"
        assert reject_response.status_code == 200
        assert reject_response.json()["status"] == "rejected"

        with SessionLocal() as session:
            approved = session.get(UnitTestPatch, approve_patch_id)
            rejected = session.get(UnitTestPatch, reject_patch_id)

        assert approved is not None
        assert approved.status == "approved"
        assert approved.review_comment == "Only tests are modified"
        assert rejected is not None
        assert rejected.status == "rejected"
        assert rejected.review_comment == "Need stronger assertions"
    finally:
        app.dependency_overrides.clear()


def test_apply_unit_test_patch_api_requires_approved_patch_and_writes_evidence_artifact() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            project, cicd_run, ai_task = seed_cicd_run_and_ai_task(session)
            patch_text = """diff --git a/tests/test_coupon.py b/tests/test_coupon.py
new file mode 100644
--- /dev/null
+++ b/tests/test_coupon.py
@@ -0,0 +1,2 @@
+def test_coupon_boundary():
+    assert True
"""
            patch = UnitTestPatch(
                cicd_run_id=cicd_run.id,
                ai_task_id=ai_task.id,
                patch_text=patch_text,
                scope_gate_result_json={"allowed": True, "checked_paths": ["tests/test_coupon.py"]},
                test_intent="Apply me",
                status="approved",
            )
            session.add(patch)
            session.commit()
            project_id = project.id
            patch_id = patch.id

        client = ASGIClient(app)
        response = client.post(
            f"/api/cicd/unit-test-patches/{patch_id}/apply",
            {"confirm_scope_gate_result": True},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["unit_test_patch_id"] == str(patch_id)
        assert body["status"] == "applied"
        assert body["applied_artifact_id"] is not None

        with SessionLocal() as session:
            applied = session.get(UnitTestPatch, patch_id)
            artifact = session.get(Artifact, uuid.UUID(body["applied_artifact_id"]))
            assert session.scalar(select(TestRun)) is None
            assert session.scalar(select(QualityGateDecision)) is None
            assert session.scalar(select(Report)) is None

        assert applied is not None
        assert applied.status == "applied"
        assert applied.patch_text == patch_text
        assert artifact is not None
        assert artifact.project_id == project_id
        assert artifact.owner_entity_type == "UnitTestPatch"
        assert artifact.owner_entity_id == patch_id
        assert artifact.artifact_type == "unit_test_patch"
        assert artifact.file_path.endswith(f"/{patch_id}/unit_test.patch")
        assert artifact.metadata_json["scope_gate_result"]["allowed"] is True
        assert artifact.metadata_json["patch_text"] == patch_text
    finally:
        app.dependency_overrides.clear()


def test_apply_unit_test_patch_api_rejects_unapproved_or_unsafe_patch() -> None:
    SessionLocal = session_factory()

    def override_get_session():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with SessionLocal() as session:
            _project, cicd_run, ai_task = seed_cicd_run_and_ai_task(session)
            unapproved = UnitTestPatch(
                cicd_run_id=cicd_run.id,
                ai_task_id=ai_task.id,
                patch_text="diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n",
                scope_gate_result_json={"allowed": True},
                test_intent="Not approved",
                status="scope_validated",
            )
            unsafe = UnitTestPatch(
                cicd_run_id=cicd_run.id,
                ai_task_id=ai_task.id,
                patch_text="diff --git a/app/coupon.py b/app/coupon.py\n--- a/app/coupon.py\n+++ b/app/coupon.py\n@@ -1 +1,2 @@\n-old\n+new\n",
                scope_gate_result_json={"allowed": True},
                test_intent="Unsafe after edit",
                status="approved",
            )
            session.add_all([unapproved, unsafe])
            session.commit()
            unapproved_id = unapproved.id
            unsafe_id = unsafe.id

        client = ASGIClient(app)
        unapproved_response = client.post(
            f"/api/cicd/unit-test-patches/{unapproved_id}/apply",
            {"confirm_scope_gate_result": True},
        )
        unsafe_response = client.post(
            f"/api/cicd/unit-test-patches/{unsafe_id}/apply",
            {"confirm_scope_gate_result": True},
        )

        assert unapproved_response.status_code == 400
        assert unapproved_response.json()["error_code"] == "UNIT_TEST_PATCH_INVALID_STATUS"
        assert unsafe_response.status_code == 400
        assert unsafe_response.json()["error_code"] == "PATCH_SCOPE_REJECTED"

        with SessionLocal() as session:
            assert session.get(UnitTestPatch, unapproved_id).status == "scope_validated"
            assert session.get(UnitTestPatch, unsafe_id).status == "apply_failed"
            assert session.scalar(select(Artifact).where(Artifact.owner_entity_type == "UnitTestPatch")) is None
    finally:
        app.dependency_overrides.clear()
