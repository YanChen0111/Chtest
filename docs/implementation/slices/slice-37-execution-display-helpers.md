# Slice 37: Execution Display Helpers

## Goal

Extract duplicated execution status and duration display helpers into a small
shared frontend utility.

Slices 33-36 extracted shared display components for manifests, artifacts,
metrics, and result tables. The remaining safe duplication in the same pages is
small pure display logic for run status labels and run duration labels.

## Product Value Answer

After this slice, execution pages share one tested source for status and timing
labels, so local runner pages stay consistent without changing runner behavior,
result data, or page layout.

## Preconditions

- Slice 33 extracts the shared execution run manifest panel.
- Slice 34 extracts the shared execution artifact table panel.
- Slice 35 extracts the shared execution metrics panel.
- Slice 36 extracts the shared execution result table panel.

## Non-goals

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No page layout extraction, entry form extraction, result data changes, result
  column changes, metric calculation changes, parsed_result semantics changes,
  artifact behavior changes, report generation, FailureAnalysis,
  QualityGateDecision, or AutomationDraft behavior.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.

## Slice Boundary

- Add `executionDisplay.ts`.
- Add focused helper tests.
- Replace page-local `runStatusLabel` functions with the shared helper.
- Replace duplicated run duration label logic with the shared helper.
- Preserve JMeter-specific parsed JTL duration formatting in the JMeter page.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Display Helpers task plan | done | `rg -n "Slice 37|Execution Display Helpers|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-37-execution-display-helpers.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add shared execution display helpers | done | `npm --prefix frontend run test -- --run src/views/execution/executionDisplay.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Use shared display helpers in execution pages | done | `npm --prefix frontend run test -- --run src/views/execution/executionDisplay.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; page layout and runner-specific data preserved |
| Slice 37 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; no backend changes made |

## Task 1: Add Execution Display Helpers Task Plan

Goal: Define the smallest pure helper slice after execution display component
extraction.

Expected files:

- `docs/implementation/slices/slice-37-execution-display-helpers.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Slice 37|Execution Display Helpers|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-37-execution-display-helpers.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Acceptance:

- Creates the Slice 37 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to frontend display helper extraction for existing
  execution pages.

Commit message:

```text
docs(v2): add execution display helpers plan
```

## Task 2: Add Shared Execution Display Helpers

Goal: Add shared helpers for execution status and duration labels.

Expected files:

- `frontend/src/views/execution/executionDisplay.ts`
- `frontend/src/views/execution/executionDisplay.spec.ts`
- `docs/implementation/slices/slice-37-execution-display-helpers.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/executionDisplay.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Helper maps existing statuses to current Chinese labels.
- Helper preserves fallback status text for unknown statuses.
- Helper formats null duration as `运行中` and numeric duration as `<n> ms`.
- No execution page behavior changes yet.

Commit message:

```text
feat(frontend): add execution display helpers
```

## Task 3: Use Shared Display Helpers In Execution Pages

Goal: Replace duplicated page-local status and run duration display helpers.

Expected files:

- `frontend/src/views/execution/executionDisplay.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-37-execution-display-helpers.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/executionDisplay.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Four execution pages use the shared status helper.
- Four execution pages use the shared run duration helper.
- JMeter parsed JTL duration and result-row duration shaping remain page-owned.
- Run manifest, metrics panel, artifact table, result table, and start/refresh
  behavior remain intact.

Commit message:

```text
feat(frontend): reuse execution display helpers
```

## Completion Gate

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Slice 37 task table records completed tasks.
- Focused display helper, result table, metrics, artifact table, manifest,
  helper, and execution page tests pass.
- Frontend build passes.
- Existing backend run manifest golden still passes.
- No unexpected dirty-worktree scope is touched.

Commit message:

```text
docs(v2): complete execution display helpers slice
```
