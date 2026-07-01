# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 21: Local Review Attribution History.

## Current Task

Slice 21 Task 6: Add review history golden smoke.

## Product Value Answer

After this task, one golden smoke proves local ReviewHistory spans existing
review-gated evidence actions and remains append-only, local, and free of team
governance features.

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
docs/fixtures/10-local-review-history-golden.md
docs/implementation/slices/slice-21-local-review-attribution-history.md
backend/app/tests/golden/test_review_history_golden.py
```

Golden smoke task. Do not add user management, roles, permissions, tenants,
assignment workflow, notifications, team inbox, comment threads, generic
ReviewHistory write endpoints, remote provider governance, RAG runtime, or MCP
runtime.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_review_history_golden.py -q
git diff --check
```

Expected result: golden smoke and diff check pass.

## Acceptance

- Golden creates at least two existing review actions, such as UnitTestPatch
  approval and QualityGateDecision compute.
- Golden confirms append-only ReviewHistory records exact entity/action/status
  transitions and evidence references.
- Golden confirms no RBAC, tenants, permissions, login/session, assignment,
  notification, or remote provider dependency is introduced.

## Commit Message

```text
test(golden): add local review history smoke
```

## Next Task

Slice 21 Completion Gate.
