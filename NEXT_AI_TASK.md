# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 12: TestRunner Pytest Execution.

## Current Task

Task 5: Add TestRun API.

## Product Value Answer

After this task, Chtest can create and retrieve controlled pytest TestRun
records through the backend API.

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
backend/app/modules/execution/__init__.py
backend/app/modules/execution/router.py
backend/app/modules/execution/service.py
backend/app/modules/execution/schemas.py
backend/app/main.py
backend/app/tests/api/test_testrunner_pytest.py
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

Do not generate reports or quality gate decisions in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

Expected result: focused TestRun API tests pass.

## Acceptance

- Adds `POST /api/test-runs`.
- Adds `GET /api/test-runs/{id}`.
- Requires approved AutomationDraft or configured TestCommand input.
- Persists stdout/stderr/JUnit/runtime artifact metadata where available.
- Persists TestResult rows from parsed pytest output.
- Does not generate reports or quality gate decisions.
- Do not add Playwright execution, reports, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to pytest execution frontend shell.

## Commit Message

```text
feat(execution): add pytest test run api
```

## Next Task

Slice 12 Task 6: Add Pytest Execution Frontend Shell.
