# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 21: Local Review Attribution History.

## Current Task

Slice 21 Task 2: Define review history contract boundary.

## Product Value Answer

After this task, Chtest contracts define local append-only review history as
evidence without introducing RBAC, permissions, tenants, login, or team
governance.

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
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-21-local-review-attribution-history.md
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
```

Contract-only task. Do not add implementation code, frontend code, migrations,
users, roles, permissions, tenants, login/session flows, assignment workflow,
notifications, remote CI provider governance, marketplace, RAG runtime, or MCP
runtime.

## Verification Command

```bash
rg -n "ReviewHistory|review history|review attribution|Default User|RBAC|permissions" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-21-local-review-attribution-history.md
git diff --check
```

Expected result: review history contract boundary docs and diff check pass.

## Acceptance

- Data contract defines append-only review history records.
- API contract defines a local read surface for review history.
- State-machine contract states review history records transitions but does not
  change approval rules.
- Artifact contract defines evidence references only when needed.
- Contracts explicitly reject RBAC, permissions, tenants, SSO, enterprise audit,
  assignment workflow, and remote provider governance.

## Commit Message

```text
docs(review): define local review history contract
```

## Next Task

Slice 21 Task 3: Add review history model and service.
