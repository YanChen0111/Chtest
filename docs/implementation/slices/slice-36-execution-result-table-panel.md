# Slice 36: Execution Result Table Panel

## Goal

Extract the duplicated execution result table section into a small shared
frontend component.

Slices 33-35 extracted the shared run manifest, artifact table, and metric tile
display blocks. The remaining local duplication in the execution pages is the
result section wrapper and table setup repeated around page-owned result columns
and rows.

## Product Value Answer

After this slice, execution pages render test/assertion/sampler results through
one tested table section component, while each runner keeps its own result
columns and row shaping.

## Preconditions

- Slice 33 extracts the shared execution run manifest panel.
- Slice 34 extracts the shared execution artifact table panel.
- Slice 35 extracts the shared execution metrics panel.

## Non-goals

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No changes to result data, result columns, row shaping, parsed_result
  semantics, metric calculations, artifact filters, artifact links, execution
  start/refresh behavior, report generation, FailureAnalysis, QualityGateDecision,
  or AutomationDraft behavior.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.

## Slice Boundary

- Add `ExecutionResultTable.vue`.
- Move the common result section title, `a-table` wrapper, and section styling
  into the component.
- Keep pages responsible for passing their existing columns and row data.
- Preserve all current result labels, values, row keys, and runner-specific
  result behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Result Table Panel task plan | done | `rg -n "Slice 36|Execution Result Table Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-36-execution-result-table-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add shared execution result table component | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionResultTable.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Use shared result table in execution pages | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionResultTable.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; runner-specific columns and rows preserved |
| Slice 36 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; no backend changes made |

## Task 1: Add Execution Result Table Panel Task Plan

Goal: Define the smallest shared result table section slice after metrics panel
extraction.

Expected files:

- `docs/implementation/slices/slice-36-execution-result-table-panel.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Slice 36|Execution Result Table Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-36-execution-result-table-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Acceptance:

- Creates the Slice 36 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to frontend result table section extraction for existing
  execution pages.

Commit message:

```text
docs(v2): add execution result table panel plan
```

## Task 2: Add Shared Execution Result Table Component

Goal: Add a shared component that renders a titled table from page-owned rows
and columns.

Expected files:

- `frontend/src/views/execution/ExecutionResultTable.vue`
- `frontend/src/views/execution/ExecutionResultTable.spec.ts`
- `docs/implementation/slices/slice-36-execution-result-table-panel.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionResultTable.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Component renders a title and an Arco table.
- Component accepts page-owned columns and rows without reshaping runner result
  data.
- Component preserves `row-key="id"`, small size, and no pagination.
- No execution page behavior changes yet.

Commit message:

```text
feat(frontend): add execution result table panel
```

## Task 3: Use Shared Result Table In Execution Pages

Goal: Replace duplicated result table section markup in execution pages with
the shared component.

Expected files:

- `frontend/src/views/execution/ExecutionResultTable.vue`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-36-execution-result-table-panel.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionResultTable.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Four execution pages render the shared result table section.
- Runner-specific result columns and row data remain page-owned.
- Run manifest, metrics panel, artifact table, and start/refresh behavior remain
  intact.

Commit message:

```text
feat(frontend): reuse execution result table panel
```

## Completion Gate

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Slice 36 task table records completed tasks.
- Focused result table, metrics, artifact table, manifest, helper, and execution
  page tests pass.
- Frontend build passes.
- Existing backend run manifest golden still passes.
- No unexpected dirty-worktree scope is touched.

Commit message:

```text
docs(v2): complete execution result table panel slice
```
