# Slice 34: Execution Artifact Table Panel

## Goal

Extract the duplicated execution artifact table display into a small shared
frontend component.

Slices 29-33 made run manifest evidence consistent across pytest, Playwright,
Newman, and JMeter execution pages. The remaining local duplication in the same
safe execution surface is the artifact table markup, columns, local-open link
slot, and section styling.

## Product Value Answer

After this slice, execution pages render persisted local artifacts through one
tested table component, so artifact type, path, metadata, and open-link behavior
stay consistent across local runners.

## Preconditions

- Slice 24 defines safe local artifact opening.
- Slice 29 defines the execution run manifest evidence boundary.
- Slice 33 extracts the shared execution run manifest panel.

## Non-goals

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  external artifact fetch, remote provider integration, broad artifact browser,
  indexing, search, dashboards, report generation, FailureAnalysis, or
  QualityGateDecision changes.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.
- No changes to runner-specific artifact filters, metrics, result tables, or
  execution start/refresh behavior.

## Slice Boundary

- Add `ExecutionArtifactTable.vue`.
- Move the common artifact table section, columns, action slot, and local-open
  link rendering into the component.
- Keep pages responsible for selecting runner-specific artifacts.
- Preserve local links only for persisted local Artifact ids already returned
  in `TestRunRead.artifacts`.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Artifact Table Panel task plan | done | `rg -n "Slice 34|Execution Artifact Table Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-34-execution-artifact-table-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add shared execution artifact table component | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionArtifactTable.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Use shared artifact table in execution pages | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; runner-specific filters preserved |
| Slice 34 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; no backend changes made |

## Task 1: Add Execution Artifact Table Panel Task Plan

Goal: Define the smallest shared artifact table slice after run manifest panel
extraction.

Expected files:

- `docs/implementation/slices/slice-34-execution-artifact-table-panel.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Slice 34|Execution Artifact Table Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-34-execution-artifact-table-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Acceptance:

- Creates the Slice 34 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to frontend artifact table extraction for existing
  execution pages.

Commit message:

```text
docs(v2): add execution artifact table panel plan
```

## Task 2: Add Shared Execution Artifact Table Component

Goal: Add a shared component that renders persisted local artifact rows.

Expected files:

- `frontend/src/views/execution/ExecutionArtifactTable.vue`
- `frontend/src/views/execution/ExecutionArtifactTable.spec.ts`
- `docs/implementation/slices/slice-34-execution-artifact-table-panel.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionArtifactTable.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Component renders artifact type, path, a size or MIME metadata column, and a
  local open link.
- Component uses existing `artifactDownloadUrl(record.id)` behavior.
- Component does not fetch, upload, mutate, delete, or infer artifact content.
- No execution page behavior changes yet.

Commit message:

```text
feat(frontend): add execution artifact table panel
```

## Task 3: Use Shared Artifact Table In Execution Pages

Goal: Replace duplicated artifact table markup in execution pages with the
shared component.

Expected files:

- `frontend/src/views/execution/ExecutionArtifactTable.vue`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-34-execution-artifact-table-panel.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Four execution pages render the shared artifact table component.
- Runner-specific artifact filtering remains page-owned.
- Local open links still render for persisted local Artifact ids.
- Runner-specific metrics and result tables remain intact.

Commit message:

```text
feat(frontend): reuse execution artifact table panel
```

## Completion Gate

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Slice 34 task table records completed tasks.
- Focused component, manifest, helper, and execution page tests pass.
- Frontend build passes.
- Existing backend run manifest golden still passes.
- No unexpected dirty-worktree scope is touched.

Commit message:

```text
docs(v2): complete execution artifact table panel slice
```
