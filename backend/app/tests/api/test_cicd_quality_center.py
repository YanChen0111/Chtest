from __future__ import annotations

import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.modules.cicd.models import CICDChangedFile, CICDRun
from backend.app.modules.cicd.schemas import (
    CICDChangedFileRead,
    CICDRunCreateRequest,
    CICDRunListRead,
    CICDRunRead,
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


def seed_project_repository(session: Session) -> tuple[Project, Repository]:
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
    return project, repository


def test_cicd_run_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, repository = seed_project_repository(session)
        cicd_run = CICDRun(
            project_id=project.id,
            repository_id=repository.id,
            source_type="local_diff",
            trigger_type="manual",
            provider="local",
            pipeline_name="local diff check",
            base_ref="main",
            head_ref="HEAD",
            summary="Coupon amount boundary change",
            overall_risk="medium",
        )
        session.add(cicd_run)
        session.commit()
        persisted = session.scalar(select(CICDRun).where(CICDRun.id == cicd_run.id))

    assert persisted is not None
    assert persisted.project_id == project.id
    assert persisted.repository_id == repository.id
    assert persisted.source_type == "local_diff"
    assert persisted.trigger_type == "manual"
    assert persisted.provider == "local"
    assert persisted.pipeline_name == "local diff check"
    assert persisted.base_ref == "main"
    assert persisted.head_ref == "HEAD"
    assert persisted.summary == "Coupon amount boundary change"
    assert persisted.overall_risk == "medium"
    assert persisted.quality_gate_status == "pending"
    assert persisted.status == "created"


def test_cicd_changed_file_model_persists_contract_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        project, repository = seed_project_repository(session)
        cicd_run = CICDRun(project_id=project.id, repository_id=repository.id)
        session.add(cicd_run)
        session.flush()
        changed_file = CICDChangedFile(
            cicd_run_id=cicd_run.id,
            path="app/coupon.py",
            old_path=None,
            change_type="modified",
            language="python",
            file_role="source",
            risk_level="medium",
            risk_reasons_json=["source file changed"],
            lines_added=12,
            lines_deleted=4,
        )
        session.add(changed_file)
        session.commit()
        persisted = session.scalar(select(CICDChangedFile).where(CICDChangedFile.id == changed_file.id))

    assert persisted is not None
    assert persisted.cicd_run_id == cicd_run.id
    assert persisted.path == "app/coupon.py"
    assert persisted.old_path is None
    assert persisted.change_type == "modified"
    assert persisted.language == "python"
    assert persisted.file_role == "source"
    assert persisted.risk_level == "medium"
    assert persisted.risk_reasons_json == ["source file changed"]
    assert persisted.lines_added == 12
    assert persisted.lines_deleted == 4


def test_cicd_run_create_request_defaults_to_local_first_contract() -> None:
    project_id = uuid.uuid4()
    repository_id = uuid.uuid4()

    request = CICDRunCreateRequest(
        project_id=project_id,
        repository_id=repository_id,
        base_ref="main",
        head_ref="HEAD",
    )

    assert request.project_id == project_id
    assert request.repository_id == repository_id
    assert request.source_type == "local_diff"
    assert request.trigger_type == "manual"
    assert request.provider == "local"
    assert request.diff_text is None


def test_cicd_run_read_schema_embeds_changed_files() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()
    repository_id = uuid.uuid4()
    changed_file_id = uuid.uuid4()

    read = CICDRunRead(
        id=run_id,
        project_id=project_id,
        repository_id=repository_id,
        source_type="local_diff",
        trigger_type="manual",
        provider="local",
        pipeline_name=None,
        base_ref="main",
        head_ref="HEAD",
        summary="Coupon amount boundary change",
        overall_risk="medium",
        quality_gate_status="pending",
        status="created",
        changed_files=[
            CICDChangedFileRead(
                id=changed_file_id,
                cicd_run_id=run_id,
                path="app/coupon.py",
                old_path=None,
                change_type="modified",
                language="python",
                file_role="source",
                risk_level="medium",
                risk_reasons=["source file changed"],
                lines_added=12,
                lines_deleted=4,
            ),
        ],
        analysis_artifacts=[],
    )
    listed = CICDRunListRead(items=[read], total=1)

    body = listed.model_dump(mode="json")
    assert body["items"][0]["id"] == str(run_id)
    assert body["items"][0]["repository_id"] == str(repository_id)
    assert body["items"][0]["changed_files"][0]["path"] == "app/coupon.py"
    assert body["items"][0]["changed_files"][0]["risk_reasons"] == ["source file changed"]
