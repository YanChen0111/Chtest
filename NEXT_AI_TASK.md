# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 17: Extension Surface.

## Current Task

Task 1: Add Extension Surface task plan.

## Product Value Answer

After this task, Chtest has a scoped Slice 17 plan for the RAG 知识库 surface,
empty KnowledgeAdapter, and MCP-ready Tool schema without adding runtime-heavy
extension infrastructure.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-17-extension-surface.md
```

Planning-only task. Do not add RAG runtime, vector indexing, embeddings,
reranking, MCP runtime dependency, RBAC, tenants, or permissions.

## Verification Command

```bash
test -f docs/implementation/slices/slice-17-extension-surface.md && rg -n "KnowledgeAdapter|RAG 知识库|MCP-ready|Non-goals" docs/implementation/slices/slice-17-extension-surface.md
```

Expected result: Slice 17 planning document exists and names scope/non-goals.

## Acceptance

- Creates `docs/implementation/slices/slice-17-extension-surface.md`.
- Splits Slice 17 into small verifiable tasks.
- Names the RAG 知识库 page as a ContextArtifact and KnowledgeAdapter surface,
  not an internal RAG runtime.
- Names empty KnowledgeAdapter and MCP-ready ToolDefinition/schema boundaries.
- Keeps RAG runtime, MCP runtime dependency, RBAC, tenants, and permissions out
  of scope.
- Updates handoff and sets the next task to the first Slice 17 contract task.

## Commit Message

```text
docs(extension): add extension surface task plan
```

## Next Task

Slice 17 Task 2: Add Extension Surface contract boundary.
