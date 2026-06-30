# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 11: AutomationDraft Foundation.

## Current Task

Task 2: Add AutomationDraft model and schema alignment.

## Product Value Answer

After this task, Chtest has AutomationDraft backend model and schema contracts
ready for draft generation API implementation.

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
backend/app/modules/automation/schemas.py
backend/app/modules/automation/__init__.py
backend/app/tests/api/test_automation_draft.py
docs/implementation/slices/slice-11-automation-draft-foundation.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Read existing module/model patterns as needed, but do not add generation,
execution, or frontend behavior in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
```

Expected result: AutomationDraft model/schema alignment tests pass.

## Acceptance

- Add AutomationDraft model and schemas aligned with contracts.
- Add focused tests for model persistence and schema shape.
- Do not add draft generation endpoint, edit/approve endpoint, execution,
  frontend, reports, CI/CD quality, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions.
- Update handoff and set the next task to draft generation API.

## Commit Message

```text
feat(automation): add automation draft model schema
```

## Next Task

Slice 11 Task 3: Add AutomationDraft generation API.
