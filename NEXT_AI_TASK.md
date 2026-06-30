# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 10: Test Case Library.

## Current Task

Task 2: Add Test Case Library API contract and task boundary.

## Product Value Answer

After this task, Chtest has a contract-first Test Case Library API boundary for
browsing reviewed cases before backend implementation starts.

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
docs/contracts/02-api-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

This is a contract/documentation task only. Do not modify product code.

## Verification Command

```bash
rg -n "Test Case Library|GET /api/test-cases|TestCaseList" docs/contracts/02-api-contract.md docs/implementation/slices/slice-10-test-case-library.md
```

Expected result: API contract and Slice 10 plan both name the Test Case Library
endpoint and response model.

## Acceptance

- Add `GET /api/test-cases` to the API contract.
- Define response fields for reviewed TestCase library items.
- Define query filters for project_id, module_id, status, test_type, priority,
  and keyword.
- Keep Slice 10 limited to browsing/searching existing reviewed TestCase records.
- Do not add AutomationDraft, execution, reports, CI/CD quality, RAG runtime,
  MCP runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to backend API implementation.

## Commit Message

```text
docs(cases): define test case library api
```

## Next Task

Slice 10 Task 3: Add Test Case Library backend API.
