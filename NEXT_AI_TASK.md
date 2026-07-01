# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 29: Execution Run Manifest.

## Current Task

Slice 29 Task 3: Add frontend run manifest panel.

## Product Value Answer

After this task, the pytest execution page shows a compact run manifest from
existing TestRun fields and Artifact metadata.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/10-v2-scope-options.md`
9. `docs/implementation/slices/slice-29-execution-run-manifest.md`
10. `memory/08-session-handoff.md`
11. `memory/07-dev-log.md`

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
docs/implementation/slices/slice-29-execution-run-manifest.md
frontend/src/views/execution/PytestExecutionView.vue
frontend/src/views/execution/PytestExecutionView.spec.ts
```

Frontend task. Do not add backend feature code, migrations, package upgrades,
artifact upload/mutation/delete, cloud storage,
external provider integration, RBAC, tenants, permissions, broad redesign work,
report generation behavior, runner behavior changes, quality gate computation
changes, RAG runtime, or MCP runtime.

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Expected result: pytest execution focused frontend test, frontend build, and
diff check pass.

## Acceptance

- Pytest execution page shows a compact `执行运行清单` panel.
- Panel shows command, working directory, runner mode, workspace, repository
  read-only flag, and network policy in readable Chinese.
- Panel shows runtime/dependency/environment snapshot rows and output artifact
  availability.
- Local links are rendered only for persisted local Artifact ids.
- Missing snapshots remain visible as unavailable.
- Page does not add new execution actions, rerun controls, report generation,
  remote provider controls, or broad redesign.

## Commit Message

```text
feat(frontend): show execution run manifest
```

## Next Task

Slice 29 Task 4: Add execution run manifest golden smoke.
