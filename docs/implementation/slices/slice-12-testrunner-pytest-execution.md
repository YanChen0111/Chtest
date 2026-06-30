# Slice 12: TestRunner Pytest Execution Task Plan

## Goal

Add approval-gated pytest execution for approved AutomationDraft or configured
TestCommand inputs, with TestRun/TestResult records and execution artifacts.

This slice must stay limited to pytest execution and evidence capture. It must
not add Playwright execution, reports, CI/CD quality gates, RAG runtime, MCP
runtime, RBAC, tenants, or permissions.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`

## Preconditions

- Slice 11 AutomationDraft Foundation is complete.
- Approved AutomationDraft records exist and remain review-gated before
  execution.
- Project TestCommand configuration exists in the project core.
- Artifact metadata and LocalArtifactStore exist for stdout/stderr/JUnit/runtime
  evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestRunner Pytest Execution task plan | done | `test -f docs/implementation/slices/slice-12-testrunner-pytest-execution.md && rg -n "TestRunner Pytest Execution|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-12-testrunner-pytest-execution.md` | `bcd8974` | scoped Slice 12 plan |
| Add TestRun API contract and task boundary | done | `rg -n "TestRun|POST /api/test-runs|TestResult" docs/contracts/02-api-contract.md docs/implementation/slices/slice-12-testrunner-pytest-execution.md` | `db5de11` | contract-first execution endpoint shape |
| Add TestRun and TestResult model/schema | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q` | pending commit | model/schema only |
| Add pytest runner adapter | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q` | - | allowlisted local subprocess, no Playwright |
| Add TestRun API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q` | - | create/get run and parsed results |
| Add pytest execution frontend shell | planned | `npm --prefix frontend run test -- --run` | - | execute approved draft/configured command, show evidence |
| Add pytest execution golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_testrunner_pytest.py -q` | - | approved golden draft executes controlled pytest |
| Slice 12 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/golden/test_testrunner_pytest.py -q && npm --prefix frontend run test -- --run` | - | docs and handoff only |

## Task 1: Add TestRun API Contract And Task Boundary

Goal: Define the minimal approval-gated pytest execution API before
implementation.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestRun|POST /api/test-runs|TestResult" docs/contracts/02-api-contract.md docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

Acceptance:

- Contract defines `POST /api/test-runs` and `GET /api/test-runs/{id}`.
- Request supports approved automation_draft_id or configured test_command_id.
- Response includes TestRun status, command, runner_mode, artifact ids,
  parsed_result, and TestResult items.
- Contract states V1 pytest execution is allowlisted and local-first.
- No Playwright, reports, CI/CD quality, RAG runtime, MCP runtime, RBAC,
  tenants, or permissions are added.

Commit message:

```text
docs(execution): define pytest test run api
```

## Task 2: Add TestRun And TestResult Model Schema

Goal: Add persisted TestRun/TestResult records aligned with the data model
contract.

Expected files:

- `backend/app/modules/execution/__init__.py`
- `backend/app/modules/execution/models.py`
- `backend/app/modules/execution/schemas.py`
- `backend/app/tests/api/test_testrunner_pytest.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

Acceptance:

- Defines TestRun fields from the data model contract.
- Defines TestResult fields from the data model contract.
- Defines request/read schemas for create/get run.
- Does not execute subprocesses in this task.

Commit message:

```text
feat(execution): add test run model schema
```

## Task 3: Add Pytest Runner Adapter

Goal: Execute an allowlisted pytest command and parse basic stdout/stderr/JUnit
evidence into a deterministic result structure.

Expected files:

- `backend/app/modules/execution/pytest_runner.py`
- `backend/app/modules/execution/schemas.py`
- `backend/app/tests/api/test_testrunner_pytest.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

Acceptance:

- Runs only pytest-style commands assembled by backend code, not arbitrary shell
  strings.
- Captures stdout, stderr, exit_code, duration_ms, and parsed pass/fail counts.
- Supports local_subprocess runner mode first.
- Network is disabled by default in TestRun metadata.
- Does not add Docker runner or Playwright in this task.

Commit message:

```text
feat(execution): add pytest runner adapter
```

## Task 4: Add TestRun API

Goal: Create and retrieve pytest TestRun records with TestResult children and
artifact metadata.

Expected files:

- `backend/app/modules/execution/router.py`
- `backend/app/modules/execution/service.py`
- `backend/app/modules/execution/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_testrunner_pytest.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

Acceptance:

- Adds `POST /api/test-runs`.
- Adds `GET /api/test-runs/{id}`.
- Requires approved AutomationDraft or configured TestCommand input.
- Persists stdout/stderr/JUnit/runtime artifact metadata where available.
- Persists TestResult rows from parsed pytest output.
- Does not generate reports or quality gate decisions.

Commit message:

```text
feat(execution): add pytest test run api
```

## Task 5: Add Pytest Execution Frontend Shell

Goal: Let users start a controlled pytest run and inspect run evidence from the
workbench.

Expected files:

- `frontend/src/api/execution.ts`
- `frontend/src/stores/execution.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Adds workbench navigation for pytest execution.
- Starts a run from approved AutomationDraft or configured TestCommand.
- Shows run status, command, exit code, duration, stdout/stderr artifact
  references, parsed result summary, and TestResult rows.
- Does not add Playwright, reports, CI/CD quality, RAG runtime, MCP runtime,
  RBAC, tenants, or permissions.

Commit message:

```text
feat(frontend): add pytest execution shell
```

## Task 6: Add Pytest Execution Golden Smoke

Goal: Prove an approved golden AutomationDraft can be executed through the
controlled pytest runner and produce evidence records.

Expected files:

- `backend/app/tests/golden/test_testrunner_pytest.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_testrunner_pytest.py -q
```

Acceptance:

- Reuses golden reviewed case -> approved AutomationDraft setup.
- Executes a controlled pytest command against a small generated fixture test.
- Persists TestRun and TestResult records.
- Captures stdout/stderr artifact metadata.
- Does not create Report or QualityGateDecision records.

Non-goals:

- Do not add Playwright execution.
- Do not add reports or CI/CD quality gate.
- Do not run arbitrary shell strings.

Commit message:

```text
test(golden): add pytest execution smoke
```

## Slice Completion Gate

- TestRun/TestResult contracts are aligned.
- Pytest runner adapter captures execution evidence.
- TestRun API can create and fetch controlled pytest runs.
- Frontend can start and inspect pytest runs.
- Golden smoke proves approved draft -> pytest evidence.
- No Playwright, reports, CI/CD quality, RAG runtime, MCP runtime, RBAC,
  tenants, or permissions are added.
