# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 6: Add Case Review API.

## Product Value Answer

After this task, Chtest can approve, approve after edit, reject, or request
optimization for generated case candidates, and approved candidates create
official TestCase records.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Case review, frontend, AutomationDraft, Playwright, CI/CD, report center, RAG
  runtime, MCP runtime, and migration reference docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/cases/router.py
backend/app/modules/cases/service.py
backend/app/modules/cases/schemas.py
backend/app/tests/api/test_case_review.py
```

Read existing Case Generation models/API patterns only as needed to implement
candidate review actions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_review.py -q
```

Expected result: Case Review API focused test passes.

## Acceptance

- Add candidate review actions for approve, approve_after_edit, reject, and
  needs_optimization.
- Approved and approved_after_edit candidates create TestCase records.
- Rejected candidates do not create TestCase records.
- needs_optimization marks the candidate for later CaseReviewAgent work but
  does not implement the optimization agent in this task.
- Do not execute cases, add AutomationDraft, frontend, real provider, RAG
  runtime, MCP runtime, RBAC, tenants, or permissions.
- `git status --short` shows only expected cases API/service/schema/test files
  and required task docs before commit.

## Commit Message

```text
feat(cases): add case review api
```

## Next Task

Slice 06 Task 7: Add Requirement To Case golden smoke.
