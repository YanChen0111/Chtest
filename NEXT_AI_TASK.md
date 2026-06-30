# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 10: Test Case Library.

## Current Task

Task 3: Add Test Case Library backend API.

## Product Value Answer

After this task, Chtest can list reviewed TestCase records through a scoped
backend API for the Test Case Library.

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
backend/app/modules/cases/router.py
backend/app/modules/cases/service.py
backend/app/modules/cases/schemas.py
backend/app/tests/api/test_test_case_library.py
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Read nearby cases tests and models as needed, but keep writes inside the files
above unless a concrete blocker requires an explained contract/doc update.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py -q
```

Expected result: Test Case Library backend API tests pass.

## Acceptance

- Add `GET /api/test-cases`.
- Return only persisted TestCase records, not generated candidates.
- Support project_id filtering and optional module_id, status, test_type,
  priority, and keyword filters.
- Return deterministic `items` and `total`.
- Do not add TestCase mutation, AutomationDraft, execution, reports, CI/CD
  quality, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to frontend shell.

## Commit Message

```text
feat(cases): add test case library api
```

## Next Task

Slice 10 Task 4: Add Test Case Library frontend shell.
