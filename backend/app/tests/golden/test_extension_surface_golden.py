from __future__ import annotations

import uuid

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.modules.ai_runtime.models import AITask, Artifact
from backend.app.modules.extension.models import KnowledgeAdapterConfig, ToolDefinition
from backend.app.modules.projects.models import Project, Workspace
from backend.app.tests.golden.test_test_case_library_golden import ASGIClient, api_client


GOLDEN_CONTEXT_CONTENT = """# Coupon API Notes

POST /api/coupons/validate validates coupon availability.
Expired coupons cannot be applied during checkout.
Coupon amount cannot exceed the order payable amount.
"""


def test_golden_extension_surface_exposes_context_and_schema_without_runtimes(
    api_client: tuple[ASGIClient, sessionmaker[Session]],
) -> None:
    client, SessionLocal = api_client
    with SessionLocal() as session:
        project = seed_project(session)
        session.commit()
        project_id = project.id

    context_response = client.post(
        "/api/context-artifacts",
        json_body={
            "project_id": str(project_id),
            "title": "coupon-api-notes.md",
            "artifact_type": "context_markdown",
            "mime_type": "text/markdown",
            "content": GOLDEN_CONTEXT_CONTENT,
            "source_ref": "manual:coupon-api-notes.md",
        },
    )
    assert context_response.status_code == 201
    context_artifact_id = uuid.UUID(context_response.json()["id"])

    with SessionLocal() as session:
        ai_task = AITask(
            project_id=project_id,
            agent_name="RequirementReviewAgent",
            task_type="requirement_review",
            prompt_version_id=project_id,
            skill_version_id=project_id,
            status="succeeded",
            context_artifact_ids=[context_artifact_id],
            output_json={
                "used_knowledge": False,
                "used_context_artifact_ids": [str(context_artifact_id)],
            },
        )
        adapter = KnowledgeAdapterConfig(
            project_id=project_id,
            adapter_name="default",
            status="not_configured",
            provider_type="none",
            config_json={},
            safety_policy_json={"allowed_for_prompt": False},
            notes="V1 empty adapter shell",
        )
        tool_definition = ToolDefinition(
            project_id=project_id,
            name="pytest_runner",
            description="Run allowlisted pytest commands",
            tool_type="test_runner",
            input_schema_json={"type": "object", "properties": {"path": {"type": "string"}}},
            output_schema_json={"type": "object", "properties": {"exit_code": {"type": "integer"}}},
            risk_level="medium",
            approval_required=False,
            command_allowlist_json=["pytest {path}"],
            allowed_working_directories_json=["/workspace"],
            artifact_policy_json={"stdout": True, "junit": True},
            is_mcp_ready=True,
            mcp_metadata_json={
                "schema_version": "v1",
                "capability_name": "pytest_runner",
                "exposure_notes": "schema only; no MCP runtime in V1",
            },
        )
        session.add_all([ai_task, adapter, tool_definition])
        session.commit()
        ai_task_id = ai_task.id
        tool_definition_id = tool_definition.id

    knowledge_response = client.get(f"/api/projects/{project_id}/knowledge-base")
    assert knowledge_response.status_code == 200
    knowledge = knowledge_response.json()
    assert knowledge["knowledge_adapter"]["status"] == "not_configured"
    assert knowledge["knowledge_adapter"]["provider_type"] == "none"
    assert knowledge["knowledge_adapter"]["used_knowledge"] is False
    assert knowledge["non_goals"] == [
        "no_vector_index",
        "no_embedding",
        "no_reranking",
        "no_external_rag_runtime",
    ]
    assert len(knowledge["context_artifacts"]) == 1
    context_item = knowledge["context_artifacts"][0]
    assert context_item["id"] == str(context_artifact_id)
    assert context_item["title"] == "coupon-api-notes.md"
    assert context_item["source_ref"] == "manual:coupon-api-notes.md"
    assert context_item["safe_to_show"] is True
    assert context_item["redaction_applied"] is False
    assert context_item["allowed_for_prompt"] is True
    assert context_item["usage_count"] == 1
    assert context_item["latest_used_at"] is not None

    tool_response = client.get(f"/api/projects/{project_id}/tool-definitions")
    assert tool_response.status_code == 200
    tools = tool_response.json()
    assert tools["total"] == 1
    tool = tools["items"][0]
    assert tool["id"] == str(tool_definition_id)
    assert tool["name"] == "pytest_runner"
    assert tool["tool_type"] == "test_runner"
    assert tool["command_allowlist"] == ["pytest {path}"]
    assert tool["is_mcp_ready"] is True
    assert tool["mcp_metadata"]["capability_name"] == "pytest_runner"
    assert "server_url" not in tool["mcp_metadata"]
    assert "transport" not in tool["mcp_metadata"]

    task_response = client.get(f"/api/ai-tasks/{ai_task_id}")
    assert task_response.status_code == 200
    task = task_response.json()
    assert task["used_knowledge"] is False
    assert task["context_artifact_ids"] == [str(context_artifact_id)]
    assert task["used_context_artifact_ids"] == [str(context_artifact_id)]

    with SessionLocal() as session:
        context_artifact = session.get(Artifact, context_artifact_id)
        persisted_task = session.get(AITask, ai_task_id)
        persisted_adapter = session.scalar(select(KnowledgeAdapterConfig).where(KnowledgeAdapterConfig.project_id == project_id))
        persisted_tool = session.get(ToolDefinition, tool_definition_id)
        tables = set(inspect(session.bind).get_table_names())

    assert context_artifact is not None
    assert context_artifact.owner_entity_type == "Project"
    assert context_artifact.metadata_json["allowed_for_prompt"] is True
    assert persisted_task is not None
    assert persisted_task.output_json["used_knowledge"] is False
    assert persisted_adapter is not None
    assert persisted_adapter.provider_type == "none"
    assert persisted_tool is not None
    assert persisted_tool.is_mcp_ready is True
    assert persisted_tool.mcp_metadata_json["schema_version"] == "v1"
    assert "rag_indexes" not in tables
    assert "embeddings" not in tables
    assert "mcp_servers" not in tables
    assert "mcp_clients" not in tables
    assert "tenants" not in tables
    assert "roles" not in tables
    assert "permissions" not in tables


def seed_project(session: Session) -> Project:
    workspace = Workspace(name="Personal Workspace")
    session.add(workspace)
    session.flush()
    project = Project(workspace_id=workspace.id, name="Extension Golden")
    session.add(project)
    session.flush()
    return project
