# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 15: CI/CD Quality Center Foundation.

## Current Task

Slice 15 completion gate.

## Product Value Answer

After this task, Slice 15 has verified API, frontend, golden smoke, and handoff
evidence for local-first CI/CD Quality Center foundation.

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
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-15-cicd-quality-center.md
```

Do not add product behavior in this task. This is verification and handoff only.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q && npm --prefix frontend run test -- --run
```

Expected result: Slice 15 backend API, golden smoke, and frontend tests pass.

## Acceptance

- Run the Slice 15 completion verification command.
- Mark Slice 15 completion gate done in the slice task plan if verification
  passes.
- Record verification evidence in handoff and dev log.
- Set the next task to Slice 16 Task 1: UnitTestPatch And Regression task plan.
- Do not add product behavior, broad refactors, UnitTestPatch, regression,
  QualityGateDecision, Report, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions.

## Commit Message

```text
docs(cicd): complete quality center slice
```

## Next Task

Slice 16 Task 1: Add UnitTestPatch And Regression task plan.
