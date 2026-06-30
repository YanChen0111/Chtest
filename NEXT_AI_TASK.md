# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 16: UnitTestPatch And Regression.

## Current Task

Slice 16 completion gate.

## Product Value Answer

After this task, Slice 16 is verified end-to-end across backend API, golden
smoke, and frontend shell.

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
docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

Only run the Slice 16 completion verification and update docs/handoff. Do not
add new product behavior unless a verification failure requires a focused fix.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
npm --prefix frontend run test -- --run
```

Expected result: Slice 16 backend API, golden smoke, and frontend shell tests pass.

## Acceptance

- Runs backend UnitTestPatch regression API tests.
- Runs UnitTestPatch golden smoke.
- Runs frontend CI/CD Quality Center shell tests.
- Confirms Slice 16 task table is complete.
- Updates handoff with completion evidence.
- Sets next task according to the next Slice 17 plan or leaves a clear planning
  handoff if no Slice 17 task exists.

## Commit Message

```text
docs(cicd): complete unit test patch regression slice
```

## Next Task

Slice 17 planning or next V1 priority.
