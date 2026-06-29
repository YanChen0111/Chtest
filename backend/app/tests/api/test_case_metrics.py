from __future__ import annotations

import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate
from backend.app.modules.cases.service import calculate_case_metrics
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.requirements.models import Requirement


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


def add_candidate(
    session: Session,
    task: CaseGenerationTask,
    *,
    title: str,
    status: str,
    steps_json: list[str] | None = None,
    expected_results_json: list[str] | None = None,
    requirement_refs_json: list[str] | None = None,
    ai_reason: str = "covers fixture behavior",
) -> None:
    session.add(
        GeneratedCaseCandidate(
            generation_task_id=task.id,
            project_id=task.project_id,
            module_id=None,
            title=title,
            priority="P0",
            test_type="functional",
            precondition="fixture precondition",
            steps_json=steps_json if steps_json is not None else ["step"],
            expected_results_json=expected_results_json if expected_results_json is not None else ["expected"],
            input_data_json={},
            tags=[],
            requirement_refs_json=requirement_refs_json if requirement_refs_json is not None else ["requirement"],
            risk_refs_json=[],
            ai_reason=ai_reason,
            status=status,
        ),
    )


def create_generation_task(session: Session) -> CaseGenerationTask:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Checkout System")
    session.add(project)
    session.flush()
    requirement = Requirement(
        project_id=project.id,
        title="Coupon checkout rules",
        content="Coupon cannot be used with points.",
    )
    session.add(requirement)
    session.flush()
    task = CaseGenerationTask(
        project_id=project.id,
        requirement_id=requirement.id,
        requirement_review_id=None,
        ai_task_id=uuid.uuid4(),
        target_test_types=["functional", "ui"],
        status="succeeded",
        generated_count=5,
    )
    session.add(task)
    session.flush()
    return task


def test_calculate_case_metrics_from_candidate_review_states() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        task = create_generation_task(session)
        add_candidate(session, task, title="main flow", status="approved")
        add_candidate(session, task, title="conflict rule", status="approved")
        add_candidate(session, task, title="expired coupon", status="approved_after_edit")
        add_candidate(session, task, title="amount boundary", status="needs_optimization")
        add_candidate(session, task, title="unclear duplicate", status="rejected")
        session.commit()

        metrics = calculate_case_metrics(session, task.id)

    assert metrics.generation_task_id == task.id
    assert metrics.generated_count == 5
    assert metrics.approved_count == 2
    assert metrics.edited_count == 1
    assert metrics.rejected_count == 1
    assert metrics.optimization_count == 1
    assert metrics.reviewed_count == 5
    assert metrics.acceptance_rate == 0.6
    assert metrics.edit_rate == 0.2
    assert metrics.rejection_rate == 0.2
    assert metrics.optimization_rate == 0.2
    assert metrics.review_progress == 1.0
    assert metrics.field_complete_rate == 1.0


def test_field_complete_rate_counts_candidates_with_required_case_fields() -> None:
    SessionLocal = session_factory()
    with SessionLocal() as session:
        task = create_generation_task(session)
        add_candidate(session, task, title="complete", status="generated")
        add_candidate(session, task, title="missing steps", status="generated", steps_json=[])
        add_candidate(session, task, title="missing expected", status="generated", expected_results_json=[])
        add_candidate(session, task, title="missing refs", status="generated", requirement_refs_json=[])
        add_candidate(session, task, title="missing reason", status="generated", ai_reason="")
        session.commit()

        metrics = calculate_case_metrics(session, task.id)

    assert metrics.generated_count == 5
    assert metrics.reviewed_count == 0
    assert metrics.review_progress == 0.0
    assert metrics.field_complete_rate == 0.2
