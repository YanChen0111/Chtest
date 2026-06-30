# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 15: CI/CD Quality Center Foundation.

## Current Task

Task 7: Add CI/CD Quality Center frontend shell.

## Product Value Answer

After this task, users can create local_diff CICDRun records and inspect changed
file/risk analysis evidence in the workbench.

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
frontend/src/router/index.ts
frontend/src/stores/index.ts
docs/implementation/slices/slice-15-cicd-quality-center.md
```

Do not show merge/release decisions or remote CI provider controls in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

Expected result: focused frontend workbench tests pass.

## Acceptance

- Adds workbench navigation for `CI/CD 质量中心`.
- Creates a local_diff CICDRun from project/repository/base/head inputs and
  diff text fixture.
- Shows changed files, file roles, risk levels, risk reasons, and analysis
  artifact references.
- Does not show merge/release decisions or remote CI provider controls.
- Updates handoff and sets the next task to CI/CD Quality Center golden smoke.

## Commit Message

```text
feat(frontend): add cicd quality shell
```

## Next Task

Slice 15 Task 8: Add CI/CD Quality Center golden smoke.
