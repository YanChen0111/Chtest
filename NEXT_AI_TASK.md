# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 12: TestRunner Pytest Execution.

## Current Task

Slice 12 completion gate.

## Product Value Answer

After this task, Slice 12 is verified end-to-end and ready to hand off to the
next V1 slice.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Playwright, CI/CD, report center, RAG runtime, MCP runtime, and migration
  reference docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

This is a verification and documentation task only. Do not modify product code
unless verification exposes a concrete blocker.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/golden/test_testrunner_pytest.py -q && npm --prefix frontend run test -- --run
```

Expected result: backend pytest execution API/golden tests and frontend shell
tests pass.

## Acceptance

- Confirm Slice 12 task table is fully done.
- Run backend API + golden pytest execution verification.
- Run frontend workbench verification.
- Record completion evidence in the Slice 12 task plan.
- Update handoff and set the next task to the next V1 slice.

## Commit Message

```text
docs(execution): complete pytest runner slice
```

## Next Task

Next V1 slice selection.
