# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 22: JMeter Local Execution Evidence.

## Current Task

Slice 22 Task 5: Add JMeter execution frontend shell.

## Product Value Answer

After this task, the frontend execution surface can display local JMeter
execution evidence: TestRun status, sampler/assertion totals, durations,
failure/error counts, and artifact links.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-22-jmeter-local-execution.md`
9. existing frontend execution views and stores

## Do Not Read Unless Needed

- JMeter distributed execution, cloud load testing, remote CI provider
  integration, webhooks, PR bots, release management, RAG runtime, MCP runtime,
  RBAC, tenants, permissions, and marketplace docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-22-jmeter-local-execution.md
frontend/src/api/execution.ts
frontend/src/stores/execution.ts
frontend/src/views/execution/*JMeter*.vue
frontend/src/views/execution/*JMeter*.spec.ts
frontend/src/router/index.ts
frontend/src/layouts/WorkbenchLayout.vue
```

Frontend shell task. Do not add backend code, golden tests, JMX editing,
performance dashboards, distributed runners, arbitrary shell execution, secrets
management, CI provider controls, RAG runtime, MCP runtime, RBAC, tenants, or
permissions.

## Verification Command

```bash
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: frontend tests and diff check pass.

## Acceptance

- UI exposes JMeter as an execution mode only when using approved local
  commands.
- UI shows TestRun status, total/passed/failed/error sampler counts, duration,
  and artifact links.
- UI uses Chinese-facing labels while keeping product terms such as TestRun,
  TestResult, JMeter, and JTL unchanged.
- Does not add a JMX editor, performance dashboard, distributed runner controls,
  secrets UI, CI provider controls, RBAC, tenants, or permissions.

## Commit Message

```text
feat(frontend): show jmeter execution evidence
```

## Next Task

Slice 22 Task 6: Add JMeter local execution golden smoke.
