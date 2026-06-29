from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.projects.models import Project, Workspace


PROJECT_CORE_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260626_0001_project_core.py"
AI_RUNTIME_MIGRATION_PATH = Path(__file__).parents[3] / "alembic/versions/20260629_0002_ai_runtime_core.py"


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


def test_ai_runtime_migration_creates_contract_tables() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    project_core_migration = load_migration("project_core_migration", PROJECT_CORE_MIGRATION_PATH)
    ai_runtime_migration = load_migration("ai_runtime_migration", AI_RUNTIME_MIGRATION_PATH)

    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        operations = Operations(context)
        original_project_core_op = project_core_migration.op
        original_ai_runtime_op = ai_runtime_migration.op
        project_core_migration.op = operations
        ai_runtime_migration.op = operations
        try:
            project_core_migration.upgrade()
            ai_runtime_migration.upgrade()
        finally:
            project_core_migration.op = original_project_core_op
            ai_runtime_migration.op = original_ai_runtime_op

        tables = set(inspect(connection).get_table_names())
        columns_by_table = {
            table_name: {column["name"] for column in inspect(connection).get_columns(table_name)}
            for table_name in ("ai_tasks", "artifacts", "llm_call_logs")
        }

    assert {"ai_tasks", "artifacts", "llm_call_logs"}.issubset(tables)
    for columns in columns_by_table.values():
        assert {"id", "created_at", "updated_at", "created_by", "updated_by"}.issubset(columns)


def test_ai_runtime_migration_context_artifact_ids_uses_uuid_array_for_postgres() -> None:
    migration = load_migration("ai_runtime_migration_type_check", AI_RUNTIME_MIGRATION_PATH)

    context_type = migration.uuid_list_type().dialect_impl(postgresql.dialect())

    assert isinstance(context_type, postgresql.ARRAY)
    assert context_type.item_type.python_type is uuid.UUID


def test_ai_task_persists_explicit_empty_context_artifact_ids(session: Session) -> None:
    project = Project(workspace=Workspace(name="Personal Workspace"), name="Checkout")
    ai_task = AITask(
        project=project,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
        context_artifact_ids=[],
    )

    session.add(ai_task)
    session.commit()
    session.refresh(ai_task)

    assert ai_task.context_artifact_ids == []
    assert ai_task.model_provider == "mock"
    assert ai_task.model_name == "mock-model"
    assert ai_task.status == "created"
    assert ai_task.input_json == {}
    assert ai_task.output_json == {}
    assert ai_task.token_usage_json == {}


def test_context_artifact_metadata_and_ai_task_context_ids_persist(session: Session) -> None:
    project_id = uuid.uuid4()
    project = Project(id=project_id, workspace=Workspace(name="Personal Workspace"), name="Checkout")
    artifact_id = uuid.uuid4()
    artifact = Artifact(
        id=artifact_id,
        project=project,
        owner_entity_type="Project",
        owner_entity_id=project_id,
        artifact_type="context_markdown",
        file_path=f"projects/{project_id}/context-artifacts/{artifact_id}/content.md",
        mime_type="text/markdown",
        size_bytes=128,
        sha256="a" * 64,
        metadata_json={
            "title": "coupon-api-notes.md",
            "source_ref": "manual:coupon-api-notes.md",
            "safe_to_show": True,
            "redaction_applied": False,
            "redaction_report_artifact_id": None,
            "allowed_for_prompt": True,
        },
    )
    ai_task = AITask(
        project=project,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
        model_name="mock-requirement-review",
        context_artifact_ids=[artifact_id],
    )

    session.add_all([artifact, ai_task])
    session.commit()
    session.refresh(artifact)
    session.refresh(ai_task)

    assert artifact.owner_entity_type == "Project"
    assert artifact.owner_entity_id == project.id
    assert artifact.artifact_type == "context_markdown"
    assert artifact.metadata_json["title"] == "coupon-api-notes.md"
    assert artifact.metadata_json["allowed_for_prompt"] is True
    assert ai_task.context_artifact_ids == [artifact_id]


def test_ai_runtime_json_dict_fields_track_in_place_updates(session: Session) -> None:
    project = Project(workspace=Workspace(name="Personal Workspace"), name="Checkout")
    ai_task = AITask(
        project=project,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
        output_json={"status": "draft"},
    )
    artifact = Artifact(
        project=project,
        owner_entity_type="AITask",
        owner_entity_id=uuid.uuid4(),
        artifact_type="parsed_output",
        file_path="projects/demo/ai-tasks/demo/parsed_output.json",
        sha256="d" * 64,
        metadata_json={"safe_to_show": True},
    )

    session.add_all([ai_task, artifact])
    session.commit()

    ai_task.output_json["status"] = "approved"
    artifact.metadata_json["redaction_applied"] = False
    session.commit()
    session.expire_all()

    refreshed_ai_task = session.get(AITask, ai_task.id)
    refreshed_artifact = session.get(Artifact, artifact.id)

    assert refreshed_ai_task is not None
    assert refreshed_artifact is not None
    assert refreshed_ai_task.output_json["status"] == "approved"
    assert refreshed_artifact.metadata_json["redaction_applied"] is False


def test_llm_call_log_persists_artifact_links_and_safe_summaries(session: Session) -> None:
    project_id = uuid.uuid4()
    ai_task_id = uuid.uuid4()
    project = Project(id=project_id, workspace=Workspace(name="Personal Workspace"), name="Checkout")
    ai_task = AITask(
        id=ai_task_id,
        project=project,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=uuid.uuid4(),
        skill_version_id=uuid.uuid4(),
    )
    request_artifact = Artifact(
        project=project,
        owner_entity_type="AITask",
        owner_entity_id=ai_task_id,
        artifact_type="input_json",
        file_path=f"projects/{project_id}/ai-tasks/{ai_task_id}/input.json",
        sha256="b" * 64,
    )
    response_artifact = Artifact(
        project=project,
        owner_entity_type="AITask",
        owner_entity_id=ai_task_id,
        artifact_type="raw_llm_output",
        file_path=f"projects/{project_id}/ai-tasks/{ai_task_id}/raw_output.json",
        sha256="c" * 64,
    )
    llm_call = LLMCallLog(
        project=project,
        ai_task=ai_task,
        prompt_version_id=ai_task.prompt_version_id,
        skill_version_id=ai_task.skill_version_id,
        model_name="mock-requirement-review",
        status="succeeded",
        request_artifact=request_artifact,
        response_artifact=response_artifact,
        input_summary_json={"task_type": "requirement_review"},
        output_summary_json={"issue_count": 2},
        token_usage_json={"prompt_tokens": 42, "completion_tokens": 18},
        latency_ms=25,
    )

    session.add(llm_call)
    session.commit()
    session.refresh(llm_call)

    assert ai_task.llm_call_logs == [llm_call]
    assert llm_call.call_index == 1
    assert llm_call.provider == "mock"
    assert llm_call.request_artifact is request_artifact
    assert llm_call.response_artifact is response_artifact
    assert llm_call.input_summary_json == {"task_type": "requirement_review"}
    assert llm_call.output_summary_json == {"issue_count": 2}
