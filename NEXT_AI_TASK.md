# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 11: AutomationDraft Foundation.

## Current Task

Task 4: Add AutomationDraft edit and approve API.

## Product Value Answer

After this task, Chtest can let a human reviewer fetch, edit, and approve an
AutomationDraft without executing it.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/implementation/slices/slice-11-automation-draft-foundation.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Execution, Playwright, CI/CD, report center, RAG runtime, MCP runtime, and
  migration reference docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/automation/models.py
backend/app/modules/automation/router.py
backend/app/modules/automation/service.py
backend/app/modules/automation/schemas.py
backend/app/tests/api/test_automation_draft.py
docs/implementation/slices/slice-11-automation-draft-foundation.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Read existing API patterns as needed, but do not add execution or frontend
behavior in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
```

Expected result: AutomationDraft model/schema alignment tests pass.

## Acceptance

- Add `GET /api/automation/drafts/{id}`.
- Add `PATCH /api/automation/drafts/{id}` for reviewer edits.
- Add `POST /api/automation/drafts/{id}/approve`.
- Enforce `edit -> edited -> approve -> approved` and reject invalid payloads.
- Do not create TestRun, TestResult, runtime artifacts, reports, execution side
  effects, frontend, CI/CD quality, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions.
- Update handoff and set the next task to frontend review shell.

## Commit Message

```text
feat(automation): add automation draft review api
```

## Next Task

Slice 11 Task 5: Add AutomationDraft frontend review shell.
