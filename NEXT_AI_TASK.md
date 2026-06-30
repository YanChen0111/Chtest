# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 13: Playwright Minimal Loop.

## Current Task

Task 5: Add Playwright execution frontend shell.

## Product Value Answer

After this task, users can start a controlled Playwright run and inspect
trace/screenshot evidence from the frontend workbench shell.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- CI/CD, report center, RAG runtime, MCP runtime, and migration reference docs
  unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-13-playwright-minimal-loop.md
frontend/src/api/execution.ts
frontend/src/stores/execution.ts
frontend/src/views/execution/PlaywrightExecutionView.vue
frontend/src/views/execution/PlaywrightExecutionView.spec.ts
frontend/src/router/index.ts
frontend/src/stores/index.ts
```

Do not add low-code automation editing, report generation, CI/CD quality, RAG
runtime, MCP runtime, RBAC, tenants, or permissions.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: frontend workbench shell tests pass.

## Acceptance

- Adds workbench navigation for Playwright minimal execution.
- Starts a run from approved Playwright AutomationDraft or configured
  Playwright TestCommand.
- Shows run status, command, exit code, duration, stdout/stderr artifact
  references, trace/screenshot references, parsed result summary, and
  TestResult rows.
- Does not add low-code automation editing, report generation, CI/CD quality,
  RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to Playwright golden smoke.

## Commit Message

```text
feat(frontend): add playwright execution shell
```

## Next Task

Slice 13 Task 6: Add Playwright golden smoke.
