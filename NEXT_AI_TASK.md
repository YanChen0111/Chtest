# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 12: TestRunner Pytest Execution.

## Current Task

Task 2: Add TestRun API contract and task boundary.

## Product Value Answer

After this task, Chtest has a contract-first API boundary for approval-gated
pytest execution before backend implementation starts.

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
docs/implementation/slices/slice-12-testrunner-pytest-execution.md
docs/contracts/02-api-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

This is a contract/documentation task only. Do not modify product code.

## Verification Command

```bash
rg -n "TestRun|POST /api/test-runs|TestResult" docs/contracts/02-api-contract.md docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

Expected result: API contract and Slice 12 plan both name the pytest TestRun
endpoint and response model.

## Acceptance

- Add `POST /api/test-runs` and `GET /api/test-runs/{id}` to the API contract.
- Define request fields for approved automation_draft_id or configured
  test_command_id.
- Define response fields for TestRun, artifacts, parsed_result, and TestResult
  items.
- Keep V1 pytest execution allowlisted and local-first.
- Do not add Playwright execution, reports, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to TestRun/TestResult model schema.

## Commit Message

```text
docs(execution): define pytest test run api
```

## Next Task

Slice 12 Task 3: Add TestRun and TestResult model schema.
