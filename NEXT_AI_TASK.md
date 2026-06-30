# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 14: Report And Failure Analysis.

## Current Task

Task 7: Add automation execution report golden smoke.

## Product Value Answer

After this task, Chtest has a golden smoke proving TestRun can produce
FailureAnalysis when failed and automation_execution Report evidence.

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
backend/app/tests/golden/test_report_failure_analysis_golden.py
```

Do not create CI/CD QualityGateDecision records in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_report_failure_analysis_golden.py -q
```

Expected result: focused report/failure analysis golden smoke passes.

## Acceptance

- Reuses golden pytest or Playwright TestRun setup.
- Creates FailureAnalysis for a failed run or verifies skipped analysis for a
  passed run.
- Creates automation_execution Report for a TestRun.
- Persists `evidence_manifest.json` artifact metadata.
- Report conclusion references TestRun/TestResult/artifact evidence.
- Does not create CI/CD QualityGateDecision records.
- Update handoff and set the next task to Slice 14 completion gate.

## Commit Message

```text
test(golden): add report failure analysis smoke
```

## Next Task

Slice 14 completion gate.
