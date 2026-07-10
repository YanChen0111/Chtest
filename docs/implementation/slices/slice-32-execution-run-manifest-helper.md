# Slice 32: Execution Run Manifest Helper

## Goal

Extract the duplicated execution run manifest row-building logic into a small
frontend helper while preserving the read-only evidence behavior from Slices 29
through 31.

Slice 30 intentionally duplicated the run manifest panel across runner pages to
ship parity safely. Slice 31 standardized availability labels. The next narrow
step is to reduce drift in the shared manifest row semantics without changing
page layout, runner-specific metrics, artifact tables, or backend contracts.

## Product Value Answer

After this slice, execution pages use one shared helper to decide manifest rows,
labels, availability, and local artifact ids, so future evidence UI changes are
less likely to diverge by runner.

## Preconditions

- Slice 29 defined the execution run manifest behavior.
- Slice 30 added run manifest panels to Playwright, Newman, and JMeter pages.
- Slice 31 added shared evidence availability labels.
- `TestRunRead` already includes command, working directory, runner mode, run
  workspace, repository/network policy, runtime artifact ids, snapshot ids, and
  persisted Artifact metadata.

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
- No shared visual component extraction unless helper extraction proves
  insufficient.

## Slice Boundary

- Add a frontend helper for execution run manifest row construction.
- Keep each runner page in charge of its own output artifact type list and
  runner-specific labels.
- Preserve the local-link invariant: a row is openable only when its id exists
  in persisted `TestRunRead.artifacts`.
- Preserve missing runtime/snapshot/output rows as visible and not openable.
- Preserve runner-specific metrics and artifact tables.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Run Manifest Helper task plan | done | `rg -n "Slice 32|Execution Run Manifest Helper|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-32-execution-run-manifest-helper.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add execution run manifest helper | done | `npm --prefix frontend run test -- --run src/views/execution/executionRunManifest.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Apply run manifest helper to execution pages | done | `npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Slice 32 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; build has existing Vite chunk warning |

## Task 1: Add Execution Run Manifest Helper Task Plan

Goal: Define the smallest helper extraction slice after availability labels.

Expected files:

- `docs/implementation/slices/slice-32-execution-run-manifest-helper.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Slice 32|Execution Run Manifest Helper|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-32-execution-run-manifest-helper.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Acceptance:

- Creates the Slice 32 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to frontend helper extraction for existing manifest rows.
- Does not touch deleted knowledge-card, prompt, skill, contract, or fixture
  scope.

Commit message:

```text
docs(v2): add execution run manifest helper plan
```

## Task 2: Add Execution Run Manifest Helper

Goal: Add a helper that builds run manifest rows from an existing `TestRunRead`
and runner-specific output artifact definitions.

Expected files:

- `frontend/src/views/execution/executionRunManifest.ts`
- `frontend/src/views/execution/executionRunManifest.spec.ts`
- `docs/implementation/slices/slice-32-execution-run-manifest-helper.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/executionRunManifest.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Helper builds runtime, dependency snapshot, environment snapshot, and output
  artifact rows.
- Helper returns local artifact ids only for persisted `TestRunRead.artifacts`
  matches.
- Helper keeps missing runtime/snapshot/output rows visible and not openable.
- Helper reuses Slice 31 availability labels.
- No execution page behavior changes yet.

Commit message:

```text
feat(frontend): add execution run manifest helper
```

## Task 3: Apply Run Manifest Helper To Execution Pages

Goal: Replace duplicated manifest row-building code in execution pages with the
shared helper.

Expected files:

- `frontend/src/views/execution/executionRunManifest.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-32-execution-run-manifest-helper.md`
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

- Execution pages use the shared row-building helper.
- Runner-specific output artifact labels remain correct.
- Local links still render only for persisted local Artifact ids.
- Missing runtime/snapshot/output evidence remains visible and not openable.
- Runner-specific metrics and artifact tables remain intact.

Commit message:

```text
feat(frontend): reuse execution run manifest helper
```

## Completion Gate

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Slice 32 task table records completed tasks.
- Focused helper and execution page tests pass.
- Frontend build passes.
- Existing backend run manifest golden still passes.
- No unexpected dirty-worktree scope is touched.

Commit message:

```text
docs(v2): complete execution run manifest helper slice
```
