from __future__ import annotations

import uuid
import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.models.base import Base
from backend.app.modules.ai_runtime.artifact_store import LocalArtifactStore
from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.prompt_skill.registry_loader import compute_content_hash
from backend.app.modules.projects.models import Project, Workspace
from backend.app.workers.enqueue import FakeAIQueue, enqueue_ai_task
from backend.app.workers.handlers.ai_task_handler import run_ai_task


@pytest.fixture()
def session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False, future=True)


def create_ai_task(
    session: Session,
    *,
    model_provider: str = "mock",
    model_name: str = "mock-requirement-review",
    mode: str = "success",
    status: str = "created",
) -> AITask:
    project = Project(workspace=Workspace(name=f"Workspace {uuid.uuid4()}"), name=f"Project {uuid.uuid4()}")
    prompt_content = "# Prompt: requirement_review v1\n\n## Agent\n\nRequirementReviewAgent"
    skill_content = "# Skill: requirement-review-skill v1\n\n## Applies To\n\n- RequirementReviewAgent"
    prompt = PromptVersion(
        name="requirement_review",
        version="v1",
        hash=compute_content_hash(prompt_content),
        agent_name="RequirementReviewAgent",
        content=prompt_content,
        input_schema_json={"type": "object"},
        output_schema_json={"type": "object"},
    )
    skill = SkillVersion(
        name="requirement-review-skill",
        version="v1",
        hash=compute_content_hash(skill_content),
        applicable_agents=["RequirementReviewAgent"],
        content=skill_content,
        quality_gates_json=["Return structured review output."],
        forbidden_actions_json=["Do not invent requirement facts."],
        tool_permissions_json=[],
    )
    session.add_all([prompt, skill])
    session.flush()
    ai_task = AITask(
        project=project,
        agent_name="RequirementReviewAgent",
        task_type="requirement_review",
        prompt_version_id=prompt.id,
        skill_version_id=skill.id,
        model_provider=model_provider,
        model_name=model_name,
        input_json={
            "requirement": "# 优惠券结算规则",
            "mock_mode": mode,
            "context_manifest": [
                {
                    "artifact_id": "00000000-0000-0000-0000-000000000371",
                    "title": "coupon-api-notes.md",
                    "mime_type": "text/markdown",
                    "sha256": "sha256:example",
                    "redaction_applied": False,
                },
            ],
        },
        context_artifact_ids=[uuid.UUID("00000000-0000-0000-0000-000000000371")],
        status=status,
    )
    session.add(ai_task)
    session.commit()
    session.refresh(ai_task)
    return ai_task


def test_enqueue_moves_created_task_to_pending(session_factory: sessionmaker[Session]) -> None:
    queue = FakeAIQueue()
    with session_factory() as session:
        ai_task = create_ai_task(session)

        job = enqueue_ai_task(session, queue, ai_task.id)

        session.refresh(ai_task)
        assert ai_task.status == "pending"
        assert job.ai_task_id == ai_task.id
        assert queue.pop_next() == job


def test_worker_runs_pending_task_and_records_artifacts_and_llm_log(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory() as session:
        ai_task = create_ai_task(session)
        queue = FakeAIQueue()
        job = enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next())

        session.refresh(ai_task)
        artifacts = list(session.scalars(select(Artifact).where(Artifact.owner_entity_id == ai_task.id)))
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))

        assert job.ai_task_id == ai_task.id
        assert ai_task.status == "succeeded"
        assert ai_task.started_at is not None
        assert ai_task.finished_at is not None
        assert ai_task.output_json["overall_score"] == 82
        assert ai_task.output_json["used_context_artifact_ids"] == [str(ai_task.context_artifact_ids[0])]
        assert {artifact.artifact_type for artifact in artifacts} == {
            "input_json",
            "raw_llm_output",
            "parsed_output",
            "schema_validation",
        }
        assert {Path(artifact.file_path).name for artifact in artifacts} >= {
            "input.json",
            "raw_output.json",
            "parsed_output.json",
            "schema_validation.json",
            "context_manifest.json",
            "runtime_policy.json",
        }
        context_manifest_artifact = next(
            artifact for artifact in artifacts if Path(artifact.file_path).name == "context_manifest.json"
        )
        context_manifest = json.loads((tmp_path / context_manifest_artifact.file_path).read_text())
        assert context_manifest["context_manifest"][0]["title"] == "coupon-api-notes.md"
        runtime_policy_artifact = next(
            artifact for artifact in artifacts if Path(artifact.file_path).name == "runtime_policy.json"
        )
        runtime_policy = json.loads((tmp_path / runtime_policy_artifact.file_path).read_text())
        assert runtime_policy["agent_name"] == "RequirementReviewAgent"
        assert runtime_policy["prompt"]["name"] == "requirement_review"
        assert runtime_policy["skill"]["quality_gates"] == ["Return structured review output."]
        assert all((tmp_path / artifact.file_path).exists() for artifact in artifacts)
        raw_artifact = next(artifact for artifact in artifacts if artifact.artifact_type == "raw_llm_output")
        assert raw_artifact.metadata_json["safe_to_show"] is False
        assert raw_artifact.metadata_json["redaction_applied"] is False
        assert llm_log is not None
        assert llm_log.status == "succeeded"
        assert llm_log.request_artifact_id is not None
        assert llm_log.response_artifact_id is not None
        assert llm_log.parsed_artifact_id is not None
        assert llm_log.schema_validation_artifact_id is not None


def test_worker_marks_schema_invalid_task_failed_and_records_error_artifact(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory() as session:
        ai_task = create_ai_task(session, mode="schema_invalid")
        queue = FakeAIQueue()
        job = enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next())

        session.refresh(ai_task)
        artifacts = list(session.scalars(select(Artifact).where(Artifact.owner_entity_id == ai_task.id)))
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))

        assert job.ai_task_id == ai_task.id
        assert ai_task.status == "failed"
        assert ai_task.error_json is not None
        assert ai_task.error_json["error_code"] == "MOCK_SCHEMA_INVALID"
        assert any(artifact.artifact_type == "schema_validation" for artifact in artifacts)
        assert llm_log is not None
        assert llm_log.status == "schema_invalid"
        assert llm_log.error_json is not None


def test_worker_fails_closed_when_published_prompt_hash_does_not_match(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory() as session:
        ai_task = create_ai_task(session)
        prompt = session.get(PromptVersion, ai_task.prompt_version_id)
        assert prompt is not None
        prompt.content += "\nchanged after publish"
        session.commit()
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next())

        session.refresh(ai_task)
        assert ai_task.status == "failed"
        assert ai_task.error_json == {
            "error_code": "RUNTIME_POLICY_INVALID",
            "message": "Prompt content hash does not match its published version.",
            "recoverable": False,
        }


def test_worker_marks_provider_error_failed_and_records_error_artifact(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory() as session:
        ai_task = create_ai_task(session, mode="provider_error")
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next())

        session.refresh(ai_task)
        artifacts = list(session.scalars(select(Artifact).where(Artifact.owner_entity_id == ai_task.id)))
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))

        assert ai_task.status == "failed"
        assert ai_task.error_json is not None
        assert ai_task.error_json["error_code"] == "MOCK_PROVIDER_ERROR"
        assert any(artifact.artifact_type == "error_json" for artifact in artifacts)
        assert llm_log is not None
        assert llm_log.status == "failed"
        assert llm_log.request_artifact_id is not None
        assert {Path(artifact.file_path).name for artifact in artifacts} >= {
            "input.json",
            "context_manifest.json",
            "error.json",
        }


def test_worker_marks_timeout_failed_and_records_timeout_log(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory() as session:
        ai_task = create_ai_task(session, mode="timeout")
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next())

        session.refresh(ai_task)
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))

        assert ai_task.status == "failed"
        assert ai_task.error_json is not None
        assert ai_task.error_json["error_code"] == "MOCK_PROVIDER_TIMEOUT"
        assert llm_log is not None
        assert llm_log.status == "timeout"
        assert llm_log.request_artifact_id is not None


def test_worker_does_not_run_cancelled_task(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory() as session:
        ai_task = create_ai_task(session, status="created")
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)
        ai_task.status = "cancelled"
        session.commit()

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next())

        session.refresh(ai_task)
        assert ai_task.status == "cancelled"
        assert session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id)) is None


def test_worker_schema_invalid_records_error_artifact(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory() as session:
        ai_task = create_ai_task(session, mode="schema_invalid")
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next())

        artifacts = list(session.scalars(select(Artifact).where(Artifact.owner_entity_id == ai_task.id)))

        assert {Path(artifact.file_path).name for artifact in artifacts} >= {
            "raw_output.json",
            "schema_validation.json",
            "error.json",
        }


def test_worker_commits_running_state_before_provider_call(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    observed_statuses: list[str] = []

    class InspectingProvider:
        def __init__(self, SessionLocal: sessionmaker[Session], ai_task_id: uuid.UUID) -> None:
            self.SessionLocal = SessionLocal
            self.ai_task_id = ai_task_id

        def generate(self, request):
            with self.SessionLocal() as observer_session:
                observed_task = observer_session.get(AITask, self.ai_task_id)
                assert observed_task is not None
                observed_statuses.append(observed_task.status)
            from backend.app.modules.ai_runtime.providers.mock_provider import MockLLMProvider

            return MockLLMProvider().generate(request)

    with session_factory() as session:
        ai_task = create_ai_task(session)
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(
            session,
            LocalArtifactStore(tmp_path),
            queue.pop_next(),
            provider=InspectingProvider(session_factory, ai_task.id),
        )

        assert observed_statuses == ["running"]


def test_worker_selects_provider_from_ai_task_model_provider(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected_provider_names: list[str] = []

    class StubProvider:
        def generate(self, request):
            from backend.app.modules.ai_runtime.providers.base import LLMProviderResponse

            return LLMProviderResponse(
                provider="openai",
                model_name=request.model_name,
                status="succeeded",
                output_json={
                    "response_text": "connected",
                    "used_knowledge": False,
                    "used_context_artifact_ids": [],
                },
                artifacts=[],
                token_usage_json={"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            )

    def fake_create_llm_provider(provider_name: str):
        selected_provider_names.append(provider_name)
        return StubProvider()

    monkeypatch.setattr(
        "backend.app.workers.handlers.ai_task_handler.create_llm_provider",
        fake_create_llm_provider,
    )

    with session_factory() as session:
        ai_task = create_ai_task(session, model_provider="openai", model_name="gpt-5.5")
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next())

        session.refresh(ai_task)
        llm_log = session.scalar(select(LLMCallLog).where(LLMCallLog.ai_task_id == ai_task.id))
        assert selected_provider_names == ["openai"]
        assert ai_task.status == "succeeded"
        assert ai_task.output_json["response_text"] == "connected"
        assert ai_task.token_usage_json["total_tokens"] == 2
        assert llm_log is not None
        assert llm_log.provider == "openai"


def test_worker_normalizes_provider_name_in_error_code(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    from backend.app.modules.ai_runtime.providers.base import LLMProviderError

    class FailingProvider:
        def generate(self, request):
            raise LLMProviderError("provider unavailable")

    with session_factory() as session:
        ai_task = create_ai_task(session, model_provider="openai-compatible", model_name="gpt-5.5")
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, LocalArtifactStore(tmp_path), queue.pop_next(), provider=FailingProvider())

        session.refresh(ai_task)
        assert ai_task.status == "failed"
        assert ai_task.error_json is not None
        assert ai_task.error_json["error_code"] == "OPENAI_COMPATIBLE_PROVIDER_ERROR"


def test_worker_marks_task_failed_when_artifact_write_fails(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    class FailingArtifactStore(LocalArtifactStore):
        def write_bytes(self, file_path: str, content: bytes):
            raise OSError("artifact write failed")

    with session_factory() as session:
        ai_task = create_ai_task(session)
        queue = FakeAIQueue()
        enqueue_ai_task(session, queue, ai_task.id)

        run_ai_task(session, FailingArtifactStore(tmp_path), queue.pop_next())

        session.refresh(ai_task)
        assert ai_task.status == "failed"
        assert ai_task.error_json is not None
        assert ai_task.error_json["error_code"] == "ARTIFACT_WRITE_FAILED"
