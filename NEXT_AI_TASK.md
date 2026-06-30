# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 17: Extension Surface.

## Current Task

Task 5: Add MCP-ready ToolDefinition schema metadata.

## Product Value Answer

After this task, Chtest exposes MCP-ready ToolDefinition schema metadata while
keeping ToolInvocation and internal allowlist rules as the only executable tool
boundary.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`
9. `docs/implementation/slices/slice-17-extension-surface.md`

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-17-extension-surface.md
backend/app/modules/extension/models.py
backend/app/modules/extension/schemas.py
backend/app/modules/extension/router.py
backend/app/modules/extension/service.py
backend/app/tests/api/test_extension_surface.py
```

Backend API shell task. Do not add frontend code, RAG runtime, vector indexing,
embeddings, reranking, MCP runtime dependency, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
```

Expected result: Extension surface API tests pass.

## Acceptance

- Exposes ToolDefinition input/output schema, risk level, approval requirement,
  artifact policy, and allowlist metadata.
- Allows `tool_type=mcp_proxy` as schema intent only.
- Requires ToolInvocation to keep using allowlisted internal execution rules.
- Does not add MCP server/client packages or runtime calls.
- Updates handoff and sets the next task to the RAG 知识库 frontend shell.

## Commit Message

```text
feat(extension): add mcp ready tool schema
```

## Next Task

Slice 17 Task 6: Add RAG 知识库 frontend shell.
