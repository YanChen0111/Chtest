# Slice 33: Execution Run Manifest Panel

## Goal

Extract the duplicated execution run manifest display block into a small shared
frontend component.

Slice 32 centralized row-building semantics. The remaining duplication is the
same panel template, table slots, columns, and scoped CSS repeated in pytest,
Playwright, Newman, and JMeter pages. This slice removes that display drift
without redesigning the execution pages.

## Product Value Answer

After this slice, execution pages render the run manifest through one tested
panel component, so the same command, workspace, safety policy, snapshot, and
artifact availability UI stays consistent across local runners.

## Preconditions

- Slice 29 defines the run manifest evidence boundary.
- Slice 30 adds the panel to Playwright, Newman, and JMeter.
- Slice 31 standardizes availability labels.
- Slice 32 centralizes manifest row construction.

## Non-goals

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.
- No artifact upload, mutation, delete, cloud storage, remote provider fetch,
  report generation, FailureAnalysis, QualityGateDecision, AutomationRepair,
  AutomationDraft, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.
- No changes to runner-specific metrics, runner-specific artifact tables, or
  execution start/refresh behavior.

## Slice Boundary

- Add `ExecutionRunManifestPanel.vue`.
- Move the common manifest descriptions/table/slots/styles into the component.
- Keep pages responsible for their own runner-specific output artifact list and
  manifest rows.
- Preserve local link behavior and missing evidence visibility.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Run Manifest Panel task plan | done | `rg -n "Slice 33|Execution Run Manifest Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-33-execution-run-manifest-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add shared execution run manifest panel component | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Use shared panel in execution pages | done | `npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Slice 33 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | `7` frontend files / `11` tests passed; build passed with existing Vite chunk warning; backend golden `1 passed`; `git diff --check` clean |

## Task 1: Add Execution Run Manifest Panel Task Plan

Goal: Define the smallest shared component slice after helper extraction.

Expected files:

- `docs/implementation/slices/slice-33-execution-run-manifest-panel.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Slice 33|Execution Run Manifest Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-33-execution-run-manifest-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Acceptance:

- Creates the Slice 33 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to frontend component extraction for existing manifest UI.

Commit message:

```text
docs(v2): add execution run manifest panel plan
```

## Task 2: Add Shared Execution Run Manifest Panel Component

Goal: Add a shared component that renders an existing run and manifest rows.

Expected files:

- `frontend/src/views/execution/ExecutionRunManifestPanel.vue`
- `frontend/src/views/execution/ExecutionRunManifestPanel.spec.ts`
- `docs/implementation/slices/slice-33-execution-run-manifest-panel.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Component shows command, working directory, runner mode, run workspace,
  repository read-only policy, network policy, and manifest rows.
- Component opens only rows whose `artifactId` is present.
- Component keeps unavailable rows visible and not openable.
- No execution page behavior changes yet.

Commit message:

```text
feat(frontend): add execution run manifest panel
```

## Task 3: Use Shared Panel In Execution Pages

Goal: Replace duplicated manifest panel markup in execution pages with the
shared component.

Expected files:

- `frontend/src/views/execution/ExecutionRunManifestPanel.vue`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-33-execution-run-manifest-panel.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Four execution pages render the shared manifest panel.
- Runner-specific metrics and artifact tables remain intact.
- Local links still render only for persisted local Artifact ids.
- Missing runtime/snapshot/output evidence remains visible and not openable.

Commit message:

```text
feat(frontend): reuse execution run manifest panel
```

## Completion Gate

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Slice 33 task table records completed tasks.
- Focused component, helper, and execution page tests pass.
- Frontend build passes.
- Existing backend run manifest golden still passes.
- No unexpected dirty-worktree scope is touched.

Commit message:

```text
docs(v2): complete execution run manifest panel slice
```
