# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

Select the next V2 small slice after Slice 19 completion.

## Product Value Answer

After this task, the next V2 implementation direction is chosen as a small,
evidence-backed slice without expanding into excluded platform scope.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/02-v1-slice-plan.md`
4. `docs/implementation/04-ai-vibecoding-governance.md`
5. `docs/implementation/10-v2-scope-options.md`
6. `docs/implementation/slices/slice-18-newman-api-execution.md`
7. `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
8. `memory/08-session-handoff.md`

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
new slice plan under docs/implementation/slices/ only if a slice is selected
```

Planning task. Compare completed V2 slices and select the next smallest product
slice. Do not add product code, frontend code, vector database, embeddings,
reranking, background indexing, external RAG provider calls, MCP runtime, RBAC,
tenants, permissions, marketplace, cloud sync, release automation, or remote CI
provider integration.

## Verification Command

```bash
rg -n "Slice 18|Slice 19|Candidate Direction|Recommended|Next" docs/implementation/10-v2-scope-options.md docs/implementation/slices
git diff --check
```

Expected result: next V2 slice recommendation is documented and diff check
passes.

## Acceptance

- Records Slice 19 as completed in V2 planning context.
- Selects one next small V2 slice with product value, non-goals, and task table.
- Keeps excluded platform scope out unless explicitly authorized.
- Updates handoff and `NEXT_AI_TASK.md` to the first task of the selected slice.

## Commit Message

```text
docs(v2): select next small slice
```

## Next Task

Start the selected V2 slice Task 1 only after the planning commit is complete.
