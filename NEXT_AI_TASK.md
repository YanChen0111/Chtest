# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

Slice 19 Task 4: Attach retrieval evidence to AI task flows.

## Product Value Answer

After this task, requirement review can request deterministic local knowledge
retrieval and persist auditable retrieval evidence on the AI task.

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
14. backend requirement review and AI runtime files needed for retrieval
    evidence only

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
backend/app/modules/requirements/service.py
backend/app/modules/requirements/schemas.py
backend/app/modules/requirements/router.py
backend/app/modules/ai_runtime/service.py
backend/app/modules/ai_runtime/providers/mock_provider.py
backend/app/tests/api/test_deterministic_knowledge_retrieval.py
backend/app/tests/api/test_requirement_review.py
```

Backend-only task. Attach deterministic retrieval evidence to the existing
requirement review AI flow. Do not add frontend, vector database, embeddings,
reranking, background indexing, external RAG provider calls, MCP runtime, RBAC,
tenants, permissions, marketplace, cloud sync, release automation, or remote CI
provider integration.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py -q
git diff --check
```

Expected result: deterministic retrieval service tests, requirement review flow
tests, and diff check pass.

## Acceptance

- Requirement review can request deterministic local knowledge retrieval.
- AITask records `used_knowledge=true` only when retrieved snippets are used.
- AITask records exact `used_context_artifact_ids`.
- Retrieval evidence artifact includes query terms, matched terms, snippets,
  scores, and ContextArtifact ids.
- Existing explicit `context_artifact_ids` behavior remains unchanged when
  `use_knowledge=false`.
- Does not create vector indexes, embeddings, reranking jobs, background
  workers, external provider calls, MCP calls, RBAC, tenants, or permissions.

## Commit Message

```text
feat(requirements): attach retrieval evidence to review tasks
```

## Next Task

Start Slice 19 Task 5 only after retrieval evidence is attached and committed.
