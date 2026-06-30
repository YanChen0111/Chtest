# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 14: Report And Failure Analysis.

## Current Task

Task 2: Add Report and FailureAnalysis API contract boundary.

## Product Value Answer

After this task, Chtest has contract-first API boundaries for evidence-backed
FailureAnalysis and automation_execution Reports.

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
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
```

This is a contract/documentation task only. Do not modify product code.

## Verification Command

```bash
rg -n "FailureAnalysis|POST /api/test-runs/.*/failure-analysis|POST /api/reports|evidence_manifest" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

Expected result: API/artifact contracts and Slice 14 plan name FailureAnalysis,
Report, and evidence manifest requirements.

## Acceptance

- Tighten create/get FailureAnalysis endpoint contract.
- Tighten create/get automation_execution Report endpoint contract.
- Require evidence_manifest artifact metadata.
- Keep report conclusions evidence-backed.
- Do not add CI/CD quality gates, merge/release decisions, RAG runtime, MCP
  runtime, RBAC, tenants, permissions, or broad report analytics.
- Update handoff and set the next task to model/schema.

## Commit Message

```text
docs(report): define failure analysis api
```

## Next Task

Slice 14 Task 3: Add FailureAnalysis and Report model schema.
