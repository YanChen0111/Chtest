# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 12: TestRunner Pytest Execution.

## Current Task

Task 4: Add Pytest Runner Adapter.

## Product Value Answer

After this task, Chtest can run an allowlisted local pytest command through a
small deterministic adapter and return parsed execution evidence.

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
backend/app/modules/execution/pytest_runner.py
backend/app/modules/execution/schemas.py
backend/app/tests/api/test_testrunner_pytest.py
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

Do not add router/API orchestration in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

Expected result: focused pytest runner adapter tests pass.

## Acceptance

- Runs only pytest-style commands assembled by backend code, not arbitrary shell
  strings.
- Captures stdout, stderr, exit_code, duration_ms, and parsed pass/fail counts.
- Supports local_subprocess runner mode first.
- Network is disabled by default in TestRun metadata.
- Does not add Docker runner or Playwright in this task.
- Do not add Playwright execution, reports, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to TestRun API.

## Commit Message

```text
feat(execution): add pytest runner adapter
```

## Next Task

Slice 12 Task 5: Add TestRun API.
