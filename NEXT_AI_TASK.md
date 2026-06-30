# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 14: Report And Failure Analysis.

## Current Task

Task 4: Add FailureAnalysis API.

## Product Value Answer

After this task, Chtest can create and retrieve deterministic evidence-backed
FailureAnalysis records for TestRun failures.

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
backend/app/modules/reporting/__init__.py
backend/app/modules/reporting/router.py
backend/app/modules/reporting/service.py
backend/app/modules/reporting/schemas.py
backend/app/main.py
backend/app/tests/api/test_report_failure_analysis.py
```

Do not create repair tasks or reports in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

Expected result: focused FailureAnalysis API tests pass.

## Acceptance

- Adds `POST /api/test-runs/{id}/failure-analysis`.
- Adds `GET /api/test-runs/{id}/failure-analysis`.
- Creates a succeeded AITask with mock FailureAnalysis output.
- Classifies from available stdout/stderr/TestResult/artifact evidence.
- Returns `insufficient_evidence` when evidence is missing.
- Does not create repair tasks or reports.
- Do not add CI/CD quality gates, merge/release decisions, RAG runtime, MCP
  runtime, RBAC, tenants, permissions, or broad report analytics.
- Update handoff and set the next task to automation execution Report API.

## Commit Message

```text
feat(reporting): add failure analysis api
```

## Next Task

Slice 14 Task 5: Add automation execution Report API.
