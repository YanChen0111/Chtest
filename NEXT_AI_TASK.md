# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 13: Playwright Minimal Loop.

## Current Task

Task 3: Add Playwright runner adapter.

## Product Value Answer

After this task, Chtest has a minimal Playwright runner adapter that can wrap an
allowlisted local command and return parsed execution evidence.

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
backend/app/modules/execution/schemas.py
backend/app/tests/api/test_playwright_minimal_loop.py
```

Do not add API/router orchestration in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q
```

Expected result: focused Playwright runner adapter tests pass.

## Acceptance

- Runs only Playwright-style commands assembled by backend code or configured
  TestCommand allowlists.
- Captures stdout, stderr, exit_code, duration_ms, and parsed pass/fail counts.
- Produces metadata entries for Playwright trace and screenshot files when
  available.
- Supports local Playwright execution first.
- Does not add browser grid, Docker runner, pytest changes, reports, or CI/CD
  quality gates.
- Update handoff and set the next task to Playwright execution API.

## Commit Message

```text
feat(execution): add playwright runner adapter
```

## Next Task

Slice 13 Task 4: Add Playwright execution API.
