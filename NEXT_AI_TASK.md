# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 16: UnitTestPatch And Regression.

## Current Task

Task 1: Add UnitTestPatch And Regression task plan.

## Product Value Answer

After this task, Slice 16 has a scoped implementation plan for UnitTestPatch,
PatchScopeGate, pytest regression, and QualityGateDecision evidence.

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
docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

This is a planning-only task. Do not add product code.

## Verification Command

```bash
test -f docs/implementation/slices/slice-16-unit-test-patch-regression.md && rg -n "UnitTestPatch|PatchScopeGate|Verification Command|Non-goals" docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

Expected result: Slice 16 task plan exists and contains scoped task table,
verification commands, and non-goals.

## Acceptance

- Creates `docs/implementation/slices/slice-16-unit-test-patch-regression.md`.
- Splits Slice 16 into small contract/model/API/frontend/golden/completion tasks.
- Scope covers UnitTestPatch, PatchScopeGate, pytest regression, and
  QualityGateDecision evidence.
- Explicitly excludes merge/release actions, remote CI provider integration,
  RAG runtime, MCP runtime, RBAC, tenants, and permissions.
- Updates handoff and sets the next task to Slice 16 contract boundary.

## Commit Message

```text
docs(cicd): add unit test patch task plan
```

## Next Task

Slice 16 Task 2: Add UnitTestPatch and regression contract boundary.
