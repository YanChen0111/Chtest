# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Select next narrow V2 slice.

## Current Task

Select and plan the next narrow V2 task after Slice 28 completion.

## Product Value Answer

After this task, the next V2 slice is selected and planned with a small,
verifiable task boundary.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/10-v2-scope-options.md`
9. `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`
10. `memory/08-session-handoff.md`
11. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, and frontend redesign docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/<next-slice>.md
```

Planning task. Do not add frontend code, backend feature code, tests,
migrations, package upgrades, artifact upload/mutation/delete, cloud storage,
external provider integration, RBAC, tenants, permissions, broad redesign work,
report generation behavior, runner behavior changes, quality gate computation
changes, RAG runtime, or MCP runtime.

## Verification Command

```bash
test -f docs/implementation/slices/<next-slice>.md
rg -n "Product Value Answer|Non-goals|Task Table" docs/implementation/slices/<next-slice>.md NEXT_AI_TASK.md
git diff --check
```

Expected result: next slice plan exists, names product value/non-goals/task
table, `NEXT_AI_TASK.md` points to the first task, and diff check passes.

## Acceptance

- Select one narrow V2 slice from current product priorities and recent handoff.
- Create the slice plan with product value, preconditions, non-goals, task
  table, expected files, verification commands, and commit messages.
- Update `NEXT_AI_TASK.md` to the first task of that new slice.
- Do not implement product code during planning.

## Commit Message

```text
docs(v2): plan next narrow v2 slice
```

## Next Task

First task of the newly planned V2 slice.
