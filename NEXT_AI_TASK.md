# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 16: UnitTestPatch And Regression.

## Current Task

Task 7: Add new-test and regression API.

## Product Value Answer

After this task, Chtest can record new-test and regression execution evidence
for a CICDRun without computing the final quality gate.

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
backend/app/modules/cicd/schemas.py
backend/app/modules/cicd/service.py
backend/app/tests/api/test_unit_test_patch_regression.py
docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

Only create CICD-linked TestRun evidence through allowlisted local command
records. Do not compute QualityGateDecision or create reports in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Expected result: focused new-test and regression API tests pass.

## Acceptance

- Adds `POST /api/cicd/runs/{id}/run-new-tests`.
- Adds `POST /api/cicd/runs/{id}/select-regression`.
- Adds `POST /api/cicd/runs/{id}/run-regression`.
- Creates TestRun records with `cicd_run_id` set.
- Requires an applied UnitTestPatch when `unit_test_patch_id` is provided.
- Writes `regression_plan.json` artifact metadata.
- Uses allowlisted TestCommand records rather than arbitrary shell strings.
- Does not compute QualityGateDecision or create Reports.
- Updates handoff and sets the next task to QualityGateDecision API.

## Commit Message

```text
feat(cicd): add new test regression api
```

## Next Task

Slice 16 Task 8: Add QualityGateDecision API.
