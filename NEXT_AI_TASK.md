# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

Slice 19 Completion Gate.

## Product Value Answer

After this gate, deterministic local ContextArtifact retrieval is fully verified
as an auditable V2 knowledge-quality improvement, with backend, frontend, golden
smoke, and documentation evidence complete.

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
14. `docs/fixtures/08-deterministic-knowledge-retrieval-golden.md`

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
```

Completion gate. Verify and document the completed deterministic retrieval
slice. Do not add frontend, vector database, embeddings, reranking, background
indexing, external RAG provider calls, MCP runtime, RBAC, tenants, permissions,
marketplace, cloud sync, release automation, or remote CI provider integration.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: backend API, golden smoke, frontend retrieval evidence display,
and diff check pass.

## Acceptance

- Slice 19 task table marks Task 1-6 done with commit ids.
- Completion evidence records backend API, requirement review, extension
  surface, golden smoke, frontend, and diff verification.
- Handoff names the next V2 slice or planning task.
- Non-goals remain excluded.

## Commit Message

```text
docs(v2): complete deterministic knowledge retrieval slice
```

## Next Task

Select the next V2 slice or planning task after Slice 19 completion is
committed.
