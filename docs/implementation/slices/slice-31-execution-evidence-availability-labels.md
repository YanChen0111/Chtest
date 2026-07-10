# Slice 31: Execution Evidence Availability Labels

## Goal

Standardize the user-facing availability labels used by existing evidence
surfaces without changing evidence storage, runner behavior, or API shape.

Slices 24-30 made local artifacts openable and added compact evidence
summaries. The next small improvement is label consistency: users should see
the same meanings for local-openable evidence, missing evidence, inert external
references, and metadata-only unsafe evidence.

## Product Value Answer

After this slice, a test engineer can scan evidence rows across execution
surfaces and understand the availability state without learning page-specific
phrasing for the same underlying evidence boundary.

## Preconditions

- Slice 24 provides read-only local artifact download links for persisted local
  Artifact ids.
- Slices 25-30 already distinguish available local artifacts from missing or
  unavailable evidence in reports, quality gates, TestRuns, and runner pages.
- Execution pages currently duplicate label and row-building logic after Slice
  30 parity.
- Existing contracts already preserve the important boundary: only persisted
  local Artifact ids can become local open links.

## Non-goals

- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.
- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No artifact upload, mutation, delete, sharing, cloud storage, signed URLs,
  remote provider fetch, external artifact download, or broad artifact browser.
- No report generation, FailureAnalysis, QualityGateDecision, AutomationRepair,
  AutomationDraft, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.

## Slice Boundary

- Define a small frontend availability-label helper for existing evidence
  states:
  - local persisted Artifact: openable;
  - missing runtime/snapshot/output evidence: unavailable;
  - inert external reference: not locally openable;
  - unsafe metadata-only artifact: metadata only.
- Use the helper first in execution run manifest rows.
- Keep page-specific runner metrics and artifact tables intact.
- Keep all local links derived only from ids present in `TestRunRead.artifacts`.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Evidence Availability Labels task plan | done | `rg -n "Slice 31|Execution Evidence Availability Labels|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-31-execution-evidence-availability-labels.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add execution evidence availability label helper | done | `npm --prefix frontend run test -- --run src/views/execution/evidenceAvailability.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Apply availability labels to execution run manifests | done | `npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Slice 31 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; build has existing Vite chunk warning |

## Task 1: Add Execution Evidence Availability Labels Task Plan

Goal: Define the smallest frontend-only consistency slice after Slice 30.

Expected files:

- `docs/implementation/slices/slice-31-execution-evidence-availability-labels.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Slice 31|Execution Evidence Availability Labels|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-31-execution-evidence-availability-labels.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

Acceptance:

- Creates the Slice 31 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to frontend label consistency for existing evidence.
- Does not touch deleted knowledge-card, prompt, skill, contract, or fixture
  scope.

Commit message:

```text
docs(v2): add execution evidence availability labels plan
```

## Task 2: Add Execution Evidence Availability Label Helper

Goal: Add a small frontend helper that maps evidence availability states to
stable display labels and action labels.

Expected files:

- `frontend/src/views/execution/evidenceAvailability.ts`
- `frontend/src/views/execution/evidenceAvailability.spec.ts`
- `docs/implementation/slices/slice-31-execution-evidence-availability-labels.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/evidenceAvailability.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Helper returns stable labels for local-openable, unavailable, external
  reference, and metadata-only states.
- Helper does not create URLs, inspect files, fetch remote data, mutate
  artifacts, or depend on backend changes.
- No execution page behavior changes yet.

Commit message:

```text
feat(frontend): add evidence availability labels
```

## Task 3: Apply Availability Labels To Execution Run Manifests

Goal: Use the helper in existing execution run manifest rows without changing
runner-specific evidence.

Expected files:

- `frontend/src/views/execution/evidenceAvailability.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-31-execution-evidence-availability-labels.md`
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

- Execution run manifest rows use shared availability labels.
- Local links still render only for persisted local Artifact ids.
- Missing runtime/snapshot/output evidence remains visible and not openable.
- Runner-specific metrics and artifact tables remain intact.
- No backend/API/runner/report behavior changes.

Commit message:

```text
feat(frontend): standardize execution evidence labels
```

## Completion Gate

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Slice 31 task table records completed tasks.
- Focused helper and execution page tests pass.
- Frontend build passes.
- Existing backend run manifest golden still passes.
- No unexpected dirty-worktree scope is touched.

Commit message:

```text
docs(v2): complete execution evidence availability labels slice
```
