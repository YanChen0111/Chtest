# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 12: TestRunner Pytest Execution.

## Current Task

Task 7: Add Pytest Execution Golden Smoke.

## Product Value Answer

After this task, the golden path proves an approved AutomationDraft can execute
through the controlled pytest runner and persist evidence records.

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
backend/app/tests/golden/test_testrunner_pytest.py
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

Do not create Report or QualityGateDecision records.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_testrunner_pytest.py -q
```

Expected result: golden pytest execution smoke passes.

## Acceptance

- Reuses golden reviewed case -> approved AutomationDraft setup.
- Executes a controlled pytest command against a small generated fixture test.
- Persists TestRun and TestResult records.
- Captures stdout/stderr artifact metadata.
- Does not create Report or QualityGateDecision records.
- Update handoff and set the next task to Slice 12 completion gate.

## Commit Message

```text
test(golden): add pytest execution smoke
```

## Next Task

Slice 12 completion gate.
