# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 18: Newman API Execution.

## Current Task

Slice 18 Task 4: Add Newman API execution frontend shell.

## Product Value Answer

After this task, users can inspect Newman API execution evidence in the
frontend using the existing light workbench UI.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`
9. `docs/implementation/00-v0.1-walking-skeleton.md`
10. `docs/fixtures/00-v1-demo-path.md`
11. `docs/implementation/10-v2-scope-options.md`
12. `docs/implementation/slices/slice-18-newman-api-execution.md`
13. frontend Newman execution view and tests needed for Slice 18 only

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-18-newman-api-execution.md
frontend/src/api/*
frontend/src/stores/*
frontend/src/views/*
frontend/src/router/*
frontend/src/layouts/*
```

Frontend-only task. Add only the Newman API execution shell and focused tests
needed for Slice 18. Do not add backend behavior, RAG runtime, MCP runtime,
RBAC, tenants, permissions, marketplace, cloud sync, release automation, remote
CI provider integration, Postman workspace parity, collection editor, or
arbitrary shell execution.

## Verification Command

```bash
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: frontend tests and diff check pass.

## Acceptance

- Adds a Chinese-facing API execution page aligned with the current light
  workbench UI.
- Keeps technical terms such as Newman, TestCommand, TestRun, Prompt, Skill,
  and Artifact unchanged when they are model/product terms.
- Shows command approval state, execution status, request/assertion summary,
  failure details, and artifact links.
- Does not add a collection editor, environment secret manager, remote CI/CD
  controls, RBAC, tenants, or marketplace controls.

## Commit Message

```text
feat(frontend): add newman execution shell
```

## Next Task

Start Slice 18 Task 5 only after the Newman frontend shell is committed.
