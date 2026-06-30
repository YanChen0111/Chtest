# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

Slice 19 Task 3: Add local KnowledgeAdapter retrieval service.

## Product Value Answer

After this task, the backend can deterministically match eligible local
ContextArtifacts and return bounded retrieval evidence without external RAG
infrastructure.

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
14. backend extension module files needed for deterministic retrieval only

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
backend/app/modules/extension/service.py
backend/app/modules/extension/schemas.py
backend/app/modules/extension/*
backend/app/tests/api/test_deterministic_knowledge_retrieval.py
```

Backend-only task. Add only deterministic local retrieval service behavior and
focused API/service tests. Do not add frontend, vector database, embeddings,
reranking, background indexing, external RAG provider calls, MCP runtime, RBAC,
tenants, permissions, marketplace, cloud sync, release automation, or remote CI
provider integration.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q
git diff --check
```

Expected result: deterministic retrieval backend tests and diff check pass.

## Acceptance

- Matches only ContextArtifacts for the same project.
- Requires `safe_to_show=true` and `allowed_for_prompt=true`.
- Uses deterministic local term matching with bounded result count.
- Returns snippet text, score, matched terms, and source ContextArtifact id.
- Does not create vector indexes, embeddings, reranking jobs, background
  workers, external provider calls, MCP calls, RBAC, tenants, or permissions.

## Commit Message

```text
feat(extension): add deterministic knowledge retrieval
```

## Next Task

Start Slice 19 Task 4 only after the local retrieval service is committed.
