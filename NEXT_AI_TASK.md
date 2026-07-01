# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 24: Local Artifact Access Links.

## Current Task

Slice 24 Task 4: Add frontend artifact links.

## Product Value Answer

After this task, execution artifact tables expose controlled local artifact
links while preserving the existing metadata display.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-24-local-artifact-access-links.md`
9. existing execution frontend artifact tables

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, and frontend redesign docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-22-jmeter-local-execution.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-23-frontend-build-baseline.md
docs/implementation/slices/slice-24-local-artifact-access-links.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
frontend/src/api/execution.ts
frontend/src/views/execution/PytestExecutionView.vue
frontend/src/views/execution/PlaywrightExecutionView.vue
frontend/src/views/execution/NewmanExecutionView.vue
frontend/src/views/execution/JMeterExecutionView.vue
frontend/src/views/execution/*.spec.ts
```

Frontend links task. Do not add artifact upload/mutation/delete, cloud storage,
external artifact fetch, RBAC, tenants, permissions, package upgrades, broad
redesign work, or backend behavior changes.

## Verification Command

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts
git diff --check
```

Expected result: frontend build, focused execution view tests, and diff check pass.

## Acceptance

- Execution artifact tables expose local artifact access links.
- Links preserve existing artifact metadata display.
- Chinese-facing labels remain readable while keeping product terms such as
  Artifact, TestRun, JTL, and trace unchanged.
- Does not add a broad artifact dashboard, upload, delete, sharing, or cloud
  storage UI.

## Commit Message

```text
feat(frontend): link local execution artifacts
```

## Next Task

Slice 24 Task 5: Add artifact access golden smoke.
