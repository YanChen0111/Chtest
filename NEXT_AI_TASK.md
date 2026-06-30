# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 15: CI/CD Quality Center Foundation.

## Current Task

Task 8: Add CI/CD Quality Center golden smoke.

## Product Value Answer

After this task, Chtest has a golden smoke proving local diff evidence can
create a CICDRun, changed files, and a mock analysis artifact.

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
backend/app/tests/golden/test_cicd_quality_center_golden.py
```

Do not create UnitTestPatch, QualityGateDecision, TestRun, or Report records in
this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_center_golden.py -q
```

Expected result: focused CI/CD Quality Center golden smoke passes.

## Acceptance

- Uses `docs/fixtures/03-golden-cicd-quality.md` as scenario intent.
- Creates Project/Repository fixture records.
- Creates CICDRun from local diff input.
- Persists CICDChangedFile rows and risk_analysis artifact metadata.
- Verifies no UnitTestPatch, QualityGateDecision, TestRun, or Report records are
  created in Slice 15.
- Updates handoff and sets the next task to Slice 15 completion gate.

## Commit Message

```text
test(golden): add cicd quality smoke
```

## Next Task

Slice 15 completion gate.
