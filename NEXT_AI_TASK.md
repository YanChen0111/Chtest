# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 21: Local Review Attribution History.

## Current Task

Slice 21 Task 4: Attach history to existing review actions.

## Product Value Answer

After this task, existing review-gated workflows append local ReviewHistory
records after successful actions without changing approval rules or introducing
RBAC, permissions, tenants, login, or team governance.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-21-local-review-attribution-history.md`

## Do Not Read Unless Needed

- Remote CI provider integration docs, webhooks, PR bots, release management,
  RAG runtime, MCP runtime, RBAC, tenants, permissions, and marketplace docs
  unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-21-local-review-attribution-history.md
backend/app/modules/review_history/models.py
backend/app/modules/review_history/schemas.py
backend/app/modules/review_history/service.py
backend/app/modules/review_history/router.py
backend/app/modules/review_history/__init__.py
backend/app/tests/api/test_review_history.py
backend/app/modules/cases/service.py
backend/app/modules/automation/service.py
backend/app/modules/cicd/service.py
backend/app/tests/api/test_case_review.py
backend/app/tests/api/test_automation_draft.py
backend/app/tests/api/test_unit_test_patch_regression.py
```

Backend action-hook task. Do not add frontend panels, broad audit/search,
generic public ReviewHistory write endpoints, users, roles, permissions,
tenants, login/session flows, assignment workflow, notifications, remote CI
provider governance, marketplace, RAG runtime, or MCP runtime.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_unit_test_patch_regression.py -q
git diff --check
```

Expected result: review history action-hook tests and diff check pass.

## Acceptance

- Records history for generated case review where current APIs support it.
- Records history for AutomationDraft edit/approve actions where current APIs
  support them.
- Records history for UnitTestPatch approve/reject.
- Records history for QualityGateDecision compute.
- Does not change whether an action is allowed or how status transitions are
  validated.
- Does not add frontend panels, user management, roles, permissions, tenants,
  assignment, notifications, remote provider governance, RAG runtime, or MCP
  runtime.

## Commit Message

```text
feat(review): record review history events
```

## Next Task

Slice 21 Task 5: Add frontend review history panels.
