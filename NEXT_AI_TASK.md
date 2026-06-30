# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 14: Report And Failure Analysis.

## Current Task

Task 6: Add Report and FailureAnalysis frontend shell.

## Product Value Answer

After this task, users can inspect FailureAnalysis and automation_execution
Report records from the workbench with evidence shown before AI explanation.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- CI/CD, report center, RAG runtime, MCP runtime, and migration reference docs
  unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-14-report-and-failure-analysis.md
frontend/src/api/reporting.ts
frontend/src/stores/reporting.ts
frontend/src/views/reporting/ReportFailureAnalysisView.vue
frontend/src/views/reporting/ReportFailureAnalysisView.spec.ts
frontend/src/router/index.ts
frontend/src/stores/index.ts
```

Do not add CI/CD quality gates, RAG runtime, MCP runtime, RBAC, tenants, or
permissions in this task.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: focused frontend workbench tests pass.

## Acceptance

- Adds workbench navigation for Report/FailureAnalysis.
- Starts FailureAnalysis for a TestRun and shows classification/confidence.
- Starts automation_execution Report generation and shows conclusion, summary,
  metrics, artifact references, and evidence manifest status.
- Shows evidence before AI explanation.
- Does not add CI/CD quality gates, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions.
- Update handoff and set the next task to automation execution report golden smoke.

## Commit Message

```text
feat(frontend): add report failure analysis shell
```

## Next Task

Slice 14 Task 7: Add automation execution report golden smoke.
