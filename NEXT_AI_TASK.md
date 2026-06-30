# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 13: Playwright Minimal Loop.

## Current Task

Task 6: Add Playwright golden smoke.

## Product Value Answer

After this task, the golden path proves an approved Playwright AutomationDraft
can execute through the controlled runner and persist browser evidence metadata.

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
backend/app/tests/golden/test_playwright_minimal_loop_golden.py
```

Do not create Report, FailureAnalysis, or QualityGateDecision records.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q
```

Expected result: golden Playwright minimal smoke passes.

## Acceptance

- Reuses golden reviewed UI case -> approved Playwright AutomationDraft setup.
- Executes a controlled Playwright smoke command against deterministic fake
  runner output.
- Persists TestRun and TestResult records.
- Captures stdout/stderr plus trace/screenshot artifact metadata.
- Does not create Report, FailureAnalysis, or QualityGateDecision records.
- Update handoff and set the next task to Slice 13 completion gate.

## Commit Message

```text
test(golden): add playwright minimal smoke
```

## Next Task

Slice 13 completion gate.
