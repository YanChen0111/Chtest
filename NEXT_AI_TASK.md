# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 16: UnitTestPatch And Regression.

## Current Task

Task 10: Add UnitTestPatch frontend shell.

## Product Value Answer

After this task, users can review UnitTestPatch candidates, scope gate results,
test/regression evidence, QualityGateDecision, and CI/CD quality report
references in the frontend CI/CD Quality Center shell.

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
frontend/src/api/cicd.ts
frontend/src/stores/cicd.ts
frontend/src/views/cicd/CicdQualityCenterView.vue
frontend/src/views/cicd/CicdQualityCenterView.spec.ts
docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

Only add the frontend shell for the existing local-first CI/CD quality workflow.
Do not expose merge, release, deployment, remote CI provider controls, PR
comments, RAG runtime, MCP runtime, RBAC, tenants, or permissions.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: frontend CI/CD Quality Center tests pass.

## Acceptance

- Shows UnitTestPatch diff, test intent, coverage target, and scope gate result.
- Supports approve/reject actions.
- Shows new-test and regression TestRun summaries.
- Shows QualityGateDecision and report artifact references.
- Does not expose merge, release, deployment, remote CI provider, or PR controls.
- Updates handoff and sets the next task to UnitTestPatch golden smoke.

## Commit Message

```text
feat(frontend): add unit test patch shell
```

## Next Task

Slice 16 Task 11: Add UnitTestPatch golden smoke.
