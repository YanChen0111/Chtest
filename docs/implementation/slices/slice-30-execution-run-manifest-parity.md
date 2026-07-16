# Slice 30: Execution Run Manifest Parity Task Plan

## Goal

Apply the read-only execution run manifest pattern from the pytest execution
page to the remaining local execution pages.

Slice 29 proved the manifest contract and golden smoke, and added the first
frontend panel to the pytest page. Slice 30 keeps the same evidence-only
boundary and makes Playwright, Newman, and JMeter execution pages answer the
same basic reviewer questions: what command ran, where it ran, which runner
mode and safety policy applied, and which existing artifacts are available.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-29-execution-run-manifest.md`
- `docs/fixtures/17-execution-run-manifest-golden.md`

## Product Value Answer

After this slice, a test engineer sees the same compact execution context and
artifact availability cues across pytest, Playwright, Newman, and JMeter runs,
without learning different evidence layouts for each runner.

## Preconditions

- Slice 29 is complete and verified.
- `TestRunRead` already exposes the manifest inputs used by the pytest page:
  command, working directory, runner mode, run workspace, repository read-only
  flag, network policy, runtime artifact ids, dependency snapshot id,
  environment snapshot id, parsed result, and artifacts.
- Playwright, Newman, and JMeter execution views already load TestRun read data
  and show runner-specific execution evidence.
- Local artifact access already supports persisted local Artifact rows through
  `GET /api/artifacts/{artifact_id}/download`.

## Non-goals

- No backend feature code, migrations, API shape changes, TestRun state-machine
  changes, runner behavior changes, command assembly changes, ToolDefinition
  changes, or allowlist expansion.
- No new runner types, Docker runner enablement, live log streaming,
  scheduling, retries, cancellation workflow, or distributed execution.
- No report generation, FailureAnalysis, QualityGateDecision,
  AutomationRepairTask, AutomationDraft behavior, artifact mutation, artifact
  upload/delete, cloud storage, remote provider fetch, PR comments, RBAC,
  tenants, permissions, RAG runtime, MCP runtime, marketplace, package upgrades,
  or frontend redesign.
- No shared component extraction unless the duplication becomes a concrete
  blocker for keeping the three pages consistent.

## Slice Boundary

- Add the compact execution run manifest panel to:
  - Playwright execution page;
  - Newman execution page;
  - JMeter execution page.
- Reuse the Slice 29 display rules:
  - local links only for ids that match persisted local Artifact rows in
    `TestRunRead.artifacts`;
  - missing runtime/dependency/environment snapshots remain visible as
    unavailable;
  - missing output artifact types remain visible as unavailable;
  - no new execution actions or report controls.
- Add focused frontend coverage for each page and reuse the Slice 29 golden
  smoke as backend evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Run Manifest Parity task plan | done | `rg -n "Execution Run Manifest Parity|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-30-execution-run-manifest-parity.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md && git diff --check` | pending | planning verification passed; `git diff --check` clean |
| Add Playwright run manifest panel | done | `npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Add Newman run manifest panel | done | `npm --prefix frontend run test -- --run src/views/execution/NewmanExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Add JMeter run manifest panel | done | `npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | verification passed; build has existing Vite chunk warning |
| Slice 30 completion gate | done | `npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts && npm --prefix frontend run build && backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | verification passed; build has existing Vite chunk warning |

## Task 1: Add Execution Run Manifest Parity Task Plan

Goal: Define the smallest parity slice for the remaining execution pages before
frontend changes.

Expected files:

- `docs/implementation/slices/slice-30-execution-run-manifest-parity.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Execution Run Manifest Parity|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-30-execution-run-manifest-parity.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 30 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps the scope limited to frontend parity for existing TestRun evidence.
- Does not add backend code, migrations, API changes, package upgrades, or tests
  beyond planning documentation.

Commit message:

```text
docs(v2): add execution run manifest parity plan
```

## Task 2: Add Playwright Run Manifest Panel

Goal: Show the Slice 29 execution run manifest panel in the Playwright
execution page.

Expected files:

- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `docs/implementation/slices/slice-30-execution-run-manifest-parity.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Playwright execution page shows command, working directory, runner mode,
  workspace, repository read-only flag, network policy, snapshots, and output
  artifact availability.
- Local links render only for persisted local Artifact ids.
- Missing snapshots and missing output artifacts remain visible.
- No new execution, rerun, report, remote provider, or redesign behavior is
  added.

Commit message:

```text
feat(frontend): show playwright run manifest
```

## Task 3: Add Newman Run Manifest Panel

Goal: Show the Slice 29 execution run manifest panel in the Newman execution
page.

Expected files:

- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.spec.ts`
- `docs/implementation/slices/slice-30-execution-run-manifest-parity.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/NewmanExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Newman execution page shows the same execution context and artifact
  availability rules as the pytest page.
- Collection/request metrics remain runner-specific evidence, not a replacement
  for the run manifest.
- No backend, runner, report, remote provider, or broad redesign behavior is
  added.

Commit message:

```text
feat(frontend): show newman run manifest
```

## Task 4: Add JMeter Run Manifest Panel

Goal: Show the Slice 29 execution run manifest panel in the JMeter execution
page.

Expected files:

- `frontend/src/views/execution/JMeterExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.spec.ts`
- `docs/implementation/slices/slice-30-execution-run-manifest-parity.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- JMeter execution page shows the same execution context and artifact
  availability rules as the pytest page.
- Sampler/assertion/latency metrics remain runner-specific evidence, not a
  replacement for the run manifest.
- No backend, runner, report, remote provider, or broad redesign behavior is
  added.

Commit message:

```text
feat(frontend): show jmeter run manifest
```

## Slice 30 Completion Gate

Goal: Validate execution run manifest parity across local execution pages and
hand off the next V2 task.

Expected files:

- `docs/implementation/slices/slice-30-execution-run-manifest-parity.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Playwright, Newman, and JMeter execution pages use the Slice 29 manifest
  rules.
- The Slice 29 golden smoke still passes.
- Non-goals remain excluded.
- Handoff names the next V2 slice or planning task.

Commit message:

```text
docs(v2): complete execution run manifest parity
```
