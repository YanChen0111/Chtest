# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 11: AutomationDraft Foundation.

## Current Task

Slice 11 completion gate.

## Product Value Answer

After this task, Chtest can prove the AutomationDraft Foundation slice is
complete across model/schema, APIs, frontend shell, and golden fixture coverage.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/implementation/slices/slice-11-automation-draft-foundation.md`
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

Do not modify product code unless the completion verification exposes a
concrete bug.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_test_case_library_golden.py -q
npm --prefix frontend run test -- --run
```

Expected result: AutomationDraft API/golden tests and frontend suite pass.

## Acceptance

- Confirm the Slice 11 task table has commit IDs for every completed task.
- Confirm AutomationDraft model/schema aligns with contracts.
- Confirm generation, edit, approve APIs work without execution side effects.
- Confirm frontend shell can review, edit, and approve drafts without run
  buttons.
- Confirm golden fixture smoke proves reviewed case -> approved draft.
- Do not add TestRun/TestResult execution, reports, CI/CD quality, RAG runtime,
  MCP runtime, RBAC, tenants, or permissions.
- Update handoff with completion evidence and next recommended slice/task.

## Commit Message

```text
docs(automation): complete automation draft slice
```

## Next Task

Slice 12 Task 1: Add TestRunner Pytest Execution task plan.
