# Slice 29: Execution Run Manifest Task Plan

## Goal

Make each TestRun's execution context understandable before a reviewer opens
individual artifacts.

Recent slices made evidence artifacts openable and added compact summaries for
reports, AI tasks, imported CI evidence, and quality gates. Slice 29 applies the
same readability pattern to the TestRun itself: what command ran, where it ran,
which runner mode and safety policy applied, and which runtime/snapshot/output
artifacts prove the run.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- Recent evidence slices:
  - `docs/implementation/slices/slice-22-jmeter-local-execution.md`
  - `docs/implementation/slices/slice-24-local-artifact-access-links.md`
  - `docs/implementation/slices/slice-25-execution-evidence-summary.md`
  - `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`

## Product Value Answer

After this slice, a test engineer can inspect a TestRun and quickly answer:
which approved command ran, which workspace and runner mode were used, whether
the repository and network policy were safe, which runtime/dependency/environment
snapshots exist, and which local artifacts can be opened.

## Preconditions

- `TestRunRead` already exposes `command`, `working_directory`, `runner_mode`,
  `run_workspace`, `repository_readonly`, `network_enabled`,
  `runtime_artifact_ids`, `dependency_snapshot_artifact_id`,
  `environment_snapshot_artifact_id`, `parsed_result`, and `artifacts`.
- Local artifact access already supports persisted local Artifact rows through
  `GET /api/artifacts/{artifact_id}/download`.
- Existing execution pages already display TestRun status, parsed result, and
  artifact tables for pytest, Playwright, Newman, and JMeter.
- Existing runner behavior is sufficient; this slice does not create new
  runtime artifacts.

## Non-goals

- No runner behavior changes, command execution changes, TestRun state-machine
  changes, ToolDefinition changes, or allowlist expansion.
- No new runner types, Docker runner enablement, browser grid, distributed
  load agents, cloud execution, scheduling, retries, cancellation workflow, or
  live log streaming.
- No report generation, FailureAnalysis, QualityGateDecision, AutomationRepair,
  or AutomationDraft behavior changes.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  broad artifact browser, indexing, search, retention policy, or external
  artifact fetch.
- No remote CI provider calls, PR comments, commit statuses, deploy/release
  controls, credentials, OAuth, webhooks, RBAC, tenants, permissions, RAG
  runtime, MCP runtime, marketplace, package upgrades, or frontend redesign.

## Slice Boundary

- Define a read-only execution run manifest contract derived from existing
  `TestRunRead` fields and existing Artifact metadata.
- Add compact run manifest panels to existing execution pages:
  - approved command and working directory;
  - runner mode, run workspace, repository read-only flag, and network policy;
  - runtime, dependency, environment, stdout/stderr, parsed result, and
    runner-specific artifacts;
  - local open links only for persisted local Artifact ids;
  - missing runtime/dependency/environment snapshots shown as unavailable, not
    hidden.
- Add focused frontend coverage for one execution page and one golden/API smoke
  proving the manifest is derived from existing TestRun evidence only.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Run Manifest task plan | done | `test -f docs/implementation/slices/slice-29-execution-run-manifest.md && rg -n "Execution Run Manifest|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-29-execution-run-manifest.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md && git diff --check` | `22b1071` | planning-only scope |
| Define execution run manifest contract | done | `rg -n "execution run manifest|runtime artifact|dependency snapshot|environment snapshot|network policy" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-29-execution-run-manifest.md && git diff --check` | `d1995eb` | contract-only |
| Add frontend run manifest panel | done | `npm --prefix frontend run test -- --run src/views/execution/PytestExecutionView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | execution page only |
| Add execution run manifest golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q && git diff --check` | pending | evidence-only proof |
| Slice 29 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q && npm --prefix frontend run build && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add Execution Run Manifest Task Plan

Goal: Define the smallest execution run manifest slice before contracts or
frontend changes.

Expected files:

- `docs/implementation/slices/slice-29-execution-run-manifest.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-29-execution-run-manifest.md
rg -n "Execution Run Manifest|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-29-execution-run-manifest.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 29 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to read-only TestRun execution context readability.
- Does not add product code, backend code, frontend code, migrations, package
  upgrades, or tests.

Commit message:

```text
docs(v2): add execution run manifest plan
```

## Task 2: Define Execution Run Manifest Contract

Goal: Clarify the read-only run manifest derived from existing TestRun and
Artifact evidence.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-29-execution-run-manifest.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "execution run manifest|runtime artifact|dependency snapshot|environment snapshot|network policy" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-29-execution-run-manifest.md
git diff --check
```

Acceptance:

- Data/API/artifact contracts define execution run manifest as presentation
  derived from existing TestRun fields and Artifact metadata.
- Contract states missing runtime/dependency/environment snapshots remain
  visible but unavailable.
- Contract states local open links are allowed only for persisted local Artifact
  ids through the existing artifact access endpoint.
- Contract preserves the no runner, report, failure analysis, quality gate,
  remote provider, RAG runtime, or MCP runtime behavior change boundary.

Commit message:

```text
docs(v2): define execution run manifest contract
```

## Task 3: Add Frontend Run Manifest Panel

Goal: Make execution context readable in the pytest execution page first.

Expected files:

- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `docs/implementation/slices/slice-29-execution-run-manifest.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Pytest execution page shows a compact `执行运行清单` panel.
- Panel shows command, working directory, runner mode, workspace, repository
  read-only flag, and network policy in readable Chinese.
- Panel shows runtime/dependency/environment snapshot rows and output artifact
  availability.
- Local links are rendered only for persisted local Artifact ids.
- Missing snapshots remain visible as unavailable.
- Page does not add new execution actions, rerun controls, report generation,
  remote provider controls, or broad redesign.

Commit message:

```text
feat(frontend): show execution run manifest
```

## Task 4: Add Execution Run Manifest Golden Smoke

Goal: Prove the run manifest inputs remain existing TestRun and Artifact
evidence only.

Expected files:

- `backend/app/tests/golden/test_execution_run_manifest_golden.py`
- `docs/fixtures/17-execution-run-manifest-golden.md`
- `docs/implementation/slices/slice-29-execution-run-manifest.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Acceptance:

- Golden proves TestRun read data keeps command, working directory,
  runner_mode, run workspace, repository/network policy, parsed result, and
  artifact metadata available for manifest display.
- Golden proves local artifact ids remain openable through existing artifact
  access when they are persisted local artifacts.
- Golden proves missing snapshot ids remain visible as missing/unavailable
  evidence.
- Golden proves run manifest display inputs do not create Report,
  FailureAnalysis, QualityGateDecision, AutomationRepair, new TestRun, artifact
  mutation, remote provider behavior, RAG runtime, or MCP runtime.

Commit message:

```text
test(golden): add execution run manifest smoke
```

## Slice 29 Completion Gate

Goal: Validate execution run manifest end to end and hand off the next V2 task.

Expected files:

- `docs/implementation/slices/slice-29-execution-run-manifest.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 29 task rows are marked done with commit ids.
- Completion evidence records frontend build/test, golden checks, and diff
  verification.
- Non-goals remain excluded.
- Handoff names the next V2 slice or planning task.

Commit message:

```text
docs(v2): complete execution run manifest slice
```
