# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 14: Report And Failure Analysis.

## Current Task

Task 1: Add Report And Failure Analysis task plan.

## Product Value Answer

After this task, Chtest has a scoped Slice 14 task plan for evidence-backed
FailureAnalysis and Report work.

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
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

This is a planning/documentation task only. Do not modify product code.

## Verification Command

```bash
test -f docs/implementation/slices/slice-14-report-and-failure-analysis.md && rg -n "Report And Failure Analysis|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

Expected result: Slice 14 task plan exists and contains task table,
verification commands, and non-goals.

## Acceptance

- Create a scoped Slice 14 Report And Failure Analysis task plan.
- Keep Slice 14 limited to FailureAnalysis, evidence manifest, and
  automation_execution Report.
- Do not add CI/CD quality gates, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions.
- Update handoff and set the next task to Slice 14 API contract/task boundary.

## Commit Message

```text
docs(report): add failure analysis task plan
```

## Next Task

Slice 14 Task 2: Add Report and FailureAnalysis API contract boundary.
