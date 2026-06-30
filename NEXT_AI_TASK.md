# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

Slice 19 Task 6: Add deterministic retrieval golden smoke.

## Product Value Answer

After this task, a golden smoke proves ContextArtifact retrieval can improve
requirement review context while preserving auditable evidence.

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
14. golden deterministic retrieval fixture and tests only

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
docs/fixtures/08-deterministic-knowledge-retrieval-golden.md
backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py
```

Golden-smoke task. Prove the existing deterministic retrieval evidence loop with
fixtures only. Do not add frontend, vector database, embeddings, reranking,
background indexing, external RAG provider calls, MCP runtime, RBAC, tenants,
permissions, marketplace, cloud sync, release automation, or remote CI provider
integration.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
git diff --check
```

Expected result: deterministic retrieval golden smoke and diff check pass.

## Acceptance

- Creates safe ContextArtifacts with coupon/API knowledge.
- Runs requirement review with deterministic retrieval enabled.
- Confirms retrieved ContextArtifact ids, snippets, scores, and matched terms
  are persisted as evidence.
- Confirms `used_knowledge=true` and exact `used_context_artifact_ids`.
- Confirms RAG 知识库 surface can read the resulting latest retrieval evidence.
- Does not add vector database, embeddings, reranking, background workers,
  external providers, MCP runtime, RBAC, tenants, or permissions.

## Commit Message

```text
test(golden): add deterministic knowledge retrieval smoke
```

## Next Task

Start Slice 19 completion gate only after the deterministic retrieval golden
smoke is committed.
