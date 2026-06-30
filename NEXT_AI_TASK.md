# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 17: Extension Surface.

## Current Task

Task 7: Add Extension Surface golden smoke.

## Product Value Answer

After this task, Chtest has a golden smoke proving ContextArtifact project
knowledge, empty KnowledgeAdapter state, and MCP-ready ToolDefinition schema
work together without hidden RAG/MCP runtime infrastructure.

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
frontend/src/api/extension.ts
frontend/src/stores/extension.ts
frontend/src/views/extension/KnowledgeBaseView.vue
frontend/src/views/extension/KnowledgeBaseView.spec.ts
backend/app/tests/golden/test_extension_surface_golden.py
docs/fixtures/06-extension-surface-golden.md
```

Golden smoke task. Do not add RAG runtime, vector indexing, embeddings,
reranking, MCP runtime dependency, RBAC, tenants, permissions, marketplace, or
cloud sync controls.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_extension_surface_golden.py -q
```

Expected result: Extension Surface golden smoke passes.

## Acceptance

- Creates or references ContextArtifacts as project knowledge.
- Runs an AI task that records `used_context_artifact_ids`.
- Confirms `used_knowledge=false` while KnowledgeAdapter remains empty.
- Confirms ToolDefinition schema metadata is visible but no MCP runtime executes.
- Confirms no vector/RAG/MCP/RBAC/tenant/permission tables or dependencies are
  introduced.
- Updates handoff and sets the next task to Slice 17 completion gate.

## Commit Message

```text
test(extension): add extension surface golden smoke
```

## Next Task

Slice 17 completion gate.
