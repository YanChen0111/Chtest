# Slice 38: Execution Output Artifact Definitions

## Goal

Extract duplicated execution run manifest output artifact definitions into a
small shared frontend module.

Slices 32 and 33 centralized run manifest row building and display. The pages
still repeat the same output artifact definition objects for stdout, stderr,
parsed output, JUnit, and runner-specific outputs before passing them into the
manifest helper.

## Product Value Answer

After this slice, execution pages share one tested source for run manifest
output artifact definitions, so artifact labels stay consistent without
changing manifest row semantics, artifact filters, or runner behavior.

## Preconditions

- Slice 32 extracts `buildExecutionRunManifestRows`.
- Slice 33 extracts the shared execution run manifest panel.
- Slice 37 extracts shared execution display helpers.

## Non-goals

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No changes to artifact lookup, artifact filtering, artifact link behavior,
  run manifest row-building semantics, result data, metric calculations,
  parsed_result semantics, report generation, FailureAnalysis,
  QualityGateDecision, or AutomationDraft behavior.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.

## Slice Boundary

- Add `executionOutputArtifacts.ts`.
- Add focused tests for shared and runner-specific definitions.
- Replace page-local `outputArtifacts` arrays with shared constants.
- Preserve each page's existing manifest output artifact ordering.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Output Artifact Definitions task plan | done | `rg -n "Slice 38|Execution Output Artifact Definitions|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-38-execution-output-artifact-definitions.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add shared execution output artifact definitions | done | `npm --prefix frontend run test -- --run src/views/execution/executionOutputArtifacts.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Use shared output artifact definitions in execution pages | done | `npm --prefix frontend run test -- --run src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; manifest output ordering preserved |
| Slice 38 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; no backend changes made |

## Task 1: Add Execution Output Artifact Definitions Task Plan

Goal: Define the smallest shared manifest output definition slice after display
helper extraction.

Expected files:

- `docs/implementation/slices/slice-38-execution-output-artifact-definitions.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Slice 38|Execution Output Artifact Definitions|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-38-execution-output-artifact-definitions.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Acceptance:

- Creates the Slice 38 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to frontend output artifact definition extraction for
  existing execution pages.

Commit message:

```text
docs(v2): add execution output artifact definitions plan
```

## Task 2: Add Shared Execution Output Artifact Definitions

Goal: Add shared constants for common and runner-specific manifest output
artifact definitions.

Expected files:

- `frontend/src/views/execution/executionOutputArtifacts.ts`
- `frontend/src/views/execution/executionOutputArtifacts.spec.ts`
- `docs/implementation/slices/slice-38-execution-output-artifact-definitions.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/executionOutputArtifacts.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Definitions include the existing labels for stdout, stderr, parsed output,
  JUnit, coverage, Playwright trace/screenshot, Newman JSON, and JMeter JTL.
- Definitions are readonly and compatible with `buildExecutionRunManifestRows`.
- No execution page behavior changes yet.

Commit message:

```text
feat(frontend): add execution output artifact definitions
```

## Task 3: Use Shared Output Artifact Definitions In Execution Pages

Goal: Replace duplicated page-local manifest output artifact definitions.

Expected files:

- `frontend/src/views/execution/executionOutputArtifacts.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-38-execution-output-artifact-definitions.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Four execution pages use shared manifest output artifact definitions.
- Existing output artifact ordering and labels are preserved.
- Runner-specific artifact filters, manifest rows, metrics panel, artifact
  table, result table, and start/refresh behavior remain intact.

Commit message:

```text
feat(frontend): reuse execution output artifact definitions
```

## Completion Gate

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Slice 38 task table records completed tasks.
- Focused output definitions, display helper, result table, metrics, artifact
  table, manifest, helper, and execution page tests pass.
- Frontend build passes.
- Existing backend run manifest golden still passes.
- No unexpected dirty-worktree scope is touched.

Commit message:

```text
docs(v2): complete execution output artifact definitions slice
```
