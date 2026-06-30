# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 10: Test Case Library.

## Current Task

Task 1: Add Test Case Library task plan.

## Product Value Answer

After this task, Chtest has a scoped, reviewable implementation plan for the
Test Case Library slice without expanding into automation or execution work.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `memory/08-session-handoff.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- AutomationDraft, execution, Playwright, CI/CD, report center, RAG runtime,
  MCP runtime, and migration reference docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-10-test-case-library.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

This is a planning task only. Do not modify product code.

## Verification Command

```bash
test -f docs/implementation/slices/slice-10-test-case-library.md
rg -n "Test Case Library|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-10-test-case-library.md
```

Expected result: Slice 10 task plan exists and names concrete tasks,
verification commands, and non-goals.

## Acceptance

- Create a scoped Slice 10 task plan.
- Define TestCase Library API/frontend/golden tasks with one verification
  command per task.
- Keep Slice 10 limited to browsing/searching existing reviewed TestCase records
  and basic suite capability if already supported by contracts.
- Do not add AutomationDraft, execution, reports, CI/CD quality, RAG runtime,
  MCP runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to the first implementation task from
  the new Slice 10 plan.

## Commit Message

```text
docs(cases): add test case library task plan
```

## Next Task

Slice 10 Task 2 from the new task plan.
