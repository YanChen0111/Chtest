# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 13: Playwright Minimal Loop.

## Current Task

Slice 13 completion gate.

## Product Value Answer

After this task, Slice 13 is verified end-to-end and ready to hand off to the
next V1 slice.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- CI/CD, report center, RAG runtime, MCP runtime, and migration reference docs
  unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-13-playwright-minimal-loop.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-13-playwright-minimal-loop.md
```

This is a verification and documentation task only. Do not modify product code
unless verification exposes a concrete blocker.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q && npm --prefix frontend run test -- --run
```

Expected result: backend Playwright API/golden tests and frontend shell tests
pass.

## Acceptance

- Confirm Slice 13 task table is fully done.
- Run backend Playwright API + golden smoke verification.
- Run frontend workbench verification.
- Record completion evidence in the Slice 13 task plan.
- Update handoff and set the next task to Slice 14 planning.

## Commit Message

```text
docs(playwright): complete minimal loop slice
```

## Next Task

Slice 14 Task 1: Add Report And Failure Analysis task plan.
