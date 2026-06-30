# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

Slice 19 Task 5: Add retrieval evidence frontend display.

## Product Value Answer

After this task, the RAG 知识库 page can show deterministic local retrieval
status and latest matched evidence without becoming a vector-search product.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`
9. `docs/implementation/00-v0.1-walking-skeleton.md`
10. `docs/fixtures/00-v1-demo-path.md`
11. `docs/implementation/10-v2-scope-options.md`
12. `docs/implementation/slices/slice-17-extension-surface.md`
13. `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
14. frontend extension API/store/view files needed for retrieval evidence display

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
frontend/src/api/extension.ts
frontend/src/stores/extension.ts
frontend/src/views/extension/KnowledgeBaseView.vue
focused frontend tests for retrieval evidence display
```

Frontend-only task. Display existing deterministic retrieval evidence from the
RAG 知识库 surface. Do not add vector search controls, provider runtime config,
marketplace controls, RBAC, tenants, permissions, cloud sync, release
automation, or remote CI provider integration.

## Verification Command

```bash
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: focused frontend suite and diff check pass.

## Acceptance

- RAG 知识库 shows deterministic retrieval status.
- ContextArtifact rows can show whether they were retrieved recently.
- The page shows latest matched terms, snippets, and scores when available.
- UI remains Chinese-facing while preserving product terms such as
  ContextArtifact, KnowledgeAdapter, Prompt, Skill, and MCP-ready.
- Does not add vector search controls, provider configuration, marketplace
  controls, RBAC, tenants, permissions, or remote sync controls.

## Commit Message

```text
feat(frontend): show deterministic knowledge evidence
```

## Next Task

Start Slice 19 Task 6 only after retrieval evidence frontend display is
committed.
