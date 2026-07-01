# Extension Surface Golden Fixture

## Purpose

This fixture proves the V1 extension surface without adding runtime-heavy
extension infrastructure.

The golden path is:

```text
Project
  -> ContextArtifact
  -> AITask with context_artifact_ids
  -> KnowledgeAdapter empty state
  -> RAG 知识库 surface
  -> MCP-ready ToolDefinition schema
```

## Golden ContextArtifact

Title: `coupon-api-notes.md`

Source ref: `manual:coupon-api-notes.md`

Artifact type: `context_markdown`

Content:

```markdown
# Coupon API Notes

POST /api/coupons/validate validates coupon availability.
Expired coupons cannot be applied during checkout.
Coupon amount cannot exceed the order payable amount.
```

Expected metadata:

```json
{
  "safe_to_show": true,
  "redaction_applied": false,
  "allowed_for_prompt": true
}
```

## Golden AI Task

- `agent_name`: `RequirementReviewAgent`
- `task_type`: `requirement_review`
- `status`: `succeeded`
- `context_artifact_ids`: includes the golden ContextArtifact id.
- `output_json.used_knowledge`: `false`

## Golden KnowledgeAdapter

KnowledgeAdapter remains empty in V1:

```json
{
  "adapter_name": "default",
  "status": "not_configured",
  "provider_type": "none",
  "used_knowledge": false
}
```

## Golden ToolDefinition

ToolDefinition may be MCP-ready as schema metadata only:

```json
{
  "name": "pytest_runner",
  "tool_type": "test_runner",
  "is_mcp_ready": true,
  "mcp_metadata": {
    "schema_version": "v1",
    "capability_name": "pytest_runner"
  }
}
```

`tool_type=mcp_proxy` is allowed only as schema intent. It must not execute MCP
runtime calls in V1.

## Non-goals

The golden path must not create or require:

- vector indexes
- embeddings
- reranking jobs
- external RAG provider calls
- MCP server/client runtime
- RBAC
- tenants
- permissions
- plugin marketplace
- cloud sync
