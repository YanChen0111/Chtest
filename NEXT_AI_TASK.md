# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 11: AutomationDraft Foundation.

## Current Task

Task 1: Add AutomationDraft Foundation task plan.

## Product Value Answer

After this task, Chtest has a scoped, reviewable implementation plan for the
AutomationDraft Foundation slice without adding execution behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/implementation/slices/slice-10-test-case-library.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Execution, Playwright, CI/CD, report center, RAG runtime, MCP runtime, and
  migration reference docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-11-automation-draft-foundation.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

This is a planning task only. Do not modify product code.

## Verification Command

```bash
test -f docs/implementation/slices/slice-11-automation-draft-foundation.md
rg -n "AutomationDraft Foundation|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-11-automation-draft-foundation.md
```

Expected result: Slice 11 task plan exists and names concrete tasks,
verification commands, and non-goals.

## Acceptance

- Create a scoped Slice 11 task plan.
- Define AutomationDraft data/API/frontend/golden tasks with one verification
  command per task.
- Keep Slice 11 limited to draft generation/review foundation and approval
  state; do not add execution behavior.
- Do not add TestRunner execution, Playwright execution, reports, CI/CD quality,
  RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to the first implementation task from
  the new Slice 11 plan.

## Commit Message

```text
docs(automation): add automation draft task plan
```

## Next Task

Slice 11 Task 2 from the new task plan.
