# Slice 13: Playwright Minimal Loop Task Plan

## Goal

Add the minimal Playwright execution loop after pytest execution is stable:
approved Playwright AutomationDraft or configured Playwright TestCommand can
produce a TestRun with stdout/stderr, trace, screenshot, and parsed result
evidence.

This slice must stay limited to Playwright smoke execution and evidence
inspection. It must not add reports, failure analysis, CI/CD quality gates, RAG
runtime, MCP runtime, RBAC, tenants, permissions, low-code UI automation, or
broad browser grid/device matrix work.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/product/03-user-journey-and-page-prd.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/fixtures/02-golden-case-to-playwright.md`
- `docs/fixtures/04-real-user-scenarios.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`

## Preconditions

- Slice 12 TestRunner Pytest Execution is complete.
- TestRun/TestResult models, schemas, API, and frontend execution shell exist.
- AutomationDraft approval gates exist.
- Artifact metadata and LocalArtifactStore exist.
- V1 TestCommand allowlist already recognizes Playwright-style commands.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Playwright Minimal Loop task plan | done | `test -f docs/implementation/slices/slice-13-playwright-minimal-loop.md && rg -n "Playwright Minimal Loop|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-13-playwright-minimal-loop.md` | `f882a4a` | scoped Slice 13 plan |
| Add Playwright execution API contract and task boundary | done | `rg -n "Playwright|POST /api/test-runs|playwright_trace|screenshot" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-13-playwright-minimal-loop.md` | `1205e95` | contract-first Playwright endpoint shape |
| Add Playwright runner adapter | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q` | `b7c65f2` | allowlisted local command wrapper |
| Add Playwright execution API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q` | pending commit | create/get Playwright TestRun evidence |
| Add Playwright execution frontend shell | planned | `npm --prefix frontend run test -- --run` | - | inspect trace/screenshot evidence |
| Add Playwright golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q` | - | approved golden draft executes controlled Playwright smoke |
| Slice 13 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q && npm --prefix frontend run test -- --run` | - | docs and handoff only |

## Task 1: Add Playwright Execution API Contract And Task Boundary

Goal: Define the minimal Playwright execution API before implementation.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Playwright|POST /api/test-runs|playwright_trace|screenshot" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-13-playwright-minimal-loop.md
```

Acceptance:

- Contract explicitly maps Playwright execution onto `POST /api/test-runs` and
  `GET /api/test-runs/{id}` with `runner_mode=playwright_local`.
- Request supports approved Playwright AutomationDraft or configured
  Playwright TestCommand.
- Response reuses TestRun/TestResult read shape and includes Playwright trace
  and screenshot artifact metadata.
- Contract states V1 Playwright execution is local-first and allowlisted.
- No reports, failure analysis, CI/CD quality, RAG runtime, MCP runtime, RBAC,
  tenants, permissions, low-code UI automation, or broad browser matrix are
  added.

Commit message:

```text
docs(playwright): define minimal execution api
```

## Task 2: Add Playwright Runner Adapter

Goal: Execute an allowlisted Playwright command and capture deterministic
stdout/stderr, exit code, duration, and trace/screenshot artifact metadata.

Expected files:

- `backend/app/modules/execution/playwright_runner.py`
- `backend/app/modules/execution/schemas.py`
- `backend/app/tests/api/test_playwright_minimal_loop.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q
```

Acceptance:

- Runs only Playwright-style commands assembled by backend code or configured
  TestCommand allowlists.
- Captures stdout, stderr, exit_code, duration_ms, and parsed pass/fail counts.
- Produces metadata entries for Playwright trace and screenshot files when
  available.
- Supports local Playwright execution first.
- Does not add browser grid, Docker runner, pytest changes, reports, or
  CI/CD quality gates.

Commit message:

```text
feat(execution): add playwright runner adapter
```

## Task 3: Add Playwright Execution API

Goal: Create and retrieve Playwright TestRun records with artifact metadata and
TestResult rows.

Expected files:

- `backend/app/modules/execution/router.py`
- `backend/app/modules/execution/service.py`
- `backend/app/modules/execution/playwright_runner.py`
- `backend/app/tests/api/test_playwright_minimal_loop.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q
```

Acceptance:

- Adds the contract-selected Playwright execution endpoint.
- Requires approved Playwright AutomationDraft or configured Playwright
  TestCommand.
- Persists stdout/stderr/trace/screenshot/runtime artifact metadata where
  available.
- Persists TestResult rows from parsed Playwright output.
- Does not generate reports, FailureAnalysis, or QualityGateDecision records.

Commit message:

```text
feat(execution): add playwright minimal api
```

## Task 4: Add Playwright Execution Frontend Shell

Goal: Let users start a controlled Playwright run and inspect browser evidence
from the workbench.

Expected files:

- `frontend/src/api/execution.ts`
- `frontend/src/stores/execution.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Adds workbench navigation for Playwright minimal execution.
- Starts a run from approved Playwright AutomationDraft or configured
  Playwright TestCommand.
- Shows run status, command, exit code, duration, stdout/stderr artifact
  references, trace/screenshot references, parsed result summary, and
  TestResult rows.
- Does not add low-code automation editing, report generation, CI/CD quality,
  RAG runtime, MCP runtime, RBAC, tenants, or permissions.

Commit message:

```text
feat(frontend): add playwright execution shell
```

## Task 5: Add Playwright Golden Smoke

Goal: Prove an approved golden Playwright AutomationDraft can execute through
the controlled runner and produce browser evidence metadata.

Expected files:

- `backend/app/tests/golden/test_playwright_minimal_loop_golden.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q
```

Acceptance:

- Reuses golden reviewed UI case -> approved Playwright AutomationDraft setup.
- Executes a controlled Playwright smoke command against a deterministic local
  fixture page or mocked runner output when browser binaries are unavailable.
- Persists TestRun and TestResult records.
- Captures stdout/stderr plus trace/screenshot artifact metadata.
- Does not create Report, FailureAnalysis, or QualityGateDecision records.

Non-goals:

- Do not add low-code UI automation.
- Do not add reports or CI/CD quality gate.
- Do not run arbitrary shell strings.
- Do not add browser grid or device matrix support.

Commit message:

```text
test(golden): add playwright minimal smoke
```

## Slice Completion Gate

- Playwright execution contract is aligned.
- Playwright runner adapter captures execution evidence.
- Playwright execution API can create and fetch controlled TestRuns.
- Frontend can start and inspect Playwright runs.
- Golden smoke proves approved Playwright draft -> browser evidence metadata.
- No reports, failure analysis, CI/CD quality, RAG runtime, MCP runtime, RBAC,
  tenants, permissions, low-code UI automation, or broad browser matrix are
  added.
