# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 10: Test Case Library.

## Current Task

Slice 10 completion gate.

## Product Value Answer

After this task, Chtest can prove the Test Case Library slice is complete across
contract, backend API, frontend shell, and golden fixture coverage.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/implementation/slices/slice-10-test-case-library.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- AutomationDraft, execution, Playwright, CI/CD, report center, RAG runtime,
  MCP runtime, and migration reference docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-10-test-case-library.md
docs/implementation/slices/slice-10-test-case-library.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Do not modify product code unless the completion verification exposes a
concrete bug.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_requirement_to_case.py -q
npm --prefix frontend run test -- --run
```

Expected result: Test Case Library backend/golden tests and frontend suite pass.

## Acceptance

- Confirm the Slice 10 task table has commit IDs for every completed task.
- Confirm Test Case Library API contract exists.
- Confirm backend API returns reviewed TestCase records with filters.
- Confirm frontend shell can browse reviewed cases without automation/execution
  actions.
- Confirm golden fixture smoke proves reviewed cases enter the library.
- Do not add AutomationDraft, execution, reports, CI/CD quality, RAG runtime,
  MCP runtime, RBAC, tenants, or permissions.
- Update handoff with completion evidence and next recommended slice/task.

## Commit Message

```text
docs(cases): complete test case library slice
```

## Next Task

Slice 11 Task 1: Add AutomationDraft Foundation task plan.
