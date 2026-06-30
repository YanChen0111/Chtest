# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 15: CI/CD Quality Center Foundation.

## Current Task

Task 6: Add CI/CD analyze API.

## Product Value Answer

After this task, Chtest can add deterministic mock risk analysis evidence to a
local-first CICDRun.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
backend/app/modules/cicd/router.py
backend/app/modules/cicd/service.py
backend/app/modules/cicd/schemas.py
backend/app/tests/api/test_cicd_quality_center.py
docs/implementation/slices/slice-15-cicd-quality-center.md
```

Do not create UnitTestPatch, regression plan, QualityGateDecision, TestRun, or
Report records in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

Expected result: focused CI/CD analyze API tests pass.

## Acceptance

- Adds `POST /api/cicd/runs/{id}/analyze`.
- Creates a succeeded AITask with mock CICDChangeAnalysisAgent output.
- Updates CICDRun status to `analyzed` and overall_risk from changed files.
- Writes risk_analysis artifact metadata owned by CICDRun.
- Does not create UnitTestPatch, regression plan, QualityGateDecision, TestRun,
  or Report records.
- Updates handoff and sets the next task to CI/CD Quality Center frontend shell.

## Commit Message

```text
feat(cicd): add change analysis api
```

## Next Task

Slice 15 Task 7: Add CI/CD Quality Center frontend shell.
