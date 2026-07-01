# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 21: Local Review Attribution History.

## Current Task

Slice 21 Task 5: Add frontend review history panels.

## Product Value Answer

After this task, existing review surfaces show compact local ReviewHistory
panels so a tester can see action, reviewer, status transition, comment,
timestamp, and evidence count without adding team governance.

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
frontend/src/api/client.ts
frontend/src/views/automation/AutomationDraftView.vue
frontend/src/views/cicd/CicdQualityCenterView.vue
frontend/src/views/cases/CaseReviewView.vue
frontend/src/**/*.spec.ts
```

Frontend panel task. Do not add user management, roles, permissions, tenants,
assignment workflow, notifications, team inbox, comment threads, generic
ReviewHistory write endpoints, remote provider governance, RAG runtime, or MCP
runtime.

## Verification Command

```bash
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: frontend tests and diff check pass.

## Acceptance

- Adds frontend API typing/helper for `GET /api/review-history`.
- Shows compact review history entries in existing review surfaces.
- Uses Chinese-facing labels while keeping product model terms such as
  TestCase, AutomationDraft, UnitTestPatch, and QualityGateDecision unchanged.
- Keeps history panels secondary to existing review action controls.
- Does not add user management, roles, permissions, assignment, notifications,
  team inbox, or collaboration controls.

## Commit Message

```text
feat(frontend): show local review history
```

## Next Task

Slice 21 Task 6: Add review history golden smoke.
