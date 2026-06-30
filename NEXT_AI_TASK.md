# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 10: Test Case Library.

## Current Task

Task 5: Add Test Case Library golden smoke.

## Product Value Answer

After this task, Chtest can prove golden reviewed cases are visible through the
Test Case Library API after the requirement-to-case review plan.

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
backend/app/tests/golden/test_test_case_library.py
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Read existing golden requirement-to-case tests as needed, but keep writes inside
the files above unless a concrete blocker requires an explained contract/doc
update.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_case_library.py -q
```

Expected result: Test Case Library golden smoke passes.

## Acceptance

- Reuse the golden requirement-to-case fixture setup and review plan.
- Assert the library returns 4 reviewed TestCase records after review.
- Assert the edited expired-coupon case keeps the edited step and input data.
- Assert keyword filtering can find a golden case by title or requirement text.
- Do not add browser automation, AutomationDraft, execution, reports, CI/CD
  quality, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to Slice 10 completion gate.

## Commit Message

```text
test(golden): add test case library smoke
```

## Next Task

Slice 10 completion gate.
