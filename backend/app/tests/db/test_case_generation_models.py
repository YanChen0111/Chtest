from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.cases.models import CaseGenerationTask, GeneratedCaseCandidate, TestCase as CaseModel
from backend.app.modules.projects.models import Project, Workspace
from backend.app.modules.requirements.models import Requirement, RequirementReview


PROJECT_CORE_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260626_0001_project_core.py"
AI_RUNTIME_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0002_ai_runtime_core.py"
PROMPT_SKILL_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0003_prompt_skill_registry.py"
REQUIREMENT_REVIEW_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0004_requirement_review.py"
MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0005_case_generation.py"


def load_migration(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def test_case_generation_migration_creates_contract_tables() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    migrations = [
        load_migration("project_core_migration", PROJECT_CORE_MIGRATION_PATH),
        load_migration("ai_runtime_migration", AI_RUNTIME_MIGRATION_PATH),
        load_migration("prompt_skill_migration", PROMPT_SKILL_MIGRATION_PATH),
        load_migration("requirement_review_migration", REQUIREMENT_REVIEW_MIGRATION_PATH),
        load_migration("case_generation_migration", MIGRATION_PATH),
    ]

    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        operations = Operations(context)
        original_ops = [migration.op for migration in migrations]
        for migration in migrations:
            migration.op = operations
        try:
            for migration in migrations:
                migration.upgrade()
        finally:
            for migration, original_op in zip(migrations, original_ops, strict=True):
                migration.op = original_op

        inspector = inspect(connection)
        tables = set(inspector.get_table_names())
        task_columns = {column["name"] for column in inspector.get_columns("case_generation_tasks")}
        candidate_columns = {column["name"] for column in inspector.get_columns("generated_case_candidates")}
        test_case_columns = {column["name"] for column in inspector.get_columns("test_cases")}

    assert {"case_generation_tasks", "generated_case_candidates", "test_cases"}.issubset(tables)
    assert {
        "id",
        "project_id",
        "requirement_id",
        "requirement_review_id",
        "ai_task_id",
        "target_test_types",
        "status",
        "generated_count",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(task_columns)
    assert {
        "id",
        "generation_task_id",
        "project_id",
        "module_id",
        "title",
        "priority",
        "test_type",
        "precondition",
        "steps_json",
        "expected_results_json",
        "input_data_json",
        "tags",
        "requirement_refs_json",
        "risk_refs_json",
        "ai_reason",
        "duplicate_of_case_id",
        "status",
        "review_comment",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(candidate_columns)
    assert {
        "id",
        "project_id",
        "module_id",
        "source_candidate_id",
        "title",
        "priority",
        "test_type",
        "precondition",
        "steps_json",
        "expected_results_json",
        "input_data_json",
        "tags",
        "source_type",
        "review_status",
        "status",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }.issubset(test_case_columns)


def seed_requirement_review(session: Session) -> tuple[Project, Requirement, RequirementReview, AITask]:
    project = Project(workspace=Workspace(name="Personal Workspace"), name="Checkout")
    requirement = Requirement(
        project=project,
        title="Coupon checkout rules",
        content="Coupon cannot be used with points.",
    )
    ai_task = AITask(
        project=project,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
    )
    review = RequirementReview(requirement=requirement, ai_task=ai_task, status="reviewed")
    session.add_all([project, requirement, ai_task, review])
    session.commit()
    return project, requirement, review, ai_task


def test_case_generation_task_persists_contract_defaults() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project, requirement, review, ai_task = seed_requirement_review(session)
        generation_task = CaseGenerationTask(
            project_id=project.id,
            requirement_id=requirement.id,
            requirement_review_id=review.id,
            ai_task_id=ai_task.id,
            target_test_types=["functional", "ui"],
        )

        session.add(generation_task)
        session.commit()
        session.refresh(generation_task)

        assert generation_task.id is not None
        assert generation_task.status == "created"
        assert generation_task.generated_count == 0
        assert generation_task.target_test_types == ["functional", "ui"]


def test_generated_candidate_and_test_case_persist_defaults_and_relationships() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project, requirement, review, ai_task = seed_requirement_review(session)
        generation_task = CaseGenerationTask(
            project_id=project.id,
            requirement_id=requirement.id,
            requirement_review_id=review.id,
            ai_task_id=ai_task.id,
        )
        candidate = GeneratedCaseCandidate(
            generation_task=generation_task,
            project_id=project.id,
            title="Expired coupon cannot be used",
            steps_json=["Open checkout", "Select expired coupon", "Submit order"],
            expected_results_json=["Submission is blocked", "Expired coupon message is shown"],
            input_data_json={"coupon_state": "expired"},
            tags=["coupon", "checkout"],
            requirement_refs_json=[str(requirement.id)],
            risk_refs_json=[],
            ai_reason="Covers expiration boundary.",
        )
        test_case = CaseModel(
            project_id=project.id,
            source_candidate=candidate,
            title="Expired coupon cannot be used",
            steps_json=["Open checkout", "Select expired coupon", "Submit order"],
            expected_results_json=["Submission is blocked", "Expired coupon message is shown"],
            input_data_json={"coupon_state": "expired"},
            tags=["coupon", "checkout"],
        )

        session.add_all([candidate, test_case])
        session.commit()
        session.refresh(candidate)
        session.refresh(test_case)

        assert candidate.priority == "P2"
        assert candidate.test_type == "functional"
        assert candidate.precondition is None
        assert candidate.status == "generated"
        assert candidate.review_comment is None
        assert candidate.generation_task is generation_task
        assert test_case.source_candidate is candidate
        assert test_case.priority == "P2"
        assert test_case.test_type == "functional"
        assert test_case.source_type == "ai"
        assert test_case.review_status == "approved"
        assert test_case.status == "active"


def test_case_generation_json_and_list_fields_track_in_place_updates() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project, requirement, review, ai_task = seed_requirement_review(session)
        generation_task = CaseGenerationTask(
            project_id=project.id,
            requirement_id=requirement.id,
            requirement_review_id=review.id,
            ai_task_id=ai_task.id,
            target_test_types=["functional"],
        )
        candidate = GeneratedCaseCandidate(
            generation_task=generation_task,
            project_id=project.id,
            title="Coupon conflict",
            ai_reason="Covers coupon and points conflict.",
        )
        test_case = CaseModel(
            project_id=project.id,
            title="Coupon conflict",
        )

        session.add_all([candidate, test_case])
        session.commit()

        generation_task.target_test_types.append("ui")
        candidate.steps_json.append("Select coupon and points together")
        candidate.expected_results_json.append("Submit is blocked")
        candidate.input_data_json["coupon_state"] = "valid"
        candidate.tags.append("pricing")
        candidate.requirement_refs_json.append(str(requirement.id))
        candidate.risk_refs_json.append("risk-1")
        test_case.steps_json.append("Select coupon")
        test_case.expected_results_json.append("Discount is applied")
        test_case.input_data_json["coupon_state"] = "valid"
        test_case.tags.append("regression")
        session.commit()
        session.expire_all()

        refreshed_task = session.get(CaseGenerationTask, generation_task.id)
        refreshed_candidate = session.get(GeneratedCaseCandidate, candidate.id)
        refreshed_test_case = session.get(CaseModel, test_case.id)

        assert refreshed_task is not None
        assert refreshed_candidate is not None
        assert refreshed_test_case is not None
        assert refreshed_task.target_test_types == ["functional", "ui"]
        assert refreshed_candidate.steps_json == ["Select coupon and points together"]
        assert refreshed_candidate.expected_results_json == ["Submit is blocked"]
        assert refreshed_candidate.input_data_json == {"coupon_state": "valid"}
        assert refreshed_candidate.tags == ["pricing"]
        assert refreshed_candidate.requirement_refs_json == [str(requirement.id)]
        assert refreshed_candidate.risk_refs_json == ["risk-1"]
        assert refreshed_test_case.steps_json == ["Select coupon"]
        assert refreshed_test_case.expected_results_json == ["Discount is applied"]
        assert refreshed_test_case.input_data_json == {"coupon_state": "valid"}
        assert refreshed_test_case.tags == ["regression"]
