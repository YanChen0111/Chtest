# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 17: Extension Surface.

## Current Task

Task 3: Add KnowledgeAdapter empty interface/schema.

## Product Value Answer

After this task, Chtest has a backend KnowledgeAdapter empty interface/schema
that records V1 configuration state without adding retrieval, vector, embedding,
reranking, or external RAG behavior.

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

Backend shell task. Do not add frontend code, RAG runtime, vector indexing,
embeddings, reranking, MCP runtime dependency, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
```

Expected result: KnowledgeAdapter shell API tests pass.

## Acceptance

- Provides an empty KnowledgeAdapter read model or configuration state for a
  project.
- Records status such as `not_configured`, `disabled`, or `configured_stub`.
- Returns `used_knowledge=false` unless a future runtime explicitly implements
  retrieval.
- Does not call external RAG providers, create vector indexes, embed content, or
  rank search results.
- Updates handoff and sets the next task to the RAG 知识库 ContextArtifact API
  shell task.

## Commit Message

```text
feat(extension): add knowledge adapter shell
```

## Next Task

Slice 17 Task 4: Add RAG 知识库 ContextArtifact API shell.
