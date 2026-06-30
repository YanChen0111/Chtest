# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 11: AutomationDraft Foundation.

## Current Task

Task 6: Add AutomationDraft golden smoke.

## Product Value Answer

After this task, Chtest can prove a reviewed golden TestCase can produce, edit,
and approve an AutomationDraft without execution.

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
backend/app/tests/golden/test_automation_draft.py
docs/implementation/slices/slice-11-automation-draft-foundation.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Read existing golden requirement-to-case and Test Case Library tests as needed,
but do not add execution behavior in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_automation_draft.py -q
```

Expected result: AutomationDraft golden smoke passes.

## Acceptance

- Reuse golden requirement-to-case and Test Case Library setup.
- Create an AutomationDraft for a reviewed golden TestCase.
- Verify draft_code, suggested_file_path, execution_notes, risk_notes, and
  status.
- Edit then approve the draft.
- Assert no TestRun/TestResult/report is created by this slice.
- Do not run pytest or Playwright, copy draft files to runtime workspace, add
  reports, CI/CD quality, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions.
- Update handoff and set the next task to Slice 11 completion gate.

## Commit Message

```text
test(golden): add automation draft smoke
```

## Next Task

Slice 11 completion gate.
