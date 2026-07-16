from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import AITask, Artifact, LLMCallLog
from backend.app.modules.cicd.models import QualityGateDecision
from backend.app.modules.execution.models import TestRun
from backend.app.modules.reporting.models import FailureAnalysis, Report
from backend.app.tests.api.test_artifact_access import ASGIClient, api_client


FIXTURE_PATH = Path("docs/fixtures/15-ai-task-evidence-artifact-links-golden.md")


def test_golden_ai_task_evidence_artifact_links_keep_safe_display_boundary(
    api_client: tuple[ASGIClient, sessionmaker[Session], Path],
) -> None:
    assert FIXTURE_PATH.exists()
    client, SessionLocal, artifact_root = api_client
    safe_content = b'{"overall_score": 88, "used_knowledge": false}\n'
    raw_content = b'{"raw_model_text": "not shown inline"}\n'

    ai_task_id, safe_artifact_id, raw_artifact_id = seed_ai_task_artifact_link_golden(
        SessionLocal,
        artifact_root,
        safe_content=safe_content,
        raw_content=raw_content,
    )

    detail_response = client.get(f"/api/ai-tasks/{ai_task_id}")

    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    artifacts_by_id = {artifact["id"]: artifact for artifact in detail_body["artifacts"]}
    safe_row = artifacts_by_id[str(safe_artifact_id)]
    raw_row = artifacts_by_id[str(raw_artifact_id)]

    assert safe_row["artifact_type"] == "parsed_output"
    assert safe_row["safe_to_show"] is True
    assert safe_row["redaction_applied"] is False
    assert "content" not in safe_row
    assert "download_url" not in safe_row

    assert raw_row["artifact_type"] == "raw_llm_output"
    assert raw_row["safe_to_show"] is False
    assert raw_row["redaction_applied"] is False
    assert "content" not in raw_row
    assert "download_url" not in raw_row

    safe_download = client.get(f"/api/artifacts/{safe_artifact_id}/download")

    assert safe_download.status_code == 200
    assert safe_download.body == safe_content
    assert safe_download.headers["content-type"].startswith("application/json")
    assert 'filename="parsed_output.json"' in safe_download.headers["content-disposition"]
    assert f"sha256:{hashlib.sha256(safe_download.body).hexdigest()}" == safe_row["sha256"]

    with SessionLocal() as session:
        assert session.scalar(select(func.count()).select_from(AITask)) == 1
        assert session.scalar(select(func.count()).select_from(LLMCallLog)) == 1
        assert session.scalar(select(TestRun)) is None
        assert session.scalar(select(Report)) is None
        assert session.scalar(select(FailureAnalysis)) is None
        assert session.scalar(select(QualityGateDecision)) is None
        raw_artifact = session.get(Artifact, raw_artifact_id)

    assert raw_artifact is not None
    assert raw_artifact.metadata_json["safe_to_show"] is False


def seed_ai_task_artifact_link_golden(
    SessionLocal: sessionmaker[Session],
    artifact_root: Path,
    *,
    safe_content: bytes,
    raw_content: bytes,
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID]:
    with SessionLocal() as session:
        from backend.app.modules.projects.models import Project, Workspace

        workspace = Workspace(name="Personal Workspace")
        session.add(workspace)
        session.flush()
        project = Project(workspace_id=workspace.id, name="AI Task Artifact Link Golden")
        session.add(project)
        session.flush()

        ai_task = AITask(
            project_id=project.id,
            agent_name="RequirementReviewAgent",
            task_type="requirement_review",
            prompt_version_id=uuid.uuid4(),
            skill_version_id=uuid.uuid4(),
            model_provider="mock",
            model_name="mock-requirement-review",
            status="succeeded",
            input_json={"requirement_id": str(uuid.uuid4())},
            output_json={"used_knowledge": False, "used_context_artifact_ids": []},
            token_usage_json={"prompt_tokens": 128, "completion_tokens": 256},
            context_artifact_ids=[],
        )
        session.add(ai_task)
        session.flush()

        safe_path = f"projects/{project.id}/ai-tasks/{ai_task.id}/parsed_output.json"
        raw_path = f"projects/{project.id}/ai-tasks/{ai_task.id}/raw_output.json"
        for relative_path, content in ((safe_path, safe_content), (raw_path, raw_content)):
            destination = artifact_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)

        safe_artifact = Artifact(
            project_id=project.id,
            owner_entity_type="AITask",
            owner_entity_id=ai_task.id,
            artifact_type="parsed_output",
            file_path=safe_path,
            mime_type="application/json",
            size_bytes=len(safe_content),
            sha256=hashlib.sha256(safe_content).hexdigest(),
            metadata_json={
                "created_by_component": "GoldenFixture",
                "safe_to_show": True,
                "redaction_applied": False,
            },
        )
        raw_artifact = Artifact(
            project_id=project.id,
            owner_entity_type="AITask",
            owner_entity_id=ai_task.id,
            artifact_type="raw_llm_output",
            file_path=raw_path,
            mime_type="application/json",
            size_bytes=len(raw_content),
            sha256=hashlib.sha256(raw_content).hexdigest(),
            metadata_json={
                "created_by_component": "GoldenFixture",
                "safe_to_show": False,
                "redaction_applied": False,
            },
        )
        session.add_all([safe_artifact, raw_artifact])
        session.flush()

        llm_call = LLMCallLog(
            project_id=project.id,
            ai_task_id=ai_task.id,
            prompt_version_id=ai_task.prompt_version_id,
            skill_version_id=ai_task.skill_version_id,
            provider="mock",
            model_name="mock-requirement-review",
            call_index=1,
            status="succeeded",
            response_artifact_id=raw_artifact.id,
            parsed_artifact_id=safe_artifact.id,
            input_summary_json={"task_type": "requirement_review"},
            output_summary_json={"overall_score": 88},
            token_usage_json={"prompt_tokens": 128, "completion_tokens": 256},
            latency_ms=42,
        )
        session.add(llm_call)
        session.commit()

        return ai_task.id, safe_artifact.id, raw_artifact.id
