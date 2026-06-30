# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

V2 Task 4: Draft Slice 19 Deterministic Knowledge Retrieval Stub plan.

## Product Value Answer

After this task, the next V2 slice has a scoped implementation plan for local,
deterministic ContextArtifact retrieval that improves AI context evidence
without becoming a full RAG platform.

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
12. `docs/implementation/slices/slice-18-newman-api-execution.md`
13. `docs/implementation/slices/slice-17-extension-surface.md`

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
```

Planning-only task. Do not add product code, vector database, embeddings,
reranking, background indexing, external RAG provider calls, MCP runtime, RBAC,
tenants, permissions, marketplace, cloud sync, release automation, or remote CI
provider integration.

## Verification Command

```bash
test -f docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
rg -n "Product Value Answer|Non-goals|Task Table|Deterministic|ContextArtifact|KnowledgeAdapter" docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
git diff --check
```

Expected result: Slice 19 plan is visible and diff check passes.

## Acceptance

- Creates `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`.
- Defines product value, task table, expected files, verification commands, and
  non-goals.
- Keeps the slice limited to deterministic local ContextArtifact retrieval and
  evidence recording.
- Does not add implementation code.
- Does not add vector database, embeddings, reranking, background indexing,
  external RAG provider calls, MCP runtime, RBAC, tenants, permissions, or
  marketplace work.

## Commit Message

```text
docs(v2): add deterministic knowledge retrieval slice plan
```

## Next Task

Start Slice 19 Task 1 only after reviewing the slice plan.
