# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 23: Frontend Build Baseline.

## Current Task

Slice 23 Task 2: Fix frontend build TypeScript baseline.

## Product Value Answer

After this task, the frontend production build passes again, while existing
frontend behavior and Vitest coverage remain unchanged.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/10-v2-scope-options.md`
9. `docs/implementation/slices/slice-23-frontend-build-baseline.md`
10. latest frontend build output

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud CI/provider integration, RBAC, tenants,
  permissions, and frontend redesign docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-22-jmeter-local-execution.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-23-frontend-build-baseline.md
frontend/src/api/client.ts
frontend/src/api/automation.ts
frontend/src/api/cases.ts
frontend/src/api/cicd.ts
frontend/src/api/execution.ts
frontend/src/api/reporting.ts
frontend/src/api/requirements.ts
frontend/src/views/ai-workbench/AiWorkbenchView.vue
frontend/src/views/cicd/CicdQualityCenterView.vue
frontend/src/views/requirements/RequirementReviewView.vue
```

Build-baseline task. Keep edits to narrow TypeScript fixes. Do not add product
features, backend code, migrations, package upgrades, redesign work, or broad
refactors.

## Verification Command

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: frontend build, frontend tests, and diff check pass.

## Acceptance

- `npm --prefix frontend run build` passes.
- Full frontend Vitest suite still passes.
- Type fixes are narrow and preserve existing request payloads, visible text,
  routes, and page behavior.
- Does not add product features, package upgrades, backend code, migrations, or
  broad refactors.

## Commit Message

```text
fix(frontend): restore build baseline
```

## Next Task

Slice 23 Completion Gate.
