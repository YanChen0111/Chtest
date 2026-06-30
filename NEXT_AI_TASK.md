# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

V2 Task 3: Select next small V2 slice.

## Product Value Answer

After this task, the next V2 slice is chosen from current product priorities
without accidentally expanding Chtest into out-of-scope platform work.

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

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-18-newman-api-execution.md
docs/implementation/10-v2-scope-options.md
```

Planning-only task. Do not add product behavior. Choose the next small V2 slice
or pause for product review.

## Verification Command

```bash
rg -n "Recommended First V2 Slice|Candidate Direction|Still Out Of Scope|Slice 18" docs/implementation/10-v2-scope-options.md docs/implementation/slices/slice-18-newman-api-execution.md
git diff --check
```

Expected result: next V2 planning context is visible and diff check passes.

## Acceptance

- Slice 18 completion evidence is considered before choosing the next slice.
- Next slice is small, testable, and aligned with V2 scope options.
- RAG runtime, MCP runtime, RBAC, tenants, permissions, remote CI/CD control,
  broad dashboards, and marketplace work remain out unless explicitly promoted.

## Commit Message

```text
docs(v2): select next v2 slice
```

## Next Task

Choose the next V2 slice or ask for product review if priorities are unclear.
