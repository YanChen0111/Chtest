# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 14: Report And Failure Analysis.

## Current Task

Slice 14 completion gate.

## Product Value Answer

After this task, Slice 14 has verified API, frontend, golden smoke, and
handoff evidence for FailureAnalysis and automation_execution Report.

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
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

Do not add product behavior in this task. This is verification and handoff only.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py backend/app/tests/golden/test_report_failure_analysis_golden.py -q && npm --prefix frontend run test -- --run
```

Expected result: Slice 14 backend API, golden smoke, and frontend tests pass.

## Acceptance

- Run the Slice 14 completion verification command.
- Mark Slice 14 completion gate done in the slice task plan if verification
  passes.
- Record verification evidence in handoff.
- Set the next task to the next V1 slice/task from `docs/implementation/02-v1-slice-plan.md`.
- Do not add product behavior, broad refactors, CI/CD gates, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.

## Commit Message

```text
docs(report): complete report failure analysis slice
```

## Next Task

Read `docs/implementation/02-v1-slice-plan.md` and select the next smallest V1 task.
