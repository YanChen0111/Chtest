# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 13: Playwright Minimal Loop.

## Current Task

Task 4: Add Playwright execution API.

## Product Value Answer

After this task, Chtest can create and retrieve controlled Playwright TestRun
records through the backend API.

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
backend/app/modules/execution/playwright_runner.py
backend/app/modules/execution/router.py
backend/app/modules/execution/service.py
backend/app/modules/execution/schemas.py
backend/app/tests/api/test_playwright_minimal_loop.py
```

Do not generate reports, FailureAnalysis, or QualityGateDecision records in
this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q
```

Expected result: focused Playwright execution API tests pass.

## Acceptance

- Adds the contract-selected Playwright execution path through
  `POST /api/test-runs` with `runner_mode=playwright_local`.
- Requires approved Playwright AutomationDraft or configured Playwright
  TestCommand.
- Persists stdout/stderr/trace/screenshot/runtime artifact metadata where
  available.
- Persists TestResult rows from parsed Playwright output.
- Does not generate reports, FailureAnalysis, or QualityGateDecision records.
- Update handoff and set the next task to Playwright execution frontend shell.

## Commit Message

```text
feat(execution): add playwright minimal api
```

## Next Task

Slice 13 Task 5: Add Playwright execution frontend shell.
