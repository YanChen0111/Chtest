# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 17: Extension Surface.

## Current Task

Slice 17 completion gate.

## Product Value Answer

After this task, Slice 17 is fully verified and documented: backend API tests,
Extension Surface golden smoke, frontend tests, slice evidence, and handoff are
all complete.

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
memory/07-dev-log.md
```

Completion-only task. Do not add RAG runtime, vector indexing, embeddings,
reranking, MCP runtime dependency, RBAC, tenants, permissions, marketplace, or
cloud sync controls.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_extension_surface_golden.py -q && npm --prefix frontend run test -- --run
```

Expected result: backend extension tests, golden smoke, and frontend tests pass.

## Acceptance

- All Slice 17 task rows are marked done with commit ids.
- Completion evidence records backend API, golden smoke, and frontend
  verification.
- Handoff names the next V1 slice or completion task.
- Non-goals remain excluded.

## Commit Message

```text
docs(extension): complete extension surface slice
```

## Next Task

Pick next V1 slice or V1 completion task.
