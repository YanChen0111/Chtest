# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 21: Local Review Attribution History.

## Current Task

Slice 21 Task 3: Add review history model and service.

## Product Value Answer

After this task, Chtest can persist and read local append-only ReviewHistory
records for existing review-gated workflows without introducing RBAC,
permissions, tenants, login, or team governance.

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
backend/app/main.py
backend/app/models/__init__.py
backend/app/tests/api/test_review_history.py
```

Backend model/service task. Do not attach history to existing review actions
yet, add frontend panels, add broad audit/search, or introduce users, roles,
permissions, tenants, login/session flows, assignment workflow, notifications,
remote CI provider governance, marketplace, RAG runtime, or MCP runtime.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py -q
git diff --check
```

Expected result: review history model/service API tests and diff check pass.

## Acceptance

- Adds ReviewHistory persistence with entity, related entity, action,
  from_status, to_status, reviewer, comment, evidence ids, metadata, and
  timestamp fields.
- Adds append-only service helpers to create and list focused local review
  history records.
- Adds `GET /api/review-history` read surface with project and entity filters.
- Uses deterministic `Default User` attribution unless a caller supplies a
  local reviewer label.
- Does not add generic public create/update/delete endpoints or attach existing
  review actions yet.
- Does not add users, roles, permissions, tenants, login/session, assignment,
  notifications, remote provider governance, RAG runtime, or MCP runtime.

## Commit Message

```text
feat(review): add local review history service
```

## Next Task

Slice 21 Task 4: Attach history to existing review actions.
