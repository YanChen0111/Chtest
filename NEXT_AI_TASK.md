# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 16: UnitTestPatch And Regression.

## Current Task

Task 3: Add UnitTestPatch and QualityGateDecision model/schema.

## Product Value Answer

After this task, Chtest can persist UnitTestPatch and QualityGateDecision
records aligned with the review-gated CI/CD quality contract.

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
backend/app/modules/cicd/models.py
backend/app/modules/cicd/schemas.py
backend/app/tests/api/test_unit_test_patch_regression.py
docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

Do not apply patches or run tests in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Expected result: focused UnitTestPatch/QualityGateDecision model/schema tests
pass.

## Acceptance

- Defines UnitTestPatch fields from the data model contract.
- Defines QualityGateDecision fields from the data model contract.
- Defines create/read schemas for patch and gate records.
- Does not apply patches or run tests in this task.
- Updates handoff and sets the next task to PatchScopeGate service.

## Commit Message

```text
feat(cicd): add unit test patch schema
```

## Next Task

Slice 16 Task 4: Add PatchScopeGate service.
