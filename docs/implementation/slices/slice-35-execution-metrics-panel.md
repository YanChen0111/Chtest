# Slice 35: Execution Metrics Panel

## Goal

Extract the duplicated execution metrics tile display into a small shared
frontend component.

Slices 33 and 34 extracted the shared run manifest and artifact table displays.
The remaining local duplication in the same execution frontend surface is the
metric tile template and CSS repeated in pytest, Playwright, Newman, and JMeter
pages.

## Product Value Answer

After this slice, execution pages render runner metrics through one tested tile
component, so metric labels and values remain runner-specific while the display
stays consistent across local runners.

## Preconditions

- Slice 33 extracts the shared execution run manifest panel.
- Slice 34 extracts the shared execution artifact table panel.
- Each execution page already computes its own runner-specific `metricItems`.

## Non-goals

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No changes to metric calculations, parsed_result semantics, result tables,
  artifact filters, artifact links, execution start/refresh behavior, report
  generation, FailureAnalysis, QualityGateDecision, or AutomationDraft behavior.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.

## Slice Boundary

- Add `ExecutionMetricsPanel.vue`.
- Move the common metric tile template and scoped tile styles into the
  component.
- Keep pages responsible for building their own `metricItems` arrays.
- Preserve current metric labels and values exactly.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Metrics Panel task plan | done | `rg -n "Slice 35|Execution Metrics Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-35-execution-metrics-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add shared execution metrics panel component | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionMetricsPanel.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Use shared metrics panel in execution pages | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; runner-specific metric computation preserved |
| Slice 35 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; no backend changes made |

## Task 1: Add Execution Metrics Panel Task Plan

Goal: Define the smallest shared metric tile display slice after artifact table
panel extraction.

Expected files:

- `docs/implementation/slices/slice-35-execution-metrics-panel.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Slice 35|Execution Metrics Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-35-execution-metrics-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Acceptance:

- Creates the Slice 35 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to frontend metric tile display extraction for existing
  execution pages.

Commit message:

```text
docs(v2): add execution metrics panel plan
```

## Task 2: Add Shared Execution Metrics Panel Component

Goal: Add a shared component that renders metric label/value tiles.

Expected files:

- `frontend/src/views/execution/ExecutionMetricsPanel.vue`
- `frontend/src/views/execution/ExecutionMetricsPanel.spec.ts`
- `docs/implementation/slices/slice-35-execution-metrics-panel.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionMetricsPanel.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Component renders metric labels and values in the existing tile style.
- Component accepts page-owned metric items without computing runner metrics.
- Component handles numeric and string values.
- No execution page behavior changes yet.

Commit message:

```text
feat(frontend): add execution metrics panel
```

## Task 3: Use Shared Metrics Panel In Execution Pages

Goal: Replace duplicated metric tile markup in execution pages with the shared
component.

Expected files:

- `frontend/src/views/execution/ExecutionMetricsPanel.vue`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-35-execution-metrics-panel.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Four execution pages render the shared metrics panel.
- Runner-specific metric item computation remains page-owned.
- Run manifest, artifact table, result table, and start/refresh behavior remain
  intact.

Commit message:

```text
feat(frontend): reuse execution metrics panel
```

## Completion Gate

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Slice 35 task table records completed tasks.
- Focused component, artifact table, manifest, helper, and execution page tests
  pass.
- Frontend build passes.
- Existing backend run manifest golden still passes.
- No unexpected dirty-worktree scope is touched.

Commit message:

```text
docs(v2): complete execution metrics panel slice
```
