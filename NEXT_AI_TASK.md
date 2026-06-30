# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 16: UnitTestPatch And Regression.

## Current Task

Task 2: Add UnitTestPatch and regression contract boundary.

## Product Value Answer

After this task, the UnitTestPatch and regression contracts are narrowed to the
Slice 16 review-gated local workflow before implementation.

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
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

This is a contract/documentation task. Do not add product code.

## Verification Command

```bash
rg -n "UnitTestPatch|PatchScopeGate|QualityGateDecision|run-new-tests|run-regression" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

Expected result: contracts and Slice 16 plan describe review gates, scope gate,
test/regression evidence, and non-goals.

## Acceptance

- Contract requires UnitTestPatch to be review-gated.
- Contract requires PatchScopeGate to reject non-test path modifications.
- Contract defines new-test and regression TestRun evidence.
- Contract defines QualityGateDecision `passed`, `failed`, and `needs_review`
  evidence requirements.
- Contract excludes merge, push, release, deployment, remote CI provider
  integration, RAG runtime, MCP runtime, RBAC, tenants, and permissions.
- Updates handoff and sets the next task to UnitTestPatch/QualityGateDecision
  model/schema.

## Commit Message

```text
docs(cicd): define unit test patch boundary
```

## Next Task

Slice 16 Task 3: Add UnitTestPatch and QualityGateDecision model/schema.
