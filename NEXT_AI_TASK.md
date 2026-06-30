# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 17: Extension Surface.

## Current Task

Task 2: Add Extension Surface contract boundary.

## Product Value Answer

After this task, Chtest has a contract-first boundary for the RAG 知识库
surface, empty KnowledgeAdapter, and MCP-ready ToolDefinition schema without
adding runtime-heavy extension infrastructure.

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
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-17-extension-surface.md
```

Contract-only task. Do not add backend runtime code, frontend code, RAG runtime,
vector indexing, embeddings, reranking, MCP runtime dependency, RBAC, tenants,
or permissions.

## Verification Command

```bash
rg -n "KnowledgeAdapter|RAG 知识库|ToolDefinition|MCP-ready|Non-goals" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-17-extension-surface.md
```

Expected result: Slice 17 contracts name extension surface scope and non-goals.

## Acceptance

- Contract names the RAG 知识库 page as a ContextArtifact management and usage
  display surface.
- Contract defines KnowledgeAdapter as an empty interface/configuration state in
  V1, not a retrieval runtime.
- Contract defines MCP-ready ToolDefinition metadata while keeping ToolAdapter
  allowlist safety as the executable boundary.
- Contract keeps RAG runtime, MCP runtime dependency, RBAC, tenants, and
  permissions out of scope.
- Updates handoff and sets the next task to the first Slice 17 implementation
  task.

## Commit Message

```text
docs(extension): define extension surface boundary
```

## Next Task

Slice 17 Task 3: Add KnowledgeAdapter empty interface/schema.
