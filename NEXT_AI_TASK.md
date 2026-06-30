# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 16: UnitTestPatch And Regression.

## Current Task

Task 9: Add CI/CD quality report API.

## Product Value Answer

After this task, Chtest can generate CI/CD quality reports backed by the latest
QualityGateDecision and related evidence artifacts.

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

Only generate local evidence-backed Report records. Do not recompute or override
QualityGateDecision status without evidence, and do not trigger merge, push,
release, deployment, remote CI status updates, or PR comments.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Expected result: focused CI/CD quality report API tests pass.

## Acceptance

- Adds `POST /api/cicd/runs/{id}/generate-report`.
- Creates Report with `report_type=cicd_quality`.
- Report conclusion cites latest QualityGateDecision and evidence artifacts.
- Includes UnitTestPatch/PatchScopeGate/new-test/regression evidence references.
- Does not override QualityGateDecision status without evidence.
- Does not trigger merge, push, release, deployment, remote CI updates, or PR comments.
- Updates handoff and sets the next task to UnitTestPatch frontend shell.

## Commit Message

```text
feat(cicd): add cicd quality report api
```

## Next Task

Slice 16 Task 10: Add UnitTestPatch frontend shell.
