# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 17: Extension Surface.

## Current Task

Task 6: Add RAG 知识库 frontend shell.

## Product Value Answer

After this task, Chtest has a light workbench-style RAG 知识库 frontend shell
that displays ContextArtifacts, KnowledgeAdapter state, and MCP-ready
ToolDefinition readiness without runtime provider controls.

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
navigation files needed to expose the page
```

Frontend shell task. Do not add RAG runtime, vector indexing, embeddings,
reranking, MCP runtime dependency, RBAC, tenants, permissions, marketplace, or
cloud sync controls.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: frontend tests pass.

## Acceptance

- Uses a light workbench UI aligned with the final Chtest frontend direction.
- Shows ContextArtifact inventory, safety metadata, prompt eligibility, and AI
  usage references.
- Shows KnowledgeAdapter configuration as empty/not configured state.
- Shows MCP-ready ToolDefinition schema/readiness without executable MCP
  controls.
- Does not add RBAC, tenant, marketplace, cloud sync, vector search, or runtime
  provider controls.
- Updates handoff and sets the next task to Extension Surface golden smoke.

## Commit Message

```text
feat(frontend): add knowledge base shell
```

## Next Task

Slice 17 Task 7: Add Extension Surface golden smoke.
