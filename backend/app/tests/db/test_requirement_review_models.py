from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.requirements.models import Requirement, RequirementReview, RiskItem


MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0004_requirement_review.py"
PROJECT_CORE_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260626_0001_project_core.py"
AI_RUNTIME_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0002_ai_runtime_core.py"
PROMPT_SKILL_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0003_prompt_skill_registry.py"


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def load_migration(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def seed_project(session: Session) -> Project:
    workspace = Workspace(name="Personal Workspace")
    project = Project(workspace=workspace, name="Checkout")
    session.add(project)
    session.commit()
    return project


def seed_ai_task(session: Session, project: Project) -> AITask:
    ai_task = AITask(
        project_id=project.id,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
    )
    session.add(ai_task)
    session.commit()
    return ai_task


def test_requirement_review_migration_creates_contract_tables() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    project_core_migration = load_migration("project_core_migration", PROJECT_CORE_MIGRATION_PATH)
    ai_runtime_migration = load_migration("ai_runtime_migration", AI_RUNTIME_MIGRATION_PATH)
    prompt_skill_migration = load_migration("prompt_skill_migration", PROMPT_SKILL_MIGRATION_PATH)
    migration = load_migration("requirement_review_migration", MIGRATION_PATH)

    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        operations = Operations(context)
        original_project_core_op = project_core_migration.op
        original_ai_runtime_op = ai_runtime_migration.op
        original_prompt_skill_op = prompt_skill_migration.op
        original_op = migration.op
        project_core_migration.op = operations
        ai_runtime_migration.op = operations
        prompt_skill_migration.op = operations
        migration.op = operations
        try:
            project_core_migration.upgrade()
            ai_runtime_migration.upgrade()
            prompt_skill_migration.upgrade()
            migration.upgrade()
        finally:
            project_core_migration.op = original_project_core_op
            ai_runtime_migration.op = original_ai_runtime_op
            prompt_skill_migration.op = original_prompt_skill_op
            migration.op = original_op

        inspector = inspect(connection)
        tables = set(inspector.get_table_names())
        requirement_columns = {column["name"] for column in inspector.get_columns("requirements")}
        review_columns = {column["name"] for column in inspector.get_columns("requirement_reviews")}
        risk_columns = {column["name"] for column in inspector.get_columns("risk_items")}

    assert {"requirements", "requirement_reviews", "risk_items"}.issubset(tables)
    assert {
        "id",
        "project_id",
        "module_id",
        "title",
        "content",
        "source_type",
        "source_ref",
        "status",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(requirement_columns)
    assert {
        "id",
        "requirement_id",
        "ai_task_id",
        "completeness_score",
        "clarity_score",
        "consistency_score",
        "testability_score",
        "feasibility_score",
        "logic_score",
        "overall_score",
        "issues_json",
        "clarification_questions_json",
        "test_design_notes_json",
        "status",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(review_columns)
    assert {
        "id",
        "project_id",
        "requirement_review_id",
        "title",
        "risk_level",
        "category",
        "impact",
        "suggestion",
        "status",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(risk_columns)


def test_requirement_persists_contract_defaults(session: Session) -> None:
    project = seed_project(session)
    requirement = Requirement(
        project_id=project.id,
        title="Coupon can be applied at checkout",
        content="As a buyer, I can apply a valid coupon before payment.",
    )

    session.add(requirement)
    session.commit()
    session.refresh(requirement)

    assert requirement.id is not None
    assert requirement.module_id is None
    assert requirement.source_type == "manual"
    assert requirement.source_ref is None
    assert requirement.status == "active"


def test_requirement_review_persists_scores_and_json_lists(session: Session) -> None:
    project = seed_project(session)
    ai_task = seed_ai_task(session, project)
    requirement = Requirement(
        project_id=project.id,
        title="Checkout coupon",
        content="Coupon rules must be clear enough to test.",
    )
    review = RequirementReview(
        requirement=requirement,
        ai_task_id=ai_task.id,
        completeness_score=80,
        clarity_score=70,
        consistency_score=90,
        testability_score=85,
        feasibility_score=75,
        logic_score=88,
        overall_score=81,
        issues_json=[{"type": "ambiguity", "text": "Missing expiry timezone."}],
        clarification_questions_json=["Which timezone controls coupon expiry?"],
        test_design_notes_json=["Cover expired and valid coupon paths."],
    )

    session.add(review)
    session.commit()
    session.refresh(review)

    assert review.status == "draft"
    assert review.requirement_id == requirement.id
    assert review.ai_task_id == ai_task.id
    assert review.issues_json[0]["type"] == "ambiguity"
    assert review.clarification_questions_json == ["Which timezone controls coupon expiry?"]
    assert review.test_design_notes_json == ["Cover expired and valid coupon paths."]


def test_risk_item_persists_contract_defaults_and_optional_review(session: Session) -> None:
    project = seed_project(session)
    risk = RiskItem(
        project_id=project.id,
        title="Coupon stacking creates pricing risk",
        impact="Incorrect discount total can affect payment amount.",
        suggestion="Add cases for stacked, exclusive, and expired coupons.",
    )

    session.add(risk)
    session.commit()
    session.refresh(risk)

    assert risk.requirement_review_id is None
    assert risk.risk_level == "medium"
    assert risk.category == "business"
    assert risk.status == "active"


def test_requirement_review_score_constraints(session: Session) -> None:
    project = seed_project(session)
    ai_task = seed_ai_task(session, project)
    requirement = Requirement(
        project_id=project.id,
        title="Checkout coupon",
        content="Coupon rules must be clear enough to test.",
    )
    review = RequirementReview(
        requirement=requirement,
        ai_task_id=ai_task.id,
        completeness_score=101,
    )

    session.add(review)

    with pytest.raises(IntegrityError):
        session.commit()


def test_requirement_review_json_fields_track_in_place_updates(session: Session) -> None:
    project = seed_project(session)
    ai_task = seed_ai_task(session, project)
    requirement = Requirement(
        project_id=project.id,
        title="Checkout coupon",
        content="Coupon rules must be clear enough to test.",
    )
    review = RequirementReview(requirement=requirement, ai_task_id=ai_task.id)

    session.add(review)
    session.commit()

    review.issues_json.append({"type": "gap", "text": "No invalid coupon path."})
    review.clarification_questions_json.append("Can one coupon be reused?")
    review.test_design_notes_json.append("Pair boundary values with state changes.")
    session.commit()
    session.expire_all()

    refreshed = session.get(RequirementReview, review.id)

    assert refreshed is not None
    assert refreshed.issues_json == [{"type": "gap", "text": "No invalid coupon path."}]
    assert refreshed.clarification_questions_json == ["Can one coupon be reused?"]
    assert refreshed.test_design_notes_json == ["Pair boundary values with state changes."]
